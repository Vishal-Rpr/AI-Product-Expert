# Swing Trading System — 6-Week Roadmap

Living plan for turning the morning alert from a screener into a decision-grade trading system with a measurable track record. Reviewed every Friday.

**Meta-goal:** By Week 6, have enough evidence to place capital confidently based on the system's picks — with a documented trust ladder for how autonomy expands over time.

**Success metrics we're building toward:**
1. What % of high-conviction picks (BUY-STOP + top-3 sector) trigger and hit TP1?
2. Does the system beat a passive Nifty Midcap 150 ETF over the same window, after transaction costs?
3. What are the failure modes? Which pick patterns systematically lose? Which regimes make the system worst?

If we can't answer these with data by Week 6, we honestly step back.

---

## Trust ladder

| Level | System permission | Requires |
|---|---|---|
| L0 (today) | Alerts only, user decides everything | Nothing |
| L1 (Gate 1, Week 3) | Alerts + Kite GTT bulk-order text ready to paste | Positive hit rate on triggered BUY-STOPs |
| L2 (Gate 2, Week 6) | Tiered picks — L2 picks auto-approved for GTT prep, L3 held for review | Backtest + real data both positive |
| L3 (Month 3+) | Tool auto-places pre-approved trade types up to capital cap | Consistent L2 performance |
| L4 (Month 6+) | Broader mandate + real capital scaling | Consistent L3 performance |

**No advancement without a gate passed.**

---

## Weekly plan

### Week 1 — 22-26 Sep 2026 (shipping now)

**Focus:** Instrument everything so we can measure.

- [x] Predictions Log Google Sheet + auto-append per morning alert (`predictions.py`)
- [x] Market regime filter (TRADE / CAUTION / STAND_ASIDE) applied to sizing (`regime.py`)
- [x] Earnings guard — flag picks with earnings in next 5 trading days (`earnings_guard.py`)
- [x] Regime banner + earnings tag in email
- [ ] User action: create Predictions Log sheet + share with service account
- [ ] User action: add `PREDICTIONS_SHEET_ID` to GitHub Secrets

**Ships:** first-ever email with regime awareness + earnings guard + automatic prediction logging.

### Week 2 — 29 Sep – 3 Oct 2026

**Focus:** The "why" behind each pick + start closing the outcome loop.

- [ ] Nightly outcome tracker (`outcome_tracker.py`) — runs at 4 PM IST daily, iterates over Predictions Log, checks each open prediction against today's OHLC. Populates Triggered / TP1 Hit / SL Hit / etc.
- [ ] Fundamental overlay per pick — pull `screener.in` data (P/E, ROCE, sales growth, debt/equity, promoter holding trend). Filter out or flag setups with deteriorating fundamentals.
- [ ] News/catalyst summary per pick — Gemini reads last 7 days of headlines (Moneycontrol/BS/ET), generates 1-line "why moving today."
- [ ] Add a `Fundamentals` and `Catalyst` column to email rows.

### Week 3 — 6-10 Oct 2026 — **Gate 1**

**Focus:** First real evaluation.

- [ ] Friday evening: Weekly Eval Report (separate email) — hit rates, R-multiples, comparison to Nifty Midcap 150, scoring-component correlation with outcomes.
- [ ] Retune scoring weights based on Week 1-3 data if any component is inversely correlated with outcomes.
- [ ] **Gate 1 decision:** hit rate on BUY-STOPs > 40%? Avg winner > avg loser? Continue / retune / abandon.
- [ ] If Gate 1 passes → **advance to Trust Level L1** (add Kite GTT bulk-order text at bottom of morning email).

### Week 4 — 13-17 Oct 2026

**Focus:** Portfolio-level thinking + historical validation.

- [ ] Backtest engine (`backtest.py`) — replay 2 years of NSE data, run the current strategy, generate equity curve. Compare to Nifty Midcap 150.
- [ ] Portfolio-level risk model — total ₹ risk across all open positions from the positions sheet; warn if >6% of capital at risk simultaneously.
- [ ] Correlation guard — don't recommend a 4th pick in the same industry cluster if user already holds 3.
- [ ] Kite GTT bulk-order text at bottom of email (paste directly into Kite).

### Week 5 — 20-24 Oct 2026

**Focus:** More entry patterns + slippage learning.

- [ ] Pullback-to-20-SMA entry setup (Vijay's second pattern) — parallel signal alongside breakout entries. Roughly doubles opportunity set.
- [ ] Slippage tracker — user reports actual fills weekly, we measure expected vs actual to tune the 0.5% buffer.
- [ ] Sector rotation dashboard — weekly view of leadership shifts across 1M/3M/6M windows.
- [ ] FII/DII flow overlay — daily flows by sector from NSE.
- [ ] Global macro line in morning email — SGX Nifty, US futures, USD/INR, crude.

### Week 6 — 27-31 Oct 2026 — **Gate 2**

**Focus:** Full assessment.

- [ ] 6-week performance review — combined real + backtest data.
- [ ] Confidence-tiered picks (Tier 1 / 2 / 3) based on backtest + current setup quality.
- [ ] Explanation layer — for every Tier-1 pick, Gemini writes 3-sentence "why this specifically, why now, why it might fail."
- [ ] **Gate 2 decision:** Advance to Trust Level L2? Publish public case study?
- [ ] If publishing: strip credentials, open-source the repo, write LinkedIn/Substack post, tag Vijay Thakkar with results.

---

## Weekly review rhythm

Every Friday, we look at:

1. **Predictions Log outcomes** — what triggered, what hit TP, what stopped out
2. **Weekly Eval Report** — hit rates, R-multiples, benchmark comparison
3. **Refinements** — what to tweak in the next week's scoring/filters/regime rules
4. **Trust ladder position** — should we advance? stay? regress?

Log every change to `Knowledge/Swing Trading Refinements Log.md` (to be created Week 2) with reasoning.

---

## Deferred until L3+ trust level

- **Kite Connect auto-order placement** — requires paid plan + robust daily-login workaround. Not worth the operational burden until we've proven L2 for at least a month.
- **Live intraday alerts** — SL breach warnings via WhatsApp/SMS during trading day.
- **Options overlays** — using options to hedge or enhance swing positions.
- **Multi-strategy portfolio** — running breakout + pullback + mean-reversion in parallel with capital allocation across each.

---

## Anti-goals (things we consciously won't build)

- **Chart pattern recognition (head & shoulders etc.)** — too much interpretation variability, poor signal-to-noise vs. numeric filters.
- **Sentiment scraping from social media** — too noisy for capital allocation, easy to be manipulated.
- **Predicting news events** — we react to news, we don't try to front-run it.
- **Any strategy touching F&O with leverage** — different risk regime; equities-only.
