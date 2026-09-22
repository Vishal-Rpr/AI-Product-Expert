"""
Daily Swing Trading Alert — Vijay Thakkar style.

Pipeline:
  1. Load benchmark (Nifty 50), sector indices, and stock universe from universe.yaml
  2. Rank sectors by 3M relative strength vs Nifty; pick top 3-5
  3. For stocks in winning sectors, apply filters (52W-high proximity, above 20/50 SMA,
     weekly Hull MA uptrend, not overextended, liquid)
  4. Score survivors; keep top 8
  5. Compute entry / stop-loss / TP1 / TP2 / today's action per stock
  6. Ask Gemini for a 3-4 sentence narrative summary
  7. Email HTML + plaintext via SMTP

All numbers are pulled from Yahoo Finance (yfinance) — real NSE EOD data.
Designed to run via GitHub Actions cron at 02:30 UTC (08:00 AM IST) Mon–Fri.
"""

from __future__ import annotations

import logging
import os
import smtplib
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import yaml
import yfinance as yf
from dotenv import load_dotenv

# Allow "python swing_alert/alert.py" to find sibling modules
sys.path.insert(0, str(Path(__file__).parent))
from universe_fetcher import build_scan_universe, fetch_fallback_description  # noqa: E402
from positions import Position, load_positions_from_sheet, evaluate_all       # noqa: E402
from regime import Regime, evaluate_regime                                    # noqa: E402
from earnings_guard import has_earnings_soon                                  # noqa: E402
from predictions import log_predictions                                       # noqa: E402

load_dotenv(Path(__file__).parent / ".env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

LOOKBACK_DAYS = 400          # ~13 months of daily bars (enough for 52W high + weekly resample)
SECTOR_RS_WINDOW = 63        # ~3 months of trading days for sector RS ranking
TOP_N_SECTORS = 5
TOP_N_STOCKS = 8

# Diversification rules (top-down enforcement)
MAX_STOCKS_PER_SECTOR = 3    # prevents one hot sector from dominating the list
# Bonus added to a stock's composite score based on its sector's RS rank:
# index [0] = rank #1 sector, index [1] = rank #2, etc. Amplifies Vijay's top-down bias.
SECTOR_RANK_BONUS = [0.15, 0.10, 0.07, 0.05, 0.03]

# Vijay-style thresholds (see Knowledge/Swing Trading Strategy.md)
MIN_PROXIMITY_TO_52W_HIGH = 0.90   # close >= 90% of 52W high
MAX_EXTENSION_ABOVE_20SMA = 1.10   # close <= 110% of 20 SMA
MIN_MEDIAN_TRADED_VALUE_CR = 5.0   # ₹5 crore/day median liquidity
MIN_PRICE = 50.0                   # ignore penny/low-quality names

# Trade planning
BREAKOUT_BUFFER = 0.005            # 0.5% above recent 20d high
STOP_LOSS_PCT = 0.025              # 2.5% below entry
TARGET_1_PCT = 0.06                # 6% above entry (first partial exit)
TARGET_2_PCT = 0.08                # 8% above entry (second exit, then trail)

# Position sizing
# 2% capital risk per trade (classic risk-parity rule). Overridable via env.
# GitHub Actions injects unset secrets as "" (not missing), which would crash float().
def _env_float(key: str, default: float) -> float:
    raw = os.environ.get(key)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return float(raw)
    except ValueError:
        log.warning(f"Invalid {key}={raw!r}; using default {default}")
        return default


CAPITAL_INR = _env_float("CAPITAL_INR", 500000.0)       # ₹5L default; set your real number in env
RISK_PER_TRADE_PCT = _env_float("RISK_PER_TRADE_PCT", 0.02)  # 2%
RISK_PER_TRADE_INR = CAPITAL_INR * RISK_PER_TRADE_PCT
log.info(f"Position sizing: capital=INR {CAPITAL_INR:,.0f} · risk={RISK_PER_TRADE_PCT:.1%}")

IST = timezone(timedelta(hours=5, minutes=30))


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SectorScore:
    name: str
    ticker: str
    return_3m: float
    benchmark_return_3m: float
    rs: float  # relative strength = sector_return - benchmark_return


@dataclass
class StockPick:
    ticker: str
    name: str
    sector: str
    desc: str

    current_price: float
    week52_high: float
    week52_high_date: str
    sma_20: float
    sma_50: float
    hull_ma_30_weekly: float
    return_3m: float
    proximity_to_high_pct: float   # e.g. 0.94 = trading at 94% of 52W high
    distance_from_20sma_pct: float # e.g. 0.03 = 3% above 20 SMA
    score: float = 0.0

    # Trade plan
    entry: float = 0.0
    stop_loss: float = 0.0
    target_1: float = 0.0
    target_2: float = 0.0
    action_today: str = ""

    # Position sizing
    suggested_qty: int = 0
    position_value_inr: float = 0.0
    risk_amount_inr: float = 0.0

    # Risk flags
    earnings_soon: bool = False
    earnings_date: Optional[str] = None

    # Meta
    breakout_ref_high: float = 0.0

    def rr1(self) -> float:
        risk = self.entry - self.stop_loss
        reward = self.target_1 - self.entry
        return reward / risk if risk > 0 else 0.0

    def rr2(self) -> float:
        risk = self.entry - self.stop_loss
        reward = self.target_2 - self.entry
        return reward / risk if risk > 0 else 0.0


# ---------------------------------------------------------------------------
# Universe loading
# ---------------------------------------------------------------------------

def load_universe() -> dict:
    path = Path(__file__).parent / "universe.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Data fetching (yfinance)
# ---------------------------------------------------------------------------

def fetch_history(ticker: str, days: int = LOOKBACK_DAYS) -> Optional[pd.DataFrame]:
    """
    Return a DataFrame with daily OHLCV for a ticker, or None if fetch fails.

    Uses auto_adjust=False so prices match what Kite / broker platforms display
    (raw close, not dividend-adjusted).

    IMPORTANT ON DATA COMPLETENESS:
    Yahoo sometimes publishes the most recent trading day's High/Low/Volume
    before the settled Close arrives. We *keep* such rows because 52-week-high
    calculations only need valid Highs — dropping them would understate the
    high and produce wrong entry triggers (this bug was caught when Kite showed
    Ipca's 52W high as ₹2,039 while our tool still reported ₹2,014).

    We only drop rows where both High AND Close are NaN (truly empty rows).
    """
    try:
        df = yf.Ticker(ticker).history(period=f"{days}d", auto_adjust=False)
        if df is None or df.empty:
            log.warning(f"  no data for {ticker}")
            return None
        # Drop rows that are truly empty (no High and no Close)
        df = df.dropna(subset=["High", "Close"], how="all")
        return df
    except Exception as e:
        log.warning(f"  fetch failed for {ticker}: {e}")
        return None


def check_data_freshness(benchmark_df: pd.DataFrame) -> tuple[bool, str]:
    """
    Verify that the benchmark's latest bar is from the most recent completed
    Indian trading day. Returns (is_fresh, warning_message).
    """
    if benchmark_df is None or benchmark_df.empty:
        return False, "Benchmark data unavailable."

    latest_bar_date = benchmark_df.index[-1].date()
    now_ist = datetime.now(IST)
    today_ist = now_ist.date()

    # What is the most recent completed trading day?
    # If it's Sat/Sun/Mon before 4 PM IST, expected latest bar is Friday.
    # If it's Mon-Fri after ~4 PM IST, expected is today.
    # If it's Mon-Fri before ~4 PM IST, expected is yesterday (previous weekday).
    weekday = today_ist.weekday()  # 0=Mon, 6=Sun
    hour = now_ist.hour

    if weekday == 5:                  # Saturday
        expected = today_ist - timedelta(days=1)                # Fri
    elif weekday == 6:                # Sunday
        expected = today_ist - timedelta(days=2)                # Fri
    elif weekday == 0 and hour < 16:  # Monday morning
        expected = today_ist - timedelta(days=3)                # Fri
    elif hour < 16:                                              # Tue-Fri morning
        expected = today_ist - timedelta(days=1)
    else:                                                        # Any weekday evening
        expected = today_ist

    lag_days = (expected - latest_bar_date).days
    if lag_days <= 0:
        return True, f"Data current as of {latest_bar_date.strftime('%d %b %Y')}."
    else:
        msg = (f"⚠️ Data may be stale: latest bar is {latest_bar_date.strftime('%d %b %Y')}, "
               f"but latest completed trading day is {expected.strftime('%d %b %Y')}. "
               f"Kite/live prices may differ; rerun after Yahoo publishes.")
        return False, msg


# ---------------------------------------------------------------------------
# Indicators
# ---------------------------------------------------------------------------

def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=window).mean()


