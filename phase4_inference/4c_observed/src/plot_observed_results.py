"""Plot Phase 4c full-data observed outputs."""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path

import hist
import matplotlib.pyplot as plt
import mplhep as mh
import numpy as np
from rich.logging import RichHandler

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent
PHASE = HERE.parent
OUT = PHASE / "outputs"
FIG = OUT / "figures"
LOG = PHASE / "logs" / "executor_phase4c_observed_20260602T000000Z.md"

mh.style.use("CMS")

BACKGROUND_ORDER = ["DYJetsToLL", "TTbar", "W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]
SIGNALS = ["GluGluToHToTauTau", "VBF_HToTauTau"]
LABELS = {
    "GluGluToHToTauTau": "ggH H to tau tau",
    "VBF_HToTauTau": "VBF H to tau tau",
    "DYJetsToLL": "DY+jets",
    "TTbar": "ttbar",
    "W1JetsToLNu": "W+1 jet",
    "W2JetsToLNu": "W+2 jets",
    "W3JetsToLNu": "W+3 jets",
}


def append_session(message: str) -> None:
    with LOG.open("a") as handle:
        handle.write(f"\n## {message}\n")


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Wrote %s", FIG / f"{name}.pdf")


def make_weight_hist(edges: np.ndarray, values: np.ndarray, variances: np.ndarray) -> hist.Hist:
    out = hist.Hist(hist.axis.Variable(edges, name="x"), storage=hist.storage.Weight())
    view = out.view()
    view.value = np.asarray(values, dtype=float)
    view.variance = np.asarray(variances, dtype=float)
    return out


def label(ax: plt.Axes) -> None:
    mh.label.exp_label(
        exp="CMS",
        text="",
        loc=0,
        data=True,
        llabel="Open Data",
        rlabel=r"$\sqrt{s}=8$ TeV, $L=11.467$ fb$^{-1}$",
        ax=ax,
    )


def set_main_ylim(ax: plt.Axes) -> None:
    ymin, ymax = ax.get_ylim()
    if ymax > ymin:
        ax.set_ylim(0.0, ymax * 1.25)


def plot_score_templates() -> None:
    payload = np.load(OUT / "observed_templates.npz", allow_pickle=False)
    samples = [str(x) for x in payload["samples"]]
    categories = [str(x) for x in payload["categories"]]
    edges = payload["bin_edges"]
    values = payload["yields"]
    variances = payload["variances"]
    data_counts = payload["data_counts"]
    centers = 0.5 * (edges[:-1] + edges[1:])
    xerr = 0.5 * np.diff(edges)
    for icat, category in enumerate(categories):
        fig, (ax, rax) = plt.subplots(2, 1, figsize=(10, 10), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
        fig.subplots_adjust(hspace=0)
        bkg_hists = []
        bkg_labels = []
        for sample in BACKGROUND_ORDER:
            isample = samples.index(sample)
            bkg_hists.append(make_weight_hist(edges, values[isample, icat], variances[isample, icat]))
            bkg_labels.append(LABELS[sample])
        mh.histplot(bkg_hists, stack=True, histtype="fill", ax=ax, label=bkg_labels)
        signal_values = np.sum([values[samples.index(sample), icat] for sample in SIGNALS], axis=0)
        signal_variances = np.sum([variances[samples.index(sample), icat] for sample in SIGNALS], axis=0)
        mh.histplot(make_weight_hist(edges, signal_values * 20.0, signal_variances * 400.0), histtype="step", ax=ax, label="H to tau tau x20", color="black")
        data = data_counts[icat]
        ax.errorbar(centers, data, xerr=xerr, yerr=np.sqrt(np.maximum(data, 1.0)), marker="o", linestyle="", color="black", label="Full data")
        bkg = np.sum([values[samples.index(sample), icat] for sample in BACKGROUND_ORDER], axis=0)
        ratio = np.divide(data, bkg, out=np.full_like(data, np.nan, dtype=float), where=bkg > 0)
        ratio_err = np.divide(np.sqrt(np.maximum(data, 1.0)), bkg, out=np.zeros_like(data, dtype=float), where=bkg > 0)
        rax.errorbar(centers, ratio, xerr=xerr, yerr=ratio_err, marker="o", linestyle="", color="black")
        rax.axhline(1.0, color="tab:red", linestyle="--")
        rax.set_ylim(0.0, max(2.0, float(np.nanmax(ratio + ratio_err)) * 1.15 if np.any(np.isfinite(ratio)) else 2.0))
        rax.set_ylabel("Data/MC")
        rax.set_xlabel("HGB score")
        ax.set_ylabel("Events")
        ax.set_xlim(float(edges[0]), float(edges[-1]))
        ax.legend(fontsize="x-small", loc="upper right")
        set_main_ylim(ax)
        label(ax)
        save(fig, f"observed_score_{category}")


def plot_w_highmt() -> None:
    payload = json.loads((OUT / "wjets_highmt_scale_full.json").read_text())
    values = np.asarray(
        [
            payload["nonw_background_mc_yield_full_lumi"],
            payload["wjets_mc_yield_full_lumi"],
            payload["nonw_background_mc_yield_full_lumi"] + payload["applied_scale_factor"] * payload["wjets_mc_yield_full_lumi"],
            payload["data_events_full"],
        ],
        dtype=float,
    )
    errs = np.asarray(
        [
            np.sqrt(payload["nonw_background_mc_sumw2_full_lumi"]),
            np.sqrt(payload["wjets_mc_sumw2_full_lumi"]),
            payload["absolute_uncertainty"] * payload["wjets_mc_yield_full_lumi"],
            np.sqrt(max(payload["data_events_full"], 1.0)),
        ],
        dtype=float,
    )
    fig, ax = plt.subplots(figsize=(10, 10))
    x = np.arange(len(values), dtype=float)
    ax.errorbar(x, values, yerr=errs, marker="o", linestyle="", label="High-mT control")
    ax.set_xticks(x)
    ax.set_xticklabels(["non-W MC", "W MC", "scaled total", "Full data"], rotation=20, ha="right")
    ax.set_xlabel("Control-region component")
    ax.set_ylabel("Events")
    ax.legend(fontsize="x-small", loc="upper right")
    set_main_ylim(ax)
    label(ax)
    save(fig, "w_highmt_scale_full")


def plot_pull_ratio_summary() -> None:
    payload = json.loads((OUT / "observed_results.json").read_text())["validation_summary"]
    categories = list(payload["score_template_validation"].keys())
    ratios = [payload["score_template_validation"][category]["data_over_background"] for category in categories]
    pulls = [payload["score_template_validation"][category]["max_abs_pull"] for category in categories]
    fig, (ax, rax) = plt.subplots(2, 1, figsize=(10, 10), sharex=True, gridspec_kw={"height_ratios": [1, 1]})
    fig.subplots_adjust(hspace=0)
    x = np.arange(len(categories), dtype=float)
    ax.errorbar(x, ratios, yerr=np.zeros(len(ratios)), marker="o", linestyle="", label="Full data/MC")
    ax.axhline(1.0, color="tab:red", linestyle="--")
    ax.set_ylabel("Data/MC")
    ax.legend(fontsize="x-small", loc="upper right")
    rax.errorbar(x, pulls, yerr=np.zeros(len(pulls)), marker="o", linestyle="", label="Max abs pull")
    rax.axhline(3.0, color="tab:red", linestyle="--")
    rax.set_xticks(x)
    rax.set_xticklabels([category.replace("_", "-") for category in categories])
    rax.set_xlabel("Category")
    rax.set_ylabel("Pull")
    rax.legend(fontsize="x-small", loc="upper right")
    ax.set_ylim(0.0, max(2.0, float(np.nanmax(ratios)) * 1.2))
    rax.set_ylim(0.0, max(4.0, float(np.nanmax(pulls)) * 1.2))
    label(ax)
    save(fig, "observed_pull_ratio_summary")


def plot_result_summary() -> None:
    results = json.loads((OUT / "observed_results.json").read_text())
    comparison = json.loads((OUT / "comparison_to_4a_4b.json").read_text())
    fit = results["observed_fit"]
    values = [
        fit.get("mu_hat", np.nan),
        fit.get("observed_upper_limit", {}).get("observed_limit", np.nan),
        comparison["phase4a_expected"]["median_expected_limit"],
        fit.get("discovery_diagnostic", {}).get("z_value", np.nan),
    ]
    fig, ax = plt.subplots(figsize=(10, 10))
    x = np.arange(len(values), dtype=float)
    ax.errorbar(x, values, yerr=np.zeros(len(values)), marker="o", linestyle="", label="Observed fit")
    ax.set_xticks(x)
    ax.set_xticklabels(["mu hat", "obs. limit", "exp. median", "Z q0"], rotation=20, ha="right")
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Value")
    ax.legend(fontsize="x-small", loc="upper right")
    set_main_ylim(ax)
    label(ax)
    save(fig, "observed_limit_significance_summary")


def plot_comparison() -> None:
    comparison = json.loads((OUT / "comparison_to_4a_4b.json").read_text())
    fit = comparison["fit_comparison"]
    w = comparison["w_scale_comparison"]
    values = [
        fit["phase4a_median_expected_limit"],
        fit["phase4b_diagnostic_mu_hat"],
        fit["phase4c_mu_hat"],
        fit["phase4c_observed_limit"],
        w["phase4b_10pct_scale"],
        w["phase4c_full_scale"],
    ]
    labels = ["4a exp. limit", "4b mu hat", "4c mu hat", "4c obs. limit", "4b W scale", "4c W scale"]
    fig, ax = plt.subplots(figsize=(10, 10))
    x = np.arange(len(values), dtype=float)
    ax.errorbar(x, values, yerr=np.zeros(len(values)), marker="o", linestyle="", label="Phase comparison")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_xlabel("Phase quantity")
    ax.set_ylabel("Value")
    ax.legend(fontsize="x-small", loc="upper right")
    set_main_ylim(ax)
    label(ax)
    save(fig, "comparison_to_4a_4b")


def compile_note() -> None:
    commands = [
        [
            "pandoc",
            "ANALYSIS_NOTE_4c_v1.md",
            "-o",
            "ANALYSIS_NOTE_4c_v1.tex",
            "--standalone",
            "--include-in-header=../../../conventions/preamble.tex",
            "--number-sections",
            "--toc",
            "--filter",
            "pandoc-crossref",
            "--citeproc",
            "--bibliography=references.bib",
        ],
        [sys.executable, "../../../conventions/postprocess_tex.py", "ANALYSIS_NOTE_4c_v1.tex"],
        ["tectonic", "ANALYSIS_NOTE_4c_v1.tex"],
    ]
    for command in commands:
        log.info("Running %s", " ".join(command))
        subprocess.run(command, cwd=OUT, check=True)


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    plot_score_templates()
    plot_w_highmt()
    plot_pull_ratio_summary()
    plot_result_summary()
    plot_comparison()
    compile_note()
    append_session("Generated Phase 4c plots as PDF/PNG and compiled ANALYSIS_NOTE_4c_v1.pdf.")


if __name__ == "__main__":
    main()
