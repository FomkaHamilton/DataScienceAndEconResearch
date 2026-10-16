"""
Figures for the manuscript (manuscript/).

Presentation only: every figure is drawn from committed output tables,
the committed analysis panel, or the frozen live-forecast file. Nothing
is re-estimated here, and the live-forecast file is only read.

Figures are sized for a printed page (6.5 in wide), carry no figure
titles or notes (those belong in the manuscript captions), and are
written as PNG (300 dpi) and PDF (vector, TrueType fonts) to
manuscript/figures/.

Color: all business applications (BA) and establishment births are
drawn in black; color is used only to tell the narrower application
series apart. The three series colors were checked pairwise for
distinguishability on white; the green (CBA) is below 3:1 contrast, so
every colored line is also labeled directly.

Usage:
    python make_paper_figures.py
"""

from pathlib import Path

import matplotlib
import matplotlib.dates
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

matplotlib.use("Agg")
plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.size": 8})

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables"
LIVE_FILE = PROJECT_ROOT / "outputs" / "live_forecasts" / "live_forecasts_2026Q1-Q3.csv"
OUT_DIR = PROJECT_ROOT / "manuscript" / "figures"

WIDTH = 6.5  # inches, full text width
SURFACE, INK, INK_2, MUTED, GRID, SHADE = "#ffffff", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#efeee9"
NAIVE_GRAY = "#a9a79f"
SERIES_COLOR = {"BA": INK, "HBA": "#2a78d6", "WBA": "#eb6834", "CBA": "#1baf7a"}
SERIES_NAME = {
    "BA": "All applications",
    "HBA": "High-propensity",
    "WBA": "Planned wages",
    "CBA": "Corporate",
}
PERIODS = [
    ("Pandemic\n2020–21", "2020-01-01", "2022-01-01"),
    ("Test window\n2023–25", "2023-01-01", "2026-01-01"),
]


# ---------------------------------------------------------------- helpers

