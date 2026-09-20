"""
Earnings Guard — flags stocks with earnings within the next 5 trading days.

Swing trades over earnings are essentially gambling on the print — Vijay
explicitly avoids them. This module checks each pick's next earnings date
via yfinance and returns True if the stock is in the danger window.

Uses yfinance's calendar endpoint. Gracefully handles missing data.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import yfinance as yf

log = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))
DANGER_WINDOW_DAYS = 7  # calendar days ≈ 5 trading days


def has_earnings_soon(ticker: str) -> tuple[bool, Optional[str]]:
    """
    Returns (has_earnings_within_window, earnings_date_str_or_None).
    Never crashes — returns (False, None) if data is unavailable.
    """
    try:
        t = yf.Ticker(ticker)
        cal = t.calendar
        if cal is None:
            return False, None

        # yfinance calendar can be a DataFrame or a dict depending on version
        earnings_date = None
        if hasattr(cal, "loc"):  # DataFrame-like
            try:
                earnings_date = cal.loc["Earnings Date"].iloc[0]
            except Exception:
                earnings_date = None
        elif isinstance(cal, dict):
            ed = cal.get("Earnings Date")
            if isinstance(ed, list) and ed:
                earnings_date = ed[0]
            elif ed:
                earnings_date = ed

        if earnings_date is None:
            return False, None

        # Normalise to a date
        if hasattr(earnings_date, "to_pydatetime"):
            earnings_date = earnings_date.to_pydatetime()
        if isinstance(earnings_date, datetime):
            ed_date = earnings_date.date()
        else:
            ed_date = earnings_date

        today = datetime.now(IST).date()
        days_out = (ed_date - today).days

        if 0 <= days_out <= DANGER_WINDOW_DAYS:
            return True, ed_date.strftime("%d %b %Y")
        return False, ed_date.strftime("%d %b %Y") if ed_date else None

    except Exception as e:
        log.debug(f"Earnings check failed for {ticker}: {e}")
        return False, None
