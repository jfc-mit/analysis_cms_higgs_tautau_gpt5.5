"""Plot Phase 4b 10% data-validation outputs."""

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

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent
PHASE = HERE.parent
ROOT = PHASE.parent.parent
OUT = PHASE / "outputs"
FIG = OUT / "figures"
LOG = PHASE / "logs" / "executor_phase4b_partial_20260602T000000Z.md"

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


def label(ax: plt.Axes, data: bool = True) -> None:
    mh.label.exp_label(
        exp="CMS",
        text="",
        loc=0,
        data=data,
        llabel="Open Data",
        rlabel=r"$\sqrt{s}=8$ TeV, $L=1.1467$ fb$^{-1}$",
        ax=ax,
    )


def set_main_ylim(ax: plt.Axes) -> None:
    ymin, ymax = ax.get_ylim()
    if ymax > ymin:
        ax.set_ylim(0.0, ymax * 1.25)


def plot_score_templates() -> None:
    payload = np.load(OUT / "partial_templates.npz", allow_pickle=False)
    samples = [str(x) for x in payload["samples"]]
    categories = [str(x) for x in payload["categories"]]
    edges = payload["bin_edges"]
    observable = str(payload["observable"][0])
    values = payload["yields"]
    variances = payload["variances"]
    data_counts = payload["data_counts"]
    centers = 0.5 * (edges[:-1] + edges[1:])
    xerr = 0.5 * np.diff(edges)
    for icat, category in enumerate(categories):
        fig, (ax, rax) = plt.subplots(
            2,
            1,
            figsize=(10, 10),
            sharex=True,
            gridspec_kw={"height_ratios": [3, 1]},
        )
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
        mh.histplot(
            make_weight_hist(edges, signal_values * 20.0, signal_variances * 400.0),
            histtype="step",
            ax=ax,
            label="H to tau tau x20",
            color="black",
        )
        data = data_counts[icat]
        ax.errorbar(
            centers,
            data,
            xerr=xerr,
            yerr=np.sqrt(np.maximum(data, 1.0)),
            marker="o",
            linestyle="",
            color="black",
            label="10% data",
        )
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
        save(fig, f"partial_score_{category}")


def plot_w_highmt() -> None:
    payload = json.loads((OUT / "wjets_highmt_scale.json").read_text())
    values = np.asarray(
        [
            payload["nonw_background_mc_yield_10pct_lumi"],
            payload["wjets_mc_yield_10pct_lumi"],
            payload["nonw_background_mc_yield_10pct_lumi"]
            + payload["applied_scale_factor"] * payload["wjets_mc_yield_10pct_lumi"],
            payload["data_events_10pct"],
        ],
        dtype=float,
    )
    errs = np.asarray(
        [
            np.sqrt(payload["nonw_background_mc_sumw2_10pct_lumi"]),
            np.sqrt(payload["wjets_mc_sumw2_10pct_lumi"]),
            payload["absolute_uncertainty"] * payload["wjets_mc_yield_10pct_lumi"],
            np.sqrt(max(payload["data_events_10pct"], 1.0)),
        ],
        dtype=float,
    )
    fig, ax = plt.subplots(figsize=(10, 10))
    x = np.arange(len(values), dtype=float)
    ax.errorbar(x, values, yerr=errs, marker="o", linestyle="", label="High-mT control")
    ax.set_xticks(x)
    ax.set_xticklabels(["non-W MC", "W MC", "scaled total", "10% data"], rotation=20, ha="right")
    ax.set_xlabel("Control-region component")
    ax.set_ylabel("Events")
    ax.legend(fontsize="x-small", loc="upper right")
    set_main_ylim(ax)
    label(ax)
    save(fig, "w_highmt_scale")


def plot_visible_mass_summary() -> None:
    payload = json.loads((OUT / "data_validation.json").read_text())["visible_mass_validation"]
    categories = list(payload["categories"].keys())
    ratios = []
    errors = []
    for category in categories:
        row = payload["categories"][category]
        data = np.sum(np.asarray(row["data_counts"], dtype=float))
        bkg = np.sum(np.asarray(row["background_bins"], dtype=float))
        ratios.append(data / bkg if bkg > 0 else np.nan)
        errors.append(np.sqrt(max(data, 1.0)) / bkg if bkg > 0 else 0.0)
    fig, ax = plt.subplots(figsize=(10, 10))
    x = np.arange(len(categories), dtype=float)
    ax.errorbar(x, ratios, yerr=errors, marker="o", linestyle="", label="mvis 10% data/MC")
    ax.axhline(1.0, color="tab:red", linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels([category.replace("_", "-") for category in categories])
    ax.set_xlabel("Category")
    ax.set_ylabel("Data/MC")
    ax.set_ylim(0.0, max(2.0, float(np.nanmax(np.asarray(ratios) + np.asarray(errors))) * 1.15))
    ax.legend(fontsize="x-small", loc="upper right")
    label(ax)
    save(fig, "partial_mvis_summary")


def plot_pull_summary() -> None:
    payload = json.loads((OUT / "data_validation.json").read_text())
    labels = []
    pulls = []
    for category, row in payload["score_template_validation"].items():
        for ibin, pull in enumerate(row["pulls"]):
            labels.append(f"{category} b{ibin}")
            pulls.append(float(pull))
    fig, ax = plt.subplots(figsize=(10, 10))
    x = np.arange(len(pulls), dtype=float)
    ax.errorbar(x, pulls, yerr=np.zeros(len(pulls)), marker="o", linestyle="", label="Score-bin pull")
    ax.axhline(0.0, color="black", linestyle="-")
    ax.axhline(3.0, color="tab:red", linestyle="--")
    ax.axhline(-3.0, color="tab:red", linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_xlabel("Score-template bin")
    ax.set_ylabel("Pull")
    ax.legend(fontsize="x-small", loc="upper right")
    label(ax)
    save(fig, "partial_pull_summary")


def compile_note() -> None:
    commands = [
        [
            "pandoc",
            "ANALYSIS_NOTE_4b_v1.md",
            "-o",
            "ANALYSIS_NOTE_4b_v1.tex",
            "--standalone",
            "--include-in-header=../../../conventions/preamble.tex",
            "--number-sections",
            "--toc",
            "--filter",
            "pandoc-crossref",
            "--citeproc",
            "--bibliography=references.bib",
        ],
        [sys.executable, "../../../conventions/postprocess_tex.py", "ANALYSIS_NOTE_4b_v1.tex"],
        ["tectonic", "ANALYSIS_NOTE_4b_v1.tex"],
    ]
    for command in commands:
        log.info("Running %s", " ".join(command))
        subprocess.run(command, cwd=OUT, check=True)
    log.info("Compiled %s", OUT / "ANALYSIS_NOTE_4b_v1.pdf")


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    plot_score_templates()
    plot_w_highmt()
    plot_visible_mass_summary()
    plot_pull_summary()
    compile_note()
    append_session("Generated Phase 4b plots as PDF/PNG and compiled ANALYSIS_NOTE_4b_v1.pdf.")


if __name__ == "__main__":
    main()