def _style(ax, zero: float | None = 0.0) -> None:
    ax.set_facecolor(SURFACE)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    for side in ["left", "bottom"]:
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_2, labelsize=7.5, length=2.5, width=0.6)
    ax.grid(axis="y", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    if zero is not None:
        ax.axhline(zero, color=INK_2, linewidth=0.6, zorder=1)


def _shade_periods(ax, labels: bool = True) -> None:
    for label, start, end in PERIODS:
        ax.axvspan(pd.Timestamp(start), pd.Timestamp(end), color=SHADE, linewidth=0, zorder=0)
        if labels:
            ax.text(pd.Timestamp(start) + pd.Timedelta(days=25), 0.98, label,
                    transform=ax.get_xaxis_transform(), va="top", ha="left", fontsize=6.5, color=INK_2)


def _panel_title(ax, text: str) -> None:
    ax.set_title(text, loc="left", fontsize=8.5, color=INK, pad=4)


def _spread(values: list[float], min_gap: float) -> list[float]:
    """Nudge label positions apart so none sit closer than min_gap, keeping their order."""
    order = np.argsort(values)
    pos = np.array(values, dtype=float)[order]
    for _ in range(50):
        moved = False
        for i in range(1, len(pos)):
            gap = pos[i] - pos[i - 1]
            if gap < min_gap:
                shift = (min_gap - gap) / 2
                pos[i - 1] -= shift
                pos[i] += shift
                moved = True
        if not moved:
            break
    out = np.empty_like(pos)
    out[order] = pos
    return list(out)


def _end_labels(ax, ends: dict[str, tuple[pd.Timestamp, float]], min_gap: float) -> None:
    keys = list(ends)
    ys = _spread([ends[k][1] for k in keys], min_gap)
    for k, y in zip(keys, ys):
        x = ends[k][0]
        ax.text(x + pd.Timedelta(days=60), y, SERIES_NAME[k], fontsize=6.5, color=INK,
                va="center", ha="left")


def _save(fig, name: str) -> None:
    fig.savefig(OUT_DIR / f"{name}.png", dpi=300, facecolor=SURFACE)
    fig.savefig(OUT_DIR / f"{name}.pdf", facecolor=SURFACE, metadata={"CreationDate": None})
    plt.close(fig)
    print(f"  wrote {name}.png / .pdf")


def _date(year, quarter) -> pd.Series:
    return pd.to_datetime(pd.Series(year).astype(str) + "-" + (3 * pd.Series(quarter) - 2).astype(str) + "-01")


# ---------------------------------------------------------------- figure 1

def fig_raw_data() -> None:
    """National applications and establishment births, year-over-year."""
    p = pd.read_csv(PROCESSED_DIR / "analysis_panel_quarterly.csv")
    us = p[(p["geo"] == "US") & (p["seasonal_adj"] == "Not seasonally adjusted")].copy()
    us = us.sort_values(["year", "quarter"]).set_index(["year", "quarter"])
    rows = []
    for (y, q) in us.index:
        if (y - 1, q) in us.index and (y, q) <= (2025, 4):
            now, before = us.loc[(y, q)], us.loc[(y - 1, q)]
            rows.append({"year": y, "quarter": q,
                         "BA": 100 * (np.log(now["BA_BA"]) - np.log(before["BA_BA"])),
                         "births": 100 * (np.log(now["births"]) - np.log(before["births"]))})
    d = pd.DataFrame(rows)
    d["date"] = _date(d["year"], d["quarter"]).values

    fig, axes = plt.subplots(2, 1, figsize=(WIDTH, 4.0), sharex=True, sharey=True, facecolor=SURFACE)
    for ax, col, title in [
        (axes[0], "BA", "(a) Business applications (Census BFS), national"),
        (axes[1], "births", "(b) Establishment births (BLS BED), national"),
    ]:
        _style(ax)
        _shade_periods(ax, labels=(ax is axes[1]))  # panel (b): keeps clear of the applications peak label
        ax.plot(d["date"], d[col], color=INK, linewidth=1.3)
        _panel_title(ax, title)
        # Label the pandemic peak so the lead of applications over births is visible.
        w = d[(d["year"] >= 2020) & (d["year"] <= 2022)]
        peak = w.loc[w[col].idxmax()]
        ax.annotate(f"Peak {int(peak['year'])}Q{int(peak['quarter'])}",
                    xy=(peak["date"], peak[col]), xytext=(-8, 0), textcoords="offset points",
                    ha="right", va="center", fontsize=6.5, color=INK)
        print(f"  {col}: peak {int(peak['year'])}Q{int(peak['quarter'])} = {peak[col]:.1f} log points")
    fig.supylabel("Year-over-year change, log points", fontsize=7.5, color=INK_2)
    fig.tight_layout(rect=(0.015, 0, 1, 1), h_pad=1.2)
    _save(fig, "fig1_national_applications_births")


# ---------------------------------------------------------------- figure 2

def fig_test_window_intervals() -> None:
    """Point estimates with naive and dependence-robust intervals, test window."""
    c = pd.read_csv(TABLE_DIR / "phase5_comparisons.csv").set_index(["comparison", "statistic"])
    labels = {
        "econ_h0": "Applications, h = 0", "econ_h1": "Applications, h = 1",
        "econ_h2": "Applications, h = 2", "econ_h3": "Applications, h = 3",
        "econ_h4": "Applications, h = 4", "elasticnet": "Elastic net",
        "rf": "Random forest", "gb": "Gradient boosting†", "combo": "Combination",
    }
    panels = [
        ("cw", ["econ_h0", "econ_h1", "econ_h2", "econ_h3", "econ_h4", "elasticnet"], 1.645,
         "(a) Information test (Clark–West): 90% intervals", "Adjusted loss difference, % of benchmark MSE"),
        ("mse", list(labels), 1.96,
         "(b) Accuracy: 95% intervals", "Reduction in MSE, % of benchmark MSE"),
    ]

    fig, axes = plt.subplots(2, 1, figsize=(WIDTH, 5.4), facecolor=SURFACE,
                             gridspec_kw={"height_ratios": [6, 9]})
    for ax, (stat, comps, z, title, xlabel) in zip(axes, panels):
        _style(ax, zero=None)
        ax.grid(axis="y", visible=False)
        ax.grid(axis="x", color=GRID, linewidth=0.5)
        ax.axvline(0, color=INK_2, linewidth=0.7, zorder=1)
        for i, comp in enumerate(comps):
            r = c.loc[(comp, stat)]
            est = r["mean_diff_pct_of_benchmark_mse"]
            naive_se = est / r["naive_t"]
            y = len(comps) - 1 - i
            if stat == "mse" and comp == "gb":
                # The two-way clustered SE is unstable for this model (Table 1), so use the wild cluster bootstrap interval.
                lo, hi = r["wcb_ci95_low_pct"], r["wcb_ci95_high_pct"]
            else:
                robust_se = est / r["two_way_t"]
                lo, hi = est - z * robust_se, est + z * robust_se
            ax.plot([est - z * naive_se, est + z * naive_se], [y + 0.17] * 2, color=NAIVE_GRAY,
                    linewidth=2.4, solid_capstyle="butt", zorder=2)
            ax.plot([lo, hi], [y - 0.17] * 2, color=INK, linewidth=1.4, solid_capstyle="butt", zorder=2)
            for yy, col in [(y + 0.17, NAIVE_GRAY), (y - 0.17, INK)]:
                ax.plot(est, yy, "o", markersize=4, color=col, markeredgecolor=SURFACE,
                        markeredgewidth=0.8, zorder=3)
        ax.set_yticks(range(len(comps)))
        ax.set_yticklabels([labels[k] for k in comps][::-1], fontsize=7.5, color=INK)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
        ax.set_ylim(-0.6, len(comps) - 0.4)
        ax.set_xlabel(xlabel, fontsize=7.5, color=INK_2)
        _panel_title(ax, title)
    handles = [
        Line2D([], [], color=NAIVE_GRAY, linewidth=2.4, marker="o", markersize=4,
               markeredgecolor=SURFACE, label="Naive (612 state-quarters treated as independent)"),
        Line2D([], [], color=INK, linewidth=1.4, marker="o", markersize=4,
               markeredgecolor=SURFACE, label="Robust (two-way clustered by state and quarter)"),
    ]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.01, 1.0), ncol=2, frameon=False,
               fontsize=7.5, labelcolor=INK, handlelength=2.2)
    fig.tight_layout(rect=(0, 0, 1, 0.955), h_pad=1.6)
    _save(fig, "fig2_test_window_intervals")


