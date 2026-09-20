"""
Market Regime module — determines whether market conditions favour swing trading.

Vijay explicitly says: "When the underlying index is in downtrend, stop swing
trading. All setups tend to fail together in a bear tape." This module encodes
that discipline.

Regime output: TRADE | CAUTION | STAND_ASIDE

TRADE:
  - Nifty 50 > 50-day SMA
  - Nifty 50 > 200-day SMA
  - VIX < 20
  - 5-day advance-decline positive (or unavailable)

CAUTION (reduce risk per trade to 1%, watch closely):
  - Nifty > 200-SMA but < 50-SMA (medium-term ok, short-term weak), OR
  - VIX between 20-25, OR
  - Any one bearish signal

STAND_ASIDE (skip fresh entries, only manage exits):
  - Nifty < 200-day SMA (structural bear), OR
  - VIX > 25 (panic), OR
  - Multiple bearish signals combined
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf

log = logging.getLogger(__name__)

NIFTY_TICKER = "^NSEI"
VIX_TICKER = "^INDIAVIX"


@dataclass
class Regime:
    label: str                       # TRADE | CAUTION | STAND_ASIDE
    nifty_close: float = 0.0
    nifty_sma_50: float = 0.0
    nifty_sma_200: float = 0.0
    nifty_above_50: bool = False
    nifty_above_200: bool = False
    india_vix: float = 0.0
    reasons: list = field(default_factory=list)
    suggested_risk_pct: float = 0.02  # override applied to position sizing

    def short_message(self) -> str:
        return f"{self.label} · Nifty {self.nifty_close:,.0f} " \
               f"({'above' if self.nifty_above_50 else 'below'} 50-SMA, " \
               f"{'above' if self.nifty_above_200 else 'below'} 200-SMA) · " \
               f"VIX {self.india_vix:.1f}"


def _fetch_series(ticker: str, days: int = 400) -> Optional[pd.DataFrame]:
    try:
        df = yf.Ticker(ticker).history(period=f"{days}d", auto_adjust=False)
        if df is None or df.empty:
            return None
        return df
    except Exception as e:
        log.warning(f"Regime fetch failed for {ticker}: {e}")
        return None


def evaluate_regime() -> Regime:
    """Assess current market regime. Never crashes — degrades to TRADE if data unavailable."""
    nifty = _fetch_series(NIFTY_TICKER)
    if nifty is None or len(nifty) < 200:
        log.warning("Regime: insufficient Nifty data; defaulting to TRADE.")
        return Regime(label="TRADE", reasons=["Regime check skipped (data unavailable)"])

    close = nifty["Close"].dropna()
    nifty_close = float(close.iloc[-1])
    sma_50 = float(close.tail(50).mean())
    sma_200 = float(close.tail(200).mean())
    above_50 = nifty_close > sma_50
    above_200 = nifty_close > sma_200

    # India VIX (optional — Yahoo may not always publish it under ^INDIAVIX)
    vix_val = 0.0
    vix = _fetch_series(VIX_TICKER, days=60)
    if vix is not None and not vix.empty:
        vix_close = vix["Close"].dropna()
        if len(vix_close) > 0:
            vix_val = float(vix_close.iloc[-1])

    reasons = []
    stand_aside = False
    caution = False

    if not above_200:
        stand_aside = True
        reasons.append(f"Nifty ({nifty_close:,.0f}) below 200-SMA ({sma_200:,.0f}) — structural downtrend")
    elif not above_50:
        caution = True
        reasons.append(f"Nifty below 50-SMA ({sma_50:,.0f}) — short-term weakness though structure intact")

    if vix_val > 25:
        stand_aside = True
        reasons.append(f"India VIX at {vix_val:.1f} — elevated risk / panic mode")
    elif vix_val > 20:
        caution = True
        reasons.append(f"India VIX at {vix_val:.1f} — elevated, tighten risk")

    if stand_aside:
        label = "STAND_ASIDE"
        risk = 0.0
    elif caution:
        label = "CAUTION"
        risk = 0.01
    else:
        label = "TRADE"
        risk = 0.02
        reasons.append(f"Nifty trending above 50/200-SMA, VIX benign ({vix_val:.1f})")

    return Regime(
        label=label,
        nifty_close=round(nifty_close, 2),
        nifty_sma_50=round(sma_50, 2),
        nifty_sma_200=round(sma_200, 2),
        nifty_above_50=above_50,
        nifty_above_200=above_200,
        india_vix=round(vix_val, 2),
        reasons=reasons,
        suggested_risk_pct=risk,
    )
