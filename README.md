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
   - TO_EMAIL: your iCloud email (fallback if SMS_GATEWAY not set)
   - FROM_EMAIL: optional (defaults to SMTP_USER)
   - **SMS_GATEWAY**: Your phone number's email-to-SMS gateway (see below)
3. **To receive as iMessage/text**: Set SMS_GATEWAY secret with your carrier's format:
   - **AT&T**: `[10-digit-phone]@txt.att.net` (e.g., `1234567890@txt.att.net`)
   - **Verizon**: `[10-digit-phone]@vtext.com` (e.g., `1234567890@vtext.com`)
   - **T-Mobile**: `[10-digit-phone]@tmomail.net` (e.g., `1234567890@tmomail.net`)
   - **Sprint**: `[10-digit-phone]@messaging.sprintpcs.com`
   - **US Cellular**: `[10-digit-phone]@email.uscc.net`
   - **Boost Mobile**: `[10-digit-phone]@sms.myboostmobile.com`
   
   Replace `[10-digit-phone]` with your actual 10-digit phone number (no dashes or spaces).

## Schedule
Runs at 6:30am America/Detroit with DST-safe dual UTC cron entries.

## Manual test
Run the workflow via "Run workflow" in GitHub Actions.

