# Task: Daily swing trading alert (email)

**Linked goal:** Personal → Personal finance (GOALS.md)

## Objective
Send myself an automated daily 8:00 AM IST email that lists 8 Indian small/mid-cap stocks worth watching for a Vijay Thakkar–style swing trade, grounded in real NSE-backed EOD data, with clear entry/exit prices and "what to do today" guidance.

## Key goals
- Rank NSE small/mid-cap sectoral & thematic indices by 3-month relative strength vs Nifty 50, pick top 3–5.
- Within those sectors, filter stocks near 52W high, above 20 SMA / 50 SMA, in a weekly Hull MA uptrend, not overextended, liquid.
- Score and pick top 8. Compute entry, stop-loss, TP1, TP2, and today's action (buy at open / buy on trigger / wait).
- Generate a 3-4 sentence AI summary (Gemini) explaining which sectors were chosen and why, and the top 2-3 stock picks.
- Email formatted like `daily_digest/` output. Runs Mon–Fri via GitHub Actions.
- Full strategy documented in `Knowledge/Swing Trading Strategy.md`, refined over time.

## Acceptance criteria
- [ ] `Knowledge/Swing Trading Strategy.md` exists and captures the full method.
- [ ] `swing_alert/alert.py` runs end-to-end locally with `python swing_alert/alert.py` and produces a valid email.
- [ ] `swing_alert/universe.yaml` lists sectoral indices + curated stocks with 1-line descriptions.
- [ ] `swing_alert/universe_fetcher.py` auto-pulls NSE Smallcap 250 + Midcap 150 + Microcap 250 constituents; caches for 24h.
- [ ] `swing_alert/positions.py` reads open positions from a Google Sheet and evaluates exit actions.
- [ ] `.github/workflows/swing-alert.yml` scheduled for 02:30 UTC Mon–Fri; can also be triggered manually via `workflow_dispatch`.
- [ ] Email includes: (a) AI summary, (b) top-sector table, (c) **Block A — 8 entry candidates**, (d) **Block B — exit tracker for open positions** (or "no open positions" when empty), (e) footer showing scan-universe stats.
- [ ] Each entry card shows: name, 1-line description, 52W high + date, 20 SMA, weekly Hull MA 30, entry, TP1, TP2, stop-loss, R:R, action for today.
- [ ] Each exit card shows: buy price/qty/date, current price, unrealized P&L, SL, TP1/TP2, 20-SMA, colour-coded action (critical/warn/info).
- [ ] All numbers sourced from yfinance (real NSE data) / NSE India (constituents). No fabricated numbers.
- [ ] GitHub Secrets: reuse SMTP set from `daily_digest`; add `POSITIONS_SHEET_ID` and `GOOGLE_SA_JSON` for exit tracker.
- [ ] Google Sheet "Swing Trading Positions" created with the documented schema; service account added as Editor.
- [ ] First test run: manually trigger via `workflow_dispatch`, confirm email lands with both blocks.

## Deferred (out of scope for v1)
- Kite Connect auto-order placement (revisit at Trust Level L3+)
- Live intraday alerts / WhatsApp notifications
- Options overlays
- Multi-strategy parallel portfolio

## v2 roadmap (scheduled)
See `Knowledge/Swing Trading Roadmap.md` for the full 6-week phased plan.
Weekly rhythm: Friday evening review, apply refinements Sunday, monitor Mon–Fri.

- **Week 1 (this week):** Predictions Log auto-append, market regime filter, earnings guard ✅
- **Week 2:** Nightly outcome tracker, fundamental overlay (screener.in), news catalyst per pick
- **Week 3 (Gate 1):** Weekly Eval Report, scoring retune, advance to Trust Level L1 if gate passes
- **Week 4:** Backtest engine, portfolio risk model, Kite GTT bulk-order text
- **Week 5:** Pullback entry setup, slippage tracker, sector rotation, FII/DII flows
- **Week 6 (Gate 2):** 6-week review, confidence tiers, public portfolio decision
