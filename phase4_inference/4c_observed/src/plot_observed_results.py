"""Plot Phase 4c audit-corrected observed outputs."""

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

BACKGROUND_ORDER = ["QCDSameSignDataDriven", "DYJetsToLL", "TTbar", "W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]
SIGNALS = ["GluGluToHToTauTau", "VBF_HToTauTau"]
LABELS = {
    "GluGluToHToTauTau": "ggH H to tau tau",
    "VBF_HToTauTau": "VBF H to tau tau",
    "DYJetsToLL": "DY+jets",
    "TTbar": "ttbar",
    "W1JetsToLNu": "W+1 jet",
    "W2JetsToLNu": "W+2 jets",
    "W3JetsToLNu": "W+3 jets",
    "QCDSameSignDataDriven": "QCD/fake",
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
        rlabel=r"$\sqrt{s}=8$ TeV, $L=11.467$ fb$^{-1}$ ref.",
        ax=ax,
    )


def set_main_ylim(ax: plt.Axes) -> None:
    ymin, ymax = ax.get_ylim()
    if ymax > ymin:
        ax.set_ylim(0.0, ymax * 1.25)


def plot_template_file(npz_name: str, stem_prefix: str, xlabel: str, signal_scale: float) -> None:
    payload = np.load(OUT / npz_name, allow_pickle=False)
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
            if np.sum(values[isample, icat]) <= 0:
                continue
            bkg_hists.append(make_weight_hist(edges, values[isample, icat], variances[isample, icat]))
            bkg_labels.append(LABELS[sample])
        mh.histplot(bkg_hists, stack=True, histtype="fill", ax=ax, label=bkg_labels)
        signal_values = np.sum([values[samples.index(sample), icat] for sample in SIGNALS], axis=0)
        signal_variances = np.sum([variances[samples.index(sample), icat] for sample in SIGNALS], axis=0)
        signal_label = "H to tau tau x" + format(signal_scale, "g")
        mh.histplot(make_weight_hist(edges, signal_values * signal_scale, signal_variances * signal_scale * signal_scale), histtype="step", ax=ax, label=signal_label, color="black")
        data = data_counts[icat]
        ax.errorbar(centers, data, xerr=xerr, yerr=np.sqrt(np.maximum(data, 1.0)), marker="o", linestyle="", color="black", label="Full data")
        bkg = np.sum([values[samples.index(sample), icat] for sample in BACKGROUND_ORDER], axis=0)
        ratio = np.divide(data, bkg, out=np.full_like(data, np.nan, dtype=float), where=bkg > 0)
        ratio_err = np.divide(np.sqrt(np.maximum(data, 1.0)), bkg, out=np.zeros_like(data, dtype=float), where=bkg > 0)
        rax.errorbar(centers, ratio, xerr=xerr, yerr=ratio_err, marker="o", linestyle="", color="black")
        rax.axhline(1.0, color="tab:red", linestyle="--")
        rax.set_ylim(0.0, max(2.0, float(np.nanmax(ratio + ratio_err)) * 1.15 if np.any(np.isfinite(ratio)) else 2.0))
        rax.set_ylabel("Data/Pred.")
        rax.set_xlabel(xlabel)
        ax.set_ylabel("Events")
        ax.set_xlim(float(edges[0]), float(edges[-1]))
        ax.legend(fontsize="x-small", loc="upper right")
        set_main_ylim(ax)
        label(ax)
        save(fig, f"{stem_prefix}_{category}")


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
    results = json.loads((OUT / "observed_results.json").read_text())
    primary = results["validation_summary"]
    categories = list(primary["score_template_validation"].keys())
    x = np.arange(len(categories), dtype=float)
    fig, (ax, rax) = plt.subplots(2, 1, figsize=(10, 10), sharex=True, gridspec_kw={"height_ratios": [1, 1]})
    fig.subplots_adjust(hspace=0)
    ratios = [primary["score_template_validation"][category]["data_over_background"] for category in categories]
    pulls = [primary["score_template_validation"][category]["max_abs_pull"] for category in categories]
    ax.errorbar(x, ratios, yerr=np.zeros(len(ratios)), marker="o", linestyle="", label="Visible-mass baseline", color="#0072b2")
    rax.errorbar(x, pulls, yerr=np.zeros(len(pulls)), marker="o", linestyle="", label="Visible-mass baseline", color="#0072b2")
    ax.axhline(1.0, color="tab:red", linestyle="--")
    rax.axhline(3.0, color="tab:red", linestyle="--")
    ax.set_ylabel("Data/Pred.")
    rax.set_ylabel("Max pull")
    rax.set_xticks(x)
    rax.set_xticklabels([category.replace("_", "-") for category in categories])
    rax.set_xlabel("Category")
    ax.legend(fontsize="x-small", loc="upper right")
    rax.legend(fontsize="x-small", loc="upper right")
    ax.set_ylim(0.0, 2.0)
    rax.set_ylim(0.0, 5.0)
    label(ax)
    save(fig, "observed_pull_ratio_summary")


def plot_result_summary() -> None:
    results = json.loads((OUT / "observed_results.json").read_text())
    baseline = results["observed_fit"]
    nn_fit = results["nn_score_result"]["observed_fit"]
    baseline_limit = baseline["observed_upper_limit"]
    nn_limit = nn_fit["observed_upper_limit"]
    baseline_profile = baseline.get("profile_mu_interval", {})
    nn_profile = nn_fit.get("profile_mu_interval", {})
    labels = [r"$m_{\mathrm{vis}}$", r"$D_{NN}$"]
    values = np.asarray([baseline["mu_hat"], nn_fit["mu_hat"]], dtype=float)
    err_minus = np.asarray([
        baseline_profile.get("err_minus", baseline["mu_hat"]),
        nn_profile.get("err_minus", nn_fit["mu_hat"]),
    ], dtype=float)
    err_plus = np.asarray([
        baseline_profile.get("err_plus", baseline_limit["observed_limit"] - baseline["mu_hat"]),
        nn_profile.get("err_plus", nn_limit["observed_limit"] - nn_fit["mu_hat"]),
    ], dtype=float)
    expected = np.asarray([
        baseline_limit["expected_band_minus2_minus1_median_plus1_plus2"][2],
        nn_limit["expected_band_minus2_minus1_median_plus1_plus2"][2],
    ], dtype=float)
    published = [
        {
            "label": "CMS 2014",
            "mu": 0.78,
            "err_minus": 0.27,
            "err_plus": 0.27,
            "expected_z": 3.7,
        },
        {
            "label": "CMS 2018",
            "mu": 1.09,
            "err_minus": 0.26,
            "err_plus": 0.27,
            "expected_z": 4.7,
        },
    ]
    rows: list[dict[str, object]] = [
        {
            "label": r"$m_{\mathrm{vis}}$",
            "mu": values[0],
            "err_minus": err_minus[0],
            "err_plus": err_plus[0],
            "band": baseline_limit["expected_band_minus2_minus1_median_plus1_plus2"],
        },
        {
            "label": r"$D_{NN}$",
            "mu": values[1],
            "err_minus": err_minus[1],
            "err_plus": err_plus[1],
            "band": nn_limit["expected_band_minus2_minus1_median_plus1_plus2"],
        },
    ]
    for item in published:
        sigma = 1.0 / float(item["expected_z"])
        rows.append(
            {
                "label": item["label"],
                "mu": item["mu"],
                "err_minus": item["err_minus"],
                "err_plus": item["err_plus"],
                "band": [
                    max(0.0, 1.0 - 2.0 * sigma),
                    max(0.0, 1.0 - sigma),
                    1.0,
                    1.0 + sigma,
                    1.0 + 2.0 * sigma,
                ],
            }
        )
    fig, ax = plt.subplots(figsize=(10, 10))
    y = np.arange(len(rows), dtype=float)
    for idx, row in enumerate(rows):
        band = np.asarray(row["band"], dtype=float)
        ax.fill_betweenx(
            [y[idx] - 0.28, y[idx] + 0.28],
            band[0],
            band[4],
            color="#f0e442",
            alpha=0.95,
            linewidth=0,
            label=r"Expected $\pm 2\sigma$" if idx == 0 else None,
        )
        ax.fill_betweenx(
            [y[idx] - 0.28, y[idx] + 0.28],
            band[1],
            band[3],
            color="#009e73",
            alpha=0.95,
            linewidth=0,
            label=r"Expected $\pm 1\sigma$" if idx == 0 else None,
        )
    ax.axvline(1.0, color="black", linestyle="-", linewidth=1.2, label="SM mu=1")
    for idx, row in enumerate(rows):
        band = np.asarray(row["band"], dtype=float)
        ax.vlines(
            band[2],
            y[idx] - 0.34,
            y[idx] + 0.34,
            color="black",
            linestyle="--",
            linewidth=1.6,
            label="Median expected" if idx == 0 else None,
        )
        ax.errorbar(
            float(row["mu"]),
            y[idx],
            xerr=np.asarray([[float(row["err_minus"])], [float(row["err_plus"])]], dtype=float),
            marker="o",
            linestyle="",
            color="black",
            ecolor="black",
            capsize=4,
            label=r"Observed $\hat{\mu}$" if idx == 0 else None,
        )
    ax.set_yticks(y, [str(row["label"]) for row in rows])
    ax.set_xlabel(r"Signal strength $\mu$")
    upper = max(
        max(float(row["mu"]) + float(row["err_plus"]) for row in rows),
        max(float(np.asarray(row["band"], dtype=float)[4]) for row in rows),
        1.2,
    )
    ax.set_xlim(0.0, upper * 1.15)
    ax.invert_yaxis()
    ax.legend(fontsize="x-small", loc="lower right")
    label(ax)
    save(fig, "observed_limit_significance_summary")


def plot_comparison() -> None:
    comparison = json.loads((OUT / "comparison_to_4a_4b.json").read_text())
    p = comparison["baseline_fit_comparison"]
    n = comparison["nn_fit_comparison"]
    w = comparison["w_scale_comparison"]
    values = [
        p["median_expected_limit"],
        p["observed_limit"],
        p["mu_hat"],
        n["median_expected_limit"],
        n["observed_limit"],
        n["mu_hat"],
        w["phase4c_full_scale"],
    ]
    labels = ["Baseline exp. limit", "Baseline obs. limit", "Baseline mu", "D_NN exp. limit", "D_NN obs. limit", "D_NN mu", "4c W scale"]
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
    plot_template_file("visible_observed_templates.npz", "observed_visible", r"Visible mass $m_{\mu\tau_h}$ [GeV]", 20.0)
    plot_template_file("nn_score_observed_templates.npz", "observed_nn_score", r"$D_{NN}$ classifier score", 20.0)
    plot_w_highmt()
    plot_pull_ratio_summary()
    plot_result_summary()
    plot_comparison()
    compile_note()
    append_session("Generated Phase 4c audit-corrected plots as PDF/PNG and compiled ANALYSIS_NOTE_4c_v1.pdf.")


if __name__ == "__main__":
    main()
