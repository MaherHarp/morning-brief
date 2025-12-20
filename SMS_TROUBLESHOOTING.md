# SMS Gateway Troubleshooting

## Problem: Messages not arriving as texts/iMessages

If your workflow runs successfully but you don't receive the message:

### 1. Verify SMS Gateway Format
Make sure your `SMS_GATEWAY` secret is in the correct format:
- ✅ Correct: `5551234567@vtext.com` (Verizon example)
- ❌ Wrong: `555-123-4567@vtext.com` (has dashes)
- ❌ Wrong: `(555) 123-4567@vtext.com` (has parentheses/spaces)
- ❌ Wrong: `+15551234567@vtext.com` (has country code)

### 2. Check Your Carrier
Use the correct gateway for your carrier:
- **Verizon**: `[10digits]@vtext.com`
- **AT&T**: `[10digits]@txt.att.net`
- **T-Mobile**: `[10digits]@tmomail.net`
- **Sprint**: `[10digits]@messaging.sprintpcs.com`
- **US Cellular**: `[10digits]@email.uscc.net`

### 3. Carrier Blocking
Some carriers block emails from external SMTP servers. If messages aren't arriving:
- Try sending a test email manually from your Gmail to the SMS gateway address
- If that works, the issue is with the automation
- If that doesn't work, your carrier may be blocking it

### 4. Message Length
SMS has a ~160 character limit. The updated code creates a shorter version for SMS, but if it's still too long, carriers may reject it.

### 5. Test with a Simple Message
To test if your SMS gateway works, temporarily modify the code to send a simple test message like "Test message" to verify the gateway is working.

### 6. Check Spam/Blocked Messages
- Check if your phone is blocking messages from unknown senders
- Some carriers have spam filters that might block automated messages

### Alternative: Use Your iCloud Email
If SMS gateway doesn't work reliably, you can:
1. Remove the `SMS_GATEWAY` secret
2. Make sure `TO_EMAIL` is set to your iCloud email
3. Check your iCloud email inbox (it won't show as a text, but you'll get the full message)

