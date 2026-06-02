"""Produce Phase 3 selection figures from machine-readable outputs."""

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
SESSION_LOG = HERE.parent / "logs" / "executor_phase3_selection_20260602T110516Z.md"

mh.style.use("CMS")

SAMPLE_LABELS = {
    "GluGluToHToTauTau": "ggH H to tau tau",
    "VBF_HToTauTau": "VBF H to tau tau",
    "DYJetsToLL": "DY+jets",
    "TTbar": "ttbar",
    "W1JetsToLNu": "W+1 jet",
    "W2JetsToLNu": "W+2 jets",
    "W3JetsToLNu": "W+3 jets",
    "Run2012B_TauPlusX": "Run2012B",
    "Run2012C_TauPlusX": "Run2012C",
}

VARIABLE_LABELS = {
    "mu_pt": r"Selected muon $p_T$ [GeV]",
    "tau_pt": r"Selected $\tau_h$ $p_T$ [GeV]",
    "met_pt": r"$p_T^\mathrm{miss}$ [GeV]",
    "mt_mu_met": r"$m_T(\mu,p_T^\mathrm{miss})$ [GeV]",
    "m_vis": "Visible mass [GeV]",
    "m_addmet": "Add-MET mass [GeV]",
    "pt_tautau_proxy": r"Visible+MET $p_T$ proxy [GeV]",
    "n_clean_jets": "Clean jet multiplicity",
    "mjj": "Leading dijet mass [GeV]",
    "delta_eta_jj": r"Leading dijet $|\Delta\eta|$",
}

BINS = {
    "mu_pt": np.linspace(20, 160, 33),
    "tau_pt": np.linspace(20, 180, 33),
    "met_pt": np.linspace(0, 200, 41),
    "mt_mu_met": np.linspace(0, 180, 37),
    "m_vis": np.linspace(0, 250, 51),
    "m_addmet": np.linspace(0, 300, 61),
    "pt_tautau_proxy": np.linspace(0, 250, 51),
    "n_clean_jets": np.arange(-0.5, 8.5, 1),
    "mjj": np.linspace(0, 1200, 49),
    "delta_eta_jj": np.linspace(0, 8, 33),
}


def append_session(message: str) -> None:
    with SESSION_LOG.open("a") as handle:
        handle.write(f"\n## {message}\n")


def load_selected() -> dict[str, np.ndarray]:
    with np.load(OUT / "selected_events.npz") as data:
        return {key: data[key] for key in data.files}


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Wrote %s", FIG / f"{name}.pdf")


def make_hist(edges: np.ndarray, counts: np.ndarray) -> hist.Hist:
    h = hist.Hist(hist.axis.Variable(edges, name="x"), storage=hist.storage.Weight())
    view = h.view()
    view.value = counts.astype(float)
    view.variance = np.maximum(counts.astype(float), 0.0)
    return h


def normal_hist(values: np.ndarray, bins: np.ndarray) -> tuple[hist.Hist, np.ndarray]:
    values = values[np.isfinite(values)]
    counts, edges = np.histogram(values, bins=bins)
    widths = np.diff(edges)
    if np.sum(counts) > 0:
        norm = counts / np.sum(counts) / widths
        yerr = np.sqrt(counts) / np.sum(counts) / widths
    else:
        norm = counts.astype(float)
        yerr = counts.astype(float)
    h = hist.Hist(hist.axis.Variable(edges, name="x"))
    h.view()[:] = norm
    return h, yerr


def label(ax: plt.Axes, llabel: str = "Open Data + Open Sim.") -> None:
    mh.label.exp_label(exp="CMS", text="", loc=0, data=True, llabel=llabel, rlabel=r"$8$ TeV", ax=ax)


def overlay_by_role(selected: dict[str, np.ndarray], variable: str, output: str, mask: np.ndarray | None = None) -> None:
    mask = np.ones(len(selected["role"]), dtype=bool) if mask is None else mask
    fig, ax = plt.subplots(figsize=(10, 10))
    specs = [
        ("Data", selected["role"] == "data", "black"),
        ("Signal MC", selected["role"] == "signal", "tab:green"),
        ("Background MC", selected["role"] == "background", "tab:blue"),
    ]
    positive = []
    for legend, role_mask, color in specs:
        values = selected[variable][mask & role_mask]
        h, yerr = normal_hist(values, BINS[variable])
        mh.histplot(h, yerr=yerr, histtype="errorbar", ax=ax, label=legend, color=color)
        positive.extend(h.view()[h.view() > 0].tolist())
    ax.set_xlabel(VARIABLE_LABELS[variable])
    ax.set_ylabel("Normalized events")
    ax.legend(fontsize="x-small", loc="upper right")
    if positive:
        ymax = max(positive)
        ax.set_ylim(0.0, ymax * 1.35)
    label(ax)
    save(fig, output)


