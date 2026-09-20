# Swing Trading Strategy — Vijay Thakkar (adapted)

Living document. This is the source of truth for how the daily swing-trading alert works. Refine over time as we backtest and learn.

Last updated: 2026-09-19

---

## 1. Core philosophy

Top-down, trend-following swing trading in Indian equities (NSE). We don't predict — we align with what is already strong. Three ordered filters:

1. **Sector strength** — trade only in sectors outperforming Nifty 50 over the recent window.
2. **Stock strength within strong sectors** — 52-week/all-time high stocks in clear weekly uptrends.
3. **Trade planning on daily chart** — enter on breakout of prior swing high, defined stop-loss, defined targets.

> "A rising tide lifts all boats. Get on the right boats." — Vijay Thakkar

---

## 2. Universe — scan wide, recommend narrow

Focus on **small + mid cap** where the strongest swing setups live (Vijay repeatedly shows Nifty Smallcap 250, Midcap 150, High Beta 50, Microcap 250 outperforming Nifty by 20-30% in the same window).

**Scan universe (~500 stocks)** — auto-fetched at runtime from NSE India:
- Nifty Smallcap 250
- Nifty Midcap 150
- Nifty Microcap 250
- Merged with the curated list below (deduped)
- Cached locally for 24h to avoid hammering NSE endpoints

**Curated list (`swing_alert/universe.yaml`)** — ~40 hand-picked names with:
- Verified sector tagging
- Crisp 1-line description of business/moat/niche
- Always wins over auto-fetched entries during merge

**Recommendation output** — always capped at **top 8** regardless of scan size. The point of Vijay's scoring is: rank many, surface few.

**Fallback descriptions** — for auto-fetched stocks that make the top 8, we pull `longBusinessSummary` from Yahoo Finance and truncate to the first sentence. Email footer highlights these so I can promote them to hand-written curated 1-liners over time.

**Excluded:** Nifty 50 large caps (too slow for the setup), stocks priced < ₹50 (low quality), stocks with median 20-day traded value < ₹5 Cr (illiquid, hard to exit).

---

## 3. Sector selection (daily)

Rank all sectoral/thematic indices in the universe by relative strength vs Nifty 50 over the last **3 months** (approx 63 trading days).

- **Relative Strength (RS)** = `(sector return over 63d) − (Nifty 50 return over 63d)`
- Keep only sectors with **positive RS** AND positive absolute 3M return.
- Pick **top 3–5** sectors by RS score for the day.

Optional gate: if Nifty 50 itself is below its own 50-day SMA, we mark the day as "risk-off" and reduce recommended trades to shortlist only (no fresh entries suggested). Rising tide check.

---

## 4. Stock shortlist within strong sectors

For each stock in the selected sectors, apply filters:

| Filter | Rule | Why |
|---|---|---|
| Proximity to 52W high | `close ≥ 0.90 × 52W_high` | Only stocks in strong uptrends |
| Above 20-day SMA | `close > 20_SMA_daily` | Short-term trend intact |
| Above 50-day SMA | `close > 50_SMA_daily` | Medium-term trend intact |
| Weekly trend (Vijay-authentic) | `weekly_close > weekly_HullMA_30` AND `HullMA_30 > HullMA_44` | Long-term structural uptrend |
| Not extended | `close ≤ 1.10 × 20_SMA_daily` | Avoid chasing parabolic moves; want consolidation/pullback |
| Liquidity | 20-day median traded value ≥ ₹5 Cr | Can exit at size |

Score each surviving stock:

```
score =  0.40 × (proximity_to_52W_high_pct)
       + 0.30 × (3M_return_vs_nifty)
       + 0.20 × (1M_return_vs_nifty)
       + 0.10 × (1 − distance_from_20SMA_pct)   # reward pullbacks near 20 SMA
       + sector_rank_bonus                       # top-down: strongest sectors bubble up
```

`sector_rank_bonus`: 0.15 for rank-#1 sector, 0.10 for #2, 0.07 for #3, 0.05 for #4, 0.03 for #5. This bakes Vijay's top-down philosophy into the ranking so momentum in a weaker sector cannot beat a decent setup in a leading sector.

### Diversified selection (top-down enforcement)

Selecting the top-8 in three passes:

