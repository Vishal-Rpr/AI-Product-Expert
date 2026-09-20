# Swing Trading System

**Built**: September 19–20, 2026
**Status**: Live from Monday 22 September 2026, runs 8:00 AM IST Mon–Fri
**Owner**: User makes final trade decisions. System suggests and instruments; it does not auto-execute.
**Current version**: v2.0 (Phase 1 Week 1 of 6-week roadmap)

## What it does

Every weekday morning, an email lands with:

1. **Market regime banner** (TRADE / CAUTION / STAND_ASIDE) — position size auto-adjusts
2. **Top-sector ranking** by 3-month relative strength vs Nifty 50
3. **Block A — Entry Candidates** (up to 8 stocks) in a scannable table with entry / SL / TP1 / TP2 / suggested qty / colour-coded action pill (BUY NOW · BUY-STOP · WATCH · WAIT)
4. **Block B — Exit Tracker** for stocks the user already holds (from a Google Sheet), with critical/warn/info actions
5. **AI narrative** (Gemini) — 3-4 sentence "why these sectors, why these picks today"

Every pick is auto-logged to a **Predictions Log** Google Sheet for outcome tracking (Week 2 builds the nightly tracker that populates the "did it trigger?" columns).

Grounded in **real NSE EOD data via yfinance**. No fabricated numbers.

## Strategy in one paragraph

Adapted from **Vijay Thakkar's YouTube swing trading method**. Top-down: rank NSE small/mid-cap sectoral & thematic ETFs by 3M return relative to Nifty 50; keep top 3-5 sectors. Within those, filter stocks that are (a) near 52W high, (b) above daily 20 & 50-SMA, (c) in a weekly Hull MA 30/44 uptrend, (d) not overextended, (e) liquid (>₹5Cr/day median traded value). Score by proximity to 52W high + relative strength + pullback quality + sector-rank bonus. Enforce max 3 stocks per sector and guaranteed representation from top-3 sectors. Entry on breakout of the 20-day high +0.5%; stop-loss 2.5% below entry; TP1 +6%, TP2 +8%. Position sizing = quantity that risks exactly 2% of capital per trade.

Full strategy in `Knowledge/Swing Trading Strategy.md` (source of truth, refined over time).

## Architecture

- **Data**: `yfinance` (free, no auth, NSE tickers with `.NS` suffix). Sector proxies via ETFs like `AUTOBEES.NS`, `PSUBNKBEES.NS` — Yahoo's `^CNX*` symbols return metadata only.
- **Universe**: 40 curated stocks (`universe.yaml`) + ~625 auto-fetched from NSE Smallcap 250 + Midcap 150 + Microcap 250 (cached 24h in `.cache/`). Total ~666 stocks scanned; up to 8 recommended.
- **Sheets integration**: `gspread` + Google service account (same credential for Positions Sheet and Predictions Log).
- **AI narrative**: Gemini 2.5 Flash (same free-tier key as daily_digest).
- **Email delivery**: Gmail SMTP (reuses daily_digest credentials — same secrets).
- **Scheduling**: GitHub Actions cron `30 2 * * 1-5` (08:00 IST Mon–Fri) + manual `workflow_dispatch`.

## Key files

| File | Purpose |
|---|---|
| `swing_alert/alert.py` | Main pipeline: regime → sectors → filters → scoring → diversification → email. Entry point via `python swing_alert/alert.py` (sends email) or via `build_alert()` for programmatic use. |
| `swing_alert/universe.yaml` | Curated 40-stock watchlist with hand-written 1-line descriptions + sector ETF tickers. Curated entries always win over auto-fetched. |
| `swing_alert/universe_fetcher.py` | Pulls NSE index constituents (Smallcap 250/Midcap 150/Microcap 250) with 24h cache; merges with curated. Also handles fallback description fetch from Yahoo `longBusinessSummary` for auto-fetched stocks that make the top 8. |
| `swing_alert/positions.py` | Reads user's open positions from the "Swing Trading Positions" Google Sheet; evaluates each against current price; produces colour-coded exit actions (HOLD / BOOK TP1 / BOOK TP2 / SL TRIGGERED / TRAIL SL). Renders Block B. |
| `swing_alert/predictions.py` | Auto-appends every morning's picks to the "Swing Trading Predictions Log" Google Sheet (25-column schema). Foundation for Week 2's nightly outcome tracker and Week 3's Weekly Eval Report. |
| `swing_alert/regime.py` | Evaluates market regime (Nifty 50 vs 50/200-SMA + India VIX). Returns TRADE / CAUTION / STAND_ASIDE. In CAUTION → risk drops from 2% to 1%; in STAND_ASIDE → 0% (no new entries). |
| `swing_alert/earnings_guard.py` | Per-pick check: any earnings in next ~5 trading days? Flags with ⚠️ EARNINGS RISK label in the email so user avoids trading over the print. |
| `swing_alert/preview.py` | Runs the full pipeline locally without sending email; writes `preview.html` + `preview.txt` for visual review. Useful for testing strategy changes. |
| `swing_alert/requirements.txt` | Python deps: yfinance, pandas, numpy, pyyaml, python-dotenv, google-genai, requests, gspread, google-auth |
| `swing_alert/.env.example` | Template for local `.env` (never committed) |
| `.github/workflows/swing-alert.yml` | GitHub Actions cron: 02:30 UTC Mon–Fri + manual trigger |
| `Knowledge/Swing Trading Strategy.md` | Living strategy doc — filters, scoring formula, diversification rules, refinement log |
| `Knowledge/Swing Trading Roadmap.md` | 6-week phased build plan with weekly ships and gates (Gate 1 Week 3, Gate 2 Week 6) + trust ladder |
| `Tasks/swing-trading-alert.md` | Task-level acceptance criteria (per AGENTS.md pattern) |

