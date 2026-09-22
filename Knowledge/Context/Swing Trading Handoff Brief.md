# Swing Trading — Agent Handoff Brief

**Purpose**: This document exists so any new agent (or a different model) can pick up the swing trading system without losing context. Read this first when the user mentions swing trading, stock alerts, Vijay Thakkar, NSE picks, or anything about the morning trading email.

---

## Read in this order (10 minutes total)

1. **This file** — you're reading it. Frames the whole thing.
2. **`Knowledge/Context/Swing Trading System.md`** — the *what/why/how*. Architecture, files, credentials, design decisions.
3. **`Knowledge/Swing Trading Strategy.md`** — the *strategy source of truth*. Filters, scoring formula, refinement log (every historical change with reasoning).
4. **`Knowledge/Swing Trading Roadmap.md`** — the *forward plan*. 6-week phased build, weekly ships, gates at Week 3 and Week 6, trust ladder for autonomy.
5. **`Tasks/swing-trading-alert.md`** — acceptance criteria per AGENTS.md pattern.

Only after reading those, open the code:
- Start with `swing_alert/alert.py` (`build_alert()` is the pipeline entry point)
- Then `swing_alert/regime.py`, `positions.py`, `predictions.py` (the three key modules added in v2.0)
- `swing_alert/universe_fetcher.py` if you're touching universe / sector mapping

---

## The user in one paragraph

Product manager at a freight forwarding company, upskilling into AI Product Management (see `AGENTS.md` for the full context). Not a professional trader but places real swing trades. This system is being built to (a) scale up his trading confidence via evidence-based predictions and (b) serve as an AI PM portfolio piece demonstrating eval-driven product development. He treats the agent as a **work partner, not an assistant** — challenge his thinking, catch his gaps, don't be sycophantic. He has caught two real bugs in this system (sector ETF tickers, stale-data 52W-high issue) so **default to verifying claims, not defending them.**

---

## What state is the system in right now

- **v2.0 shipped Sunday 20 September 2026 evening.** Live from Monday 22 September 2026, 8:00 AM IST.
- Phase 1 Week 1 features live: Predictions Log auto-append, market regime filter, earnings guard, data freshness check.
- Weekly review rhythm starts **Friday 26 September 2026** (~5 PM IST). User pings agent; agent reviews the week's Predictions Log outcomes and specs Week 2 work.
- Google Sheets setup + GitHub Secrets configuration is a **user action still pending as of the handoff**. If those aren't done, Predictions Log will silently skip (which is fine — email still sends).

---

## User's non-negotiable working rules (from `AGENTS.md`)

- **No em dashes in output** — the user explicitly said not to use them. Use commas, semicolons, or parentheses instead. (This is one of the harder rules to follow; watch for it.)
- **Ask clarifying questions before assuming** — use the `AskQuestion` tool when you need a decision.
- **Break responses into clear actionables** — not walls of text.
- **Challenge his thinking when you see gaps** — don't just execute; push back with evidence.
- **Suggest max 3 daily priorities when asked.**
- **Remind him at the end of each session to commit and push via GitHub Desktop** so his other machine syncs.
- **Auto-create a task file in `Tasks/`** when he passes on a new requirement, using the format documented in AGENTS.md.
- **Link every task back to a goal in `GOALS.md`** (this system is linked to Personal → Personal Finance).
- **Log milestones** in `Knowledge/Milestones` at the start of new chats.

---

## What tools you actually have (be honest about it)

- **Web search + fetch** — real. Use it to verify strategy claims, ticker symbols, earnings dates, news.
- **Google Sheets/Docs/Drive MCP** — configured but requires re-auth per session. If you hit an auth wall, tell the user.
- **File system access** — full read/write on the workspace.
- **Shell execution** — full, but note the user's Windows machine currently has an Application Control policy blocking pandas locally. GitHub Actions (Ubuntu) is unaffected. **Do local previews via the `preview.py` script only if pandas imports; otherwise trigger GitHub Actions workflow.**
- **`gh` CLI** — installed but not authenticated. User uses GitHub Desktop for git; do not try `git push` from shell.
- **What you DO NOT have**: Kite API, Bloomberg, live intraday feeds, WhatsApp/SMS. Don't hallucinate access to these.

---

## The 6-week roadmap in one page

| Week | Ships | Gate |
|---|---|---|
| 1 (done) | Predictions Log, regime filter, earnings guard | – |
| 2 | Nightly outcome tracker, fundamental overlay (screener.in), news catalyst per pick | – |
| 3 | Friday Weekly Eval Report + scoring retune | **Gate 1**: hit rate > 40% on BUY-STOPs? → Trust L1 |
| 4 | Backtest engine (2y replay), portfolio risk model, Kite GTT bulk-order text | – |
| 5 | Pullback-to-20-SMA entry, slippage tracker, sector rotation, FII/DII flows | – |
| 6 | Confidence tiers, Gemini explanation layer, full performance review | **Gate 2**: continue / retune / go public? → Trust L2 |

