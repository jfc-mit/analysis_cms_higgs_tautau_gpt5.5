"""Phase 2 plotting from exploration JSON artifacts."""

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
OUT = HERE.parent / "outputs"
FIG = OUT / "figures"

mh.style.use("CMS")


def mpl_magic(ax: plt.Axes) -> None:
    """Add simple y-axis headroom for legends when mplhep lacks mpl_magic."""
    ymin, ymax = ax.get_ylim()
    if ymax > ymin:
        if ax.get_yscale() == "log" and ymin > 0:
            ax.set_ylim(ymin, ymax * 4)
        else:
            ax.set_ylim(ymin, ymax * 1.35)


def load_json(name: str) -> dict:
    return json.loads((OUT / name).read_text())


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Wrote %s", FIG / f"{name}.pdf")


def make_hist(edges: list[float], counts: list[float]) -> hist.Hist:
    h = hist.Hist(hist.axis.Variable(edges, name="x"), storage=hist.storage.Weight())
    view = h.view()
    view.value = np.asarray(counts, dtype=float)
    view.variance = np.asarray(counts, dtype=float)
    return h


def plot_counts(inventory: dict) -> None:
    names = list(inventory["samples"])
    events = [inventory["samples"][name]["trees"]["Events"]["entries"] for name in names]
    sizes = [inventory["samples"][name]["size_bytes"] / 1e6 for name in names]
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.plot(x, events, marker="o", linestyle="", label="Events")
    ax.set_yscale("log")
    ax.set_ylabel("Events")
    ax.set_xlabel("Sample")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=90)
    ax2 = ax.twinx()
    ax2.plot(x, sizes, marker="s", linestyle="", color="tab:red", label="File size")
    ax2.set_ylabel("File size [MB]")
    ax.legend(fontsize="x-small", loc="upper left")
    ax2.legend(fontsize="x-small", loc="upper right")
    mh.label.exp_label(exp="CMS", text="", loc=0, data=True, llabel="Open Data / Open Simulation", rlabel=r"$\sqrt{s} = 8$ TeV", ax=ax)
    save(fig, "sample_event_count_file_size")


def plot_availability(inventory: dict) -> None:
    flags = [
        "has_genpart",
        "has_direct_genmet",
        "has_pileup_weight",
        "has_pv_npvs",
        "has_tau_antimu_tight",
        "has_btag",
        "has_met_covariance",
        "has_event_weight",
    ]
    names = list(inventory["samples"])
    matrix = np.asarray([[inventory["samples"][name]["feature_flags"][flag] for flag in flags] for name in names], dtype=float)
    fig, ax = plt.subplots(figsize=(10, 10))
    im = ax.imshow(matrix, vmin=0, vmax=1, cmap="viridis", aspect="auto")
    cax = mh.utils.make_square_add_cbar(ax)
    fig.colorbar(im, cax=cax)
    ax.set_xticks(np.arange(len(flags)))
    ax.set_xticklabels([flag.replace("has_", "").replace("_", " ") for flag in flags], rotation=90)
    ax.set_yticks(np.arange(len(names)))
    ax.set_yticklabels(names)
    ax.set_xlabel("Feature")
    ax.set_ylabel("Sample")
    mh.label.exp_label(exp="CMS", text="", loc=0, data=True, llabel="Open Data / Open Simulation", rlabel=r"$\sqrt{s} = 8$ TeV", ax=ax)
    save(fig, "branch_feature_availability")


def combined_counts(histograms: dict, variable: str, roles: set[str]) -> tuple[list[float], list[float]]:
    edges = None
    total = None
    for sample in histograms["samples"].values():
        if sample["role"] not in roles:
            continue
        h = sample["histograms"][variable]
        edges = h["edges"]
        counts = np.asarray(h["counts"], dtype=float)
        total = counts if total is None else total + counts
    if edges is None or total is None:
        return [], []
    return edges, total.tolist()


