"""
AI PM Daily Digest
Fetches latest articles from key PM/AI blogs via RSS, generates an AI-powered
daily brief, and sends a formatted email digest.
Designed to run daily via GitHub Actions cron schedule.
"""

import os
import re
import sys
import smtplib
import logging
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import feedparser
import yaml
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

LOOKBACK_HOURS = 48
MAX_ARTICLES_PER_FEED = 3


def load_feeds() -> list[dict]:
    feeds_path = Path(__file__).parent / "feeds.yaml"
    with open(feeds_path) as f:
        config = yaml.safe_load(f)

    flat = []
    for section_feeds in config.values():
        for feed in section_feeds:
            flat.append(feed)
    return flat


def fetch_recent_articles(feed: dict, cutoff: datetime) -> list[dict]:
    try:
        parsed = feedparser.parse(feed["url"])
    except Exception as e:
        log.warning(f"Failed to parse {feed['name']}: {e}")
        return []

    articles = []
    for entry in parsed.entries[:MAX_ARTICLES_PER_FEED]:
        published = None
        for date_field in ("published_parsed", "updated_parsed"):
            raw = getattr(entry, date_field, None)
            if raw:
                published = datetime(*raw[:6], tzinfo=timezone.utc)
                break

        if published and published < cutoff:
            continue

        summary = ""
        if hasattr(entry, "summary"):
            summary = entry.summary
        elif hasattr(entry, "description"):
            summary = entry.description

        summary = strip_html(summary)
        if len(summary) > 300:
            summary = summary[:297] + "..."

        articles.append({
            "title": getattr(entry, "title", "Untitled"),
            "link": getattr(entry, "link", ""),
            "summary": summary,
            "source": feed["name"],
            "category": feed.get("category", ""),
            "published": published,
        })

    return articles