## Data flow

```
             ┌─────────────────────────────────────────────┐
             │  GitHub Actions cron (08:00 IST Mon-Fri)   │
             └────────────────────┬────────────────────────┘
                                  │
                                  ▼
   ┌───────────────────────────────────────────────────────────┐
   │ 1. evaluate_regime()  →  TRADE / CAUTION / STAND_ASIDE   │
   │                             ↓ overrides RISK_PER_TRADE_PCT │
   │ 2. rank_sectors()     →  top 5 sectors by 3M RS           │
   │ 3. check_data_freshness() → yellow banner if stale        │
   │ 4. build_scan_universe() → ~666 stocks (40 curated + NSE) │
   │ 5. analyze_stock() per stock in top sectors:              │
   │      • 6 filters (52W high, SMAs, weekly Hull, etc.)     │
   │      • composite score + sector-rank bonus                │
   │      • trade plan (entry, SL, TP1/TP2, qty)              │
   │ 6. diversify_and_select() → top 8, max 3/sector,          │
   │      guaranteed top-3 sector coverage                     │
   │ 7. has_earnings_soon() per pick → flag if <=5 days        │
   │ 8. load_positions_from_sheet() + evaluate_all()           │
   │ 9. log_predictions() → append to Predictions Log sheet    │
   │ 10. generate_narrative() → Gemini 3-4 sentence summary    │
   │ 11. build_html() + build_plaintext() → compact tables    │
   │ 12. send_email() via SMTP                                 │
   └───────────────────────────────────────────────────────────┘
```

## Credentials (GitHub Secrets)

Reuses `daily_digest` SMTP + Gemini secrets; adds four new ones:

