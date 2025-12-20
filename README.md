# Morning Brief (Daily News Digest)

This project sends a daily Morning Brief to your iCloud email at 6:30am America/Detroit.

**Note:** Email-to-SMS gateways are often unreliable or blocked by carriers. This project sends to your iCloud email inbox, where you'll receive the full digest with all links.

## Data Sources
- BBC World RSS by region
- ESPN Top Headlines RSS
- Hacker News Firebase API

## Setup
1. Create a GitHub repo and add these files.
2. In GitHub: Settings → Secrets and variables → Actions → Secrets
   - **SMTP_USER**: your Gmail address (e.g., `you@gmail.com`)
   - **SMTP_PASS**: Gmail App Password (requires 2FA - see TROUBLESHOOTING.md)
   - **TO_EMAIL**: your iCloud email address (e.g., `you@icloud.com`)
   - **FROM_EMAIL**: optional (defaults to SMTP_USER)
   - **SMS_GATEWAY**: optional - if your carrier supports email-to-SMS, you can add this (see SMS_TROUBLESHOOTING.md)

**Recommended:** Just use `TO_EMAIL` with your iCloud address. You'll get the full morning brief in your email inbox.

## Schedule
Runs at 6:30am America/Detroit with DST-safe dual UTC cron entries.

## Manual test
Run the workflow via "Run workflow" in GitHub Actions.

