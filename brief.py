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
    return title, link


def fetch_espn_top(n=3):
    feed = feedparser.parse(ESPN_TOP)
    out = []
    for e in getattr(feed, "entries", [])[:n]:
        title = clean(getattr(e, "title", ""))
        link = clean(getattr(e, "link", ""))
        if title and link:
            out.append((title, link))
    return out


def fetch_hn_top(n=5, timeout=20):
    ids = requests.get(HN_TOPSTORIES, timeout=timeout).json()
    out = []
    for story_id in ids[: max(n * 2, n)]:
        data = requests.get(HN_ITEM.format(id=story_id), timeout=timeout).json()
        if not data or data.get("type") != "story":
            continue
        title = clean(data.get("title", ""))
        link = clean(data.get("url") or f"https://news.ycombinator.com/item?id={story_id}")
        if title and link:
            out.append((title, link))
        if len(out) >= n:
            break
    return out


def build_digest(now_local: datetime):
    lines = []
    lines.append(f"\U0001F5DE Morning Brief — {now_local.strftime('%a %b %d, %Y')} (6:30am)")
    lines.append("")

    lines.append("\U0001F30D World (BBC by region)")
    for region, url in BBC_FEEDS.items():
        top = pick_top_from_rss(url)
        if not top:
            lines.append(f"• {region}: (no items)")
            continue
        title, link = top
        lines.append(f"• {region}: {title}")
        lines.append(f"  {link}")

    lines.append("")
    lines.append("\U0001F3C8 Sports (ESPN Top)")
    for title, link in fetch_espn_top(n=3):
        lines.append(f"• {title}")
        lines.append(f"  {link}")

    lines.append("")
    lines.append("\U0001F4BB Tech (Hacker News Top)")
    for title, link in fetch_hn_top(n=5):
        lines.append(f"• {title}")
        lines.append(f"  {link}")

    msg = "\n".join(lines)
    max_chars = 7000
    if len(msg) > max_chars:
        msg = msg[: max_chars - 50] + "\n…(truncated)"
    return msg


def send_email(subject: str, body: str):
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ["SMTP_USER"]
    smtp_pass = os.environ["SMTP_PASS"]

    to_email = os.environ["TO_EMAIL"]
    from_email = os.environ.get("FROM_EMAIL", smtp_user)

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls(context=context)
        server.login(smtp_user, smtp_pass)
        server.sendmail(from_email, [to_email], msg.as_string())


def main():
    now_utc = datetime.now(timezone.utc)
    now_local = now_utc.astimezone(DETROIT_TZ)

    # DST-safe: workflow runs at two UTC times; only send when exactly 6:30am Detroit.
    if not (now_local.hour == 6 and now_local.minute == 30):
        print(f"Not 6:30am Detroit. Local time is {now_local}. Exiting.")
        return

    digest = build_digest(now_local)
    send_email(subject="Morning Brief", body=digest)
    print("Sent.")


if __name__ == "__main__":
    main()

