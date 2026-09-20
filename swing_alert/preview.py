"""
Preview the swing alert without sending an email.
Runs the full pipeline and writes email HTML + plaintext to disk for review.

Usage:
    python swing_alert/preview.py

Outputs:
    swing_alert/preview.html
    swing_alert/preview.txt
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import alert as A  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main():
    subject, html, plaintext, meta = A.build_alert(preview_mode=True)

    out_dir = Path(__file__).parent
    (out_dir / "preview.html").write_text(html, encoding="utf-8")
    (out_dir / "preview.txt").write_text(plaintext, encoding="utf-8")

    per_sector = {}
    for p in meta["picks"]:
        per_sector[p.sector] = per_sector.get(p.sector, 0) + 1

    print("\n" + "=" * 60)
    print(f"Subject: {subject}")
    print(f"Preview written to: {out_dir / 'preview.html'}")
    print(f"Universe scanned: {meta['universe_stats']['total']} stocks")
    print(f"Top sectors: {meta['top_sectors']}")
    print(f"Picks per sector: {per_sector}")
    print(f"Total picks: {meta['picks_count']} | Open positions: {meta['positions_count']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
