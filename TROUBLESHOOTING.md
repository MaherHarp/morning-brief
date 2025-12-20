# Troubleshooting Gmail SMTP Authentication

## Error: "Username and Password not accepted"

If you see `SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')`, follow these steps:

### Step 1: Enable 2FA on Your Gmail Account

1. Go to https://myaccount.google.com/security
2. Under "Signing in to Google", click "2-Step Verification"
3. Follow the prompts to enable 2FA (you'll need your phone)

### Step 2: Generate a Gmail App Password

**Important:** You MUST use an App Password, NOT your regular Gmail password!

1. After enabling 2FA, go to: https://myaccount.google.com/apppasswords
   - (You can also navigate: Google Account → Security → 2-Step Verification → App passwords)
2. Select "Mail" as the app
3. Select "Other (Custom name)" as the device, and enter "Morning Brief" or any name
4. Click "Generate"
5. Copy the 16-character password (it will look like: `abcd efgh ijkl mnop`)
6. **Remove all spaces** when using it (so it becomes: `abcdefghijklmnop`)

### Step 3: Set GitHub Secrets Correctly

Go to: https://github.com/MaherHarp/morning-brief/settings/secrets/actions

Set these secrets:

- **SMTP_USER**: Your full Gmail address (e.g., `yourname@gmail.com`)
- **SMTP_PASS**: The 16-character App Password (NO SPACES, just the characters)
- **TO_EMAIL**: Your iCloud email address (e.g., `yourname@icloud.com`)
- **FROM_EMAIL**: (Optional) Leave empty or set to your Gmail address

### Step 4: Test Again

1. Go to Actions tab
2. Click "Run workflow" on the "Morning Brief" workflow
3. Check the logs to see if it works

### Common Mistakes

- ❌ Using your regular Gmail password instead of App Password
- ❌ Including spaces in the App Password (remove all spaces)
- ❌ Not enabling 2FA first
- ❌ Typo in the Gmail address or App Password
- ❌ Using the wrong email format (make sure SMTP_USER is your full Gmail address)

