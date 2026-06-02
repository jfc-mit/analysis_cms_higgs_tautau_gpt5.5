"""Plot Phase 4a expected inference outputs from machine-readable artifacts."""

from __future__ import annotations

import json
import logging
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
OUT = PHASE / "outputs"
FIG = OUT / "figures"
LOG = PHASE / "logs" / "executor_phase4a_expected_20260602T124406Z.md"

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


def make_count_hist(edges: np.ndarray, values: np.ndarray) -> hist.Hist:
    out = hist.Hist(hist.axis.Variable(edges, name="x"))
    out.view()[:] = np.asarray(values, dtype=float)
    return out


def mpl_magic(ax: plt.Axes, scale: float = 1.25) -> None:
    ymin, ymax = ax.get_ylim()
    if ymax > ymin:
        ax.set_ylim(ymin, ymax * scale)


def label(ax: plt.Axes) -> None:
    mh.label.exp_label(
        exp="CMS",
        text="",
        loc=0,
        data=True,
        llabel="Open Simulation",
        rlabel=r"$\sqrt{s}=8$ TeV, $L=11.467$ fb$^{-1}$",
        ax=ax,
    )


def plot_templates() -> None:
    payload = np.load(OUT / "templates.npz", allow_pickle=False)
    samples = [str(x) for x in payload["samples"]]
    categories = [str(x) for x in payload["categories"]]
    edges = payload["bin_edges"]
    observable = str(payload["observable"][0]) if "observable" in payload.files else "classifier score"
    values = payload["yields"]
    variances = payload["variances"]
    for icat, category in enumerate(categories):
        fig, ax = plt.subplots(figsize=(10, 10))
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
        ax.set_xlabel(observable.replace(chr(95), " "))
        ax.set_ylabel("Expected events")
        ax.set_xlim(float(edges[0]), float(edges[-1]))
        ax.legend(fontsize="x-small", loc="upper right")
        mpl_magic(ax)
        label(ax)
        save(fig, f"expected_mva_score_{category}")


def plot_s_over_b() -> None:
    yields = json.loads((OUT / "nominal_yields.json").read_text())
    categories = yields["categories"]
    values = [
        yields["totals"][category]["signal_total"] / yields["totals"][category]["background_total"]
        for category in categories
    ]
    errors = np.zeros(len(values), dtype=float)
    fig, ax = plt.subplots(figsize=(10, 10))
    x = np.arange(len(categories), dtype=float)
    ax.errorbar(x, values, yerr=errors, marker="o", linestyle="", label="Nominal S/B")
    ax.set_xticks(x)
    ax.set_xticklabels(
        ["Inclusive SR" if category == "inclusive_sr" else category.replace("_", "-") for category in categories]
    )
    ax.set_xlabel("Score-template channel")
    ax.set_ylabel("Expected signal / background")
    ax.set_ylim(0.0, max(values) * 1.4 if values else 1.0)
    ax.legend(fontsize="x-small", loc="upper right")
    mpl_magic(ax)
    label(ax)
    save(fig, "expected_s_over_b")


def plot_nuisance_summary() -> None:
    systematics = json.loads((OUT / "systematics.json").read_text())
    labels = []
    sizes = []
    for row in systematics["implemented"]:
        if row["type"] == "normsys":
            labels.append(row["name"].replace("_", " "))
            sizes.append(float(row["size"].replace("%", "")) / 100.0)
    payload = np.load(OUT / "templates.npz", allow_pickle=False)
    variances = payload["variances"]
    values = payload["yields"]
    stat_frac = float(np.sqrt(np.sum(variances)) / np.sum(values))
    labels.append("global MC stat proxy")
    sizes.append(stat_frac)
    fig, ax = plt.subplots(figsize=(10, 10))
    x = np.arange(len(labels), dtype=float)
    ax.errorbar(x, sizes, yerr=np.zeros(len(sizes)), marker="o", linestyle="", label="Nominal relative size")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_xlabel("Implemented uncertainty handle")
    ax.set_ylabel("Relative size")
    ax.set_ylim(0.0, max(sizes) * 1.4 if sizes else 1.0)
    ax.legend(fontsize="x-small", loc="upper right")
    mpl_magic(ax)
    label(ax)
    save(fig, "expected_nuisance_summary")


def plot_injection() -> None:
    payload = json.loads((OUT / "signal_injection.json").read_text())
    injected = np.asarray([row["injected_mu"] for row in payload["rows"]], dtype=float)
    fitted = np.asarray([row["fitted_mu"] for row in payload["rows"]], dtype=float)
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.errorbar(injected, fitted, yerr=np.zeros_like(fitted), marker="o", linestyle="", label="Asimov fit")
    ax.plot([0.0, 5.0], [0.0, 5.0], linestyle="--", color="tab:red", label="Ideal recovery")
    ax.set_xlabel("Injected signal strength")
    ax.set_ylabel("Fitted signal strength")
    ax.set_xlim(-0.2, 5.2)
    ax.set_ylim(-0.2, 5.2)
    ax.legend(fontsize="x-small", loc="upper right")
    mpl_magic(ax)
    label(ax)
    save(fig, "signal_injection_recovery")


def plot_gof() -> None:
    payload = json.loads((OUT / "gof_validation.json").read_text())
    combined = payload["combined"]
    toys = np.asarray(combined["toy_statistics"], dtype=float)
    edges = np.linspace(0.0, max(float(np.max(toys)), combined["toy_p95"]) * 1.1, 31)
    fig, ax = plt.subplots(figsize=(10, 10))
    mh.histplot(make_count_hist(edges, np.histogram(toys, bins=edges)[0]), histtype="step", ax=ax, label="Toy statistic proxy")
    ax.axvline(combined["asimov_saturated_stat"], color="tab:red", linestyle="--", label="Asimov")
    ax.set_xlabel("Saturated statistic")
    ax.set_ylabel("Toy count")
    ax.legend(fontsize="x-small", loc="upper right")
    mpl_magic(ax)
    label(ax)
    save(fig, "gof_toys")


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    plot_templates()
    plot_s_over_b()
    plot_nuisance_summary()
    plot_injection()
    plot_gof()
    append_session("Phase 4a expected figures generated as PDF and PNG from machine-readable outputs.")


if __name__ == "__main__":
    main()