**Trust ladder** (documented in `Knowledge/Swing Trading Roadmap.md`): L0 (today, alerts only) → L1 (alerts + GTT text) → L2 (tiered picks auto-approved for GTT prep) → L3 (auto-order placement up to a cap) → L4 (broader mandate). No advancement without a gate passed.

---

## Common tasks and how to do them

### User asks "why did stock X get / not get picked today?"
1. Check the strategy filters in `Knowledge/Swing Trading Strategy.md` §4
2. Run a debug script that calls `analyze_stock()` on the ticker with the current benchmark return
3. Trace which filter (52W proximity / SMA / weekly Hull / extension / liquidity) rejected it, OR check if it was in `all_passing` but got cap-blocked in diversification
4. Answer with specific numbers, not vague explanation. This was the exact debug flow that caught the Ipca bug.

### User wants to change a strategy threshold
1. Ask: is this based on new data (real outcomes from Predictions Log) or intuition?
2. If data-driven, make the change in `alert.py` constants, log it in `Knowledge/Swing Trading Strategy.md` refinement log with reasoning + before/after evidence
3. If intuition-only, push back gently: "let's wait for the Week 3 eval report to have data — otherwise we're guessing"

### User wants to add a new feature not in the roadmap
1. Ask which existing week it displaces or whether it's additive
2. Update `Knowledge/Swing Trading Roadmap.md` explicitly
3. Update `Tasks/swing-trading-alert.md` acceptance criteria

### User asks for a preview
1. Try `python swing_alert/preview.py` first — writes `preview.html` + `preview.txt`, no email, no sheet write
2. If local pandas is blocked, direct user to manually trigger the GitHub Actions workflow (Actions → Swing Trading Alert → Run workflow)
3. Never fabricate preview numbers — always run the actual pipeline

### User pings for the Friday weekly review
1. Read Predictions Log sheet via gspread (need `PREDICTIONS_SHEET_ID` + `GOOGLE_SA_JSON` from env, or ask user)
2. Compute hit rates: % of BUY-STOPs triggered, % of triggered that hit TP1, average R-multiple
3. Compare to Nifty Midcap 150 return over the same week
4. Identify scoring components inversely correlated with outcomes (candidates for pruning)
5. Present 3 concrete refinement proposals with expected impact
6. **Never advance the trust ladder without gate criteria met.** If Gate 1 fails, honest conversation about whether to continue.

---

## Bugs caught in the past (don't repeat)

1. **Sector ticker mismatch** (Sep 19): Yahoo's `^CNXAUTO`, `^CNXPSUBANK` etc. return metadata only via yfinance. Fix: use tracked sector ETFs (`AUTOBEES.NS`, `PSUBNKBEES.NS`, etc.). All correct tickers are in `swing_alert/universe.yaml`. Do not change back to `^CNX*` symbols.

2. **Auto sector dominating over Pharma** (Sep 19): scoring gave too much weight to individual stock momentum vs sector rank. Fix: added `SECTOR_RANK_BONUS = [0.15, 0.10, 0.07, 0.05, 0.03]` + `MAX_STOCKS_PER_SECTOR = 3` cap + guaranteed top-3-sector coverage in 2-pass diversifier.

3. **Ipca 52W high reported ₹2,014 vs Kite's ₹2,039** (Sep 19, caught by user): `fetch_history` was dropping rows with NaN Close, discarding today's fresh intraday high. Fix: keep rows with valid High even if Close is NaN; downstream calcs use `close.dropna()` explicitly. Also added `check_data_freshness()` guard.

4. **STAND_ASIDE email looked like a shopping list** (Sep 22, caught by user): Block A still said "Entry Candidates" with BUY-STOP pills even when regime forbade entries. Fix: on STAND_ASIDE, heading is "Watchlist only (do not enter)", pills are SKIP, qty is n/a, Gemini prompt forbids buy language, subject says `(watchlist N, no new entries)`.

If you see these classes of issue recurring, treat as a regression, not a new bug.

---

## What "success" looks like at the end of Week 6

By Friday 31 October 2026:
1. **Data**: 6 weeks × 5 trading days × ~6-8 picks = 180-240 tracked predictions with outcomes
2. **Answer**: What % of BUY-STOP picks triggered? Of triggered, what % hit TP1? R-multiple distribution? Does the system beat Nifty Midcap 150 net of costs?
3. **Backtest**: 2-year replay run at least once, results compared to real 6-week data
4. **Decision**: Trust ladder position for the next 6 weeks
5. **Optional**: Public case study (open-sourced repo + LinkedIn/Substack post + Vijay Thakkar tag)

If we can't answer the questions in #2 with confidence, we honestly step back. Don't paper over failure to keep the project alive.

---

## Session opening ritual for you

When the user opens a new chat about swing trading:

1. Read `Knowledge/Milestones` for where they left off (per AGENTS.md rule)
2. Read this handoff brief + `Knowledge/Context/Swing Trading System.md`
3. Check `Knowledge/Swing Trading Strategy.md` refinement log for the most recent version
4. Ask what they want to work on: weekly review / bug fix / feature add / eval report
5. Don't propose anything not on the roadmap without asking why

Good luck. Take care of him.
