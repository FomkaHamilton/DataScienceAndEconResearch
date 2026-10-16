"""
Fetch Census Business Formation Statistics (BFS), monthly, national/regional/state.

Source: https://www.census.gov/econ/bfs/csv/bfs_monthly.csv
Methodology: https://www.census.gov/econ/bfs/technicaldocumentation/methodology.html

This is a single bulk CSV covering US, Census regions, all states + DC + PR,
seasonally adjusted and not seasonally adjusted, for all published BFS series
(business applications BA/HBA/WBA/CBA and business formation projections
BF4Q/BF8Q/PBF4Q/PBF8Q/etc.), wide format (one column per calendar month).

No API key required. No robots.txt restriction found on census.gov for this path
(checked 2026-10-14).

Usage:
    python fetch_bfs.py
"""

from datetime import date, datetime, timezone
from pathlib import Path

import requests

from user_agent import user_agent

SOURCE_URL = "https://www.census.gov/econ/bfs/csv/bfs_monthly.csv"
RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "bfs"


def fetch(retrieval_date: date | None = None) -> Path:
    """Download the BFS monthly CSV and save it with a retrieval-dated filename.

    Returns the path to the saved file. Does not overwrite a file already
    retrieved on the same date (BFS is revised; re-running on a later date
    creates a new dated file rather than silently replacing the old one).
    """
    retrieval_date = retrieval_date or datetime.now(timezone.utc).date()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / f"bfs_monthly_{retrieval_date.isoformat()}.csv"

    if out_path.exists():
        print(f"Already retrieved today: {out_path}")
        return out_path

    resp = requests.get(SOURCE_URL, headers={"User-Agent": user_agent()}, timeout=60)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    print(f"Saved {len(resp.content):,} bytes to {out_path}")
    return out_path


if __name__ == "__main__":
    fetch()
