# GitHub Actions Workflow Setup

This project uses **parallel GitHub Actions workflows** where each TikTok account has its own dedicated workflow file. This provides better isolation, scalability, and reliability.

## Adding New Accounts

### Step 1: Add Account to Config

Add the new account to `src/config.py`:

```python
ACCOUNTS = [
    {
        "name": "@account1",
        "tiktok_username": "account1",
        "post_times": ["07:00", "22:00"],
        "webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
    },
    {
        "name": "@your_new_account",
        "tiktok_username": "your_new_account",
        "post_times": ["07:00", "22:00"],  # Or custom times
        "webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
    },
]
```

**Note:** Each account should have its own Discord webhook URL for separate logging channels.

### Step 2: Generate Workflow File

Use the provided utility script:

```bash
python3 generate_workflow.py your_new_account
```

This will create `.github/workflows/post-your_new_account.yml` with the correct schedule.

### Step 3: Commit and Push

```bash
git add .
git commit -m "Add workflow for @your_new_account"
git push
```

## Manual Testing

### Test All Accounts

```bash
python3 -m src.main --once
```

### Test Specific Account

```bash
python3 -m src.main --once --account account1
```

### Test via GitHub Actions

Go to the Actions tab in GitHub and manually trigger any workflow using the "Run workflow" button.

## Architecture Benefits

### ✅ Isolation

- Each account runs independently
- If one account fails, others continue
- Account-specific error logs and artifacts
- **Separate Discord channels** for each account's logs

### ✅ Scalability

- Adding new accounts is simple and automated
- No complex matrix configurations
- Each workflow can have different schedules if needed

### ✅ Reliability

- No single point of failure
- Easier debugging per account
- Independent rate limiting and error handling

### ✅ Maintainability

- Clear separation of concerns
- Easy to disable/enable specific accounts
- Account-specific monitoring and logs
- **Organized Discord logging** with per-account channels

## Timezone Handling

The workflows automatically handle EST/EDT transitions by running duplicate cron jobs:

- **Winter (EST)**: UTC-5 offset
- **Summer (EDT)**: UTC-4 offset

This ensures posts go out at the correct Toronto time year-round.

## Environment Variables

All workflows use the same GitHub Secrets:

- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `UPLOAD_POST_API_KEY`

Plus a workflow-specific `TARGET_ACCOUNT` environment variable that filters to the specific TikTok username.

**Note:** Discord webhook URLs are now configured per-account in `src/config.py` instead of using environment variables.