# ---------------------------------------------------------------- figures 3-4

def _cumulative_gains(preds: pd.DataFrame, series: str, h: int) -> pd.DataFrame:
    """Cumulative reduction in squared error as % of the benchmark's total squared error, 2010-2025.

    The final value equals the model's whole-period accuracy gain (% of benchmark MSE).
    """
    d = preds.assign(
        se_bench=(preds["births_yoy"] - preds["pred_benchmark"]) ** 2,
        se_model=(preds["births_yoy"] - preds[f"pred_{series}_h{h}"]) ** 2,
    )
    q = d.groupby(["year", "quarter"])[["se_bench", "se_model"]].mean().reset_index()
    q["gain"] = q["se_bench"] - q["se_model"]
    q["cum_pct"] = 100 * q["gain"].cumsum() / q["se_bench"].sum()
    q["date"] = _date(q["year"], q["quarter"]).values
    return q


def _check_against_committed(preds: pd.DataFrame) -> None:
    """The BA h3 quarterly gains must equal the committed Addendum 2 table (rq2_quarterly_gains_h3.csv)."""
    q = _cumulative_gains(preds, "BA", 3)
    ref = pd.read_csv(TABLE_DIR / "rq2_quarterly_gains_h3.csv").query("series == 'BA'")
    m = q.merge(ref, on=["year", "quarter"], suffixes=("", "_ref"))
    assert len(m) == len(q) == 64, "quarter coverage differs from committed table"
    assert np.allclose(m["gain"], m["gain_ref"], rtol=1e-9, atol=1e-12), "gains differ from committed table"


def fig_cumulative_ba(preds: pd.DataFrame) -> None:
    q = _cumulative_gains(preds, "BA", 3)
    fig, ax = plt.subplots(figsize=(WIDTH, 3.0), facecolor=SURFACE)
    _style(ax)
    _shade_periods(ax)
    ax.plot(q["date"], q["cum_pct"], color=INK, linewidth=1.4)
    ax.set_ylabel("Cumulative accuracy gain,\n% of benchmark total squared error", fontsize=7.5, color=INK_2)
    fig.tight_layout()
    _save(fig, "fig3_cumulative_gain_ba_h3")
    print(f"  BA h3: cumulative gain end-2019 {q.loc[q['year'] <= 2019, 'cum_pct'].iloc[-1]:.1f}%, "
          f"peak {q['cum_pct'].max():.1f}%, end-2025 {q['cum_pct'].iloc[-1]:.1f}%")


