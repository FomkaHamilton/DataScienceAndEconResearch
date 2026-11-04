"""
Check that regenerated outputs match the committed ones.

Compares every tracked CSV under data/processed/ and outputs/ (the
tables and the live-forecast file) against its version in git HEAD: same
columns and shape, identical non-numeric values, and numeric values equal
within a tolerance. Also checks that every tracked figure (outputs/figures
and manuscript/figures) is present, and reports, for information only,
whether each figure file is byte-identical to the committed version.

Requires git and a clone of the repository (it reads the committed
versions with `git show`); it does not work on a downloaded ZIP archive.

    python replication/verify_outputs.py [--rtol 1e-6] [--atol 1e-9]

Exits with status 1 if a table differs or any tracked file is missing.
"""

import argparse
import io
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=PROJECT, check=True, capture_output=True, text=True
    ).stdout


def compare(committed: pd.DataFrame, current: pd.DataFrame, rtol: float, atol: float) -> str | None:
    if list(committed.columns) != list(current.columns):
        return "columns differ"
    if committed.shape != current.shape:
        return f"shape {current.shape} vs committed {committed.shape}"
    worst = 0.0
    for col in committed.columns:
        a, b = committed[col], current[col]
        if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
            a, b = a.to_numpy(float), b.to_numpy(float)
            if not np.allclose(a, b, rtol=rtol, atol=atol, equal_nan=True):
                bad = ~np.isclose(a, b, rtol=rtol, atol=atol, equal_nan=True)
                return f"column {col}: {bad.sum()} values differ (max abs diff {np.nanmax(np.abs(a - b)):.3g})"
            if np.any(np.isfinite(a) & np.isfinite(b)):
                worst = max(worst, float(np.nanmax(np.abs(a - b))))
        elif not a.astype(str).equals(b.astype(str)):
            return f"column {col}: non-numeric values differ"
    return None if worst == 0 else f"OK (max abs diff {worst:.2g})"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rtol", type=float, default=1e-6)
    parser.add_argument("--atol", type=float, default=1e-9)
    args = parser.parse_args()

    tracked = git("ls-files", "--full-name", "data/processed", "outputs", "manuscript/figures").split()
    csvs = [f for f in tracked if f.endswith(".csv")]
    figures = [f for f in tracked if f.endswith((".png", ".pdf"))]
    repo_root = Path(git("rev-parse", "--show-toplevel").strip())

    failures = 0
    for f in csvs:
        current_path = repo_root / f
        if not current_path.exists():
            print(f"MISSING  {f}")
            failures += 1
            continue
        committed = pd.read_csv(io.StringIO(git("show", f"HEAD:{f}")), low_memory=False)
        current = pd.read_csv(current_path, low_memory=False)
        result = compare(committed, current, args.rtol, args.atol)
        if result is None or result.startswith("OK"):
            print(f"match    {f}" + (f"  {result}" if result else ""))
        else:
            print(f"DIFFERS  {f}: {result}")
            failures += 1

    identical = 0
    for f in figures:
        path = repo_root / f
        if not path.exists():
            print(f"MISSING  {f}")
            failures += 1
            continue
        committed = subprocess.run(["git", "show", f"HEAD:{f}"], cwd=PROJECT, check=True, capture_output=True).stdout
        same = path.read_bytes() == committed
        identical += same
        print(f"{'identical' if same else 'present  '} {f}")

    print(f"\n{len(csvs)} tables and {len(figures)} figures checked; {failures} problem(s).")
    print(f"{identical} of {len(figures)} figure files are byte-identical to the committed versions "
          "(informational: fonts and libraries can differ across machines, so differing figures "
          "are not counted as problems).")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
