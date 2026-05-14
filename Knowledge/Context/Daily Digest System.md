# Daily Digest System

**Built**: April 14, 2026
**Status**: Live and running daily at 8 AM IST

## What it does

Automated daily email digest that aggregates articles from 25+ PM, AI, and logistics RSS sources. A Gemini-powered AI summary sits at the top, highlighting the day's key themes and a "read first" recommendation tailored to AI PM learning goals.

## Architecture

- **RSS fetching**: Python script using `feedparser` pulls from feeds defined in `daily_digest/feeds.yaml`
- **AI summary**: Gemini 2.5 Flash (free tier, via `google-genai` SDK) reads all article titles/excerpts and generates a 4-6 sentence daily brief
- **Email delivery**: HTML email sent via Gmail SMTP (App Password auth)
- **Scheduling**: GitHub Actions cron job (`30 2 * * *` UTC = 8:00 AM IST)
- **Trigger**: Automatic daily + manual via GitHub Actions "Run workflow" button

## Key files

| File | Purpose |
|---|---|
| `daily_digest/digest.py` | Main script: fetch feeds, call Gemini, compose email, send |
| `daily_digest/feeds.yaml` | All RSS source URLs and categories (edit here to add/remove sources) |
| `daily_digest/requirements.txt` | Python dependencies |
| `daily_digest/.env.example` | Template for local testing credentials |
| `.github/workflows/daily-digest.yml` | GitHub Actions workflow definition |
| `.gitignore` | Keeps `.env` (credentials) out of the repo |

## Source categories

- **PM**: Lenny's Newsletter, SVPG, Product Talk, First Round Review, Reforge, Department of Product, Shreyas Doshi, Mind the Product, Product School
- **AI**: Simon Willison, Ethan Mollick, Andrew Ng (The Batch), Stratechery, a16z, Chip Huyen, Eugene Yan, Hamel Husain, Maggie Appleton
- **AI Labs**: Anthropic, OpenAI, Google DeepMind
- **Logistics**: FreightWaves, Supply Chain Dive
- **Community**: Hacker News (AI PM + LLM feeds), Reddit r/ProductManagement, Reddit r/artificial

## Credentials (stored as GitHub repo secrets)

Six secrets configured in GitHub > Settings > Secrets and variables > Actions:
`GEMINI_API_KEY`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `RECIPIENT_EMAIL`

## Design decisions

- **Gemini over Claude/OpenAI**: Free tier (250 req/day), no billing required. One call/day is 0.4% of the cap.
- **GitHub Actions over Cursor Automations**: Free, reliable, designed for scheduled jobs. Cursor Automations is built for code workflows and costs per Cloud Agent run.
- **RSS over web scraping**: Simpler, more reliable, respects source APIs. Tradeoff: can't cover sources without RSS (Slack communities, Twitter, Discord).
- **48-hour lookback window**: Catches articles across timezone gaps without duplicating too much.
- **Graceful degradation**: If Gemini API fails, the email still sends without the AI summary.

## How to modify

- **Add a source**: Add an entry to `daily_digest/feeds.yaml` with name, url, and category. Commit and push.
- **Change schedule**: Edit the cron expression in `.github/workflows/daily-digest.yml`.
- **Change AI summary tone**: Edit the prompt string in the `generate_daily_brief` function in `digest.py`.
- **Test manually**: GitHub Actions tab > AI PM Daily Digest > Run workflow.