def fig_cumulative_by_series(preds: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 3.0), sharey=True, facecolor=SURFACE)
    for ax, h, title in [(axes[0], 0, "(a) Same quarter (h = 0)"), (axes[1], 3, "(b) Three quarters ahead (h = 3)")]:
        _style(ax)
        _shade_periods(ax, labels=False)  # panels too narrow for labels; the caption names the shaded periods
        ends = {}
        for s in ["BA", "HBA", "WBA", "CBA"]:
            q = _cumulative_gains(preds, s, h)
            ax.plot(q["date"], q["cum_pct"], color=SERIES_COLOR[s], linewidth=1.6 if s == "BA" else 1.2,
                    zorder=3 if s == "BA" else 2)
            ends[s] = (q["date"].iloc[-1], q["cum_pct"].iloc[-1])
            print(f"  {s} h{h}: end-2019 {q.loc[q['year'] <= 2019, 'cum_pct'].iloc[-1]:.1f}%, "
                  f"end-2025 {q['cum_pct'].iloc[-1]:.1f}%")
        _end_labels(ax, ends, min_gap=0.7)
        _panel_title(ax, title)
        ax.set_xlim(pd.Timestamp("2009-07-01"), pd.Timestamp("2030-06-01"))
        ax.set_xticks([pd.Timestamp(f"{y}-01-01") for y in [2010, 2014, 2018, 2022, 2026]])
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y"))
    axes[0].set_ylabel("Cumulative accuracy gain,\n% of benchmark total squared error", fontsize=7.5, color=INK_2)
    handles = [Line2D([], [], color=SERIES_COLOR[s], linewidth=1.6 if s == "BA" else 1.2, label=SERIES_NAME[s])
               for s in ["BA", "HBA", "WBA", "CBA"]]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.01, 1.0), ncol=4, frameon=False,
               fontsize=7.5, labelcolor=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.93), w_pad=1.5)
    _save(fig, "fig4_cumulative_gain_by_series")


# ---------------------------------------------------------------- figure 5

def fig_weights_indexed() -> None:
    c = pd.read_csv(TABLE_DIR / "rq2_coefficient_paths_h3.csv")
    c["date"] = pd.to_datetime(c["date"])
    fig, ax = plt.subplots(figsize=(WIDTH, 3.0), facecolor=SURFACE)
    _style(ax, zero=100)
    _shade_periods(ax)
    ends = {}
    for s in ["BA", "HBA", "WBA", "CBA"]:
        d = c[c["series"] == s].sort_values("date")
        base = d.loc[d["year"] <= 2019, "coef"].mean()
        idx = 100 * d["coef"] / base
        ax.plot(d["date"], idx, color=SERIES_COLOR[s], linewidth=1.6 if s == "BA" else 1.2,
                zorder=3 if s == "BA" else 2)
        ends[s] = (d["date"].iloc[-1], idx.iloc[-1])
        late = idx[d["year"] >= 2022].mean()
        print(f"  {s}: 2010-19 mean coef {base:.3f}; 2022-25 mean index {late:.0f}")
    _end_labels(ax, ends, min_gap=10)
    ax.set_xlim(pd.Timestamp("2009-07-01"), pd.Timestamp("2028-06-01"))
    ax.set_xticks([pd.Timestamp(f"{y}-01-01") for y in range(2010, 2027, 2)])
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y"))
    ax.set_ylabel("Estimated weight on applications,\nindex (2010–19 average = 100)", fontsize=7.5, color=INK_2)
    handles = [Line2D([], [], color=SERIES_COLOR[s], linewidth=1.6 if s == "BA" else 1.2, label=SERIES_NAME[s])
               for s in ["BA", "HBA", "WBA", "CBA"]]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.01, 1.0), ncol=4, frameon=False,
               fontsize=7.5, labelcolor=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    _save(fig, "fig5_weight_paths_indexed")


# ---------------------------------------------------------------- figure 6

