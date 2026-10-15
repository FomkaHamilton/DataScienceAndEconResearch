"""
Clean BLS Business Employment Dynamics (BED) raw flat files into a tidy,
state-level establishment births/deaths panel.

Reads the raw files downloaded by src/acquisition/fetch_bed.py and selects
only the series this project needs:
  - geography: national total + all 50 states + DC + PR + VI (msa_code
    00000, county_code 000 -- i.e. state-level geography, not MSA/county)
  - industry: total private (industry_code 000000)
  - unit of analysis: establishment (not employment)
  - data element: number of establishments (not employment)
  - size class: all size classes combined (00)
  - data class: establishment births (07) and establishment deaths (08)
  - periodicity: quarterly
  - both seasonal adjustments (S, U) and both rate/level (L, R) are kept,
    so the primary-spec vs. robustness-spec choice can be made downstream
    in analysis code, not baked in here.

Output: data/processed/bed_state_establishment_births_deaths.csv
One row per (state, dataclass, seasonal, ratelevel, year, quarter).

Usage:
    python clean_bed.py [retrieval_date]
If no retrieval_date is given, uses the most recent dated subfolder under
data/raw/bed/.
"""

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_BED_DIR = PROJECT_ROOT / "data" / "raw" / "bed"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Filter criteria -- see module docstring.
WANT = {
    "msa_code": {"00000"},
    "county_code": {"000"},
    "industry_code": {"000000"},
    "unitanalysis_code": {"1"},
    "dataelement_code": {"2"},  # 2 = Number of Establishments
    "sizeclass_code": {"00"},  # all size classes
    "dataclass_code": {"07", "08"},  # 07 = Births, 08 = Deaths
    "periodicity_code": {"Q"},
}


def _latest_raw_dir() -> Path:
    candidates = sorted(p for p in RAW_BED_DIR.iterdir() if p.is_dir())
    if not candidates:
        raise FileNotFoundError(
            f"No dated subfolder found under {RAW_BED_DIR}. Run fetch_bed.py first."
        )
    return candidates[-1]


def _read_lookup(raw_dir: Path, name: str) -> pd.DataFrame:
    df = pd.read_csv(raw_dir / name, sep="\t", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    for c in df.columns:
        df[c] = df[c].str.strip()
    return df


def build_target_series(raw_dir: Path) -> pd.DataFrame:
    """Return the subset of bd.series matching WANT, with decoded labels."""
    series = _read_lookup(raw_dir, "bd.series")
    series.columns = [c.strip() for c in series.columns]
    series["series_id"] = series["series_id"].str.strip()

    mask = pd.Series(True, index=series.index)
    for col, allowed in WANT.items():
        mask &= series[col].isin(allowed)
    target = series.loc[mask].copy()

    state = _read_lookup(raw_dir, "bd.state").rename(
        columns={"state_code": "state_code", "state_name": "state_name"}
    )
    dataclass = _read_lookup(raw_dir, "bd.dataclass")
    # bd.seasonal's code column is "seasonal_code", but bd.series calls the
    # same field "seasonal" -- rename so the merge key matches.
    seasonal = _read_lookup(raw_dir, "bd.seasonal").rename(
        columns={"seasonal_code": "seasonal"}
    )
    ratelevel = _read_lookup(raw_dir, "bd.ratelevel")

    target = target.merge(state, on="state_code", how="left")
    target = target.merge(dataclass, on="dataclass_code", how="left")
    target = target.merge(seasonal, on="seasonal", how="left")
    target = target.merge(ratelevel, on="ratelevel_code", how="left")

    return target[
        [
            "series_id",
            "state_code",
            "state_name",
            "dataclass_code",
            "dataclass_name",
            "seasonal",
            "seasonal_text",
            "ratelevel_code",
            "ratelevel_name",
            "begin_year",
            "begin_period",
            "end_year",
            "end_period",
        ]
    ]


def clean(retrieval_date: str | None = None) -> Path:
    raw_dir = RAW_BED_DIR / retrieval_date if retrieval_date else _latest_raw_dir()
    print(f"Reading raw BED files from {raw_dir}")

    target = build_target_series(raw_dir)
    target_ids = set(target["series_id"])
    print(f"Target series: {len(target_ids)}")

    data_path = raw_dir / "bd.data.1.AllItems"
    chunks = []
    reader = pd.read_csv(
        data_path,
        sep="\t",
        dtype=str,
        chunksize=500_000,
        names=["series_id", "year", "period", "value", "footnote_codes"],
        header=0,
    )
    for chunk in reader:
        chunk["series_id"] = chunk["series_id"].str.strip()
        chunk = chunk[chunk["series_id"].isin(target_ids)]
        if len(chunk):
            chunks.append(chunk)

    data = pd.concat(chunks, ignore_index=True)
    data["value"] = pd.to_numeric(data["value"].str.strip(), errors="coerce")
    data["year"] = data["year"].astype(int)
    data["quarter"] = data["period"].str.strip().str.replace("Q", "", regex=False).astype(int)

    out = data.merge(target, on="series_id", how="left")
    out = out.rename(
        columns={
            "dataclass_name": "dataclass",
            "seasonal_text": "seasonal_adj",
            "ratelevel_name": "ratelevel",
        }
    )
    out = out[
        [
            "state_code",
            "state_name",
            "year",
            "quarter",
            "dataclass",
            "seasonal_adj",
            "ratelevel",
            "value",
            "series_id",
        ]
    ].sort_values(["state_code", "dataclass", "seasonal_adj", "ratelevel", "year", "quarter"])

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "bed_state_establishment_births_deaths.csv"
    out.to_csv(out_path, index=False)
    print(f"Wrote {len(out):,} rows to {out_path}")
    print(f"States/geographies: {out['state_name'].nunique()}")
    print(f"Year range: {out['year'].min()}-{out['year'].max()}")
    return out_path


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    clean(arg)
