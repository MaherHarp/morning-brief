# Morning Brief (Free iMessage Digest)

This project sends a daily Morning Brief to your iCloud email so it shows up in iMessage.

## Data Sources
- BBC World RSS by region
- ESPN Top Headlines RSS
- Hacker News Firebase API

## Setup
1. Create a GitHub repo and add these files.
2. In GitHub: Settings → Secrets and variables → Actions → Secrets
   - SMTP_USER: your Gmail address
   - SMTP_PASS: Gmail App Password (requires 2FA)
   - TO_EMAIL: your iCloud email (enabled in iMessage)
   - FROM_EMAIL: optional (defaults to SMTP_USER)
3. Enable iMessage for your iCloud email: iPhone Settings → Messages → Send & Receive.

## Schedule
Runs at 6:30am America/Detroit with DST-safe dual UTC cron entries.

## Manual test
Run the workflow via "Run workflow" in GitHub Actions.