def wma(series: pd.Series, window: int) -> pd.Series:
    """Weighted moving average — weights 1..window."""
    weights = np.arange(1, window + 1)
    return series.rolling(window=window).apply(
        lambda x: np.dot(x, weights) / weights.sum(), raw=True
    )


def hull_ma(series: pd.Series, window: int) -> pd.Series:
    """Hull Moving Average — HMA = WMA(2*WMA(n/2) - WMA(n), sqrt(n))."""
    half = max(1, window // 2)
    sqrt_n = max(1, int(np.sqrt(window)))
    wma_half = wma(series, half)
    wma_full = wma(series, window)
    diff = 2 * wma_half - wma_full
    return wma(diff, sqrt_n)


def pct_return(series: pd.Series, periods: int) -> float:
    if len(series) <= periods:
        return 0.0
    return float(series.iloc[-1] / series.iloc[-1 - periods] - 1.0)


# ---------------------------------------------------------------------------
# Sector ranking
# ---------------------------------------------------------------------------

def rank_sectors(universe: dict) -> tuple[list[SectorScore], Optional[pd.DataFrame]]:
    """Returns (top_sectors, benchmark_df_for_freshness_check)."""
    benchmark_ticker = universe["benchmark"]["ticker"]
    log.info(f"Fetching benchmark {benchmark_ticker}...")
    bench_df = fetch_history(benchmark_ticker)
    if bench_df is None or len(bench_df) < SECTOR_RS_WINDOW + 1:
        log.error("Benchmark data unavailable; cannot rank sectors.")
        return [], None

    bench_return = pct_return(bench_df["Close"], SECTOR_RS_WINDOW)
    log.info(f"Benchmark 3M return: {bench_return*100:.2f}%")

    scores: list[SectorScore] = []
    for sec in universe["sector_indices"]:
        df = fetch_history(sec["ticker"])
        if df is None or len(df) < SECTOR_RS_WINDOW + 1:
            log.warning(f"  skipping {sec['name']} (insufficient data)")
            continue
        ret = pct_return(df["Close"], SECTOR_RS_WINDOW)
        scores.append(SectorScore(
            name=sec["name"],
            ticker=sec["ticker"],
            return_3m=ret,
            benchmark_return_3m=bench_return,
            rs=ret - bench_return,
        ))

    # Keep only sectors outperforming benchmark AND with positive absolute return
    filtered = [s for s in scores if s.rs > 0 and s.return_3m > 0]
    filtered.sort(key=lambda s: s.rs, reverse=True)
    return filtered[:TOP_N_SECTORS], bench_df


# ---------------------------------------------------------------------------
# Stock analysis
# ---------------------------------------------------------------------------

def analyze_stock(stock_cfg: dict, benchmark_return_3m: float, sector_bonus: float = 0.0) -> Optional[StockPick]:
    ticker = stock_cfg["ticker"]
    df = fetch_history(ticker)
    if df is None or len(df) < 252:
        return None

    # High-based series (may include today's in-progress bar with NaN Close)
    high = df["High"].dropna()
    # Close-based series (only settled closes for SMA/HMA/returns)
    close_full = df["Close"].dropna()
    volume = df["Volume"].dropna()

    if len(high) < 252 or len(close_full) < 252:
        return None

    # For "current price" we use the latest settled close
    current_price = float(close_full.iloc[-1])
    if current_price < MIN_PRICE:
        return None

    # Keep the close series aliased for existing code below
    close = close_full

    # 52-week high & date — use HIGH series (includes today's intraday if available)
    window_252 = high.tail(252)
    week52_high = float(window_252.max())
    week52_high_date = window_252.idxmax().strftime("%d %b %Y")

    # SMAs
    sma_20_series = sma(close, 20)
    sma_50_series = sma(close, 50)
    if sma_20_series.iloc[-1] != sma_20_series.iloc[-1]:  # NaN check
        return None
    sma_20_val = float(sma_20_series.iloc[-1])
    sma_50_val = float(sma_50_series.iloc[-1])

    # Weekly Hull MA 30
    weekly_close = close.resample("W-FRI").last().dropna()
    if len(weekly_close) < 40:
        return None
    hull30_series = hull_ma(weekly_close, 30)
    hull44_series = hull_ma(weekly_close, 44)
    hull30_val = float(hull30_series.iloc[-1]) if not np.isnan(hull30_series.iloc[-1]) else 0.0
    hull44_val = float(hull44_series.iloc[-1]) if not np.isnan(hull44_series.iloc[-1]) else 0.0

    # Filters
    proximity = current_price / week52_high
    distance_from_20sma = (current_price - sma_20_val) / sma_20_val

    if proximity < MIN_PROXIMITY_TO_52W_HIGH:
        return None
    if current_price <= sma_20_val:
        return None
    if current_price <= sma_50_val:
        return None
    if current_price > MAX_EXTENSION_ABOVE_20SMA * sma_20_val:
        return None
    # Vijay-authentic weekly trend gate: weekly close > Hull30 AND Hull30 > Hull44
    if hull30_val <= 0 or hull44_val <= 0:
        return None
    if float(weekly_close.iloc[-1]) <= hull30_val or hull30_val <= hull44_val:
        return None

    # Liquidity: median (close × volume) over last 20 days in ₹ crore
    traded_value = (close.tail(20) * volume.tail(20)) / 1e7  # to crore
    med_tv = float(traded_value.median())
    if med_tv < MIN_MEDIAN_TRADED_VALUE_CR:
        return None

    # Returns
    ret_3m = pct_return(close, 63)
    ret_1m = pct_return(close, 21)

    # Composite score
    rs_3m = ret_3m - benchmark_return_3m
    rs_1m = ret_1m - benchmark_return_3m
    score = (
        0.40 * proximity
        + 0.30 * rs_3m
        + 0.20 * rs_1m
        + 0.10 * (1.0 - min(distance_from_20sma, 0.10))  # reward pullbacks near 20SMA
        + sector_bonus                                    # top-down: strongest sectors bubble up
    )

    # Trade plan
    recent_20d_high = float(high.tail(20).max())
    entry = round(recent_20d_high * (1 + BREAKOUT_BUFFER), 2)
    stop_loss = round(entry * (1 - STOP_LOSS_PCT), 2)
    target_1 = round(entry * (1 + TARGET_1_PCT), 2)
    target_2 = round(entry * (1 + TARGET_2_PCT), 2)

    # Position sizing — qty such that (entry - stop_loss) * qty ≈ RISK_PER_TRADE_INR
    per_share_risk = entry - stop_loss
    suggested_qty = int(RISK_PER_TRADE_INR // per_share_risk) if per_share_risk > 0 else 0
    position_value = round(suggested_qty * entry, 2)
    risk_amount = round(suggested_qty * per_share_risk, 2)

    # Today's action
    if current_price >= entry:
        # Already broken out
        if current_price > entry * 1.02:
            action = f"Already extended ~{((current_price/entry)-1)*100:.1f}% above trigger — wait for pullback to 20 SMA (₹{sma_20_val:.0f})"
        else:
            action = f"Broke out; buy on any dip near ₹{entry:.2f} today"
    else:
        gap_to_entry = (entry - current_price) / current_price
        if gap_to_entry <= 0.02:
            action = f"Place buy-stop at ₹{entry:.2f} (trigger {gap_to_entry*100:.1f}% away)"
        elif gap_to_entry <= 0.05:
            action = f"Watchlist — trigger ₹{entry:.2f} is {gap_to_entry*100:.1f}% away; alert when it closes above ₹{entry:.2f}"
        else:
            action = f"Too far from trigger ({gap_to_entry*100:.1f}% away); revisit if it consolidates higher"

    return StockPick(
        ticker=ticker,
        name=stock_cfg["name"],
        sector=stock_cfg["sector"],
        desc=stock_cfg["desc"],
        current_price=round(current_price, 2),
        week52_high=round(week52_high, 2),
        week52_high_date=week52_high_date,
        sma_20=round(sma_20_val, 2),
        sma_50=round(sma_50_val, 2),
        hull_ma_30_weekly=round(hull30_val, 2),
        return_3m=ret_3m,
        proximity_to_high_pct=proximity,
        distance_from_20sma_pct=distance_from_20sma,
        score=score,
        entry=entry,
        stop_loss=stop_loss,
        target_1=target_1,
        target_2=target_2,
        action_today=action,
        suggested_qty=suggested_qty,
        position_value_inr=position_value,
        risk_amount_inr=risk_amount,
        breakout_ref_high=round(recent_20d_high, 2),
    )


# ---------------------------------------------------------------------------
# AI narrative
# ---------------------------------------------------------------------------

def generate_narrative(
    sectors: list[SectorScore],
    picks: list[StockPick],
    regime: Optional[Regime] = None,
) -> Optional[str]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not picks:
        return None
    try:
        from google import genai
    except ImportError:
        log.warning("google-genai not installed; skipping narrative")
        return None

    sector_lines = "\n".join(
        f"- {s.name}: 3M return {s.return_3m*100:+.1f}% (vs Nifty {s.benchmark_return_3m*100:+.1f}%, RS {s.rs*100:+.1f}%)"
        for s in sectors
    )
    stock_lines = "\n".join(
        f"- {p.name} ({p.sector}): {p.desc} Trading at {p.proximity_to_high_pct*100:.0f}% of 52W high, 3M return {p.return_3m*100:+.1f}%. Score {p.score:.2f}."
        for p in picks
    )

    stand_aside = regime is not None and regime.label == "STAND_ASIDE"
    if stand_aside:
        prompt = f"""You are a swing-trading analyst writing a brief morning note for an Indian equities investor following Vijay Thakkar's top-down strategy.

MARKET REGIME IS STAND_ASIDE. Nifty is below its 50-day and/or 200-day SMA. Fresh swing entries are forbidden today. Cash is the position.

Leading sectors on 3M relative strength vs Nifty 50 (context only, not a buy list):
{sector_lines}

Watchlist names that passed filters (NOT trades, NOT buy-stops):
{stock_lines}

Write 3-4 crisp sentences covering:
1. State clearly that regime is STAND_ASIDE and no new entries today
2. Name the leading sector(s) as context for a later reclaim
3. Mention 1-2 watchlist names as names to revisit if Nifty reclaims its 50-SMA, not as orders
4. Do not use the words buy, buy-stop, enter, or pick as an instruction

Be direct. No greetings, no disclaimers, no bullet points."""
    else:
        prompt = f"""You are a swing-trading analyst writing a brief morning note for an Indian equities investor following Vijay Thakkar's top-down strategy.

Today's winning sectors (ranked by 3M relative strength vs Nifty 50):
{sector_lines}

Today's top {len(picks)} stock picks from those sectors:
{stock_lines}

Write 3-4 crisp sentences (or slightly more if needed) covering:
1. Which sectors are leading and the theme connecting them (e.g. capex, defence indigenisation, PSU re-rating, EV cycle)
2. The top 2-3 stock picks and one line on why they stand out today
3. Any caveat if picks are mostly extended vs still setting up

Be direct. No greetings, no disclaimers, no bullet points. Write like a sharp fund manager, not a hype account."""

    try:
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        text = getattr(resp, "text", None)
        return text.strip() if text else None
    except Exception as e:
        log.warning(f"Narrative generation failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

URGENCY_STYLES = {
    "critical": ("#b23a3a", "#fff0f0", "#f5c6c6"),
    "warn":     ("#7a5c00", "#fff8e1", "#f0dca0"),
    "info":     ("#0d5f3f", "#f0fff7", "#c5e6d3"),
}


def _action_pill(action_text: str, stand_aside: bool = False) -> tuple[str, str, str]:
    """Classify entry action into (label, bg, fg) for a compact pill."""
    if stand_aside:
        return ("SKIP", "#721c24", "#fff")
    lower = action_text.lower()
    if lower.startswith("broke out") or "buy on any dip" in lower:
        return ("BUY NOW", "#0d5f3f", "#fff")
    if lower.startswith("place buy-stop"):
        return ("BUY-STOP", "#148055", "#fff")
    if lower.startswith("watchlist"):
        return ("WATCH", "#7a5c00", "#fff")
    if lower.startswith("too far") or "already extended" in lower:
        return ("WAIT", "#888", "#fff")
    return ("REVIEW", "#555", "#fff")


def _entry_block_html(picks: list, stand_aside: bool = False) -> str:
    """
    Block A: TRADE/CAUTION = entry candidates.
    STAND_ASIDE = watchlist only. Levels kept for a later reclaim; pills are SKIP.
    """
    if stand_aside:
        heading = (
            f'<h2 style="font-size: 15px; color: #721c24; border-bottom: 2px solid #b23a3a; '
            f'padding-bottom: 6px; margin-top: 28px;">Block A &middot; Watchlist only '
            f'(do not enter) &middot; {len(picks)} names</h2>'
        )
        notice = (
            '<div style="padding: 12px 14px; margin-bottom: 12px; background: #f8d7da; '
            'border-left: 4px solid #b23a3a; border-radius: 4px; font-size: 13px; color: #721c24;">'
            '<b>Cash is the trade.</b> Nifty is below its 50-day and/or 200-day SMA. '
            'Do not place BUY-STOPs. Names below passed filters so you can revisit them '
            'if the index reclaims the 50-SMA. Qty is zero on purpose.</div>'
        )
        head_bg, name_color, entry_color = "#721c24", "#721c24", "#555"
        details_title = "Levels if regime flips (not orders)"
    else:
        heading = (
            f'<h2 style="font-size: 15px; color: #0d5f3f; border-bottom: 2px solid #148055; '
            f'padding-bottom: 6px; margin-top: 28px;">Block A &middot; Entry Candidates '
            f'(Top {len(picks)})</h2>'
        )
        notice = ""
        head_bg, name_color, entry_color = "#0d5f3f", "#0d5f3f", "#148055"
        details_title = "Why these stocks"

    html = [
        heading,
        notice,
        '<div style="overflow-x: auto;">',
        '<table style="width: 100%; border-collapse: collapse; font-size: 12px; background: #fff; box-shadow: 0 1px 2px rgba(0,0,0,0.04); border-radius: 6px; overflow: hidden;">',
        f'<thead><tr style="background: {head_bg}; color: #fff; text-align: left;">'
        '<th style="padding: 8px 6px;">#</th>'
        '<th style="padding: 8px 6px;">Stock</th>'
        '<th style="padding: 8px 6px;">Sector</th>'
        '<th style="padding: 8px 6px; text-align: right;">CMP</th>'
        '<th style="padding: 8px 6px; text-align: right;">52W High</th>'
        '<th style="padding: 8px 6px; text-align: right;">20 SMA</th>'
        '<th style="padding: 8px 6px; text-align: right;">Entry</th>'
        '<th style="padding: 8px 6px; text-align: right;">SL</th>'
        '<th style="padding: 8px 6px; text-align: right;">TP1 / TP2</th>'
        '<th style="padding: 8px 6px; text-align: right;">Qty</th>'
        '<th style="padding: 8px 6px;">Action</th>'
        '</tr></thead><tbody>'
    ]

    for i, p in enumerate(picks, 1):
        pill_label, pill_bg, pill_fg = _action_pill(p.action_today, stand_aside=stand_aside)
        distance_from_high = (p.week52_high - p.current_price) / p.week52_high
        row_bg = "#fafafa" if i % 2 == 0 else "#fff"
        earnings_tag = ""
        if p.earnings_soon:
            earnings_tag = (
                f'<br><span style="background: #ffc107; color: #856404; padding: 2px 6px; '
                f'border-radius: 3px; font-size: 9px; font-weight: 700;">⚠️ EARNINGS {p.earnings_date}</span>'
            )
        if stand_aside:
            qty_html = (
                '<td style="padding: 8px 6px; text-align: right; color: #999;">n/a'
                '<br><span style="font-size: 10px;">no size</span></td>'
            )
        else:
            qty_html = (
                f'<td style="padding: 8px 6px; text-align: right; font-weight: 600;">{p.suggested_qty:,}'
                f'<br><span style="color: #999; font-size: 10px;">₹{p.position_value_inr/1000:,.0f}k</span></td>'
            )
        html.append(
            f'<tr style="background: {row_bg}; border-bottom: 1px solid #eee;">'
            f'<td style="padding: 8px 6px; color: #888;">{i}</td>'
            f'<td style="padding: 8px 6px;"><b style="color: {name_color};">{p.name}</b><br><span style="color: #999; font-size: 10px;">{p.ticker}</span>{earnings_tag}</td>'
            f'<td style="padding: 8px 6px; color: #555; font-size: 11px;">{p.sector.replace("Nifty ", "")}</td>'
            f'<td style="padding: 8px 6px; text-align: right; font-weight: 600;">₹{p.current_price:,.0f}</td>'
            f'<td style="padding: 8px 6px; text-align: right;">₹{p.week52_high:,.0f}<br><span style="color: #b23a3a; font-size: 10px;">-{distance_from_high*100:.1f}%</span></td>'
            f'<td style="padding: 8px 6px; text-align: right;">₹{p.sma_20:,.0f}</td>'
            f'<td style="padding: 8px 6px; text-align: right; font-weight: 700; color: {entry_color};">₹{p.entry:,.0f}</td>'
            f'<td style="padding: 8px 6px; text-align: right; color: #b23a3a;">₹{p.stop_loss:,.0f}</td>'
            f'<td style="padding: 8px 6px; text-align: right; color: #0d5f3f;">₹{p.target_1:,.0f}<br><span style="color: #148055; font-size: 10px;">₹{p.target_2:,.0f}</span></td>'
            f'{qty_html}'
            f'<td style="padding: 8px 6px;"><span style="background: {pill_bg}; color: {pill_fg}; padding: 3px 8px; border-radius: 10px; font-size: 10px; font-weight: 700; letter-spacing: 0.3px; white-space: nowrap;">{pill_label}</span></td>'
            f'</tr>'
        )
    html.append('</tbody></table></div>')

    html.append('<div style="margin-top: 14px; padding: 12px 14px; background: #fff; border-radius: 6px; border: 1px solid #e0e0e0;">')
    html.append(
        f'<div style="font-size: 11px; font-weight: 700; color: {name_color}; text-transform: uppercase; '
        f'letter-spacing: 0.5px; margin-bottom: 8px;">{details_title}</div>'
    )
    for i, p in enumerate(picks, 1):
        display_action = (
            f"DO NOT ENTER. Setup if regime flips: {p.action_today}"
            if stand_aside else p.action_today
        )
        html.append(
            f'<div style="font-size: 12px; color: #333; line-height: 1.6; margin-bottom: 6px;">'
            f'<b style="color: {name_color};">{i}. {p.name}</b> '
            f'<span style="color: #888;">&middot; 3M {p.return_3m*100:+.1f}% &middot; at {p.proximity_to_high_pct*100:.0f}% of 52W high &middot; wkly HullMA {p.hull_ma_30_weekly:,.0f}</span><br>'
            f'<span style="color: #555;">{p.desc}</span><br>'
            f'<span style="color: #7a5c00; font-size: 11px;">↳ {display_action}</span>'
            f'</div>'
        )
    html.append('</div>')

    return "".join(html)


def _exit_block_html(positions: list[Position]) -> str:
    """Block B: exit tracker as a compact scannable table. Always renders."""
    html = ['<h2 style="font-size: 15px; color: #b23a3a; border-bottom: 2px solid #b23a3a; padding-bottom: 6px; margin-top: 28px;">Block B &middot; Exit Tracker (Open Positions)</h2>']

    if not positions:
        html.append("""
        <div style="padding: 14px 16px; background: #f5f5f5; border-radius: 6px; border-left: 4px solid #bbb; text-align: center;">
            <div style="font-size: 14px; color: #555;">No open positions — all cash.</div>
            <div style="font-size: 12px; color: #888; margin-top: 4px;">Log new buys in the Google Sheet to enable exit alerts.</div>
        </div>
        """)
        return "".join(html)

    html.extend([
        '<div style="overflow-x: auto;">',
        '<table style="width: 100%; border-collapse: collapse; font-size: 12px; background: #fff; box-shadow: 0 1px 2px rgba(0,0,0,0.04); border-radius: 6px; overflow: hidden;">',
        '<thead><tr style="background: #b23a3a; color: #fff; text-align: left;">'
        '<th style="padding: 8px 6px;">Stock</th>'
        '<th style="padding: 8px 6px;">Bought</th>'
        '<th style="padding: 8px 6px; text-align: right;">Buy</th>'
        '<th style="padding: 8px 6px; text-align: right;">CMP</th>'
        '<th style="padding: 8px 6px; text-align: right;">P&amp;L</th>'
        '<th style="padding: 8px 6px; text-align: right;">SL</th>'
        '<th style="padding: 8px 6px; text-align: right;">TP1 / TP2</th>'
        '<th style="padding: 8px 6px;">Status</th>'
        '<th style="padding: 8px 6px;">Action</th>'
        '</tr></thead><tbody>'
    ])

    for i, p in enumerate(positions):
        text_color, bg_color, _ = URGENCY_STYLES.get(p.urgency, URGENCY_STYLES["info"])
        pnl_color = "#0d5f3f" if p.unrealized_pnl_pct >= 0 else "#b23a3a"
        row_bg = "#fafafa" if i % 2 == 0 else "#fff"
        html.append(
            f'<tr style="background: {row_bg}; border-bottom: 1px solid #eee;">'
            f'<td style="padding: 8px 6px;"><b>{p.company or p.ticker}</b><br><span style="color: #999; font-size: 10px;">{p.ticker}</span></td>'
            f'<td style="padding: 8px 6px; color: #555; font-size: 11px;">{p.buy_date}</td>'
            f'<td style="padding: 8px 6px; text-align: right;">₹{p.buy_price:,.0f}<br><span style="color: #999; font-size: 10px;">× {p.quantity}</span></td>'
            f'<td style="padding: 8px 6px; text-align: right; font-weight: 600;">₹{p.current_price:,.0f}</td>'
            f'<td style="padding: 8px 6px; text-align: right; font-weight: 700; color: {pnl_color};">{p.unrealized_pnl_pct*100:+.1f}%<br><span style="font-size: 10px;">₹{p.unrealized_pnl_inr:,.0f}</span></td>'
            f'<td style="padding: 8px 6px; text-align: right; color: #b23a3a;">₹{p.stop_loss:,.0f}</td>'
            f'<td style="padding: 8px 6px; text-align: right; color: #0d5f3f;">₹{p.target_1:,.0f}<br><span style="font-size: 10px;">₹{p.target_2:,.0f}</span></td>'
            f'<td style="padding: 8px 6px; font-size: 11px;">{p.status}</td>'
            f'<td style="padding: 8px 6px;"><span style="background: {text_color}; color: #fff; padding: 3px 8px; border-radius: 10px; font-size: 10px; font-weight: 700; white-space: nowrap;">{p.urgency.upper()}</span></td>'
            f'</tr>'
        )
    html.append('</tbody></table></div>')

    # Action details strip
    html.append('<div style="margin-top: 12px; padding: 12px 14px; background: #fff; border-radius: 6px; border: 1px solid #e0e0e0;">')
    html.append('<div style="font-size: 11px; font-weight: 700; color: #b23a3a; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Actions for today</div>')
    for p in positions:
        text_color, _, _ = URGENCY_STYLES.get(p.urgency, URGENCY_STYLES["info"])
        html.append(
            f'<div style="font-size: 12px; color: #333; line-height: 1.6; margin-bottom: 6px;">'
            f'<b style="color: {text_color};">{p.company or p.ticker}:</b> {p.action}'
            f'</div>'
        )
    html.append('</div>')

    return "".join(html)


def build_html(
    sectors: list[SectorScore],
    picks: list[StockPick],
    positions: list[Position],
    narrative: Optional[str],
    date_str: str,
    universe_stats: Optional[dict] = None,
    new_names: Optional[list[str]] = None,
    freshness_msg: str = "",
    is_fresh: bool = True,
    regime: Optional[Regime] = None,
) -> str:
    parts = [f"""
    <html><body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 720px; margin: 0 auto; color: #1a1a1a;">
    <div style="background: linear-gradient(135deg, #0d5f3f 0%, #148055 100%); padding: 28px 24px; border-radius: 8px 8px 0 0;">
        <h1 style="color: #fff; margin: 0; font-size: 22px;">Swing Trading Alert &middot; India</h1>
        <p style="color: #b8f0d4; margin: 6px 0 0; font-size: 14px;">{date_str} &middot; Vijay Thakkar top-down method</p>
    </div>
    <div style="padding: 20px 24px; background: #f8f9fa; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 8px 8px;">
    """]

    # Market regime banner — top priority signal
    if regime is not None:
        if regime.label == "STAND_ASIDE":
            r_bg, r_border, r_fg = "#f8d7da", "#b23a3a", "#721c24"
            r_prefix = "🛑 STAND ASIDE"
        elif regime.label == "CAUTION":
            r_bg, r_border, r_fg = "#fff3cd", "#ffc107", "#856404"
            r_prefix = "⚠️ CAUTION"
        else:
            r_bg, r_border, r_fg = "#d4edda", "#28a745", "#155724"
            r_prefix = "✅ TRADE"
        reasons_html = " · ".join(regime.reasons) if regime.reasons else ""
        parts.append(f"""
        <div style="background: {r_bg}; border: 1px solid {r_border}; border-left: 4px solid {r_border}; border-radius: 6px; padding: 12px 16px; margin-bottom: 16px;">
            <div style="font-size: 13px; font-weight: 700; color: {r_fg}; margin-bottom: 4px;">{r_prefix} · Market Regime</div>
            <div style="font-size: 12px; color: {r_fg}; line-height: 1.5;">{regime.short_message()}</div>
            <div style="font-size: 11px; color: {r_fg}; margin-top: 4px; opacity: 0.85;">{reasons_html}</div>
            <div style="font-size: 11px; color: {r_fg}; margin-top: 4px;">Position sizing overridden to <b>{regime.suggested_risk_pct*100:.1f}% risk per trade</b> ({'no new entries' if regime.suggested_risk_pct == 0 else 'reduced' if regime.suggested_risk_pct < 0.02 else 'normal'}).</div>
        </div>
        """)

    # Data freshness banner — prominent if stale
    if not is_fresh:
        parts.append(f"""
        <div style="background: #fff3cd; border: 1px solid #ffc107; border-left: 4px solid #ffc107; border-radius: 6px; padding: 12px 16px; margin-bottom: 16px;">
            <div style="font-size: 12px; font-weight: 700; color: #856404; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Data Freshness</div>
            <p style="font-size: 13px; color: #856404; margin: 0; line-height: 1.5;">{freshness_msg}</p>
        </div>
        """)
    elif freshness_msg:
        parts.append(f"""
        <div style="font-size: 11px; color: #888; margin-bottom: 12px; text-align: right;">{freshness_msg}</div>
        """)

    if narrative:
        parts.append(f"""
        <div style="background: linear-gradient(135deg, #f0fff7 0%, #e8faf0 100%); border: 1px solid #b5e0c8; border-radius: 8px; padding: 16px 20px; margin-bottom: 20px;">
            <div style="font-size: 12px; font-weight: 700; color: #0d5f3f; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Today's Summary</div>
            <p style="font-size: 14px; color: #2c3e50; line-height: 1.65; margin: 0;">{narrative.replace(chr(10), '<br>')}</p>
        </div>
        """)

    # Sectors
    if sectors:
        parts.append('<h2 style="font-size: 15px; color: #0d5f3f; border-bottom: 2px solid #148055; padding-bottom: 6px; margin-top: 20px;">Top Sectors (3M Relative Strength vs Nifty)</h2>')
        parts.append('<table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 20px;"><thead><tr style="background: #eaf5ef; text-align: left;"><th style="padding: 8px;">Sector</th><th style="padding: 8px; text-align: right;">3M Return</th><th style="padding: 8px; text-align: right;">vs Nifty</th></tr></thead><tbody>')
        for s in sectors:
            parts.append(f'<tr style="border-bottom: 1px solid #e0e0e0;"><td style="padding: 8px;">{s.name}</td><td style="padding: 8px; text-align: right; color: #0d5f3f; font-weight: 600;">{s.return_3m*100:+.1f}%</td><td style="padding: 8px; text-align: right; color: #0d5f3f; font-weight: 600;">{s.rs*100:+.1f}%</td></tr>')
        parts.append("</tbody></table>")

    # Stocks — Block A: entry candidates, or watchlist-only on STAND_ASIDE
    stand_aside = regime is not None and regime.label == "STAND_ASIDE"
    if picks:
        parts.append(_entry_block_html(picks, stand_aside=stand_aside))
    else:
        parts.append('<p style="color: #666; font-size: 14px;">No stocks passed all filters today. Market may be in risk-off mode — stay in cash.</p>')

    # Block B: Exit tracker (always renders)
    parts.append(_exit_block_html(positions))

    # Footer meta
    footer_meta = ""
    if universe_stats:
        footer_meta = (f"Scanned {universe_stats['total']} stocks "
                       f"({universe_stats['curated']} curated + {universe_stats['nse_added']} auto-fetched). "
                       f"Position sizing: {RISK_PER_TRADE_PCT*100:.0f}% risk of ₹{CAPITAL_INR:,.0f} = ₹{RISK_PER_TRADE_INR:,.0f} per trade.")
    new_desc_note = ""
    if new_names:
        new_desc_note = f"<br><b>New to your watchlist today:</b> {', '.join(new_names)} — descriptions auto-generated. Consider adding hand-written 1-liners to <code>swing_alert/universe.yaml</code>."

    parts.append(f"""
    <hr style="border: none; border-top: 1px solid #ddd; margin: 24px 0 12px;">
    <p style="font-size: 11px; color: #999; text-align: center;">
        {footer_meta}{new_desc_note}<br>
        Grounded in NSE EOD data via yfinance. Strategy: Vijay Thakkar top-down (see <code>Knowledge/Swing Trading Strategy.md</code>).<br>
        Not investment advice. Do your own diligence and manage position size.
    </p>
    </div></body></html>
    """)
    return "".join(parts)


def build_plaintext(
    sectors: list[SectorScore],
    picks: list[StockPick],
    positions: list[Position],
    narrative: Optional[str],
    date_str: str,
    freshness_msg: str = "",
    regime: Optional[Regime] = None,
) -> str:
    lines = [f"Swing Trading Alert — {date_str}", "=" * 50, ""]
    if regime is not None:
        lines += [
            f"MARKET REGIME: {regime.label}",
            f"  {regime.short_message()}",
        ]
        for r in regime.reasons:
            lines.append(f"  - {r}")
        lines += [f"  Risk per trade overridden to {regime.suggested_risk_pct*100:.1f}%", ""]
    if freshness_msg:
        lines += [freshness_msg, ""]
    if narrative:
        lines += ["SUMMARY", "-" * 20, narrative, ""]
    if sectors:
        lines += ["TOP SECTORS (3M RS vs Nifty)", "-" * 20]
        for s in sectors:
            lines.append(f"  {s.name}: {s.return_3m*100:+.1f}% (RS {s.rs*100:+.1f}%)")
        lines.append("")
    if picks:
        stand_aside = regime is not None and regime.label == "STAND_ASIDE"
        if stand_aside:
            lines += [
                f"BLOCK A - WATCHLIST ONLY (DO NOT ENTER) - {len(picks)} names",
                "-" * 20,
                "Cash is the trade. Do not place buy-stops. Qty is zero on purpose.",
                "",
            ]
        else:
            lines += [f"BLOCK A — ENTRY CANDIDATES (Top {len(picks)})", "-" * 20]
        for i, p in enumerate(picks, 1):
            earnings_line = f"   ⚠️ EARNINGS RISK: {p.earnings_date} (within 5 trading days)" if p.earnings_soon else None
            qty_line = (
                "   Suggested qty: n/a (STAND_ASIDE - no size)"
                if stand_aside
                else f"   Suggested qty: {p.suggested_qty} | Position value: ₹{p.position_value_inr:,.0f} | Risk: ₹{p.risk_amount_inr:,.0f}"
            )
            action_line = (
                f"   Action: DO NOT ENTER. Setup if regime flips: {p.action_today}"
                if stand_aside
                else f"   Action: {p.action_today}"
            )
            entry_lines = [
                f"{i}. {p.name} ({p.ticker}) — {p.sector}",
                f"   {p.desc}",
                f"   Price: ₹{p.current_price} | 52W high: ₹{p.week52_high} ({p.week52_high_date})",
                f"   20 SMA: ₹{p.sma_20} | Weekly HullMA30: ₹{p.hull_ma_30_weekly} | 3M return: {p.return_3m*100:+.1f}%",
                f"   Entry: ₹{p.entry} | SL: ₹{p.stop_loss} | TP1: ₹{p.target_1} | TP2: ₹{p.target_2}",
                qty_line,
                action_line,
            ]
            if earnings_line:
                entry_lines.append(earnings_line)
            entry_lines.append("")
            lines += entry_lines
    else:
        lines.append("No stocks passed all filters today.")
        lines.append("")

    # Block B — exit tracker
    lines += ["BLOCK B — EXIT TRACKER (Open Positions)", "-" * 20]
    if not positions:
        lines += ["  No open positions — all cash.", ""]
    else:
        for p in positions:
            lines += [
                f"  {p.company or p.ticker} ({p.ticker}) — Status: {p.status}",
                f"     Buy: ₹{p.buy_price} x {p.quantity} on {p.buy_date}",
                f"     Current: ₹{p.current_price} | PnL: {p.unrealized_pnl_pct*100:+.2f}% (₹{p.unrealized_pnl_inr:,.0f})",
                f"     SL: ₹{p.stop_loss} | TP1: ₹{p.target_1} | TP2: ₹{p.target_2} | 20SMA: ₹{p.sma_20_daily}",
                f"     ACTION [{p.urgency.upper()}]: {p.action}",
                "",
            ]
    return "\n".join(lines)


def send_email(subject: str, html: str, plaintext: str):
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port_raw = os.environ.get("SMTP_PORT") or "587"
    port = int(port_raw)
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    recipient = os.environ.get("RECIPIENT_EMAIL", user)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Swing Alert <{user}>"
    msg["To"] = recipient
    msg.attach(MIMEText(plaintext, "plain"))
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(user, [recipient], msg.as_string())
    log.info(f"Swing alert sent to {recipient}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_alert(preview_mode: bool = False) -> tuple[str, str, str, dict]:
    """
    Run the full pipeline and return (subject, html, plaintext, meta).
    Used by both main() (sends email) and preview.py (dumps to disk).
    """
    log.info("Starting Swing Trading Alert" + (" [PREVIEW MODE]" if preview_mode else ""))
    universe = load_universe()

    # 0. Market regime — may reduce or zero out risk before we even scan
    regime = evaluate_regime()
    log.info(f"Market regime: {regime.short_message()}")
    # Override the global risk pct if regime says so
    global RISK_PER_TRADE_INR
    effective_risk_pct = regime.suggested_risk_pct if regime.label != "TRADE" else RISK_PER_TRADE_PCT
    RISK_PER_TRADE_INR = CAPITAL_INR * effective_risk_pct

    # 1. Rank sectors + capture benchmark for freshness check
    top_sectors, benchmark_df = rank_sectors(universe)
    is_fresh, freshness_msg = check_data_freshness(benchmark_df)
    log.info(freshness_msg)

    picks: list[StockPick] = []
    universe_stats: dict = {"total": 0, "curated": 0, "nse_added": 0}
    new_names: list[str] = []

    if not top_sectors:
        log.error("No sectors ranked — sending alert with empty pick list instead of aborting.")
        freshness_msg = (freshness_msg + " " if freshness_msg else "") + (
            "No sector beat Nifty on 3M RS (or Yahoo data was unavailable). "
            "No new entries today."
        )
        is_fresh = False
    else:
        top_sector_names = {s.name for s in top_sectors}
        log.info(f"Top sectors: {[s.name for s in top_sectors]}")

        # 2. Build FULL scan universe (curated 40 + NSE Smallcap/Midcap/Microcap constituents)
        curated_path = Path(__file__).parent / "universe.yaml"
        scan_stocks, universe_stats = build_scan_universe(curated_path)

        # 3. Filter to stocks in top sectors
        eligible_stocks = [s for s in scan_stocks if s["sector"] in top_sector_names]
        log.info(f"Analysing {len(eligible_stocks)} stocks from winning sectors "
                 f"(universe total: {universe_stats['total']})")

        # 4. Analyse each stock (with sector-rank bonus applied to the score)
        benchmark_3m = top_sectors[0].benchmark_return_3m
        sector_bonus_by_name = {
            s.name: (SECTOR_RANK_BONUS[i] if i < len(SECTOR_RANK_BONUS) else 0.0)
            for i, s in enumerate(top_sectors)
        }
        all_passing: list[StockPick] = []
        for cfg in eligible_stocks:
            bonus = sector_bonus_by_name.get(cfg["sector"], 0.0)
            pick = analyze_stock(cfg, benchmark_3m, sector_bonus=bonus)
            if pick:
                all_passing.append(pick)

        log.info(f"{len(all_passing)} stocks passed all filters")

        # 5. Diversified top-N selection:
        #    - sort by score desc
        #    - cap per sector at MAX_STOCKS_PER_SECTOR
        #    - guarantee at least 1 stock from top-3 sectors if they have any passer
        all_passing.sort(key=lambda p: p.score, reverse=True)

        per_sector_count: dict[str, int] = {}

        # Pass 1: guarantee coverage of top-3 sectors (highest scorer from each)
        for sector_score in top_sectors[:3]:
            best_in_sector = next((p for p in all_passing if p.sector == sector_score.name), None)
            if best_in_sector and best_in_sector not in picks:
                picks.append(best_in_sector)
                per_sector_count[best_in_sector.sector] = 1

        # Pass 2: fill remaining slots by score, respecting the per-sector cap
        for p in all_passing:
            if len(picks) >= TOP_N_STOCKS:
                break
            if p in picks:
                continue
            if per_sector_count.get(p.sector, 0) >= MAX_STOCKS_PER_SECTOR:
                log.debug(f"  cap-skipped {p.name} ({p.sector}, count={per_sector_count[p.sector]})")
                continue
            picks.append(p)
            per_sector_count[p.sector] = per_sector_count.get(p.sector, 0) + 1

        log.info(f"Selected {len(picks)} picks across sectors: {per_sector_count}")

        # Final ordering: by score for presentation
        picks.sort(key=lambda p: p.score, reverse=True)

        # 6. Lazy-fetch descriptions + earnings check for stocks that made the top N
        for p in picks:
            if not p.desc:
                p.desc = fetch_fallback_description(p.ticker)
                new_names.append(p.name)
            # Earnings guard — flag stocks with earnings in next ~5 trading days
            p.earnings_soon, p.earnings_date = has_earnings_soon(p.ticker)
            if p.earnings_soon:
                log.warning(f"  ⚠️ {p.name} has earnings on {p.earnings_date}")
        if new_names:
            log.info(f"Fetched fallback descriptions for: {new_names}")

    # 7. Load and evaluate open positions from Google Sheet (exit tracker)
    open_positions = load_positions_from_sheet()
    evaluated_positions = evaluate_all(open_positions) if open_positions else []

    # 7b. Log predictions to Google Sheet (skip in preview to avoid polluting live log)
    if not preview_mode:
        rows_logged, log_err = log_predictions(picks, top_sectors, regime=regime.label)
        if log_err:
            log.info(f"Predictions Log: {log_err}")
        else:
            log.info(f"Predictions Log: wrote {rows_logged} rows.")

    # 8. Narrative
    narrative = generate_narrative(top_sectors, picks, regime=regime)

    # 9. Build email content
    date_str = datetime.now(IST).strftime("%A, %B %d, %Y")
    if regime.label == "STAND_ASIDE":
        subject = f"[STAND_ASIDE] Swing Alert - {date_str} (watchlist {len(picks)}, no new entries)"
    else:
        regime_tag = "" if regime.label == "TRADE" else f"[{regime.label}] "
        subject = f"{regime_tag}Swing Alert — {date_str} ({len(picks)} new / {len(evaluated_positions)} open)"
    if not is_fresh:
        subject = "⚠️ " + subject + " [STALE DATA]"
    html = build_html(top_sectors, picks, evaluated_positions, narrative, date_str, universe_stats, new_names, freshness_msg=freshness_msg, is_fresh=is_fresh, regime=regime)
    plaintext = build_plaintext(top_sectors, picks, evaluated_positions, narrative, date_str, freshness_msg=freshness_msg, regime=regime)

    meta = {
        "universe_stats": universe_stats,
        "top_sectors": [(s.name, round(s.rs*100, 2)) for s in top_sectors],
        "picks_count": len(picks),
        "positions_count": len(evaluated_positions),
        "regime": regime.label,
        "picks": picks,
    }
    return subject, html, plaintext, meta


def main():
    try:
        subject, html, plaintext, meta = build_alert(preview_mode=False)
    except Exception as e:
        log.exception("Alert pipeline crashed")
        try:
            send_email(
                "⚠️ Swing Alert FAILED",
                f"<p>The morning pipeline crashed before picks were built.</p><pre>{e}</pre>",
                f"Swing alert pipeline crashed: {e}",
            )
        except Exception:
            log.exception("Also failed to send crash-notification email")
        sys.exit(1)
        return
    try:
        send_email(subject, html, plaintext)
    except KeyError as e:
        log.error(f"Missing env var {e}. Copy .env.example to .env or set GitHub secrets.")
        sys.exit(1)
    except Exception as e:
        log.error(f"Email send failed: {e}")
        sys.exit(1)
    log.info("Done.")


if __name__ == "__main__":
    main()
