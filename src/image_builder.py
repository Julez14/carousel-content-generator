"""Image processing utilities for adding text overlays."""

from __future__ import annotations

import io
import textwrap
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple

from .config import TEXT_SETTINGS, IMAGE_QUALITY


def _get_font(size: int) -> ImageFont.ImageFont:
    """Get a stylish TrueType font for social media text rendering with emoji support.
    
    Args:
        size: Font size in pixels.
        
    Returns:
        ImageFont object, prioritizing fonts that support both text and emojis.
    """
    # Prioritize fonts that support both modern styling and emojis
    font_paths = [
        # macOS - Fonts with emoji support
        "/System/Library/Fonts/SF-Pro.ttf",           # Apple's modern font with emoji support
        "/System/Library/Fonts/SF-Pro-Display.ttf",   # SF Pro Display variant
        "/System/Library/Fonts/Helvetica.ttc",        # Helvetica with some emoji support
        "/Library/Fonts/Arial Unicode MS.ttf",        # Arial Unicode with emoji support
        "/System/Library/Fonts/PingFang.ttc",         # Good emoji support
        "/System/Library/Fonts/Hiragino Sans GB.ttc", # Good emoji support
        "/System/Library/Fonts/Apple Symbols.ttf",    # Apple symbols font
        
        # Windows - Fonts with emoji support
        "/Windows/Fonts/seguiemj.ttf",          # Segoe UI Emoji (dedicated emoji font)
        "/Windows/Fonts/seguisym.ttf",          # Segoe UI Symbol
        "/Windows/Fonts/segoeui.ttf",           # Segoe UI with some emoji support
        "/Windows/Fonts/calibri.ttf",           # Clean and modern
        "/Windows/Fonts/arialuni.ttf",          # Arial Unicode MS
        
        # Linux - Fonts with emoji support
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",  # Google Noto Color Emoji
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        
        # Fallback fonts with basic emoji support
        "/System/Library/Fonts/Avenir.ttc",     # Elegant and readable
        "/System/Library/Fonts/Futura.ttc",     # Geometric, modern
        "/System/Library/Fonts/Arial Black.ttf", # Bold and impactful
        "/System/Library/Fonts/Impact.ttf",     # Strong impact
        "/Windows/Fonts/arialbd.ttf",           # Arial Bold
        "/Windows/Fonts/impact.ttf",            # Impact font
        "/System/Library/Fonts/Arial.ttf",
        "/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            continue
    
    # Fall back to default font
    try:
        return ImageFont.load_default()
    except (OSError, IOError):
        return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    """Wrap text to fit within specified width.
    
    Args:
        text: Text to wrap.
        font: Font to use for measurement.
        max_width: Maximum width in pixels.
        
    Returns:
        List of text lines.
    """
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        # Test if adding this word would exceed the width
        test_line = ' '.join(current_line + [word])
        
        # Use standard PIL text measurement (emojis will be approximately sized)
        bbox = font.getbbox(test_line)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # Single word is too long, add it anyway
                lines.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines


def _draw_text_with_stroke(
    draw: ImageDraw.ImageDraw,
    position: Tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill_color: Tuple[int, int, int],
    stroke_color: Tuple[int, int, int],
    stroke_width: int
) -> None:
    """Draw text with stroke/outline effect.
    
    Args:
        draw: ImageDraw object.
        position: (x, y) position for text.
        text: Text to draw.
        font: Font to use.
        fill_color: RGB color for text fill.
        stroke_color: RGB color for stroke.
        stroke_width: Stroke width in pixels.
    """
    x, y = position
    
    # Draw stroke by drawing text in stroke color at offset positions
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    
    # Draw main text
    draw.text((x, y), text, font=font, fill=fill_color)


def add_overlay(img_bytes: bytes, text: str, text_settings: dict = None) -> bytes:
    """Add text overlay to an image.
    
    Args:
        img_bytes: Source image as bytes.
        text: Text to overlay on the image. The last character (emoji) will be removed.
        text_settings: Optional custom text settings dict. If None, uses default TEXT_SETTINGS.
        
    Returns:
        Modified image as bytes with text overlay.
    """
    # Use default settings if none provided
    if text_settings is None:
        text_settings = TEXT_SETTINGS
        
    try:
        # Load the image
        image = Image.open(io.BytesIO(img_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
    except Exception as e:
        raise ValueError(f"Cannot process image: {str(e)}. Image might be corrupted or in unsupported format (HEIC files need conversion to JPG/PNG).")
    
    # Remove the last character (emoji) from the text, handling trailing punctuation
    if text:
        # Remove trailing punctuation first (., !, ?, etc.)
        text = text.rstrip('.,!?;: ')
        # Then remove the last character (which should be the emoji)
        if text:
            text = text[:-1].strip()
    
    # Get image dimensions
    img_width, img_height = image.size
    
    # Create drawing context
    draw = ImageDraw.Draw(image)
    
    # Calculate font size as a percentage of the smaller image dimension for consistent scaling
    base_font_size = text_settings["font_size"]
    min_dimension = min(img_width, img_height)
    
    # Scale font size based on image dimensions while maintaining reasonable bounds
    # For a 1080x1920 image, min_dimension is 1080, so font_size would be ~43px (4% of 1080)
    # For a 720x1280 image, min_dimension is 720, so font_size would be ~29px (4% of 720)
    font_size = max(24, min(80, int(min_dimension * 0.04)))  # Between 24px and 80px
    
    font = _get_font(font_size)
    
    # Calculate maximum text width (90% of image width)
    max_width = int(img_width * (text_settings["max_width_percent"] / 100))
    
    # Wrap text to fit within max width
    lines = _wrap_text(text, font, max_width)
    
    # Calculate total text height
    line_height = font.getbbox("Ay")[3] - font.getbbox("Ay")[1]  # Height of a typical line
    total_text_height = line_height * len(lines)
    
    # Calculate starting Y position (80% down from top)
    y_position = int(img_height * (text_settings["y_position_percent"] / 100))
    start_y = y_position - (total_text_height // 2)
    
    # Draw each line of text
    for i, line in enumerate(lines):
        # Calculate text width for centering
        bbox = font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        
        # Center the text horizontally
        x_position = (img_width - text_width) // 2
        line_y = start_y + (i * line_height)
        
        # Draw text with stroke
        _draw_text_with_stroke(
            draw=draw,
            position=(x_position, line_y),
            text=line,
            font=font,
            fill_color=text_settings["font_color"],
            stroke_color=text_settings["stroke_color"],
            stroke_width=text_settings["stroke_width"]
        )
    
    # Save the modified image to bytes with TikTok-compatible settings
    output_buffer = io.BytesIO()
    
    # Ensure we're using RGB mode (not RGBA or other modes)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Use TikTok-compatible JPEG settings
    image.save(
        output_buffer, 
        format='JPEG', 
        quality=IMAGE_QUALITY,
        optimize=True,
        progressive=False,  # TikTok might not like progressive JPEGs
        subsampling=0,      # No chroma subsampling for better quality
        qtables='web_high'  # Use web-optimized quantization tables
    )
    
    return output_buffer.getvalue()


def convert_to_jpeg(img_bytes: bytes) -> bytes:
    """Convert any image format to TikTok-compatible JPEG.
    
    Args:
        img_bytes: Source image as bytes (can be PNG, JPEG, etc.).
        
    Returns:
        JPEG image as bytes.
    """
    try:
        # Load the image
        image = Image.open(io.BytesIO(img_bytes))
        
        # Convert to RGB if necessary (removes alpha channel from PNG)
        if image.mode != 'RGB':
            # If it has transparency, create white background
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                else:
                    background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                image = background
            else:
                image = image.convert('RGB')
                
    except Exception as e:
        raise ValueError(f"Cannot process image: {str(e)}. Image might be corrupted or in unsupported format.")
    
    # Save as TikTok-compatible JPEG
    output_buffer = io.BytesIO()
    
    # Use TikTok-compatible JPEG settings
    image.save(
        output_buffer, 
        format='JPEG', 
        quality=IMAGE_QUALITY,
        optimize=True,
        progressive=False,  # TikTok might not like progressive JPEGs
        subsampling=0,      # No chroma subsampling for better quality
        qtables='web_high'  # Use web-optimized quantization tables
    )
    
    return output_buffer.getvalue()


def resize_image_for_tiktok(img_bytes: bytes, target_size: Tuple[int, int] = (1080, 1920)) -> bytes:
    """Resize image to TikTok dimensions (9:16 aspect ratio) by cropping from center.
    
    Args:
        img_bytes: Source image as bytes.
        target_size: Target dimensions (width, height). Default is 1080x1920 (9:16 ratio).
        
    Returns:
        Resized and cropped image as bytes that fills the entire frame.
    """
    image = Image.open(io.BytesIO(img_bytes))
    
    # Convert to RGB if necessary
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Get original and target dimensions
    original_width, original_height = image.size
    target_width, target_height = target_size
    
    # Calculate target aspect ratio and current aspect ratio
    target_ratio = target_width / target_height  # 9:16 = 0.5625
    current_ratio = original_width / original_height
    
    if current_ratio > target_ratio:
        # Image is wider than target - crop from sides
        # Scale based on height to fill vertically
        scale = target_height / original_height
        new_width = int(original_width * scale)
        new_height = target_height
        
        # Resize first
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Crop from center horizontally
        crop_x = (new_width - target_width) // 2
        final_image = resized_image.crop((crop_x, 0, crop_x + target_width, target_height))
        
    else:
        # Image is taller than target - crop from top/bottom
        # Scale based on width to fill horizontally
        scale = target_width / original_width
        new_width = target_width
        new_height = int(original_height * scale)
        
        # Resize first
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Crop from center vertically
        crop_y = (new_height - target_height) // 2
        final_image = resized_image.crop((0, crop_y, target_width, crop_y + target_height))
    
    # Save to bytes with TikTok-compatible settings
    output_buffer = io.BytesIO()
    
    # Use TikTok-compatible JPEG settings
    final_image.save(
        output_buffer, 
        format='JPEG', 
        quality=IMAGE_QUALITY,
        optimize=True,
        progressive=False,  # TikTok might not like progressive JPEGs
        subsampling=0,      # No chroma subsampling for better quality
        qtables='web_high'  # Use web-optimized quantization tables
    )
    
    return output_buffer.getvalue() 