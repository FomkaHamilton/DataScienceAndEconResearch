"""
Clean the Census Business Formation Statistics (BFS) raw monthly CSV into a
tidy long-format panel.

Reads data/raw/bfs/bfs_monthly_<date>.csv (wide: one column per calendar
month) and reshapes to one row per (geography, series, seasonal adjustment,
year, month).

Geography note: BFS publishes industry (NAICS) detail only at the national
level; states/DC/PR/regions get totals only (naics_sector == "TOTAL"). This
project's analysis is state-level, so this script keeps naics_sector ==
"TOTAL" rows only, but keeps every geography (national, 4 Census regions,
50 states, DC, PR) with a `geo_type` column so the state panel is filtered
downstream rather than baked in here.

Series kept: BA_BA (all applications), BA_HBA (high-propensity), BA_WBA
(planned-wage), BA_CBA (corporate) -- the four predictor series used for
RQ1/RQ2 -- plus the BF_* "business formation" projection series Census
itself publishes, kept for context/comparison even though they are not
currently used as predictors.

Output: data/processed/bfs_state_applications.csv

Usage:
    python clean_bfs.py [path_to_raw_csv]
If no path is given, uses the most recently retrieved file under
data/raw/bfs/.
"""

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_BFS_DIR = PROJECT_ROOT / "data" / "raw" / "bfs"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MONTH_COLS = [
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec",
]

REGION_CODES = {"MW", "NO", "SO", "WE"}
NATIONAL_CODE = {"US"}
TERRITORY_CODES = {"PR"}

SEASONAL_LABELS = {"U": "Not seasonally adjusted", "A": "Seasonally adjusted"}


def _latest_raw_file() -> Path:
    candidates = sorted(RAW_BFS_DIR.glob("bfs_monthly_*.csv"))
    if not candidates:
        raise FileNotFoundError(
            f"No bfs_monthly_*.csv found under {RAW_BFS_DIR}. Run fetch_bfs.py first."
        )
    return candidates[-1]


def _geo_type(geo: str) -> str:
    if geo in NATIONAL_CODE:
        return "national"
    if geo in REGION_CODES:
        return "region"
    if geo in TERRITORY_CODES:
        return "territory"
    if geo == "DC":
        return "state"  # treated as a state for this project's panel
    return "state"


def clean(raw_path: str | None = None) -> Path:
    path = Path(raw_path) if raw_path else _latest_raw_file()
    print(f"Reading {path}")

    df = pd.read_csv(path, dtype=str)
    df = df[df["naics_sector"] == "TOTAL"].copy()

    long = df.melt(
        id_vars=["sa", "series", "geo", "year"],
        value_vars=MONTH_COLS,
        var_name="month_abbr",
        value_name="value",
    )
    long["value"] = pd.to_numeric(long["value"], errors="coerce")
    month_map = {m: i + 1 for i, m in enumerate(MONTH_COLS)}
    long["month"] = long["month_abbr"].map(month_map)
    long["year"] = long["year"].astype(int)
    long["seasonal_adj"] = long["sa"].map(SEASONAL_LABELS)
    long["geo_type"] = long["geo"].map(_geo_type)

    out = long[
        ["geo", "geo_type", "series", "seasonal_adj", "year", "month", "value"]
    ].sort_values(["geo", "series", "seasonal_adj", "year", "month"])

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "bfs_state_applications.csv"
    out.to_csv(out_path, index=False)
    print(f"Wrote {len(out):,} rows to {out_path}")
    print(f"Series kept: {sorted(out['series'].unique())}")
    print(f"Geo types: {out['geo_type'].value_counts().to_dict()}")
    return out_path


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    clean(arg)