def fig_new_firm_share() -> None:
    d = pd.read_csv(TABLE_DIR / "rq4_state_data.csv")
    r = pd.read_csv(TABLE_DIR / "rq4_correlations.csv").query("role == 'primary'").set_index("lead")
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 2.9), sharey=True, facecolor=SURFACE)
    for ax, h, name in [(axes[0], 0, "Same quarter (h = 0)"), (axes[1], 3, "Three quarters ahead (h = 3)")]:
        _style(ax)
        ax.grid(axis="x", color=GRID, linewidth=0.5)
        ax.scatter(100 * d["new_firm_share_2010_19"], d[f"gain_BA_h{h}_2010_19"], s=16, color=INK,
                   edgecolor=SURFACE, linewidth=0.6, zorder=3)
        rr = r.loc[h]
        _panel_title(ax, f"({'ab'[h == 3]}) {name}")
        ax.text(0.02, 0.03, f"Spearman ρ = {rr['spearman_rho']:.2f}\nHolm-adjusted p = {rr['spearman_p_holm']:.2g}",
                transform=ax.transAxes, va="bottom", ha="left", fontsize=7, color=INK)
        ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))
        ax.set_xlabel("New establishments from new firms, 2010–19 (%)", fontsize=7.5, color=INK_2)
    axes[0].set_ylabel("Accuracy gain from applications,\n2010–19 (% of benchmark MSE)", fontsize=7.5, color=INK_2)
    fig.tight_layout(w_pad=1.5)
    _save(fig, "fig6_gain_vs_new_firm_share")


# ---------------------------------------------------------------- figure 7

def fig_live_forecasts() -> None:
    """Pre-registered forecasts, averaged across states with equal weights (as in the evaluation,
    which scores each state equally). Reads the frozen file only."""
    f = pd.read_csv(LIVE_FILE)
    f = f[f["model"].isin(["benchmark", "BA_h0", "BA_h3"])]
    nat = (f.groupby(["year", "quarter", "training", "model"])["forecast_births_yoy"]
           .mean().mul(100).rename("yoy").reset_index())
    rows = [("benchmark", "Benchmark"), ("BA_h0", "Applications, h = 0"), ("BA_h3", "Applications, h = 3")]
    quarters = sorted(set(zip(nat["year"], nat["quarter"])))

    fig, axes = plt.subplots(1, len(quarters), figsize=(WIDTH, 2.2), sharey=True, sharex=True, facecolor=SURFACE)
    for ax, (y, q) in zip(axes, quarters):
        _style(ax, zero=None)
        ax.grid(axis="y", visible=False)
        ax.grid(axis="x", color=GRID, linewidth=0.5)
        ax.axvline(0, color=INK_2, linewidth=0.6, zorder=1)
        for i, (m, _) in enumerate(rows):
            yy = len(rows) - 1 - i
            v = nat[(nat["year"] == y) & (nat["quarter"] == q) & (nat["model"] == m)].set_index("training")["yoy"]
            ax.plot([v["excl_2020_2022"], v["full"]], [yy, yy], color=GRID, linewidth=1.2, zorder=2)
            ax.plot(v["full"], yy, "o", markersize=5, color=INK, markeredgecolor=INK, zorder=3)
            ax.plot(v["excl_2020_2022"], yy, "o", markersize=5, color=SURFACE, markeredgecolor=INK,
                    markeredgewidth=1.1, zorder=3)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels([lab for _, lab in rows][::-1], fontsize=7.5, color=INK)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
        ax.set_ylim(-0.6, len(rows) - 0.4)
        _panel_title(ax, f"{y}Q{q}")
    fig.supxlabel("Forecast year-over-year change in establishment births, log points (average of 51 states)",
                  fontsize=7.5, color=INK_2)
    handles = [
        Line2D([], [], linestyle="none", marker="o", markersize=5, color=INK, label="Estimated on all data"),
        Line2D([], [], linestyle="none", marker="o", markersize=5, color=SURFACE, markeredgecolor=INK,
               markeredgewidth=1.1, label="Estimated excluding 2020–22"),
    ]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.01, 1.0), ncol=2, frameon=False,
               fontsize=7.5, labelcolor=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.88), w_pad=1.0)
    _save(fig, "fig7_live_forecasts_2026")
    print(nat.pivot_table(index=["year", "quarter", "model"], columns="training", values="yoy").round(1).to_string())


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    preds = pd.read_csv(TABLE_DIR / "rq2_predictions.csv")
    _check_against_committed(preds)
    print("Figure 1"); fig_raw_data()
    print("Figure 2"); fig_test_window_intervals()
    print("Figure 3"); fig_cumulative_ba(preds)
    print("Figure 4"); fig_cumulative_by_series(preds)
    print("Figure 5"); fig_weights_indexed()
    print("Figure 6"); fig_new_firm_share()
    print("Figure 7"); fig_live_forecasts()


if __name__ == "__main__":
    main()
