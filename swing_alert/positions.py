"""
Positions module — reads open swing-trade positions from a Google Sheet and
evaluates each against current market price to produce exit guidance.

Google Sheet schema (first row must be headers, exact case-insensitive names):
  Ticker | Company | Buy Date | Buy Price | Quantity | Stop Loss | Target 1 | Target 2 | Status | Notes

Status values: OPEN, TP1_HIT, CLOSED
  - OPEN: still holding full quantity
  - TP1_HIT: booked 50% at TP1, holding remainder with SL moved to breakeven
  - CLOSED: exited fully (script ignores these)

Authentication:
  - Uses a Google service account (JSON key stored as GitHub secret GOOGLE_SA_JSON)
  - Service account email must be added as an Editor on the sheet
  - Sheet ID stored as env var POSITIONS_SHEET_ID
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import yfinance as yf

log = logging.getLogger(__name__)


@dataclass
class Position:
    ticker: str
    company: str
    buy_date: str
    buy_price: float
    quantity: int
    stop_loss: float
    target_1: float
    target_2: float
    status: str            # OPEN, TP1_HIT
    notes: str

    # Filled in by evaluate()
    current_price: float = 0.0
    unrealized_pnl_pct: float = 0.0
    unrealized_pnl_inr: float = 0.0
    action: str = ""       # HOLD / BOOK PARTIAL AT TP1 / BOOK FULL AT TP2 / STOP-LOSS TRIGGERED / TRAIL SL
    urgency: str = "info"  # info | warn | critical
    sma_20_daily: float = 0.0


def _fetch_current(ticker: str) -> tuple[float, float]:
    """Return (last_close, sma_20_daily). Returns (0, 0) on failure."""
    try:
        df = yf.Ticker(ticker).history(period="60d", auto_adjust=False)
        if df is None or df.empty:
            return 0.0, 0.0
        last_close = float(df["Close"].iloc[-1])
        sma_20 = float(df["Close"].tail(20).mean()) if len(df) >= 20 else 0.0
        return last_close, sma_20
    except Exception as e:
        log.warning(f"  current price fetch failed for {ticker}: {e}")
        return 0.0, 0.0


def load_positions_from_sheet() -> list[Position]:
    """
    Read open positions from the configured Google Sheet.
    Returns [] if sheet not configured or read fails (never crashes the alert).
    """
    sheet_id = os.environ.get("POSITIONS_SHEET_ID")
    sa_json = os.environ.get("GOOGLE_SA_JSON")

    if not sheet_id:
        log.info("POSITIONS_SHEET_ID not set — skipping exit tracker")
        return []
    if not sa_json:
        log.info("GOOGLE_SA_JSON not set — skipping exit tracker")
        return []

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        log.warning("gspread/google-auth not installed — skipping exit tracker")
        return []

    try:
        creds_dict = json.loads(sa_json)
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).sheet1
        records = sheet.get_all_records()
    except Exception as e:
        log.warning(f"Positions sheet read failed: {e}")
        return []

    positions: list[Position] = []
    for row in records:
        # Case-insensitive column access
        rowl = {str(k).strip().lower(): v for k, v in row.items()}
        status = str(rowl.get("status", "")).strip().upper()
        if status in ("", "CLOSED"):
            continue
        try:
            positions.append(Position(
                ticker=str(rowl["ticker"]).strip(),
                company=str(rowl.get("company", "")).strip(),
                buy_date=str(rowl.get("buy date", "")).strip(),
                buy_price=float(rowl["buy price"]),
                quantity=int(float(rowl.get("quantity", 0) or 0)),
                stop_loss=float(rowl["stop loss"]),
                target_1=float(rowl["target 1"]),
                target_2=float(rowl["target 2"]),
                status=status if status in ("OPEN", "TP1_HIT") else "OPEN",
                notes=str(rowl.get("notes", "")).strip(),
            ))
        except (KeyError, ValueError, TypeError) as e:
            log.warning(f"Skipping malformed position row {row}: {e}")

    log.info(f"Loaded {len(positions)} open positions from sheet")
    return positions


def evaluate_position(pos: Position) -> Position:
    """Mutates and returns the position with current price, PnL, and action."""
    price, sma_20 = _fetch_current(pos.ticker)
    if price <= 0:
        pos.action = "Price fetch failed — check manually"
        pos.urgency = "warn"
        return pos

    pos.current_price = round(price, 2)
    pos.sma_20_daily = round(sma_20, 2)
    pos.unrealized_pnl_pct = (price - pos.buy_price) / pos.buy_price
    pos.unrealized_pnl_inr = round((price - pos.buy_price) * pos.quantity, 2)

    # Decision tree — order matters (evaluate worst-case first)
    if price <= pos.stop_loss:
        pos.action = f"STOP-LOSS TRIGGERED at ₹{pos.stop_loss:.2f} — exit at market, mark row as CLOSED"
        pos.urgency = "critical"
    elif pos.status == "OPEN" and price >= pos.target_2:
        pos.action = f"TP2 hit — book full position at ₹{price:.2f}, mark CLOSED"
        pos.urgency = "critical"
    elif pos.status == "OPEN" and price >= pos.target_1:
        pos.action = f"TP1 hit — book 50% at ₹{price:.2f}, move SL to breakeven (₹{pos.buy_price:.2f}), set Status = TP1_HIT"
        pos.urgency = "critical"
    elif pos.status == "TP1_HIT" and price >= pos.target_2:
        pos.action = f"TP2 hit on remainder — book at ₹{price:.2f}, mark CLOSED"
        pos.urgency = "critical"
    elif pos.status == "TP1_HIT" and sma_20 > pos.stop_loss and price > sma_20:
        pos.action = f"Trail SL up to 20-day SMA (₹{sma_20:.2f}) — update Stop Loss column"
        pos.urgency = "warn"
    elif price <= pos.stop_loss * 1.02:
        pos.action = f"Approaching SL (~{((price/pos.stop_loss)-1)*100:.1f}% above) — tighten mental stop"
        pos.urgency = "warn"
    elif price >= pos.target_1 * 0.98 and pos.status == "OPEN":
        pos.action = f"Approaching TP1 (~{((pos.target_1/price)-1)*100:.1f}% away) — ready booking order"
        pos.urgency = "warn"
    else:
        pos.action = f"HOLD — {pos.unrealized_pnl_pct*100:+.1f}% unrealized"
        pos.urgency = "info"

    return pos


def evaluate_all(positions: list[Position]) -> list[Position]:
    return [evaluate_position(p) for p in positions]
