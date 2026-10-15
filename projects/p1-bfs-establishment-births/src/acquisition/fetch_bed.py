"""
Fetch BLS Business Employment Dynamics (BED) flat files: state-level
establishment births and deaths.

Source: https://download.bls.gov/pub/time.series/bd/
No robots.txt restriction found on download.bls.gov (checked 2026-10-14).
No API key required for the flat-file bulk download (unlike the BLS API,
which is used elsewhere for registered, rate-limited pulls).

These are BLS's full time-series flat files for the "bd" (Business
Employment Dynamics) survey. `bd.data.1.AllItems` (~205 MB as of
2026-10-14) contains ALL published BED series — every geography,
industry, size class, data class, rate/level, and seasonal adjustment
combination. `bd.series` (~5.6 MB) is the series directory: one row per
series_id, decoded into its component dimensions, used here to look up
which series_ids correspond to state-level, total-private, all-size-class
establishment births (dataclass 07) and deaths (dataclass 08).

This script does not filter -- it only downloads the raw files as BLS
publishes them. Filtering to the ~400 series this project needs happens
in src/cleaning/clean_bed.py, which reads these raw files directly (they
are not meant to be hand-edited).

Usage:
    python fetch_bed.py
"""

from datetime import date, datetime, timezone
from pathlib import Path

import requests

BASE_URL = "https://download.bls.gov/pub/time.series/bd/"
RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "bed"
USER_AGENT = (
    "DataScienceAndEconResearch/0.1 "
    "(independent research project; contact: thomas.hamilton@plexusworldwide.com)"
)

# Large data file + all small lookup/reference files needed to decode series_ids.
# bd.data.0.Current is NOT fetched: bd.data.1.AllItems is BLS's complete file
# (confirmed by inspecting the directory listing and series coverage), and
# fetching both would just duplicate ~200 MB for no benefit.
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
    dated folder (BED revises; keep prior pulls instead of overwriting).
    """
    retrieval_date = retrieval_date or datetime.now(timezone.utc).date()
    dest = RAW_DIR / retrieval_date.isoformat()
    dest.mkdir(parents=True, exist_ok=True)

    for name in FILES:
        out_path = dest / name
        if out_path.exists():
            print(f"Already have {out_path}")
            continue
        resp = requests.get(
            BASE_URL + name, headers={"User-Agent": USER_AGENT}, timeout=300
        )
        resp.raise_for_status()
        out_path.write_bytes(resp.content)
        print(f"Saved {len(resp.content):,} bytes to {out_path}")

    return dest


if __name__ == "__main__":
    fetch()