def plot_cutflow() -> None:
    payload = json.loads((OUT / "cutflow.json").read_text())
    steps = payload["steps"]
    fig, ax = plt.subplots(figsize=(10, 10))
    edges = np.arange(len(steps) + 1) - 0.5
    for role, color in [("data", "black"), ("signal", "tab:green"), ("background", "tab:blue")]:
        counts = np.zeros(len(steps), dtype=float)
        for sample in payload["samples"].values():
            if sample["role"] == role:
                counts += np.asarray([sample["counts"][step] for step in steps], dtype=float)
        mh.histplot(make_hist(edges, counts), yerr=np.sqrt(counts), histtype="errorbar", ax=ax, label=role.title(), color=color)
    ax.set_yscale("log")
    ax.set_xlabel("Cutflow step")
    ax.set_ylabel("Events")
    ax.set_xticks(np.arange(len(steps)))
    ax.set_xticklabels([step.replace("_", " ") for step in steps], rotation=90)
    ax.legend(fontsize="x-small", loc="upper right")
    label(ax)
    save(fig, "cutflow_summary")


def plot_category_yields() -> None:
    payload = json.loads((OUT / "category_yields.json").read_text())
    categories = payload["categories"]
    edges = np.arange(len(categories) + 1) - 0.5
    fig, ax = plt.subplots(figsize=(10, 10))
    for role, color in [("data", "black"), ("signal", "tab:green"), ("background", "tab:blue")]:
        counts = np.zeros(len(categories), dtype=float)
        for sample in payload["samples"].values():
            if sample["role"] == role:
                counts += np.asarray([sample["raw_counts"][category] for category in categories], dtype=float)
        mh.histplot(make_hist(edges, counts), yerr=np.sqrt(counts), histtype="errorbar", ax=ax, label=role.title(), color=color)
    ax.set_yscale("log")
    ax.set_xlabel("Exclusive category")
    ax.set_ylabel("Raw events")
    ax.set_xticks(np.arange(len(categories)))
    ax.set_xticklabels([category.replace("_", "-") for category in categories])
    ax.legend(fontsize="x-small", loc="upper right")
    label(ax)
    save(fig, "category_yields")


def plot_mass_by_category(selected: dict[str, np.ndarray], variable: str, prefix: str) -> None:
    for category in ["vbf", "boosted", "zero_jet"]:
        overlay_by_role(selected, variable, f"{prefix}_{category}", selected["category"] == category)


def plot_modelling() -> None:
    payload = json.loads((OUT / "variable_modeling.json").read_text())
    rows = payload["rows"]
    names = [row["variable"] for row in rows]
    values = [row["chi2_ndf"] if row["chi2_ndf"] is not None else np.nan for row in rows]
    x = np.arange(len(names), dtype=float)
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.plot(x, values, marker="o", linestyle="", label=r"Shape $\chi^2/\mathrm{ndf}$")
    ax.axhline(5.0, color="tab:red", linestyle="--", label="MVA gate")
    ax.set_xticks(x)
    ax.set_xticklabels([name.replace("_", " ") for name in names], rotation=90)
    ax.set_xlabel("Candidate input")
    ax.set_ylabel(r"Validation shape $\chi^2/\mathrm{ndf}$")
    ax.set_ylim(0, np.nanmax(values) * 1.15 if np.any(np.isfinite(values)) else 6)
    ax.legend(fontsize="x-small", loc="upper right")
    label(ax)
    save(fig, "mva_input_modeling_chi2")


def plot_approach_comparison() -> None:
    payload = json.loads((OUT / "approach_comparison.json").read_text())
    names = ["visible_mass", "addmet_mass"]
    values = [payload["approaches"][name]["combined_metric_sum_over_categories"] for name in names]
    edges = np.arange(len(names) + 1) - 0.5
    fig, ax = plt.subplots(figsize=(10, 10))
    mh.histplot(make_hist(edges, np.asarray(values)), yerr=np.zeros(len(values)), histtype="errorbar", ax=ax, label="MC-only metric")
    ax.set_xlabel("Approach")
    ax.set_ylabel(r"Combined $\sqrt{\sum S^2/(B+1)}$")
    ax.set_xticks(np.arange(len(names)))
    ax.set_xticklabels(["Visible mass", "Add-MET mass"])
    ax.legend(fontsize="x-small", loc="upper right")
    label(ax, llabel="Open Simulation")
    save(fig, "approach_comparison")


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    selected = load_selected()
    signal_region = selected["region"] == "signal"
    plot_cutflow()
    plot_category_yields()
    for variable in ["mu_pt", "tau_pt", "met_pt", "mt_mu_met", "pt_tautau_proxy"]:
        overlay_by_role(selected, variable, variable, signal_region)
    overlay_by_role(selected, "mt_mu_met", "w_high_mt_control_mt", selected["region"] == "w_high_mt")
    overlay_by_role(selected, "m_vis", "qcd_same_sign_mvis", selected["region"] == "qcd_same_sign")
    overlay_by_role(selected, "m_vis", "z_rich_validation_mvis", selected["region"] == "z_rich")
    plot_mass_by_category(selected, "m_vis", "visible_mass")
    plot_mass_by_category(selected, "m_addmet", "addmet_mass")
    overlay_by_role(selected, "n_clean_jets", "clean_jet_multiplicity", signal_region)
    overlay_by_role(selected, "mjj", "vbf_dijet_mass", signal_region & (selected["n_clean_jets"] >= 2))
    overlay_by_role(selected, "delta_eta_jj", "vbf_delta_eta_jj", signal_region & (selected["n_clean_jets"] >= 2))
    plot_modelling()
    plot_approach_comparison()
    append_session("Phase 3 selection figures generated as PDF and PNG.")


if __name__ == "__main__":
    main()
