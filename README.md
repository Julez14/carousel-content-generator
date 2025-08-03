# TikTok Carousel Content Generator

A fully automated TikTok carousel bot that generates and posts 7-slide carousels 3 times per day across multiple accounts.

## Features

- **Automated Content Generation**: Creates 7-slide carousels (1 hook + 5 screenshots + 1 CTA)
- **Google Drive Integration**: Pulls images from organized Drive folders
- **Multi-Account Support**: Manages multiple accounts with custom posting schedules
- **Zero-Cost Hosting**: Deploys on GitHub Actions
- **Smart Logging**: Discord webhook notifications for success/failure

## Quick Start

1. **Setup Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys and credentials
   ```

3. **Test Locally**
   ```bash
   python src/main.py --once
   ```

## Environment Setup

### Required Services

1. **Google Drive API**

   - Create a Google Cloud Project
   - Enable the Google Drive API
   - Create a Service Account and download the JSON key
   - Share your Drive folders with the service account email

2. **Upload-Post API**

   - Get an API key from https://upload-post.com/

3. **Discord Webhook**
   - Create a webhook in your Discord server

### Environment Variables (.env)

```env
GOOGLE_SERVICE_ACCOUNT_JSON=service-account.json
UPLOAD_POST_API_KEY=up_...
```

## Google Drive Setup

1. Create three folders in your Google Drive:

   - `hook-photos` - Images for hook slides
   - `product-screenshots` - Product screenshot images
   - `cta-photos` - Images for CTA slides

2. **Set Folder Permissions**:

   - Right-click each folder → Share
   - Set to "Anyone with the link can view"
   - OR share directly with your service account email

3. **Get Folder IDs**:
   - Open each folder in browser
   - Copy the folder ID from the URL: `https://drive.google.com/drive/folders/FOLDER_D_HERE`
   - Update the folder IDs in `src/config.py`

### Deployment: GitHub Actions

1. **Fork this repository**

2. **Add Repository Secrets**:
   Go to Settings → Secrets and variables → Actions, add:

   - `GOOGLE_SERVICE_ACCOUNT_JSON` (entire JSON content)
   - `UPLOAD_POST_API_KEY`

3. **Enable Actions**:
   - Go to Actions tab
   - Enable workflows
   - The bot will automatically run at the specified times

## Configuration

### Account Setup

Edit `src/config.py` to configure your accounts:

```python
ACCOUNTS = [
    {
        "name": "@account1", # What you want to call the account
        "tiktok_username": "account1", # Tiktok username must match the username specified in upload-post
        "post_times": ["07:00", "11:00", "15:00", "19:00"], # When to fire the GitHub Action
        "webhook_url": "" # The Discord webhook to send notifications to
    },
    # Add more accounts...
]
```

### CTA Text Options

Customize your call-to-action texts in `src/config.py`:

```python
CTA_TEXTS = [
    "Follow for more tips! 💫",
    "Save this post for later! ✨",
    "Which will you try first? 🤔",
    # Add more CTAs...
]
```

### Google Drive Folder Mappings

Configure your Google Drive folder IDs in `src/config.py`:

```python
DRIVE_FOLDERS = {
    "HOOK": "YOUR_HOOK_FOLDER_ID",
    "SCREEN": "YOUR_PRODUCT_SCREENSHOTS_FOLDER_ID",
    "CTA": "YOUR_CTA_PHOTOS_FOLDER_ID"
}
```

### Hashtag Settings

Adjust the number of hashtags to be randomly selected and the predefined list in `src/config.py`:

```python
HASHTAG_COUNT = 12

ALL_HASHTAGS = [
    "#fyp", "#viral", "#trending", # ... more hashtags
]
```

### Pre-generated Hooks

Modify or add to the list of pre-generated hooks in `src/config.py`:

```python
PREGENERATED_HOOKS = [
    "Products that completely changed my skin texture 😭",
    # ... more hooks
]
```

### Timezone Settings

Set the timezone for scheduling posts in `src/config.py`:

```python
TIMEZONE = "America/Toronto"
```

### Text Overlay Settings

Customize text appearance on slides in `src/config.py`. Separate settings for general text, hooks, and CTAs:

```python
TEXT_SETTINGS = {
    "font_size": 56,
    "font_color": (255, 255, 255),
    "stroke_color": (0, 0, 0),
    "stroke_width": 2,
    "y_position_percent": 70,
    "max_width_percent": 85,
}

HOOK_TEXT_SETTINGS = {
    "font_size": 48,
    "font_color": (255, 255, 255),
    "stroke_color": (0, 0, 0),
    "stroke_width": 2,
    "y_position_percent": 70,
    "max_width_percent": 85,
}

CTA_TEXT_SETTINGS = {
    "font_size": 64,
    "font_color": (255, 255, 255),
    "stroke_color": (0, 0, 0),
    "stroke_width": 2,
    "y_position_percent": 50,
    "max_width_percent": 85,
}
```

### Image Quality and Retry Settings

Adjust image quality and retry parameters for API calls in `src/config.py`:

```python
IMAGE_QUALITY = 90
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
```

## Monitoring

- **Discord Notifications**: Success/failure alerts sent to configured webhook
- **GitHub Actions Logs**: View execution logs in the Actions tab

## Troubleshooting

### Common Issues

1. **Drive Access Denied**

   - Verify service account has access to folders
   - Check folder sharing settings

2. **Upload-Post Failures**
   - Check API key validity
   - Verify image formats and sizes

### Local Testing

Run with debug mode:

```bash
python src/main.py --once --debug
```