def plot_overlay(histograms: dict, variable: str, xlabel: str, output: str, density: bool = True) -> None:
    fig, ax = plt.subplots(figsize=(10, 10))
    specs = [
        ("Data slice", {"data"}, "black"),
        ("Signal MC slice", {"signal"}, "tab:green"),
        ("Background MC slice", {"background"}, "tab:blue"),
    ]
    for label, roles, color in specs:
        edges, counts = combined_counts(histograms, variable, roles)
        if not edges:
            continue
        counts_array = np.asarray(counts, dtype=float)
        if density and np.sum(counts_array) > 0:
            widths = np.diff(np.asarray(edges, dtype=float))
            counts_array = counts_array / np.sum(counts_array) / widths
            yerr = np.sqrt(np.asarray(counts, dtype=float)) / np.sum(counts) / widths if np.sum(counts) > 0 else np.zeros_like(counts_array)
        else:
            yerr = np.sqrt(counts_array)
        h = hist.Hist(hist.axis.Variable(edges, name="x"))
        h.view()[:] = counts_array
        mh.histplot(h, yerr=yerr, histtype="errorbar", ax=ax, label=label, color=color)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Normalized events" if density else "Events")
    ax.legend(fontsize="x-small", loc="upper right")
    mpl_magic(ax)
    mh.label.exp_label(exp="CMS", text="", loc=0, data=True, llabel="Open Data / Open Simulation", rlabel=r"$\sqrt{s} = 8$ TeV", ax=ax)
    save(fig, output)


def plot_yields(yields: dict) -> None:
    regions = ["has_mu_tau", "loose_accept", "baseline_os_lowmt", "high_mt_w_cr", "vbf_like"]
    labels = {
        "has_mu_tau": "Has muon and tau",
        "loose_accept": "Loose acceptance",
        "baseline_os_lowmt": "OS low-mT baseline",
        "high_mt_w_cr": "High-mT W CR",
        "vbf_like": "VBF-like",
    }
    names = list(yields["samples"])
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(10, 10))
    for region in regions:
        vals = [yields["samples"][name][region] for name in names]
        ax.plot(x, vals, marker="o", linestyle="", label=labels[region])
    ax.set_yscale("log")
    ax.set_ylabel("Events in 5k-event slice")
    ax.set_xlabel("Sample")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=90)
    ax.legend(fontsize="x-small", loc="upper right")
    mpl_magic(ax)
    mh.label.exp_label(exp="CMS", text="", loc=0, data=True, llabel="Open Data / Open Simulation", rlabel=r"$\sqrt{s} = 8$ TeV", ax=ax)
    save(fig, "preselection_yield_summary")


def plot_separation(separation: dict) -> None:
    rows = separation["ranking"][:12]
    names = [row["variable"].replace("_", " ") for row in rows]
    values = [row["separation_from_random"] for row in rows]
    y = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.plot(values, y, marker="o", linestyle="", label="Single-variable separation")
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xlabel("abs(AUC - 0.5)")
    ax.set_ylabel("Variable")
    ax.legend(fontsize="x-small", loc="upper right")
    mpl_magic(ax)
    mh.label.exp_label(exp="CMS", text="", loc=0, data=True, llabel="Open Simulation", rlabel=r"$\sqrt{s} = 8$ TeV", ax=ax)
    save(fig, "variable_separation_ranking")


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    inventory = load_json("sample_inventory.json")
    histograms = load_json("variable_histograms.json")
    yields = load_json("preselection_yields.json")
    separation = load_json("variable_separation.json")
    plot_counts(inventory)
    plot_availability(inventory)
    plot_overlay(histograms, "mu_pt", r"Leading muon $p_T$ [GeV]", "muon_pt_slice")
    plot_overlay(histograms, "tau_pt", r"Leading $\tau_h$ $p_T$ [GeV]", "tau_pt_slice")
    plot_overlay(histograms, "met_pt", r"$p_T^\mathrm{miss}$ [GeV]", "met_pt_slice")
    plot_overlay(histograms, "m_vis", r"Visible mass [GeV]", "visible_mass_slice")
    plot_overlay(histograms, "m_addmet", r"Add-MET mass [GeV]", "addmet_mass_slice")
    plot_overlay(histograms, "mt_mu_met", r"$m_T(\mu, p_T^\mathrm{miss})$ [GeV]", "mt_mu_met_slice")
    plot_overlay(histograms, "njet", "Jet multiplicity", "jet_multiplicity_slice", density=False)
    plot_overlay(histograms, "dijet_mass", r"Dijet mass [GeV]", "dijet_mass_slice")
    plot_overlay(histograms, "delta_eta_jj", r"Dijet $|\Delta\eta|$", "dijet_deltaeta_slice")
    plot_yields(yields)
    plot_separation(separation)


if __name__ == "__main__":
    main()
