#!/usr/bin/env python3
"""
Utility script to generate GitHub Actions workflow files for TikTok accounts.
Usage: python3 generate_workflow.py <tiktok_username>
"""

import sys
import os
from pathlib import Path

def generate_workflow(tiktok_username: str) -> None:
    """Generate a GitHub Actions workflow file for a TikTok account."""
    
    workflow_content = f'''name: TikTok Carousel Auto-Poster - {tiktok_username}

on:
  schedule:
    # 7:00 AM Toronto time (EST) / 8:00 AM Toronto time (EDT)
    - cron: "0 12 * * *" # 7:00 EST = 12:00 UTC, 8:00 EDT = 12:00 UTC

    # 10:00 PM Toronto time (EST) / 11:00 PM Toronto time (EDT)  
    - cron: "0 3 * * *" # 22:00 EST = 03:00 UTC next day, 23:00 EDT = 03:00 UTC next day

  # Allow manual triggering
  workflow_dispatch:

env:
  GOOGLE_SERVICE_ACCOUNT_JSON: ${{{{ secrets.GOOGLE_SERVICE_ACCOUNT_JSON }}}}
  UPLOAD_POST_API_KEY: ${{{{ secrets.UPLOAD_POST_API_KEY }}}}
  TARGET_ACCOUNT: "{tiktok_username}"

jobs:
  post-carousel:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Create service account file
        run: |
          echo '${{{{ secrets.GOOGLE_SERVICE_ACCOUNT_JSON }}}}' > service-account.json
          chmod 600 service-account.json
          echo "Service account file created with $(wc -c < service-account.json) bytes"
          echo "First 100 characters of service account file:"
          head -c 100 service-account.json
          echo ""
          echo "Checking if it's valid JSON..."
          if python3 -m json.tool service-account.json > /dev/null 2>&1; then
            echo "✅ Valid JSON format"
          else
            echo "❌ Invalid JSON format"
            echo "File contents:"
            cat service-account.json
          fi

      - name: Verify environment setup
        run: |
          echo "Python version: $(python --version)"
          echo "Current timezone: $(date)"
          echo "Target account: $TARGET_ACCOUNT"
          echo "Service account file created: $(ls -la service-account.json)"
          echo "Service account file size: $(wc -c < service-account.json) bytes"
          echo "Working directory: $(pwd)"
          echo "Files in directory: $(ls -la)"

      - name: Test API connectivity (for debugging)
        run: |
          python3 test_api_connectivity.py
        env:
          PYTHONPATH: .
          GOOGLE_SERVICE_ACCOUNT_JSON: service-account.json
        continue-on-error: true

      - name: Run carousel generation for {tiktok_username}
        run: |
          python -m src.main --once
        env:
          PYTHONPATH: .
          GOOGLE_SERVICE_ACCOUNT_JSON: service-account.json

      - name: Cleanup sensitive files
        if: always()
        run: |
          rm -f service-account.json

      - name: Upload logs on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: error-logs-{tiktok_username}
          path: |
            *.log
            /tmp/*.log
          retention-days: 7
'''

    # Create the workflow file
    workflows_dir = Path(".github/workflows")
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_file = workflows_dir / f"post-{tiktok_username}.yml"
    
    with open(workflow_file, "w") as f:
        f.write(workflow_content)
    
    print(f"✅ Created workflow file: {workflow_file}")
    print(f"🔧 Don't forget to add the account to src/config.py!")
    print(f"📝 Example config entry:")
    print(f'    {{')
    print(f'        "name": "@{tiktok_username}",')
    print(f'        "tiktok_username": "{tiktok_username}",')
    print(f'        "post_times": ["07:00", "22:00"],')
    print(f'        "webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"')
    print(f'    }},')

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 generate_workflow.py <tiktok_username>")
        print("Example: python3 generate_workflow.py myaccount123")
        sys.exit(1)
    
    tiktok_username = sys.argv[1]
    
    # Show help if requested
    if tiktok_username in ["-h", "--help"]:
        print("Usage: python3 generate_workflow.py <tiktok_username>")
        print("Example: python3 generate_workflow.py myaccount123")
        print("\nThis script generates a GitHub Actions workflow file for a TikTok account.")
        print("The workflow will automatically post at 7 AM and 10 PM Toronto time.")
        sys.exit(0)
    
    # Basic validation - allow letters, numbers, and underscores
    if not tiktok_username.replace("_", "").isalnum():
        print("❌ TikTok username should contain only letters, numbers, and underscores")
        sys.exit(1)
    
    generate_workflow(tiktok_username)

if __name__ == "__main__":
    main() 