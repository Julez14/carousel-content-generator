"""Main application for TikTok carousel content generator.
Test with `python3 -m src.main --once`
"""

from __future__ import annotations

import argparse
import os
import random
import sys
from datetime import datetime
from typing import Any

import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from .config import ACCOUNTS, CTA_TEXTS, TIMEZONE, HOOK_TEXT_SETTINGS, CTA_TEXT_SETTINGS
from .logger import DiscordWebhookLogger
from .drive_utils import get_random_file_bytes, init_service
from .image_builder import add_overlay, convert_to_jpeg, resize_image_for_tiktok
from .text_gen import generate_complete_caption_with_cta
from .uploader import upload_carousel_with_rate_limit


def setup_environment() -> None:
    """Check that all required environment variables are set."""
    required_vars = [
        'GOOGLE_SERVICE_ACCOUNT_JSON',
        'UPLOAD_POST_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


def create_carousel_post(account: dict[str, Any]) -> None:
    """Create and upload a complete carousel post for an account.
    
    Args:
        account: Account configuration dictionary.
    """
    account_name = account['name']
    tiktok_username = account['tiktok_username']
    webhook_url = account['webhook_url']
    api_key = os.getenv('UPLOAD_POST_API_KEY')
    
    # Initialize logger with account-specific webhook URL
    logger = DiscordWebhookLogger(webhook_url)
    
    try:
        logger.info(f"Starting carousel generation for {account_name}", account_name)
        print(f"🎬 Starting carousel generation for {account_name}")
        
        # Initialize Drive service
        print("🔧 Initializing Google Drive service...")
        drive_service = init_service()
        print("✅ Drive service initialized")
        
        # Step 1: Get hook image and generate text
        print("📸 Getting hook image...")
        hook_image_bytes, hook_url = get_random_file_bytes('HOOK')
        print(f"✅ Hook image retrieved: {len(hook_image_bytes)} bytes")
        
        # Step 1.5: Select CTA text early so we can use it for both caption and CTA slide
        print("📢 Selecting CTA text...")
        cta_text = random.choice(CTA_TEXTS)
        print(f"📢 Selected CTA text: {cta_text}")
        
        print("🤖 Generating hook text and caption...")
        hook_text, complete_caption = generate_complete_caption_with_cta('src/schema/prompt.txt', cta_text)
        print(f"✅ Hook text generated: {hook_text[:50]}...")
        print(f"✅ Caption generated: {len(complete_caption)} chars")
        
        # Step 2: Create hook slide with text overlay
        print("🎨 Creating hook slide with overlay...")
        hook_slide = add_overlay(hook_image_bytes, hook_text, HOOK_TEXT_SETTINGS)
        print(f"✅ Hook slide created: {len(hook_slide)} bytes")
        
        # Resize hook slide to TikTok standard dimensions (9:16 aspect ratio)
        print("📐 Resizing hook slide to TikTok dimensions...")
        hook_slide = resize_image_for_tiktok(hook_slide, target_size=(1080, 1920))
        print(f"✅ Hook slide resized: {len(hook_slide)} bytes (1080x1920)")
        
        # Step 3: Get 5 random screenshot images (no overlays)
        print("📱 Getting screenshot images...")
        screenshot_slides = []
        for i in range(5):
            print(f"📱 Getting screenshot {i+1}/5...")
            screenshot_bytes, screenshot_url = get_random_file_bytes('SCREEN')
            
            # Convert screenshots to JPEG format for TikTok compatibility
            print(f"🔄 Converting screenshot {i+1} to JPEG...")
            jpeg_screenshot = convert_to_jpeg(screenshot_bytes)
            
            # Resize to TikTok standard dimensions (9:16 aspect ratio)
            print(f"📐 Resizing screenshot {i+1} to TikTok dimensions...")
            resized_screenshot = resize_image_for_tiktok(jpeg_screenshot, target_size=(1080, 1920))
            screenshot_slides.append(resized_screenshot)
            print(f"✅ Screenshot {i+1}: {len(resized_screenshot)} bytes (1080x1920)")
        
        # Step 4: Get CTA image and add the selected CTA text
        print("📢 Creating CTA slide...")
        cta_image_bytes, cta_url = get_random_file_bytes('CTA')
        print(f"📢 Using CTA text: {cta_text}")
        cta_slide = add_overlay(cta_image_bytes, cta_text, CTA_TEXT_SETTINGS)
        print(f"✅ CTA slide created: {len(cta_slide)} bytes")
        
        # Resize CTA slide to TikTok standard dimensions (9:16 aspect ratio)
        print("📐 Resizing CTA slide to TikTok dimensions...")
        cta_slide = resize_image_for_tiktok(cta_slide, target_size=(1080, 1920))
        print(f"✅ CTA slide resized: {len(cta_slide)} bytes (1080x1920)")
        
        # Step 5: Combine all slides
        all_slides = [hook_slide] + screenshot_slides + [cta_slide]
        print(f"📊 Total slides prepared: {len(all_slides)}")
        print(f"📊 Total data size: {sum(len(slide) for slide in all_slides)} bytes")
        
        # Step 6: Upload carousel
        logger.info(f"Uploading carousel with {len(all_slides)} slides", account_name)
        print(f"🚀 Starting upload process...")
        
        upload_response = upload_carousel_with_rate_limit(
            photos=all_slides,
            caption=complete_caption,
            hook_text=hook_text,
            api_key=api_key,
            tiktok_username=tiktok_username
        )
        
        # Step 7: Check for errors in the response before claiming success
        print(f"🔍 Checking upload response for errors...")
        tiktok_result = upload_response.get('results', {}).get('tiktok', {})
        
        # Check if TikTok returned an error
        if 'error' in tiktok_result:
            error_message = tiktok_result.get('error', 'Unknown error')
            print(f"❌ TikTok upload failed: {error_message}")
            raise Exception(f"TikTok upload failed: {error_message}")
        
        # Check for success indicators
        post_url = tiktok_result.get('url', 'No URL provided')
        post_status = tiktok_result.get('status', 'Unknown status')
        publish_id = tiktok_result.get('publish_id', 'No ID')
        tiktok_success = tiktok_result.get('success', False)
        
        print(f"📊 TikTok Result Details:")
        print(f"   Success: {tiktok_success}")
        print(f"   Status: {post_status}")
        print(f"   Publish ID: {publish_id}")
        print(f"   URL: {post_url}")
        
        if not tiktok_success or post_status != 'PUBLISH_COMPLETE':
            print(f"⚠️  Upload may not have completed successfully")
            print(f"🔍 Full TikTok response: {tiktok_result}")
            raise Exception(f"TikTok upload incomplete. Status: {post_status}, Success: {tiktok_success}")
        
        print(f"✅ Upload completed successfully!")
        
        success_message = (
            f"Successfully posted carousel!\n"
            f"**Hook:** {hook_text}\n"
            f"**Slides:** {len(all_slides)}\n"
            f"**Status:** {post_status}\n"
            f"**Post ID:** {publish_id}\n"
            f"**URL:** {post_url}"
        )
        
        logger.info(success_message, account_name)
        
    except Exception as e:
        # Check if this is a rate limiting error (including wrapped in RetryError)
        error_str = str(e)
        underlying_error_str = ""
        underlying_exception = None
        
        # If it's a RetryError, get the underlying exception
        if hasattr(e, 'last_attempt') and hasattr(e.last_attempt, 'exception'):
            underlying_exception = e.last_attempt.exception()
            underlying_error_str = str(underlying_exception)
            print(f"🔍 Debug: RetryError detected. Underlying error: {underlying_error_str}")
            print(f"🔍 Debug: Underlying error type: {type(underlying_exception).__name__}")
        
        # Check for specific TikTok upload errors
        if "photo_pull_failed" in error_str.lower() or "photo_pull_failed" in underlying_error_str.lower():
            error_message = f"🔄 TikTok temporarily rejected photos for {account_name}. This is usually temporary and will retry automatically."
            print(f"🔄 {account_name}: TikTok photo_pull_failed error detected.")
            print("   This error usually means TikTok's backend is temporarily unavailable or overloaded.")
            print("   The system will automatically retry on the next scheduled run.")
            print("   If this persists, it might indicate image content policy issues.")
        elif ("daily limit" in error_str.lower() or "429" in error_str or 
              "daily limit" in underlying_error_str.lower() or "429" in underlying_error_str):
            error_message = f"⏰ Daily upload limit reached for {account_name}. Try again tomorrow!"
            print(f"⏰ {account_name}: Daily upload limit reached. The upload-post API allows 3 uploads per day.")
            print("   Your posts will resume tomorrow when the limit resets.")
        else:
            error_message = f"Failed to create carousel post: {str(e)}"
            print(f"❌ Error for {account_name}: {error_message}")
            
            # Print additional debug info for non-rate-limit errors
            if underlying_exception:
                print(f"🔍 Debug: Full underlying error details: {repr(underlying_exception)}")
            print(f"🔍 Debug: Full error details: {repr(e)}")
        
        logger.error(error_message, account_name, e)


def run_single_cycle(target_username: str = None) -> None:
    """Run a single posting cycle for all accounts or a specific account (for testing)."""
    setup_environment()
    
    # Filter accounts if target_username is specified
    accounts_to_process = ACCOUNTS
    if target_username:
        accounts_to_process = [acc for acc in ACCOUNTS if acc['tiktok_username'] == target_username]
        if not accounts_to_process:
            print(f"❌ No account found with TikTok username: {target_username}")
            print(f"Available accounts: {[acc['tiktok_username'] for acc in ACCOUNTS]}")
            return
        
        # Log to the target account's webhook
        target_account = accounts_to_process[0]
        logger = DiscordWebhookLogger(target_account['webhook_url'])
        logger.info(f"Starting single cycle run for account: {target_username}")
    else:
        # For all accounts, we'll log to the first account's webhook for general messages
        # Each account will use its own webhook when processing
        general_logger = DiscordWebhookLogger(ACCOUNTS[0]['webhook_url'])
        general_logger.info("Starting single cycle run for all accounts")
    
    # Process each account
    for account in accounts_to_process:
        print(f"Processing account: {account['name']} (@{account['tiktok_username']})")
        create_carousel_post(account)
    
    # Log completion to appropriate webhook
    if target_username:
        logger.info("Single cycle completed")
    else:
        general_logger.info("Single cycle completed")


def schedule_posts() -> None:
    """Set up scheduled posts using APScheduler."""
    setup_environment()
    
    # Initialize logger for general scheduling messages (use first account's webhook)
    general_logger = DiscordWebhookLogger(ACCOUNTS[0]['webhook_url'])
    
    # Create scheduler with timezone
    timezone = pytz.timezone(TIMEZONE)
    scheduler = BlockingScheduler(timezone=timezone)
    
    general_logger.info("Setting up scheduled posts")
    
    # Schedule jobs for each account and time
    job_count = 0
    for account in ACCOUNTS:
        account_name = account['name']
        post_times = account['post_times']
        
        for post_time in post_times:
            # Parse time (format: "HH:MM")
            hour, minute = map(int, post_time.split(':'))
            
            # Create cron trigger
            trigger = CronTrigger(
                hour=hour,
                minute=minute,
                timezone=timezone
            )
            
            # Add job
            job_id = f"{account_name}_{post_time.replace(':', '')}"
            scheduler.add_job(
                func=create_carousel_post,
                trigger=trigger,
                args=[account],
                id=job_id,
                name=f"Post for {account_name} at {post_time}",
                misfire_grace_time=300  # 5 minutes grace period
            )
            
            job_count += 1
            print(f"Scheduled: {account_name} at {post_time} ({TIMEZONE})")
    
    general_logger.info(f"Scheduled {job_count} jobs across {len(ACCOUNTS)} accounts")
    
    # Print next few upcoming jobs
    print(f"\nNext 5 upcoming jobs:")
    for job in scheduler.get_jobs()[:5]:
        next_run = job.next_run_time
        print(f"  {job.name}: {next_run.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Start the scheduler
    print(f"\nStarting scheduler in {TIMEZONE} timezone...")
    print("Press Ctrl+C to stop")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\nShutting down scheduler...")
        general_logger.info("Scheduler stopped by user")
        scheduler.shutdown()


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='TikTok Carousel Content Generator')
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once for all accounts and exit (for testing)'
    )
    parser.add_argument(
        '--account',
        type=str,
        help='Target specific TikTok username (only works with --once)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with verbose output'
    )
    
    args = parser.parse_args()
    
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        print("Debug mode enabled")
    
    # Check for environment variable for target account (for GitHub Actions)
    target_account = args.account or os.getenv('TARGET_ACCOUNT')
    
    try:
        if args.once:
            if target_account:
                print(f"Running single cycle for account: {target_account}")
            else:
                print("Running single cycle for all accounts...")
            run_single_cycle(target_account)
            print("Single cycle completed")
        else:
            if target_account:
                print("❌ --account parameter only works with --once mode")
                sys.exit(1)
            print("Starting scheduled posting mode...")
            schedule_posts()
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 