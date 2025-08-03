"""Text generation utilities."""

from __future__ import annotations

import random
from typing import Any

from .config import HASHTAG_COUNT, ALL_HASHTAGS, PREGENERATED_HOOKS


def generate_hook(prompt_path: str = None) -> str:
    """Generate a hook headline by randomly selecting from pre-generated hooks.
    
    Args:
        prompt_path: Path to the prompt template file (unused, kept for compatibility).
        
    Returns:
        Randomly selected hook text from pre-generated list.
    """
    return random.choice(PREGENERATED_HOOKS)


def generate_hashtags(seed: str, k: int = HASHTAG_COUNT) -> list[str]:
    """Generate skincare-related hashtags by randomly selecting from a predefined list.
    
    Args:
        seed: Seed text (unused, kept for compatibility).
        k: Number of hashtags to generate.
        
    Returns:
        List of hashtags with # prefix.
    """
    # Randomly select k hashtags from the list
    selected_hashtags = random.sample(ALL_HASHTAGS, min(k, len(ALL_HASHTAGS)))
    
    return selected_hashtags


def create_caption(hook_text: str, hashtags: list[str]) -> str:
    """Create a complete caption with hook text and hashtags.
    
    Args:
        hook_text: The hook text for the post.
        hashtags: List of hashtags to include.
        
    Returns:
        Complete caption string.
    """
    # Combine hook text with hashtags
    hashtags_str = ' '.join(hashtags)
    
    # Add some spacing and formatting
    caption = f"{hook_text}\n\n{hashtags_str}"
    
    return caption


def create_cta_caption(cta_text: str, hashtags: list[str]) -> str:
    """Create a complete caption with CTA text and hashtags.
    
    Args:
        cta_text: The CTA text for the post.
        hashtags: List of hashtags to include.
        
    Returns:
        Complete caption string.
    """
    # Combine CTA text with hashtags
    hashtags_str = ' '.join(hashtags)
    
    # Add some spacing and formatting
    caption = f"{cta_text}\n\n{hashtags_str}"
    
    return caption


def generate_complete_caption(prompt_path: str) -> tuple[str, str]:
    """Generate complete caption with hook and hashtags.
    
    Args:
        prompt_path: Path to the prompt template file.
        
    Returns:
        Tuple of (hook_text, complete_caption).
    """
    # Generate hook text
    hook_text = generate_hook(prompt_path)
    
    # Generate hashtags based on hook
    hashtags = generate_hashtags(hook_text)
    
    # Create complete caption
    caption = create_caption(hook_text, hashtags)
    
    return hook_text, caption


def generate_complete_caption_with_cta(prompt_path: str, cta_text: str) -> tuple[str, str]:
    """Generate complete caption with hook text and CTA-based caption.
    
    Args:
        prompt_path: Path to the prompt template file.
        cta_text: The CTA text to use in the caption.
        
    Returns:
        Tuple of (hook_text, complete_caption_with_cta).
    """
    # Generate hook text
    hook_text = generate_hook(prompt_path)
    
    # Generate hashtags based on hook
    hashtags = generate_hashtags(hook_text)
    
    # Create complete caption using CTA text instead of hook
    caption = create_cta_caption(cta_text, hashtags)
    
    return hook_text, caption 