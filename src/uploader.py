"""Upload-Post API client for uploading carousel images."""

from __future__ import annotations

import requests
from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import MAX_RETRIES


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=4, max=20)
)
def upload_carousel(photos: list[bytes], caption: str, hook_text: str, api_key: str, tiktok_username: str) -> dict[str, Any]:
    """Upload a carousel of photos to TikTok via upload-post API.
    
    Args:
        photos: List of image bytes to upload (max 7 for carousel).
        caption: Caption text for the post (CTA + hashtags).
        hook_text: Hook text to use as the title (with emoji).
        api_key: Upload-Post API key.
        tiktok_username: TikTok username to post to.
        
    Returns:
        API response as dictionary.
        
    Raises:
        requests.RequestException: If the API request fails.
        ValueError: If invalid parameters are provided.
    """
    if not photos:
        raise ValueError("Photos list cannot be empty")
    
    if len(photos) > 7:
        raise ValueError("Maximum 7 photos allowed for carousel")
    
    if not caption.strip():
        raise ValueError("Caption cannot be empty")
    
    if not hook_text.strip():
        raise ValueError("Hook text cannot be empty")
    
    if not api_key:
        raise ValueError("API key is required")
    
    if not tiktok_username:
        raise ValueError("TikTok username is required")
    
    # Prepare headers with API key authentication
    headers = {
        'Authorization': f'Apikey {api_key}'
    }
    
    # Prepare multipart form data for TikTok
    files = []
    
    # Process hook text for title - remove quotes if present but keep emoji
    title_text = hook_text.strip()
    if title_text.startswith('"') and title_text.endswith('"'):
        title_text = title_text[1:-1]
    
    # Ensure title is reasonable length
    if len(title_text) < 10:
        title_text = "Check out these amazing skincare products!"
    
    data = {
        'title': title_text,  # Use hook text as title (keeps emoji)
        'caption': caption,  # Full caption with CTA + hashtags
        'platform[]': 'tiktok',
        'user': tiktok_username,
        'auto_add_music': 'true',  # String format for compatibility
        'disable_comment': 'false',  # Allow comments
        'branded_content': 'false',  # Not branded content
        'photo_cover_index': 0  # Use first photo as cover
    }
    
    # Add each photo to the files list with proper multipart format
    for i, photo_bytes in enumerate(photos):
        # Validate photo data
        if not isinstance(photo_bytes, bytes):
            raise ValueError(f"Photo {i+1} is not bytes data: {type(photo_bytes)}")
        if len(photo_bytes) == 0:
            raise ValueError(f"Photo {i+1} is empty (0 bytes)")
        if len(photo_bytes) > 50 * 1024 * 1024:  # 50MB limit
            raise ValueError(f"Photo {i+1} is too large: {len(photo_bytes)} bytes")
        
        # Check image format and properties for TikTok compatibility
        try:
            from PIL import Image
            import io
            
            img = Image.open(io.BytesIO(photo_bytes))
            print(f"📷 Photo {i+1}: {len(photo_bytes)} bytes, format={img.format}, mode={img.mode}, size={img.size}")
            
            # Verify it's a valid JPEG (should always be JPEG now after conversion)
            if img.format != 'JPEG':
                print(f"❌ Photo {i+1} is not JPEG format: {img.format} - This should not happen!")
                raise ValueError(f"Photo {i+1} should be JPEG but is {img.format}")
            else:
                print(f"✅ Photo {i+1} is JPEG format")
            
            # Check if dimensions are TikTok-compatible (9:16 aspect ratio)
            width, height = img.size
            if width == 1080 and height == 1920:
                print(f"✅ Photo {i+1} has perfect TikTok dimensions: {width}x{height} (9:16 ratio)")
            else:
                print(f"⚠️  Photo {i+1} has unexpected dimensions: {width}x{height} (expected 1080x1920)")
                # Don't fail validation but warn about unexpected size
            
            # Additional TikTok compatibility checks
            if len(photo_bytes) > 10 * 1024 * 1024:  # 10MB
                print(f"⚠️  Photo {i+1} is quite large: {len(photo_bytes)} bytes - TikTok might reject it")
            
            # Check for potential content issues (very basic)
            if img.mode != 'RGB':
                print(f"⚠️  Photo {i+1} is not RGB mode: {img.mode} - This might cause issues")
                
        except Exception as img_error:
            print(f"❌ Error analyzing photo {i+1}: {img_error}")
            raise ValueError(f"Photo {i+1} is not a valid image: {img_error}")
            
        print(f"✅ Photo {i+1} validation passed")
        files.append(
            ('photos[]', (f'image_{i+1}.jpg', photo_bytes, 'image/jpeg'))
        )
    
    # Make the API request to correct endpoint
    try:
        # Add User-Agent header to mimic browser requests
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        # Debug logging before request
        print(f"🚀 Making API request to upload-post.com...")
        print(f"📊 Request data keys: {list(data.keys())}")
        print(f"📊 Request data values:")
        for key, value in data.items():
            if len(str(value)) > 100:  # Truncate very long values
                print(f"   {key}: {str(value)[:100]}...")
            else:
                print(f"   {key}: {value}")
        print(f"📁 Number of files: {len(files)}")
        print(f"📏 Total file sizes: {sum(len(f[1][1]) for f in files)} bytes")
        
        try:
            response = requests.post(
                'https://api.upload-post.com/api/upload_photos',
                headers=headers,
                data=data,
                files=files,
                timeout=120  # 2 minutes timeout for upload
            )
        except Exception as request_error:
            print(f"❌ Request failed before getting response: {request_error}")
            print(f"❌ Request error type: {type(request_error).__name__}")
            raise
        
        # Log response details for debugging
        print(f"✅ API Response Status: {response.status_code}")
        print(f"📋 API Response Headers: {dict(response.headers)}")
        print(f"📏 API Response Content Length: {len(response.content)}")
        print(f"📄 API Response Content Type: {response.headers.get('content-type', 'Not specified')}")
        
        # Show first 200 chars of response for debugging
        response_preview = response.text[:200] if response.text else "(empty response)"
        print(f"📄 API Response Preview: {response_preview}")
        
        # Check for rate limiting before raising for status
        if response.status_code == 429:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            error_message = error_data.get('message', 'Rate limit exceeded')
            raise requests.RequestException(f"Daily upload limit reached: {error_message}")
        
        # For non-success status codes, show the full response
        if response.status_code >= 400:
            print(f"❌ API Error Response: {response.text}")

        response.raise_for_status()
        
        # Check if response is JSON before parsing
        content_type = response.headers.get('content-type', '').lower()
        if not content_type.startswith('application/json'):
            response_text = response.text[:500]  # First 500 chars for debugging
            raise ValueError(f"API returned non-JSON response. Content-Type: {content_type}, Response: {response_text}")
        
        # Parse JSON response
        try:
            result = response.json()
            print(f"✅ Successfully parsed JSON response with keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            # Show full response for debugging
            print(f"🔍 Full API Response:")
            import json
            print(json.dumps(result, indent=2))
            
            # Check for photo_pull_failed error and raise specific exception for retry
            tiktok_result = result.get('results', {}).get('tiktok', {})
            if tiktok_result.get('error') == 'TikTok photo upload failed: photo_pull_failed':
                print(f"🔄 photo_pull_failed error detected - this will trigger a retry")
                raise requests.RequestException("TikTok photo upload failed: photo_pull_failed - temporary error, retrying...")
            
        except ValueError as json_error:
            response_text = response.text[:500]  # First 500 chars for debugging
            print(f"❌ JSON parsing failed. Response text: '{response_text}'")
            raise ValueError(f"Failed to parse JSON response. Raw response: {response_text}") from json_error
        
        return result
        
    except requests.exceptions.RequestException as e:
        # Re-raise with more context
        raise requests.RequestException(f"Upload-Post API request failed: {str(e)}") from e
    
    except ValueError as e:
        # JSON parsing error
        raise ValueError(f"Invalid JSON response from Upload-Post API: {str(e)}") from e
    
    finally:
        # Close file handles to free memory
        for file_tuple in files:
            if hasattr(file_tuple[1], 'close'):
                file_tuple[1].close()

# I dont think this actually works
def validate_api_key(api_key: str) -> bool:
    """Validate an Upload-Post API key.
    
    Args:
        api_key: API key to validate.
        
    Returns:
        True if valid, False otherwise.
    """
    try:
        # Make a simple request to validate the key using proper auth header
        headers = {
            'Authorization': f'Apikey {api_key}'
        }
        response = requests.get(
            'https://api.upload-post.com/api/uploadposts/users/validate-jwt',
            headers=headers,
            timeout=10
        )
        
        return response.status_code == 200
        
    except requests.RequestException:
        return False

# I don't think this works either
def get_upload_status(upload_id: str, api_key: str) -> dict[str, Any]:
    """Get the status of an upload.
    
    Args:
        upload_id: ID of the upload to check.
        api_key: Upload-Post API key.
        
    Returns:
        Status information as dictionary.
    """
    try:
        headers = {
            'Authorization': f'Apikey {api_key}'
        }
        response = requests.get(
            f'https://api.upload-post.com/api/uploadposts/status/{upload_id}',
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
        
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to get upload status: {str(e)}") from e


# Rate limiting helpers
class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60) -> None:
        """Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in time window.
            time_window: Time window in seconds.
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: list[float] = []
    
    def can_make_request(self) -> bool:
        """Check if a request can be made without hitting rate limits.
        
        Returns:
            True if request is allowed, False otherwise.
        """
        import time
        
        current_time = time.time()
        
        # Remove old requests outside the time window
        self.requests = [
            req_time for req_time in self.requests 
            if current_time - req_time < self.time_window
        ]
        
        return len(self.requests) < self.max_requests
    
    def record_request(self) -> None:
        """Record that a request was made."""
        import time
        self.requests.append(time.time())


# Global rate limiter instance
_rate_limiter = RateLimiter()


def upload_carousel_with_rate_limit(photos: list[bytes], caption: str, hook_text: str, api_key: str, tiktok_username: str) -> dict[str, Any]:
    """Upload carousel with built-in rate limiting.
    
    Args:
        photos: List of image bytes to upload.
        caption: Caption text for the post (CTA + hashtags).
        hook_text: Hook text to use as the title (with emoji).
        api_key: Upload-Post API key.
        tiktok_username: TikTok username to post to.
        
    Returns:
        API response as dictionary.
    """
    import time
    
    # Wait if we're hitting rate limits
    while not _rate_limiter.can_make_request():
        time.sleep(1)
    
    # Record the request
    _rate_limiter.record_request()
    
    # Make the upload
    return upload_carousel(photos, caption, hook_text, api_key, tiktok_username) 