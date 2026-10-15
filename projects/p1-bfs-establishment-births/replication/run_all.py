"""
One-command reproduction of Project 1's results.

    python replication/run_all.py          # exact: from the committed processed data
    python replication/run_all.py --full   # also re-download raw data and rebuild it

Exact mode reproduces the committed numbers; check with
replication/verify_outputs.py afterwards.

Full mode downloads the *current* data from Census and BLS. Both revise
their series (BED annually), so once a revision is published, full-mode
results can differ from the committed ones. The committed processed files
preserve the vintage used here (retrieved 2026-10-14/15; checksums of the
raw files are in data/MANIFEST.md).

Run from the project folder, with the pinned environment:
    pip install -r ../../requirements.txt
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]

FULL_ONLY = [
    "src/acquisition/fetch_bfs.py",
    "src/acquisition/fetch_bed.py",
    "src/acquisition/fetch_bds.py",
    "src/cleaning/clean_bfs.py",
    "src/cleaning/clean_bed.py",
    "src/cleaning/clean_bds.py",
]
PIPELINE = [
    "src/cleaning/build_panel.py",
    "src/analysis/exploratory_analysis.py",
    "src/cleaning/build_forecast_dataset.py",
    "src/analysis/run_phase5_evaluation.py",  # primary results
    "src/analysis/run_phase5_extensions.py",  # Addendum 1
    "src/analysis/run_rq2.py",  # Addendum 2
    "src/analysis/make_live_forecasts.py",  # Addendum 3: checks the frozen forecasts, never overwrites
    "src/analysis/run_rq4.py",  # Addendum 4
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--full", action="store_true", help="re-download raw data first")
    args = parser.parse_args()

    steps = (FULL_ONLY if args.full else []) + PIPELINE
    start = time.time()
    for step in steps:
        print(f"\n=== {step} ===", flush=True)
        t0 = time.time()
        path = PROJECT / step
        subprocess.run([sys.executable, "-u", str(path)], cwd=path.parent, check=True)
        print(f"--- done in {time.time() - t0:.0f}s", flush=True)
    print(f"\nAll {len(steps)} steps finished in {(time.time() - start) / 60:.1f} min.")


if __name__ == "__main__":
    main()