1. **Guarantee coverage.** From the top-3 sectors, pick the highest-scoring stock in each (if any of that sector's stocks pass filters). This ensures we never miss a leading sector entirely.
2. **Fill by score.** Fill remaining slots by descending score, subject to a **max of 3 stocks per sector** (prevents one hot sector from monopolising the list).
3. **Final ordering.** Sort the 8 picks by score for presentation.

---

## 5. Trade planning per stock

For each of the 8 shortlisted stocks:

- **Entry (Vijay method):** Buy on breakout of the **most recent swing high on the daily chart**. We compute the "target entry price" as `1.005 × recent_20d_high` (0.5% breakout buffer). If already trading above that level today, we mark it "already broken out — wait for retest of 20 SMA".
- **Stop-loss:** `entry × (1 − 0.025)` — 2.5% below entry (Vijay's typical risk).
- **Target exit 1:** `entry × 1.06` — first partial exit at +6% (initial reward:risk ≈ 2.4:1). Book 50%.
- **Target exit 2:** `entry × 1.08` — second exit at +8% (reward:risk ≈ 3.2:1). Book remaining or start trailing to 20-SMA.

### Position sizing (2% risk rule)

For every trade the email suggests a quantity such that:

```
per_share_risk = entry_price − stop_loss
qty            = floor( (CAPITAL × 2%) / per_share_risk )
```

Example: ₹5,00,000 capital → ₹10,000 max loss per trade. If entry is ₹1,000 and SL is ₹975, per-share risk is ₹25 → suggested qty = 400 shares (position value ₹4,00,000, risk ₹10,000).

This means position size is **inversely proportional to volatility** — wider stop = smaller position, tight stop = bigger position. All trades cost the same in ₹ terms regardless of stock price. This is the single most important discipline for surviving a losing streak.

Configuration via env vars `CAPITAL_INR` (default 5,00,000) and `RISK_PER_TRADE_PCT` (default 0.02).

We also compute and display:
- 52W high value and the date it was hit
- 20-day SMA (daily) and weekly Hull MA 30 (as trend reference)
- 3-month return %

---

## 6. Trades to be made TODAY

The alert lists "trades to be made on the day the alert is sent" — this means, of the 8 recommendations, which ones have a **live actionable setup today**:

1. **"Buy today at market open"** — if yesterday's close broke above the swing high AND today is not gap-up > 2%.
2. **"Buy on trigger"** — if the stock is 0-2% below the swing high; place a buy-stop at `target_entry_price`.
3. **"Wait for pullback"** — if the stock is > 5% above 20 SMA (extended); wait for retest.

Every recommendation shows the current status so I know exactly what to do (or not do) at market open.

---

## 7. Data & infrastructure

- **Data source (v1):** `yfinance` — free, no auth, NSE tickers with `.NS` suffix. EOD daily bars.
- **Sector index constituents:** maintained in `swing_alert/universe.yaml` — refreshed manually from NSE India website (quarterly rebalance).
- **Schedule:** GitHub Actions cron at **02:30 UTC (08:00 AM IST)**, Monday–Friday only.
- **Delivery:** SMTP email (same infra as `daily_digest/`).
- **AI narrative summary:** Gemini generates the 3-4 sentence intro block explaining sector picks + top stock rationale (same pattern as daily digest brief).

### Kite Connect — deferred to v2
- Requires paid plan (₹500/mo per API key).
- Access token expires daily at ~6 AM IST → requires manual login OR fragile headless-selenium workaround (arguably against ToS).
- Value-add for v1 is marginal (EOD data is enough for swing alerts). Revisit when we want:
  - Intraday quotes to show live gap-up % at 8:00 AM
  - Auto-place GTT orders directly from the email
  - Real-time margin / holdings view

---

## 8. Exit tracker (Block B of the daily email)

The email has **two blocks**:

**Block A — Entry Candidates** (top 8 new setups, per Section 4-6 above).

**Block B — Exit Tracker** for stocks I already hold, sourced from a Google Sheet titled *"Swing Trading Positions"*.

**Google Sheet schema** (first row = headers):
```
Ticker | Company | Buy Date | Buy Price | Quantity | Stop Loss | Target 1 | Target 2 | Status | Notes
```

**Status values:**
- `OPEN` — still holding full position
- `TP1_HIT` — booked 50% at TP1, holding remainder with SL moved to breakeven
- `CLOSED` — exited (script ignores these; kept in sheet for history)

**Auth:** Google service account (JSON key stored as GitHub secret `GOOGLE_SA_JSON`); the SA email must be added as an Editor on the sheet. Sheet ID stored as `POSITIONS_SHEET_ID`.

**Exit decision tree** (evaluated per position each morning, ordered worst-case first):
1. Price ≤ Stop-Loss → **STOP-LOSS TRIGGERED** — exit at market, mark CLOSED (critical)
2. Status=OPEN AND Price ≥ TP2 → **BOOK FULL** — mark CLOSED (critical)
3. Status=OPEN AND Price ≥ TP1 → **BOOK 50%, move SL to breakeven, set Status=TP1_HIT** (critical)
4. Status=TP1_HIT AND Price ≥ TP2 → **BOOK REMAINDER** — mark CLOSED (critical)
5. Status=TP1_HIT AND 20-SMA > current SL AND price > 20-SMA → **TRAIL SL up to 20-SMA** (warn)
6. Price within 2% of SL → **APPROACHING SL — tighten mental stop** (warn)
7. Status=OPEN AND Price within 2% of TP1 → **APPROACHING TP1 — ready booking order** (warn)
8. Otherwise → **HOLD** (info)

I update the sheet manually after each trade — the script never modifies it. This keeps me in the loop and prevents automated slippage. When zero positions are open, Block B still renders with "No open positions — all cash" for discipline.

---

## 9. What's explicitly NOT included yet

- Automated order placement (out of scope; this is a **research + alerting** tool, not an autotrader).
- Position sizing / capital allocation (add once we agree on risk budget per trade).
- Backtest engine (v2 — validate the score formula on 2 years of data before we trust it).
- Options / F&O (out of scope; equities only).
- Sentiment / news overlay (v3).
- Auto-update Google Sheet from the email (v3 — action buttons that mark rows CLOSED, update SL).

---

## 10. Refinement log

Add dated entries here as we tune the strategy.

- **2026-09-19** — Initial version. Score weights and thresholds are educated guesses based on Vijay's videos; needs backtest validation before we trust the ranking.
- **2026-09-19** — v1.1: Scan-wide-recommend-narrow. Universe expanded from 40 curated to ~500 via NSE Smallcap/Midcap/Microcap constituent auto-fetch. Recommendations still capped at 8. Fallback descriptions from yfinance. Added Block B exit tracker reading from Google Sheet.
- **2026-09-19** — v1.2: TP1 moved from +4% to +6% (per user preference for wider targets). Added 2% capital-risk position sizing; each entry card now shows suggested quantity, position value, and rupee risk.
- **2026-09-19** — v1.3: Fixed sector ETF tickers (Yahoo `^CNX*` symbols don't return price history via yfinance; now using tracked ETFs like `AUTOBEES.NS`, `PSUBNKBEES.NS`, `MOREALTY.NS`, `MODEFENCE.NS`). Added sector-rank bonus to score + max-3-per-sector cap + guaranteed top-3-sector coverage — fixes the bug where Auto momentum dominated over Pharma (higher-ranked sector). Redesigned email as compact scannable table (Zerodha Aftermarket / Axis Morning Note style) instead of stacked cards. Fixed industry→sector map so Realty/Media stocks tag correctly.
- **2026-09-19** — v1.4 (bug fix caught by user): Kite showed Ipca 52W high as ₹2,039 while our tool reported ₹2,014. Root cause — yfinance publishes the current day's High/Low/Volume before the settled Close, and we were dropping rows with NaN Close, discarding the fresh intraday high. Fix: `fetch_history` now keeps rows with valid High even if Close is NaN; downstream calcs use only fully-settled closes. Also added a `check_data_freshness` guard that compares the benchmark's latest bar to the expected most-recent Indian trading day; prints a prominent warning banner in the email if stale.
- **2026-09-20** — v2.0 Phase 1 Week 1: **Learning loop foundation shipped.** (1) New `predictions.py` — every morning's picks auto-append to a Google Sheet with 25-column schema for outcome tracking. Nightly outcome tracker built in Week 2. (2) New `regime.py` — evaluates market regime (TRADE / CAUTION / STAND_ASIDE) based on Nifty position vs its own 50/200 SMA + India VIX. In CAUTION regime, position size auto-reduced from 2% → 1% risk. In STAND_ASIDE, no new entries suggested. (3) New `earnings_guard.py` — flags picks with earnings within next ~5 trading days as "⚠️ EARNINGS RISK". (4) Email subject line now prefixed with regime tag when non-TRADE.

---

## 11. Sources & references

- Vijay Thakkar YouTube: [Swing Trading Strategy Ep.5](https://www.youtube.com/watch?v=pIl6xhvSZjs), [Weekly Watchlist Process](https://www.youtube.com/watch?v=tNehUF2fem0), [3-Step Stock Selection](https://www.youtube.com/watch?v=DVLQ2m3-xro)
- Kite Connect API: [pricing](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/kite-connect-api-faqs), [historical data](https://www.kite.trade/docs/connect/v3/historical/)
