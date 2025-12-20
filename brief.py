import os
import re
import smtplib
import ssl
from datetime import datetime, timezone
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

import feedparser
import requests

DETROIT_TZ = ZoneInfo("America/Detroit")

BBC_FEEDS = {
    "Africa": "https://feeds.bbci.co.uk/news/world/africa/rss.xml",
    "Asia": "https://feeds.bbci.co.uk/news/world/asia/rss.xml",
    "Europe": "https://feeds.bbci.co.uk/news/world/europe/rss.xml",
    "Latin America": "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml",
    "US & Canada": "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
    "Australia": "https://feeds.bbci.co.uk/news/world/australia/rss.xml",
}

ESPN_TOP = "https://www.espn.com/espn/rss/news"

HN_TOPSTORIES = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{id}.json"


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def pick_top_from_rss(url: str):
    feed = feedparser.parse(url)
    if not getattr(feed, "entries", None):
        return None
    e = feed.entries[0]
    title = clean(getattr(e, "title", ""))
    link = clean(getattr(e, "link", ""))
    if not title:
        return None
    
    # Get description/summary (RSS feeds usually have one of these)
    description = ""
    if hasattr(e, "summary"):
        description = clean(e.summary)
    elif hasattr(e, "description"):
        description = clean(e.description)
    
    # Clean HTML tags and truncate to ~150 chars
    if description:
        # Remove HTML tags
        description = re.sub(r'<[^>]+>', '', description)
        # Truncate to ~150 chars, ending at word boundary
        if len(description) > 150:
            description = description[:147].rsplit(' ', 1)[0] + "..."
    
    return title, link, description


def fetch_espn_top(n=3):
    feed = feedparser.parse(ESPN_TOP)
    out = []
    for e in getattr(feed, "entries", [])[:n]:
        title = clean(getattr(e, "title", ""))
        link = clean(getattr(e, "link", ""))
        if not title or not link:
            continue
        
        # Get description/summary
        description = ""
        if hasattr(e, "summary"):
            description = clean(e.summary)
        elif hasattr(e, "description"):
            description = clean(e.description)
        
        # Clean HTML tags and truncate
        if description:
            description = re.sub(r'<[^>]+>', '', description)
            if len(description) > 150:
                description = description[:147].rsplit(' ', 1)[0] + "..."
        
        out.append((title, link, description))
    return out


def fetch_hn_top(n=5, timeout=20):
    ids = requests.get(HN_TOPSTORIES, timeout=timeout).json()
    out = []
    for story_id in ids[: max(n * 2, n)]:
        data = requests.get(HN_ITEM.format(id=story_id), timeout=timeout).json()
        if not data or data.get("type") != "story":
            continue
        title = clean(data.get("title", ""))
        link = data.get("url") or f"https://news.ycombinator.com/item?id={story_id}"
        if not title:
            continue
        
        # Hacker News doesn't have descriptions in the API, but we can use the score/comments as context
        score = data.get("score", 0)
        descendants = data.get("descendants", 0)  # number of comments
        
        # Create a simple description from metadata
        description = ""
        if score > 0 or descendants > 0:
            parts = []
            if score > 0:
                parts.append(f"{score} points")
            if descendants > 0:
                parts.append(f"{descendants} comments")
            description = f" • {', '.join(parts)}"
        
        out.append((title, link, description))
        if len(out) >= n:
            break
    return out