| Secret | Purpose | Required for |
|---|---|---|
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` / `RECIPIENT_EMAIL` | Email delivery | Everything |
| `GEMINI_API_KEY` | AI narrative summary | Optional (email sends without it) |
| `POSITIONS_SHEET_ID` | Google Sheet ID for open positions | Block B — else shows "no open positions" |
| `PREDICTIONS_SHEET_ID` | Google Sheet ID for prediction outcome tracking | Learning loop — else silently skips |
| `GOOGLE_SA_JSON` | Full JSON of a Google service account with Editor access to both sheets | Both sheets above |
| `CAPITAL_INR` | User's real swing-trading capital in rupees | Position sizing (defaults to 5,00,000) |
| `RISK_PER_TRADE_PCT` | Fraction of capital risked per trade | Position sizing (defaults to 0.02 = 2%) |

## Google Sheet schemas

**Swing Trading Positions** (user manually maintains; read-only for the script):
```
Ticker | Company | Buy Date | Buy Price | Quantity | Stop Loss | Target 1 | Target 2 | Status | Notes
```
Status values: `OPEN`, `TP1_HIT`, `CLOSED`.

**Swing Trading Predictions Log** (machine-written, both morning script and future nightly outcome tracker):
```
Date | Ticker | Company | Sector | Sector Rank | Action Pill | Score |
CMP at Alert | Entry Trigger | SL | TP1 | TP2 | Suggested Qty |
Triggered | Trigger Date | TP1 Hit | TP1 Date | TP2 Hit | TP2 Date |
SL Hit | SL Date | Days Held | Return % | R-Multiple |
Regime | Notes
```
Header row is auto-written on first append if the sheet is empty.

## Design decisions worth knowing

- **yfinance not Kite Connect for v1**: Kite Connect requires paid ₹500/mo per API key AND manual daily browser login to refresh the access token (~6 AM IST) — breaks headless GitHub Actions cron. Revisit at Trust Level L3+ when auto-order-placement earns its keep.
- **Sector ETFs, not `^CNX*` index symbols**: Yahoo's `^CNXAUTO`, `^CNXPSUBANK` etc. return metadata only via yfinance (no price history). We proxy each sector via a liquid ETF (returns match within a few bps). Fully documented in `universe.yaml` comments.
- **`auto_adjust=False`** on all yfinance calls so prices match Kite/broker displays (raw close, not dividend-adjusted).
- **Keep rows with NaN Close** (only drop rows where both High AND Close are NaN). Yahoo publishes intraday H/L/V before the settled Close; we need those Highs for the 52W high calc. This was a real bug caught by the user on Sep 19 — Kite showed Ipca's 52W high as ₹2,039 while our tool was reporting ₹2,014 because we were discarding the fresh intraday row.
- **Data freshness check**: compares benchmark's latest bar to expected most-recent Indian trading day (Mon-Fri, accounting for weekends and pre-4-PM-IST hours). Fires a prominent yellow banner + subject prefix if stale.
- **Scan wide, recommend narrow**: 666 stocks scanned, 8 recommended. Diversified with max 3/sector cap + guaranteed top-3 sector representation, so momentum in a weaker sector can't monopolize the list over leadership in a stronger one.
- **Sector-rank bonus** in scoring: rank-#1 sector gets +0.15 to every stock's score, #2 gets +0.10, etc. Bakes Vijay's top-down philosophy into the ranking math.
- **No auto-trading**: the tool never places orders. User places all trades manually in Kite. Trust ladder for expanding autonomy is documented in `Knowledge/Swing Trading Roadmap.md`.
- **Google Sheet, not YAML, for positions**: User can update the sheet in 3 seconds on their phone. YAML would require git-push after every trade — unsustainable.

## How to modify

- **Add curated stock**: Add entry to `swing_alert/universe.yaml` under `stocks:` with ticker (`SYMBOL.NS`), name, sector (must match a `sector_indices` name), and one-line description.
- **Change strategy filters/thresholds**: Constants at top of `alert.py` — `MIN_PROXIMITY_TO_52W_HIGH`, `MAX_EXTENSION_ABOVE_20SMA`, `MIN_MEDIAN_TRADED_VALUE_CR`, `TP1_PCT`, `TP2_PCT`, `STOP_LOSS_PCT`, `MAX_STOCKS_PER_SECTOR`, `SECTOR_RANK_BONUS`. Log every change to `Knowledge/Swing Trading Strategy.md` refinement log with reasoning.
- **Change schedule**: cron in `.github/workflows/swing-alert.yml`.
- **Change email tone/format**: `build_html()` and `_entry_block_html()` / `_exit_block_html()` in `alert.py`. Style follows Zerodha Aftermarket Report + Axis Direct Morning Note pattern (compact tables + colour-coded pills).
- **Test locally**: `python swing_alert/preview.py` — runs pipeline, writes `preview.html` + `preview.txt`, no email sent, no sheet writes.
- **Test manually via GitHub**: Actions tab → "Swing Trading Alert" → Run workflow.

## Weekly review rhythm

Every Friday evening (starting Week 3), user + agent review:
1. Predictions Log outcomes for the week
2. Weekly Eval Report (Week 3+)
3. Refinements needed for next week
4. Trust ladder position (advance / hold / regress)

Log every strategy tweak in `Knowledge/Swing Trading Strategy.md` refinement log with reasoning.

## What's NOT built yet (deferred by design)

- **Nightly outcome tracker** (Week 2) — iterates over Predictions Log, populates Triggered/TP1 Hit/SL Hit columns based on today's OHLC
- **Fundamental overlay** (Week 2) — screener.in data per pick (P/E, ROCE, sales growth, promoter holding)
- **News catalyst summary** (Week 2) — Gemini reads last 7 days of headlines per pick
- **Weekly Eval Report** (Week 3) — separate Friday email with hit rates, R-multiples, benchmark comparison
- **Backtest engine** (Week 4) — 2-year replay of the strategy
- **Portfolio-level risk model** (Week 4) — total ₹ risk across all open positions
- **Kite GTT bulk-order text** (Week 4) — paste-into-Kite ready
- **Pullback-to-20-SMA entry** (Week 5) — Vijay's second entry pattern
- **Sector rotation dashboard + FII/DII flows** (Week 5)
- **Confidence-tiered picks + Gemini explanation layer** (Week 6)

See `Knowledge/Swing Trading Roadmap.md` for the full week-by-week plan.

## Anti-goals (things we consciously won't build)

- Chart pattern recognition (too much interpretation variability)
- Social sentiment scraping (noisy, easy to manipulate)
- News-event prediction (we react, we don't front-run)
- Any F&O leverage strategies (different risk regime; equities-only)
