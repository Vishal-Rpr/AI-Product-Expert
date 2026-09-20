"""
Predictions Log module — appends every morning's picks to a Google Sheet so
we can measure outcomes over time (did the trigger fire? TP1/TP2/SL hit? R-multiple?).

Sheet schema (first row = headers, exact case-insensitive names):
  Date | Ticker | Company | Sector | Sector Rank | Action Pill | Score |
  CMP at Alert | Entry Trigger | SL | TP1 | TP2 | Suggested Qty |
  Triggered | Trigger Date | TP1 Hit | TP1 Date | TP2 Hit | TP2 Date |
  SL Hit | SL Date | Days Held | Return % | R-Multiple |
  Regime | Notes

The morning cron populates columns 1-13 (through Suggested Qty).
A separate nightly cron (built Week 2) populates outcome columns.

Auth uses the same GOOGLE_SA_JSON secret as positions.py. Sheet ID is
stored in PREDICTIONS_SHEET_ID env var.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

log = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

HEADERS = [
    "Date", "Ticker", "Company", "Sector", "Sector Rank", "Action Pill", "Score",
    "CMP at Alert", "Entry Trigger", "SL", "TP1", "TP2", "Suggested Qty",
    "Triggered", "Trigger Date", "TP1 Hit", "TP1 Date", "TP2 Hit", "TP2 Date",
    "SL Hit", "SL Date", "Days Held", "Return %", "R-Multiple",
    "Regime", "Notes",
]


def _get_client_and_sheet():
    """Returns (worksheet, None) or (None, error_message)."""
    sheet_id = os.environ.get("PREDICTIONS_SHEET_ID")
    sa_json = os.environ.get("GOOGLE_SA_JSON")

    if not sheet_id:
        return None, "PREDICTIONS_SHEET_ID not set"
    if not sa_json:
        return None, "GOOGLE_SA_JSON not set"

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        return None, "gspread/google-auth not installed"

    try:
        creds_dict = json.loads(sa_json)
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).sheet1
        return sheet, None
    except Exception as e:
        return None, f"Sheet auth/open failed: {e}"


def _ensure_headers(sheet) -> None:
    """If the sheet is empty, write the header row. Non-destructive if headers exist."""
    try:
        first_row = sheet.row_values(1)
    except Exception:
        first_row = []
    if not first_row:
        sheet.update("A1", [HEADERS])
        log.info("Predictions Log: wrote header row.")


def log_predictions(
    picks: list,
    top_sectors: list,
    regime: str = "UNKNOWN",
    dry_run: bool = False,
) -> tuple[int, Optional[str]]:
    """
    Append today's picks to the Predictions Log sheet.
    Returns (rows_written, error_message_or_None).

    - picks: list of StockPick objects (from alert.py)
    - top_sectors: list of SectorScore objects (for sector rank lookup)
    - regime: current market regime string (TRADE / CAUTION / STAND_ASIDE)
    - dry_run: if True, just log what would be written without touching the sheet
    """
    if not picks:
        log.info("Predictions Log: no picks to log.")
        return 0, None

    sheet, err = _get_client_and_sheet()
    if err:
        log.info(f"Predictions Log skipped: {err}")
        return 0, err

    _ensure_headers(sheet)

    sector_rank_map = {s.name: i + 1 for i, s in enumerate(top_sectors)}
    date_str = datetime.now(IST).strftime("%Y-%m-%d")

    rows = []
    for p in picks:
        # Derive action pill label (same logic as email)
        lower = p.action_today.lower()
        if lower.startswith("broke out") or "buy on any dip" in lower:
            pill = "BUY NOW"
        elif lower.startswith("place buy-stop"):
            pill = "BUY-STOP"
        elif lower.startswith("watchlist"):
            pill = "WATCH"
        elif lower.startswith("too far") or "already extended" in lower:
            pill = "WAIT"
        else:
            pill = "REVIEW"

        rows.append([
            date_str,
            p.ticker,
            p.name,
            p.sector,
            sector_rank_map.get(p.sector, 0),
            pill,
            round(p.score, 4),
            p.current_price,
            p.entry,
            p.stop_loss,
            p.target_1,
            p.target_2,
            p.suggested_qty,
            # Outcome columns start blank — nightly tracker populates them
            "", "", "", "", "", "",
            "", "", "", "", "",
            regime,
            "",
        ])

    if dry_run:
        log.info(f"Predictions Log DRY RUN: would append {len(rows)} rows.")
        return len(rows), None

    try:
        sheet.append_rows(rows, value_input_option="USER_ENTERED")
        log.info(f"Predictions Log: appended {len(rows)} predictions for {date_str}.")
        return len(rows), None
    except Exception as e:
        err_msg = f"Predictions Log append failed: {e}"
        log.warning(err_msg)
        return 0, err_msg
