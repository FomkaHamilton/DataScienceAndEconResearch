"""
Export the state-level actual values used to score the pre-registered live
forecasts, so that the manuscript figure can show them without the raw BLS
files (which are not committed).

Usage (after src/acquisition/fetch_bed.py):
    python src/analysis/export_live_actuals.py data/raw/bed/<date>

Uses actuals_from_release() from the committed scoring script
(evaluate_live_forecasts.py), which is not modified. Writes
outputs/live_forecasts/actuals_<date>.csv.
"""

import sys
from pathlib import Path

from evaluate_live_forecasts import actuals_from_release
from make_live_forecasts import OUT_DIR


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raw_dir = Path(sys.argv[1]).resolve()
    actuals = actuals_from_release(raw_dir)
    out = OUT_DIR / f"actuals_{raw_dir.name}.csv"
    actuals.to_csv(out, index=False)
    print(f"Wrote {out} ({len(actuals)} state-quarters)")


if __name__ == "__main__":
    main()