def strip_html(text: str) -> str:
    clean = re.sub(r"<[^>]+>", "", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


# ---------------------------------------------------------------------------
# AI Summary
# ---------------------------------------------------------------------------

def generate_daily_brief(all_articles: list[dict]) -> str | None:
    """Call Gemini to produce a short daily brief from today's articles."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        log.info("No GEMINI_API_KEY set, skipping AI summary.")
        return None

    if not all_articles:
        log.info("No articles found, skipping AI summary.")
        return None

    try:
        from google import genai
    except ImportError:
        log.warning("google-genai package not installed, skipping AI summary.")
        return None

    article_list = "\n".join(
        f"- [{a['title']}] ({a['source']}, {a['category']}): {a['summary']}"
        for a in all_articles[:30]
    )

    prompt = f"""You are a daily briefing writer for a Product Manager who is upskilling into AI Product Management.

Here are today's articles from PM, AI, and logistics sources:

{article_list}

Write a "Daily Brief" in 4-6 sentences. Cover:
1. The biggest theme or story across these articles
2. One or two specific insights relevant to someone learning AI product management
3. One thing worth reading first if short on time (name the article title)

Be direct and specific. No fluff, no greetings. Write like a sharp analyst, not a morning show host."""

    try:
        client = genai.Client(api_key=api_key)
        log.info("Calling Gemini API for daily brief...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        brief = getattr(response, "text", None)
        if not brief or not brief.strip():
            log.warning(f"Gemini returned empty response. Full response: {response}")
            return None
        brief = brief.strip()
        log.info(f"AI daily brief generated ({len(brief)} chars).")
        return brief
    except Exception as e:
        log.warning(f"AI summary failed, continuing without it: {e}")
        return None


# ---------------------------------------------------------------------------
# Email builders
# ---------------------------------------------------------------------------

def build_email_html(
    articles_by_section: dict[str, list[dict]],
    date_str: str,
    daily_brief: str | None = None,
) -> str:
    html_parts = [f"""
    <html><body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 680px; margin: 0 auto; color: #1a1a1a;">
    <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); padding: 28px 24px; border-radius: 8px 8px 0 0;">
        <h1 style="color: #fff; margin: 0; font-size: 22px;">AI PM Daily Digest</h1>
        <p style="color: #b8d4f0; margin: 6px 0 0; font-size: 14px;">{date_str}</p>
    </div>
    <div style="padding: 20px 24px; background: #f8f9fa; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 8px 8px;">
    """]

    total_count = sum(len(arts) for arts in articles_by_section.values())

    if daily_brief:
        brief_html = daily_brief.replace("\n", "<br>")
        html_parts.append(f"""
        <div style="background: linear-gradient(135deg, #f0f7ff 0%, #e8f4f8 100%); border: 1px solid #c5ddf0; border-radius: 8px; padding: 16px 20px; margin-bottom: 24px;">
            <div style="font-size: 13px; font-weight: 700; color: #1e3a5f; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Today's Brief</div>
            <p style="font-size: 14px; color: #2c3e50; line-height: 1.65; margin: 0;">{brief_html}</p>
        </div>
        """)

    if total_count == 0:
        html_parts.append('<p style="color: #666;">No new articles found in the past 48 hours. Quiet day!</p>')
    else:
        html_parts.append(f'<p style="color: #555; font-size: 14px; margin-top: 0;">{total_count} articles across your PM & AI sources.</p>')

        for section, articles in articles_by_section.items():
            if not articles:
                continue
            section_label = section.replace("_", " ").title()
            html_parts.append(f"""
            <h2 style="font-size: 16px; color: #1e3a5f; border-bottom: 2px solid #2d5a87; padding-bottom: 6px; margin-top: 24px;">{section_label}</h2>
            """)

            for art in articles:
                pub_str = ""
                if art["published"]:
                    pub_str = art["published"].strftime("%b %d")
                html_parts.append(f"""
                <div style="margin-bottom: 16px; padding: 12px; background: #fff; border-radius: 6px; border-left: 3px solid #2d5a87;">
                    <a href="{art['link']}" style="font-size: 15px; font-weight: 600; color: #1e3a5f; text-decoration: none;">{art['title']}</a>
                    <div style="font-size: 12px; color: #888; margin: 4px 0;">{art['source']} {f'&middot; {art["category"]}' if art['category'] else ''} {f'&middot; {pub_str}' if pub_str else ''}</div>
                    <p style="font-size: 13px; color: #444; margin: 6px 0 0; line-height: 1.5;">{art['summary']}</p>
                </div>
                """)

    html_parts.append("""
    <hr style="border: none; border-top: 1px solid #ddd; margin: 24px 0 12px;">
    <p style="font-size: 11px; color: #999; text-align: center;">
        Sent by your AI PM Daily Digest via GitHub Actions.<br>
        Edit sources in <code>daily_digest/feeds.yaml</code>
    </p>
    </div></body></html>
    """)

    return "".join(html_parts)


def build_plaintext(
    articles_by_section: dict[str, list[dict]],
    date_str: str,
    daily_brief: str | None = None,
) -> str:
    lines = [f"AI PM Daily Digest - {date_str}", "=" * 40, ""]

    if daily_brief:
        lines.append("TODAY'S BRIEF")
        lines.append("-" * 20)
        lines.append(daily_brief)
        lines.append("")

    for section, articles in articles_by_section.items():
        if not articles:
            continue
        lines.append(f"## {section.replace('_', ' ').title()}")
        lines.append("")
        for art in articles:
            lines.append(f"  {art['title']}")
            lines.append(f"  {art['link']}")
            if art["summary"]:
                lines.append(f"  {art['summary']}")
            lines.append("")

    if not any(articles_by_section.values()):
        lines.append("No new articles found in the past 48 hours.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Email sender
# ---------------------------------------------------------------------------

def send_email(subject: str, html: str, plaintext: str):
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    recipient = os.environ.get("RECIPIENT_EMAIL", user)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"AI PM Digest <{user}>"
    msg["To"] = recipient

    msg.attach(MIMEText(plaintext, "plain"))
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(user, [recipient], msg.as_string())

    log.info(f"Digest sent to {recipient}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info("Starting AI PM Daily Digest")

    feeds = load_feeds()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    date_str = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")

    articles_by_section: dict[str, list[dict]] = {}
    all_articles: list[dict] = []

    for feed in feeds:
        section = feed.get("category", "Other")
        articles = fetch_recent_articles(feed, cutoff)
        if articles:
            articles_by_section.setdefault(section, []).extend(articles)
            all_articles.extend(articles)
            log.info(f"  {feed['name']}: {len(articles)} articles")
        else:
            log.info(f"  {feed['name']}: no recent articles")

    for section in articles_by_section:
        articles_by_section[section].sort(
            key=lambda a: a["published"] or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )

    daily_brief = generate_daily_brief(all_articles)

    subject = f"AI PM Digest - {date_str}"
    html = build_email_html(articles_by_section, date_str, daily_brief)
    plaintext = build_plaintext(articles_by_section, date_str, daily_brief)

    try:
        send_email(subject, html, plaintext)
    except KeyError as e:
        log.error(f"Missing env var {e}. Copy .env.example to .env and fill in your SMTP credentials.")
        sys.exit(1)
    except Exception as e:
        log.error(f"Failed to send email: {e}")
        sys.exit(1)

    log.info("Done.")


if __name__ == "__main__":
    main()
