"""
Fetch Census Business Dynamics Statistics (BDS), state x firm-age cross-tab.

Used only for RQ4 (exploratory): is the BFS->BED predictive relationship
stronger in states where more establishment entry comes from genuinely new
firms (firm age 0) rather than new establishments opened by existing firms?

Source: https://www.census.gov/data/datasets/time-series/econ/bds/bds-datasets.html
File:   https://www2.census.gov/programs-surveys/bds/tables/time-series/2023/bds2023_st_fa.csv
No API key required for this bulk CSV (distinct from the Census API,
used elsewhere in this project for other series). No robots.txt
restriction found on www2.census.gov (checked 2026-10-14).

Coverage: annual, 1978-2023 (BDS's March-to-March reference year), state
x firm-age. This is annual data, not the quarterly frequency of the core
BFS/BED panel -- it is used only for the RQ4 cross-section, not the main
forecasting exercise.

Usage:
    python fetch_bds.py
"""

from datetime import date, datetime, timezone
from pathlib import Path

import requests

SOURCE_URL = (
    "https://www2.census.gov/programs-surveys/bds/tables/time-series/2023/"
    "bds2023_st_fa.csv"
)
RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "bds"
USER_AGENT = (
    "DataScienceAndEconResearch/0.1 "
    "(independent research project; contact: thomas.hamilton@plexusworldwide.com)"
)


def fetch(retrieval_date: date | None = None) -> Path:
    retrieval_date = retrieval_date or datetime.now(timezone.utc).date()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / f"bds2023_st_fa_{retrieval_date.isoformat()}.csv"

    if out_path.exists():
        print(f"Already retrieved today: {out_path}")
        return out_path

    resp = requests.get(SOURCE_URL, headers={"User-Agent": USER_AGENT}, timeout=60)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    print(f"Saved {len(resp.content):,} bytes to {out_path}")
    return out_path


if __name__ == "__main__":
    fetch()
