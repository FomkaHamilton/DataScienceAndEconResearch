"""
Build the integrated quarterly state panel from the cleaned BFS and BED
files: aggregates BFS from monthly to quarterly, merges with BED
establishment births/deaths, and writes one analysis-ready file.

This file keeps the FULL history (2004-2026) with an explicit
`in_test_window` flag -- it does not delete the test-window rows, since
MANIFEST/provenance transparency matters more than deletion. But per the
pre-analysis-plan discipline in research_question.md, Phase 3 (exploratory
analysis) code must filter `in_test_window == False` before computing or
plotting anything. The test window is locked until the Phase 4
pre-analysis plan is committed -- see DEVELOPMENT_END below.

Output: data/processed/analysis_panel_quarterly.csv
One row per (state, year, quarter), wide on series.

Usage:
    python build_panel.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Development window ends here; 2023Q1 onward is the locked test window.
# Matches research_question.md / the approved research plan.
DEVELOPMENT_END_YEAR = 2022
DEVELOPMENT_END_QUARTER = 4

BFS_SERIES_KEEP = ["BA_BA", "BA_HBA", "BA_WBA", "BA_CBA"]

# Join key: BFS uses 2-letter postal codes (geo), BED uses state names. This
# crosswalk maps BFS geo codes to BED's state_name, including the U.S. total
# and Puerto Rico rows both sources carry.
GEO_TO_NAME = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "US": "U.S. totals", "PR": "Puerto Rico",
}


def _bfs_to_quarterly(bfs: pd.DataFrame) -> pd.DataFrame:
    bfs = bfs[bfs["series"].isin(BFS_SERIES_KEEP)].copy()
    bfs["quarter"] = ((bfs["month"] - 1) // 3) + 1
    q = (
        bfs.groupby(["geo", "geo_type", "series", "seasonal_adj", "year", "quarter"])["value"]
        .agg(lambda s: s.sum() if s.notna().sum() == 3 else np.nan)
        .reset_index()
    )
    wide = q.pivot_table(
        index=["geo", "geo_type", "seasonal_adj", "year", "quarter"],
        columns="series",
        values="value",
    ).reset_index()
    wide.columns.name = None
    return wide


def _bed_wide(bed: pd.DataFrame) -> pd.DataFrame:
    bed = bed[
        (bed["dataclass"].isin(["Establishment Births", "Establishment Deaths"]))
        & (bed["ratelevel"] == "Level")
    ].copy()
    bed["dataclass_short"] = bed["dataclass"].map(
        {"Establishment Births": "births", "Establishment Deaths": "deaths"}
    )
    wide = bed.pivot_table(
        index=["state_code", "state_name", "seasonal_adj", "year", "quarter"],
        columns="dataclass_short",
        values="value",
    ).reset_index()
    wide.columns.name = None
    return wide


def build() -> Path:
    bfs = pd.read_csv(PROCESSED_DIR / "bfs_state_applications.csv")
    bed = pd.read_csv(
        PROCESSED_DIR / "bed_state_establishment_births_deaths.csv",
        dtype={"state_code": str},
    )

    bfs_q = _bfs_to_quarterly(bfs)
    bed_w = _bed_wide(bed)

    bfs_q = bfs_q[bfs_q["geo"].isin(GEO_TO_NAME)].copy()
    bfs_q["state_name"] = bfs_q["geo"].map(GEO_TO_NAME)

    panel = bfs_q.merge(
        bed_w, on=["state_name", "seasonal_adj", "year", "quarter"], how="inner"
    )

    panel["in_test_window"] = (panel["year"] > DEVELOPMENT_END_YEAR) | (
        (panel["year"] == DEVELOPMENT_END_YEAR) & (panel["quarter"] > DEVELOPMENT_END_QUARTER)
    )
    panel["date"] = pd.to_datetime(
        panel["year"].astype(str) + "-" + ((panel["quarter"] - 1) * 3 + 1).astype(str) + "-01"
    )

    panel = panel.sort_values(["geo", "seasonal_adj", "year", "quarter"])

    out_path = PROCESSED_DIR / "analysis_panel_quarterly.csv"
    panel.to_csv(out_path, index=False)
    print(f"Wrote {len(panel):,} rows to {out_path}")
    print(f"Geographies: {sorted(panel['geo'].unique())}")
    print(f"Development-window rows: {(~panel['in_test_window']).sum():,}")
    print(f"Test-window rows (locked): {panel['in_test_window'].sum():,}")
    return out_path


if __name__ == "__main__":
    build()
