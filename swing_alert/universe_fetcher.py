"""
Universe fetcher — pulls Smallcap 250, Midcap 150, Microcap 250 constituents
from NSE India, merges with the curated list in universe.yaml, and returns
the full scan universe.

Design:
- Curated stocks (universe.yaml) always win on descriptions.
- NSE-fetched stocks fill the gap, using yfinance's longBusinessSummary as
  a fallback description (truncated).
- Sector tagging for NSE-fetched stocks uses NSE's own industry classification
  where available, else "Uncategorised" and filtered out downstream.

NSE endpoints require a browser-like User-Agent header. We cache the CSV
response to disk so we don't hammer NSE on every run.
"""

from __future__ import annotations

import csv
import io
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests
import yaml

log = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)
CACHE_TTL_HOURS = 24  # NSE constituents change quarterly; 24h cache is plenty

# NSE archive URLs for index constituents (CSV format)
INDEX_URLS = {
    "Nifty Smallcap 250":  "https://nsearchives.nseindia.com/content/indices/ind_niftysmallcap250list.csv",
    "Nifty Midcap 150":    "https://nsearchives.nseindia.com/content/indices/ind_niftymidcap150list.csv",
    "Nifty Microcap 250":  "https://nsearchives.nseindia.com/content/indices/ind_niftymicrocap250_list.csv",
}

# Map NSE Industry field → our sector taxonomy in universe.yaml
# Keep this aligned with the sector_indices list in universe.yaml. If a sector
# ETF isn't in universe.yaml, its stocks will still be scanned but never win
# sector-ranking (because there's no index to rank).
# NOTE: NSE Industry strings can include trailing spaces or minor variations —
# we normalise (strip + collapse whitespace) before lookup.
INDUSTRY_TO_SECTOR = {
    "Automobile and Auto Components": "Nifty Auto",
    "Capital Goods": "Nifty Infra",
    "Chemicals": "Nifty Metal",
    "Construction": "Nifty Infra",
    "Construction Materials": "Nifty Infra",
    "Consumer Durables": "Nifty Consumer Durables",
    "Consumer Services": "Nifty FMCG",
    "Diversified": "Nifty Infra",
    "Fast Moving Consumer Goods": "Nifty FMCG",
    "Financial Services": "Nifty Financial Services",
    "Forest Materials": "Nifty Infra",
    "Healthcare": "Nifty Pharma",
    "Information Technology": "Nifty IT",
    "Media Entertainment & Publication": "Nifty Consumer Durables",  # closest tracked proxy
    "Metals & Mining": "Nifty Metal",
    "Oil Gas & Consumable Fuels": "Nifty Infra",   # no reliable Nifty Energy ETF in yfinance
    "Power": "Nifty Infra",
    "Realty": "Nifty Realty",
    "Services": "Nifty Financial Services",
    "Telecommunication": "Nifty IT",
    "Textiles": "Nifty Consumer Durables",
}


def _normalise_industry(s: str) -> str:
    return " ".join(s.split()).strip()

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/csv,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}


def _cache_path(index_name: str) -> Path:
    slug = index_name.lower().replace(" ", "_")
    return CACHE_DIR / f"{slug}.csv"


def _is_cache_fresh(path: Path) -> bool:
    if not path.exists():
        return False
    age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
    return age < timedelta(hours=CACHE_TTL_HOURS)


def fetch_index_constituents(index_name: str, url: str) -> list[dict]:
    """Fetch (or read from cache) the constituent list for one NSE index."""
    cache_file = _cache_path(index_name)

    if _is_cache_fresh(cache_file):
        log.info(f"  {index_name}: using cached list")
        text = cache_file.read_text(encoding="utf-8")
    else:
        log.info(f"  {index_name}: fetching from NSE...")
        try:
            r = requests.get(url, headers=NSE_HEADERS, timeout=15)
            r.raise_for_status()
            text = r.text
            cache_file.write_text(text, encoding="utf-8")
        except Exception as e:
            log.warning(f"  {index_name}: fetch failed ({e}); falling back to cache if any")
            if cache_file.exists():
                text = cache_file.read_text(encoding="utf-8")
            else:
                return []

    rows = []
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        # NSE CSV columns: Company Name, Industry, Symbol, Series, ISIN Code
        symbol = (row.get("Symbol") or "").strip()
        company = (row.get("Company Name") or "").strip()
        industry = (row.get("Industry") or "").strip()
        if not symbol or not company:
            continue
        # Filter NSE placeholder rows (e.g. DUMMYINGL1 in Microcap 250)
        if symbol.upper().startswith("DUMMY"):
            continue
        rows.append({
            "symbol": symbol,
            "name": company,
            "industry": industry,
            "index": index_name,
        })
    return rows


def build_scan_universe(curated_yaml_path: Path) -> tuple[list[dict], dict]:
    """
    Returns:
      (scan_stocks, stats)
      scan_stocks: list of dicts with keys ticker, name, sector, desc, source
      stats: {curated: N, nse_added: N, total: N, unmapped: N}
    """
    with open(curated_yaml_path) as f:
        cfg = yaml.safe_load(f)

    # Curated stocks — indexed by symbol (without .NS suffix) for merging
    curated: dict[str, dict] = {}
    for s in cfg.get("stocks", []):
        symbol = s["ticker"].replace(".NS", "").upper()
        curated[symbol] = {
            "ticker": s["ticker"],
            "name": s["name"],
            "sector": s["sector"],
            "desc": s["desc"],
            "source": "curated",
        }

    # NSE constituents from the three broad indices
    nse_rows: dict[str, dict] = {}
    for idx_name, url in INDEX_URLS.items():
        for row in fetch_index_constituents(idx_name, url):
            sym = row["symbol"].upper()
            if sym in nse_rows:
                continue
            nse_rows[sym] = row

    # Merge: curated wins; NSE fills in
    scan: list[dict] = list(curated.values())
    added = 0
    unmapped = 0
    for sym, row in nse_rows.items():
        if sym in curated:
            continue
        industry_clean = _normalise_industry(row["industry"])
        sector = INDUSTRY_TO_SECTOR.get(industry_clean)
        if not sector:
            unmapped += 1
            continue
        scan.append({
            "ticker": f"{sym}.NS",
            "name": row["name"],
            "sector": sector,
            "desc": "",  # will be lazily filled from yfinance if this stock makes it to top-N
            "source": "nse",
        })
        added += 1

    stats = {
        "curated": len(curated),
        "nse_added": added,
        "total": len(scan),
        "unmapped_industry": unmapped,
    }
    log.info(f"Scan universe built: {stats}")
    return scan, stats


def fetch_fallback_description(ticker: str) -> str:
    """Fetch a short description from yfinance for stocks not in curated list."""
    try:
        import yfinance as yf
        info = yf.Ticker(ticker).info
        summary = (info.get("longBusinessSummary") or "").strip()
        if not summary:
            return "Small/mid-cap NSE listed company (description pending)."
        # Take first sentence, cap at 180 chars
        first_sentence = summary.split(".")[0].strip()
        if len(first_sentence) > 180:
            first_sentence = first_sentence[:177] + "..."
        return first_sentence + "."
    except Exception as e:
        log.warning(f"  fallback desc failed for {ticker}: {e}")
        return "Small/mid-cap NSE listed company (description pending)."
