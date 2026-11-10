"""
Extract state establishment births (not seasonally adjusted, levels) from a
BED raw-file folder into a small processed file, so that analyses can use a
later BLS vintage without the 250 MB raw files.

Usage:
    python extract_bed_vintage.py ../../data/raw/bed/<date>

Writes data/processed/bed_state_births_nsa_<date>.csv with columns
state_name, year, quarter, births. Used by src/analysis/run_addendum5.py
(pre_analysis_plan_addendum_5.md, item G3), which re-scores the test window
against the BLS release of 28 October 2026 (retrieved 2026-11-04).
"""

import sys
from pathlib import Path

from clean_bed import load_bed

PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raw_dir = Path(sys.argv[1]).resolve()
    bed = load_bed(raw_dir)
    births = bed[(bed["dataclass"] == "Establishment Births")
                 & (bed["seasonal_adj"] == "Not seasonally adjusted")
                 & (bed["ratelevel"] == "Level")]
    out = (births[["state_name", "year", "quarter", "value"]]
           .rename(columns={"value": "births"})
           .sort_values(["state_name", "year", "quarter"]))
    path = PROCESSED_DIR / f"bed_state_births_nsa_{raw_dir.name}.csv"
    out.to_csv(path, index=False)
    print(f"Wrote {path} ({len(out):,} rows)")


if __name__ == "__main__":
    main()
