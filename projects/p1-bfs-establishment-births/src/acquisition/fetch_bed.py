"""
Fetch BLS Business Employment Dynamics (BED) flat files: state-level
establishment births and deaths.

Source: https://download.bls.gov/pub/time.series/bd/
No robots.txt restriction found on download.bls.gov (checked 2026-10-14).
No API key is required for the flat-file bulk download (the registered,
rate-limited BLS API is not used).

These are BLS's full time-series flat files for the "bd" (Business
Employment Dynamics) survey. `bd.data.1.AllItems` (~205 MB as of
2026-10-14) contains every published BED series: all geography,
industry, size class, data class, rate/level, and seasonal adjustment
combinations. `bd.series` (~5.6 MB) is the series directory: one row per
series_id, decoded into its component dimensions, used here to look up
which series_ids correspond to state-level, total-private, all-size-class
establishment births (dataclass 07) and deaths (dataclass 08).

This script does not filter; it downloads the raw files as BLS publishes
them. Filtering to the ~400 series this project needs happens in
src/cleaning/clean_bed.py, which reads these raw files directly (they are
not meant to be hand-edited).

Usage:
    python fetch_bed.py
"""

from datetime import date, datetime, timezone
from pathlib import Path

import requests

from user_agent import user_agent

BASE_URL = "https://download.bls.gov/pub/time.series/bd/"
RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "bed"

# The large data file plus the small lookup files needed to decode series_ids.
# bd.data.0.Current is not fetched: bd.data.1.AllItems is BLS's complete file
# (confirmed by inspecting the directory listing and series coverage), so
# fetching both would duplicate ~200 MB.
FILES = [
    "bd.data.1.AllItems",
    "bd.series",
    "bd.dataclass",
    "bd.state",
    "bd.seasonal",
    "bd.ratelevel",
    "bd.sizeclass",
    "bd.ownership",
    "bd.periodicity",
    "bd.unitanalysis",
    "bd.dataelement",
    "bd.industry",
    "bd.footnote",
    "bd.contacts",
]


def fetch(retrieval_date: date | None = None) -> Path:
    """Download all BED flat files into a retrieval-dated subfolder.

    Returns the folder path. Re-running on a later date creates a new
    dated folder (BED is revised, so prior pulls are kept, not overwritten).
    """
    retrieval_date = retrieval_date or datetime.now(timezone.utc).date()
    dest = RAW_DIR / retrieval_date.isoformat()
    dest.mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": user_agent()}
    for name in FILES:
        out_path = dest / name
        if out_path.exists():
            print(f"Already have {out_path}")
            continue
        resp = requests.get(
            BASE_URL + name, headers=headers, timeout=300
        )
        resp.raise_for_status()
        out_path.write_bytes(resp.content)
        print(f"Saved {len(resp.content):,} bytes to {out_path}")

    return dest


if __name__ == "__main__":
    fetch()