def build_digest(now_local: datetime, sms_mode=False):
    lines = []
    date_str = now_local.strftime('%a %b %d')
    
    if sms_mode:
        # Short SMS version (no links, just headlines with short descriptions)
        lines.append(f"📰 Brief {date_str}")
        lines.append("🌍 World:")
        for region, url in list(BBC_FEEDS.items())[:3]:  # Only top 3 regions for SMS
            top = pick_top_from_rss(url)
            if top:
                title, _, desc = top
                # Truncate long titles
                short_title = title[:50] + "..." if len(title) > 50 else title
                if desc:
                    short_desc = desc[:60] + "..." if len(desc) > 60 else desc
                    lines.append(f"• {region}: {short_title}")
                    lines.append(f"  {short_desc}")
                else:
                    lines.append(f"• {region}: {short_title}")
        
        lines.append("⚽ Sports:")
        for title, _, desc in fetch_espn_top(n=2):  # Only 2 for SMS
            short_title = title[:50] + "..." if len(title) > 50 else title
            if desc:
                short_desc = desc[:60] + "..." if len(desc) > 60 else desc
                lines.append(f"• {short_title}")
                lines.append(f"  {short_desc}")
            else:
                lines.append(f"• {short_title}")
        
        lines.append("💻 Tech:")
        for title, _, desc in fetch_hn_top(n=3):  # Only 3 for SMS
            short_title = title[:50] + "..." if len(title) > 50 else title
            if desc:
                lines.append(f"• {short_title}{desc}")
            else:
                lines.append(f"• {short_title}")
        
        msg = "\n".join(lines)
        # Limit SMS to ~800 chars (some carriers support longer but be safe)
        if len(msg) > 800:
            msg = msg[:750] + "\n...(truncated)"
    else:
        # Full email version with links
        lines.append(f"\U0001F5DE Morning Brief — {now_local.strftime('%a %b %d, %Y')} (6:30am)")
        lines.append("")

        lines.append("\U0001F30D World (BBC by region)")
        for region, url in BBC_FEEDS.items():
            top = pick_top_from_rss(url)
            if not top:
                lines.append(f"• {region}: (no items)")
                continue
            title, link, desc = top
            lines.append(f"• {region}: {title}")
            if desc:
                lines.append(f"  {desc}")
            lines.append(f"  {link}")

        lines.append("")
        lines.append("\U0001F3C8 Sports (ESPN Top)")
        for title, link, desc in fetch_espn_top(n=3):
            lines.append(f"• {title}")
            if desc:
                lines.append(f"  {desc}")
            lines.append(f"  {link}")

        lines.append("")
        lines.append("\U0001F4BB Tech (Hacker News Top)")
        for title, link, desc in fetch_hn_top(n=5):
            lines.append(f"• {title}{desc}")
            lines.append(f"  {link}")

        msg = "\n".join(lines)
        max_chars = 7000
        if len(msg) > max_chars:
            msg = msg[: max_chars - 50] + "\n…(truncated)"
    
    return msg


def send_email(subject: str, body: str, sms_mode=False):
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ["SMTP_USER"]
    smtp_pass = os.environ["SMTP_PASS"]

    to_email = os.environ["TO_EMAIL"]
    from_email = os.environ.get("FROM_EMAIL", smtp_user)
    
    # Check if SMS gateway is configured (for sending to phone number as SMS/iMessage)
    # Format: 10-digit-phone@gateway (e.g., 1234567890@vtext.com for Verizon)
    sms_gateway = os.environ.get("SMS_GATEWAY", "").strip()
    if sms_gateway:
        # Use SMS gateway to send as text message
        to_email = sms_gateway
        print(f"Using SMS gateway: {to_email[:20]}... (will arrive as text/iMessage)")
        if not sms_mode:
            print("Warning: SMS gateway detected but full message will be sent (may be truncated by carrier)")

    print(f"Sending email from {from_email} to {to_email[:30]}...")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    try:
        context = ssl.create_default_context()
        print(f"Connecting to {smtp_host}:{smtp_port}...")
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            print("Starting TLS...")
            server.starttls(context=context)
            print("Logging in...")
            server.login(smtp_user, smtp_pass)
            print("Sending email...")
            server.sendmail(from_email, [to_email], msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {type(e).__name__}: {e}")
        raise


def main():
    now_utc = datetime.now(timezone.utc)
    now_local = now_utc.astimezone(DETROIT_TZ)

    # Allow test mode via environment variable to bypass time check
    test_mode_raw = os.environ.get("TEST_MODE", "")
    test_mode = test_mode_raw.lower() == "true"
    
    print(f"TEST_MODE environment variable: '{test_mode_raw}' (interpreted as: {test_mode})")
    print(f"Current Detroit time: {now_local}")
    
    # DST-safe: workflow runs at two UTC times; only send when exactly 6:30am Detroit.
    if not test_mode and not (now_local.hour == 6 and now_local.minute == 30):
        print(f"Not 6:30am Detroit. Local time is {now_local}. Exiting.")
        print("To test, set TEST_MODE=true in workflow environment variables.")
        return

    if test_mode:
        print(f"✓ TEST MODE: Running at {now_local} (bypassing time check)")

    # Check if SMS gateway is being used
    sms_gateway = os.environ.get("SMS_GATEWAY", "").strip()
    sms_mode = bool(sms_gateway)
    
    print("Building digest...")
    if sms_mode:
        print("SMS mode: Creating short version (no links)")
        digest = build_digest(now_local, sms_mode=True)
    else:
        digest = build_digest(now_local, sms_mode=False)
    print(f"Digest built ({len(digest)} characters)")
    
    print("Sending email...")
    send_email(subject="Morning Brief", body=digest, sms_mode=sms_mode)
    print("✓ Sent successfully!")


if __name__ == "__main__":
    main()

