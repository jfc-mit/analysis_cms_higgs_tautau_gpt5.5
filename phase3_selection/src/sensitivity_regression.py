"""Expected-only sensitivity remediation scans for Phase 3 regression."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import mplhep as mh
import numpy as np
import pyhf
from rich.logging import RichHandler
from scipy.stats import norm
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBClassifier
except ImportError:  # pragma: no cover - environment-dependent optional model
    XGBClassifier = None

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)
mh.style.use("CMS")

HERE = Path(__file__).resolve().parent
PHASE = HERE.parent
ROOT = PHASE.parent
OUT = PHASE / "outputs"
FIG = OUT / "figures"
SESSION_LOG = PHASE / "logs" / "fixer_sensitivity_20260602T134700Z.md"
EXPERIMENT_LOG = ROOT / "experiment_log.md"

SIGNALS = ["GluGluToHToTauTau", "VBF_HToTauTau"]
BACKGROUNDS = ["DYJetsToLL", "TTbar", "W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]
SAMPLES = SIGNALS + BACKGROUNDS

BASELINE_CATEGORIES = ["vbf", "boosted", "zero_jet"]
BASELINE_BINS = np.asarray([0.0, 40.0, 60.0, 80.0, 100.0, 120.0, 160.0, 250.0])
ADDMET_BINS = np.asarray([0.0, 50.0, 70.0, 90.0, 110.0, 130.0, 160.0, 220.0, 320.0])
PT_TAUTAU_BINS = np.asarray([0.0, 25.0, 50.0, 75.0, 100.0, 130.0, 170.0, 250.0])
MVA_SCORE_BINS = np.asarray([0.0, 0.20, 0.35, 0.50, 0.65, 0.78, 0.88, 0.94, 0.985, 1.0])
MVA_COARSE_BINS = np.asarray([0.0, 0.35, 0.55, 0.72, 0.86, 0.94, 1.0])
MIN_EXPECTED_BACKGROUND_PER_BIN = 5.0
MAX_STABLE_AUC_GAP = 0.20

MVA_INPUTS = [
    "m_vis",
    "m_addmet",
    "mu_pt",
    "mu_eta",
    "mu_reliso",
    "tau_pt",
    "tau_eta",
    "tau_reliso",
    "met_pt",
    "mt_mu_met",
    "pt_tautau_proxy",
    "n_clean_jets",
    "mjj",
    "delta_eta_jj",
    "jet1_pt",
    "btag_max",
]

MODEL_DISPLAY_LABELS = {
    "hist_gradient_boosting": "Gradient-boosted classifier",
    "xgboost": "XGBoost classifier",
    "mlp": "Neural-network classifier",
    "transformer": "Transformer discriminator",
}

NUISANCE_DISPLAY_LABELS = {
    "nominal": "Nominal nuisances",
    "no_staterror": "No MC-stat nuisance",
    "no_normsys": "No normalization nuisances",
    "no_nuisance": "No nuisances",
    "low_nuisance_diagnostic": "Reduced nuisance diagnostic",
}


@dataclass(frozen=True)
class ModelSpec:
    name: str
    family: str
    category_labels: np.ndarray
    categories: list[str]
    observable: str
    bins: np.ndarray
    description: str
    caveat: str | None = None
    category_bins: dict[str, np.ndarray] | None = None
    model_name: str | None = None
    selection_role: str = "comparison"
    sparse_bin_handling: dict[str, Any] | None = None


def append_markdown(path: Path, message: str) -> None:
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with path.open("a") as handle:
        handle.write(f"\n## {timestamp}\n\n{message}\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    log.info("Wrote %s", path)


def load_selected() -> dict[str, np.ndarray]:
    with np.load(OUT / "selected_events.npz", allow_pickle=False) as payload:
        return {key: payload[key] for key in payload.files}


def load_norm() -> dict[str, Any]:
    return json.loads((OUT / "normalization_inputs.json").read_text())


def load_phase4a_baseline() -> dict[str, float]:
    payload = json.loads((ROOT / "phase4_inference" / "4a_expected" / "outputs" / "expected_results.json").read_text())
    return {
        "expected_z": float(payload["discovery_sensitivity"]["z_value"]),
        "median_limit": float(payload["expected_upper_limit"]["expected_band_minus2_minus1_median_plus1_plus2"][2]),
        "observed_on_background_asimov_limit": float(payload["expected_upper_limit"]["observed_on_background_asimov"]),
    }


def sample_weights(norm_payload: dict[str, Any]) -> dict[str, float]:
    return {
        sample: float(payload["absolute_weight_per_local_entry"])
        for sample, payload in norm_payload["mc_samples"].items()
        if sample in SAMPLES
    }


def weighted_hist(values: np.ndarray, event_weight: float, bins: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    finite = values[np.isfinite(values)]
    counts, _ = np.histogram(finite, bins=bins)
    yields = counts.astype(float) * event_weight
    variances = counts.astype(float) * event_weight * event_weight
    return counts.astype(int), yields, variances


def sanitize_category(name: str) -> str:
    return name.replace("-", "_").replace("/", "_")


def model_display_label(name: str) -> str:
    return MODEL_DISPLAY_LABELS.get(name, name.replace("_", " ").title())


def transformer_feasibility() -> dict[str, Any]:
    stacks = {name: find_spec(name) is not None for name in ["torch", "tabpfn", "pytorch_tabular"]}
    feasible = any(stacks.values())
    return {
        "tried": False,
        "selected": False,
        "available_stacks": stacks,
        "decision": "not_attempted_missing_fast_stack",
        "reason": (
            "No lightweight transformer/attention stack is available in the current pixi environment. "
            "Adding PyTorch or a tabular-transformer package would dominate this quick method update, "
            "so the comparison uses already-available xgboost and sklearn tree/neural-network models."
        )
        if not feasible
        else (
            "A transformer-capable stack is present, but no maintained lightweight tabular-transformer "
            "entry point was configured for this analysis; fast tree and neural-network candidates were "
            "kept as the maintainable quick comparison."
        ),
    }


def genmet_regression_feasibility(selected: dict[str, np.ndarray]) -> dict[str, Any]:
    keys = sorted(selected.keys())
    target_keys = [key for key in keys if "gen" in key.lower() and "met" in key.lower()]
    return {
        "requested_approach": "transformer regression of genMET direction / genMET phi followed by combined-mass construction",
        "target_branches_found": target_keys,
        "reco_met_branches_found": [key for key in keys if key in {"met_pt", "met_phi"}],
        "feasible": bool(target_keys),
        "decision": "not_implemented_missing_genmet_targets" if not target_keys else "target_available_not_primary_quick_pass",
        "reason": (
            "The reduced selected-event artifact has reconstructed MET variables but no genMET/genMET_phi target. "
            "Training a genMET-direction regressor without a real target would fabricate labels, so this branch is documented as infeasible."
        )
        if not target_keys
        else (
            "A genMET-like target appears to exist, but the quick pass prioritizes the discriminator candidate; "
            "the target should be validated before a regressed-mass observable is promoted."
        ),
    }


def tau_antimuon_status() -> dict[str, Any]:
    return {
        "requested": "tight anti-muon veto on hadronic tau ID",
        "status": "implemented_in_phase3_selection",
        "branch": "Tau_idAntiMuTight",
        "selection": "Tau_idAntiMuTight > 0 in phase3_selection/src/build_selection.py",
        "note": "The per-event selected_events.npz keeps the selected tau kinematics and isolation, not a separate anti-muon flag, so the veto is documented from the selection code path.",
    }


def spec_display_label(name: str) -> str:
    if name == "baseline_phase4a_mvis":
        return "Visible mass baseline"
    if name == "baseline_addmet":
        return "Add-MET mass baseline"
    if name == "baseline_pt_tautau_proxy":
        return "pT(tau tau) proxy baseline"
    if name == "jhep_refined_mvis":
        return "Boosted/VBF refined categories"
    if name.startswith("mva_") and name.endswith("_score_baseline_categories"):
        model_name = name.removeprefix("mva_").removesuffix("_score_baseline_categories")
        return f"{model_display_label(model_name)} score, baseline categories"
    if name.startswith("mva_") and name.endswith("_score_single_category"):
        model_name = name.removeprefix("mva_").removesuffix("_score_single_category")
        return f"{model_display_label(model_name)} score, inclusive signal region"
    if name.startswith("grid_"):
        rest = name.removeprefix("grid_mjj")
        try:
            mjj_cut, rest = rest.split("_deta", maxsplit=1)
            detajj_cut, pttt_cut = rest.split("_pt", maxsplit=1)
            return f"Dijet/boost scan, {mjj_cut} GeV, separation {detajj_cut}, boost pT {pttt_cut} GeV"
        except ValueError:
            return "Dijet/boost category scan"
    if name.startswith("btag_veto_le") and name.endswith("_split"):
        threshold = name.removeprefix("btag_veto_le").removesuffix("_split")
        return f"Top-veto scan, max b tag <= {threshold}"
    if name.startswith("taupt_split_"):
        threshold = name.removeprefix("taupt_split_")
        return f"Tau pT scan, threshold {threshold} GeV"
    return name.replace("_", " ").title()


def bins_for_category(spec: ModelSpec, category: str) -> np.ndarray:
    if spec.category_bins is not None and category in spec.category_bins:
        return spec.category_bins[category]
    return spec.bins


def weighted_background_bins(
    selected: dict[str, np.ndarray],
    labels: np.ndarray,
    category: str,
    observable: str,
    bins: np.ndarray,
    weights: dict[str, float],
) -> np.ndarray:
    total = np.zeros(len(bins) - 1, dtype=float)
    for sample in BACKGROUNDS:
        mask = (labels == category) & (selected["sample"] == sample)
        counts, _ = np.histogram(selected[observable][mask].astype(float), bins=bins)
        total += counts.astype(float) * weights[sample]
    return total


def merge_edges_for_background(
    selected: dict[str, np.ndarray],
    labels: np.ndarray,
    categories: list[str],
    observable: str,
    initial_edges: np.ndarray,
    weights: dict[str, float],
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    category_edges: dict[str, np.ndarray] = {}
    rows: dict[str, Any] = {}
    for category in categories:
        edges = [float(value) for value in initial_edges]
        merges: list[dict[str, Any]] = []
        while len(edges) > 2:
            bins = np.asarray(edges, dtype=float)
            background = weighted_background_bins(selected, labels, category, observable, bins, weights)
            low = np.flatnonzero(background < MIN_EXPECTED_BACKGROUND_PER_BIN)
            if low.size == 0:
                break
            idx = int(low[-1])
            if idx == 0:
                removed_edge_index = 1
                merge_with = "next"
            else:
                removed_edge_index = idx
                merge_with = "previous"
            merges.append(
                {
                    "low_bin_index": idx,
                    "low_bin_range": [float(edges[idx]), float(edges[idx + 1])],
                    "low_bin_background": float(background[idx]),
                    "removed_edge": float(edges[removed_edge_index]),
                    "merged_with": merge_with,
                }
            )
            del edges[removed_edge_index]
        final_edges = np.asarray(edges, dtype=float)
        final_background = weighted_background_bins(selected, labels, category, observable, final_edges, weights)
        impossible = bool(len(final_edges) == 2 and np.any(final_background < MIN_EXPECTED_BACKGROUND_PER_BIN))
        category_edges[category] = final_edges
        rows[category] = {
            "initial_edges": initial_edges.tolist(),
            "merged_edges": final_edges.tolist(),
            "merges": merges,
            "merge_count": len(merges),
            "background_bins": final_background.tolist(),
            "min_background_bin": float(np.min(final_background)) if final_background.size else 0.0,
            "passes_min_background": bool(np.all(final_background >= MIN_EXPECTED_BACKGROUND_PER_BIN)),
            "impossible_to_satisfy": impossible,
        }
    return category_edges, {
        "minimum_expected_background_per_fit_bin": MIN_EXPECTED_BACKGROUND_PER_BIN,
        "method": "Iteratively merge the sparsest high-score bin with its adjacent lower-score bin, using expected MC background only.",
        "categories": rows,
        "all_pass": all(row["passes_min_background"] for row in rows.values()),
    }


def merge_common_edges_for_background(
    selected: dict[str, np.ndarray],
    labels: np.ndarray,
    categories: list[str],
    observable: str,
    initial_edges: np.ndarray,
    weights: dict[str, float],
) -> tuple[np.ndarray, dict[str, Any]]:
    edges = [float(value) for value in initial_edges]
    merges: list[dict[str, Any]] = []
    while len(edges) > 2:
        bins = np.asarray(edges, dtype=float)
        low_rows = []
        for category in categories:
            background = weighted_background_bins(selected, labels, category, observable, bins, weights)
            for ibin, value in enumerate(background):
                if value < MIN_EXPECTED_BACKGROUND_PER_BIN:
                    low_rows.append((float(value), category, ibin))
        if not low_rows:
            break
        value, category, idx = min(low_rows, key=lambda row: (row[0], -row[2]))
        if idx == 0:
            removed_edge_index = 1
            merge_with = "next"
        else:
            removed_edge_index = idx
            merge_with = "previous"
        merges.append(
            {
                "category": category,
                "low_bin_index": idx,
                "low_bin_range": [float(edges[idx]), float(edges[idx + 1])],
                "low_bin_background": value,
                "removed_edge": float(edges[removed_edge_index]),
                "merged_with": merge_with,
            }
        )
        del edges[removed_edge_index]

    final_edges = np.asarray(edges, dtype=float)
    category_rows = {}
    for category in categories:
        background = weighted_background_bins(selected, labels, category, observable, final_edges, weights)
        category_rows[category] = {
            "background_bins": background.tolist(),
            "min_background_bin": float(np.min(background)) if background.size else 0.0,
            "passes_min_background": bool(np.all(background >= MIN_EXPECTED_BACKGROUND_PER_BIN)),
        }
    return final_edges, {
        "minimum_expected_background_per_fit_bin": MIN_EXPECTED_BACKGROUND_PER_BIN,
        "method": "common adjacent-bin merging across all fit categories using expected MC background only",
        "initial_edges": initial_edges.tolist(),
        "merged_edges": final_edges.tolist(),
        "merges": merges,
        "merge_count": len(merges),
        "categories": category_rows,
        "all_pass": all(row["passes_min_background"] for row in category_rows.values()),
    }


def assign_baseline(selected: dict[str, np.ndarray]) -> np.ndarray:
    labels = np.full(len(selected["role"]), "none", dtype="<U32")
    sr = selected["is_signal_region"].astype(bool)
    for category in BASELINE_CATEGORIES:
        labels[sr & (selected["category"] == category)] = category
    return labels


def assign_jhep_refined(selected: dict[str, np.ndarray]) -> np.ndarray:
    labels = np.full(len(selected["role"]), "none", dtype="<U32")
    sr = selected["is_signal_region"].astype(bool)
    njet = selected["n_clean_jets"]
    mjj = np.nan_to_num(selected["mjj"].astype(float), nan=-1.0)
    detajj = np.nan_to_num(selected["delta_eta_jj"].astype(float), nan=-1.0)
    pttt = np.nan_to_num(selected["pt_tautau_proxy"].astype(float), nan=-1.0)
    tau_pt = np.nan_to_num(selected["tau_pt"].astype(float), nan=-1.0)
    vbf_tight = sr & (njet >= 2) & (mjj > 700.0) & (detajj > 4.0)
    vbf_loose = sr & ~vbf_tight & (njet >= 2) & (mjj > 300.0) & (detajj > 2.5)
    non_vbf = sr & ~vbf_tight & ~vbf_loose
    boosted_high = non_vbf & (njet >= 1) & (pttt > 100.0)
    boosted_tau_high = non_vbf & (njet >= 1) & ~boosted_high & (tau_pt > 45.0)
    boosted_low = non_vbf & (njet >= 1) & ~boosted_high & ~boosted_tau_high
    zero_tau_high = non_vbf & (njet == 0) & (tau_pt > 45.0)
    zero_low = non_vbf & (njet == 0) & ~zero_tau_high
    labels[vbf_tight] = "vbf_tight"
    labels[vbf_loose] = "vbf_loose"
    labels[boosted_high] = "boosted_pt_high"
    labels[boosted_tau_high] = "boosted_tau_high"
    labels[boosted_low] = "boosted_low"
    labels[zero_tau_high] = "zero_tau_high"
    labels[zero_low] = "zero_low"
    return labels


def assign_grid(
    selected: dict[str, np.ndarray],
    mjj_cut: float,
    detajj_cut: float,
    pttt_cut: float,
    tau_cut: float | None = None,
    btag_cut: float | None = None,
) -> np.ndarray:
    labels = np.full(len(selected["role"]), "none", dtype="<U32")
    sr = selected["is_signal_region"].astype(bool)
    if btag_cut is not None:
        sr = sr & (np.nan_to_num(selected["btag_max"].astype(float), nan=-1.0) <= btag_cut)
    njet = selected["n_clean_jets"]
    mjj = np.nan_to_num(selected["mjj"].astype(float), nan=-1.0)
    detajj = np.nan_to_num(selected["delta_eta_jj"].astype(float), nan=-1.0)
    pttt = np.nan_to_num(selected["pt_tautau_proxy"].astype(float), nan=-1.0)
    tau_pt = np.nan_to_num(selected["tau_pt"].astype(float), nan=-1.0)
    vbf = sr & (njet >= 2) & (mjj > mjj_cut) & (detajj > detajj_cut)
    non_vbf = sr & ~vbf
    boosted_high = non_vbf & (njet >= 1) & (pttt > pttt_cut)
    boosted_low = non_vbf & (njet >= 1) & ~boosted_high
    if tau_cut is not None:
        zero_high = non_vbf & (njet == 0) & (tau_pt > tau_cut)
        zero_low = non_vbf & (njet == 0) & ~zero_high
        labels[zero_high] = "zero_tau_high"
        labels[zero_low] = "zero_low"
    else:
        labels[non_vbf & (njet == 0)] = "zero_jet"
    labels[vbf] = "vbf"
    labels[boosted_high] = "boosted_high"
    labels[boosted_low] = "boosted_low"
    return labels


def categories_from_labels(labels: np.ndarray) -> list[str]:
    categories = [str(value) for value in np.unique(labels) if str(value) != "none"]
    return sorted(categories)


def build_templates(
    selected: dict[str, np.ndarray],
    spec: ModelSpec,
    weights: dict[str, float],
) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    categories = spec.categories
    bins = spec.bins
    values = np.zeros((len(SAMPLES), len(categories), len(bins) - 1), dtype=float)
    variances = np.zeros_like(values)
    raw = np.zeros_like(values, dtype=int)
    per_sample: dict[str, Any] = {}
    for isample, sample in enumerate(SAMPLES):
        per_sample[sample] = {"categories": {}, "weight": weights[sample]}
        for icat, category in enumerate(categories):
            mask = (spec.category_labels == category) & (selected["sample"] == sample)
            counts, yld, var = weighted_hist(selected[spec.observable][mask].astype(float), weights[sample], bins)
            raw[isample, icat, :] = counts
            values[isample, icat, :] = yld
            variances[isample, icat, :] = var
            per_sample[sample]["categories"][category] = {
                "bin_edges": bins.tolist(),
                "raw_counts": counts.tolist(),
                "weighted_yields": yld.tolist(),
                "sumw2": var.tolist(),
                "total_yield": float(np.sum(yld)),
                "raw_total": int(np.sum(counts)),
            }
    totals: dict[str, Any] = {}
    sig_idx = [SAMPLES.index(sample) for sample in SIGNALS]
    bkg_idx = [SAMPLES.index(sample) for sample in BACKGROUNDS]
    low_background_bins = 0
    populated_bins = 0
    min_background_bins = []
    for icat, category in enumerate(categories):
        sig = np.sum(values[sig_idx, icat, :], axis=0)
        bkg = np.sum(values[bkg_idx, icat, :], axis=0)
        active = (sig + bkg) > 0
        low_background_bins += int(np.sum(active & (bkg < 5.0)))
        populated_bins += int(np.sum(active))
        if np.any(active):
            min_background_bins.append(float(np.min(bkg[active])))
        totals[category] = {
            "bin_edges": bins.tolist(),
            "signal_bins": sig.tolist(),
            "background_bins": bkg.tolist(),
            "signal_total": float(np.sum(sig)),
            "background_total": float(np.sum(bkg)),
            "s_over_b": float(np.sum(sig) / np.sum(bkg)) if np.sum(bkg) > 0 else None,
            "s_over_sqrt_b": float(np.sum(sig) / np.sqrt(np.sum(bkg))) if np.sum(bkg) > 0 else None,
            "best_bin_s_over_b": float(np.max(np.divide(sig, bkg, out=np.zeros_like(sig), where=bkg > 0))) if np.sum(bkg > 0) else 0.0,
            "min_background_bin": float(np.min(bkg[active])) if np.any(active) else 0.0,
        }
    signal_total = float(np.sum(values[sig_idx, :, :]))
    background_total = float(np.sum(values[bkg_idx, :, :]))
    summary = {
        "name": spec.name,
        "family": spec.family,
        "description": spec.description,
        "caveat": spec.caveat,
        "observable": spec.observable,
        "bin_edges": bins.tolist(),
        "categories": categories,
        "model_name": spec.model_name,
        "selection_role": spec.selection_role,
        "sparse_bin_handling": getattr(spec, "sparse_bin_handling", None),
        "samples": per_sample,
        "totals": totals,
        "combined": {
            "signal_total": signal_total,
            "background_total": background_total,
            "s_over_b": signal_total / background_total if background_total > 0 else None,
            "s_over_sqrt_b": signal_total / np.sqrt(background_total) if background_total > 0 else None,
            "low_background_bins_lt5": low_background_bins,
            "populated_bins": populated_bins,
            "low_background_fraction": low_background_bins / populated_bins if populated_bins else None,
            "min_background_bin": min(min_background_bins) if min_background_bins else 0.0,
        },
    }
    return summary, values, variances


def stat_errors(values: np.ndarray, variances: np.ndarray, isample: int, icat: int) -> list[float]:
    errs = np.sqrt(np.maximum(variances[isample, icat, :], 0.0))
    vals = values[isample, icat, :]
    return [float(err) if val > 0 else 0.0 for err, val in zip(errs, vals, strict=True)]


def sample_modifiers(
    sample: str,
    category: str,
    values: np.ndarray,
    variances: np.ndarray,
    isample: int,
    icat: int,
    nuisance_mode: str,
) -> list[dict[str, Any]]:
    modifiers: list[dict[str, Any]] = []
    if sample in SIGNALS:
        modifiers.append({"name": "mu", "type": "normfactor", "data": None})
    if nuisance_mode not in {"no_normsys", "no_nuisance"}:
        tau_hi, tau_lo = (1.15, 0.85)
        dy_hi, dy_lo = (1.15, 0.85)
        if nuisance_mode == "low_nuisance_diagnostic":
            tau_hi, tau_lo = (1.05, 0.95)
            dy_hi, dy_lo = (1.05, 0.95)
        modifiers.extend(
            [
                {"name": "lumi_2012", "type": "normsys", "data": {"hi": 1.026, "lo": 0.974}},
                {"name": "tau_open_data_acceptance", "type": "normsys", "data": {"hi": tau_hi, "lo": tau_lo}},
            ]
        )
        if sample == "DYJetsToLL":
            modifiers.append({"name": "dy_norm_open_data", "type": "normsys", "data": {"hi": dy_hi, "lo": dy_lo}})
    if nuisance_mode not in {"no_staterror", "no_nuisance"}:
        modifiers.append(
            {
                "name": f"mc_stat_{sanitize_category(category)}",
                "type": "staterror",
                "data": stat_errors(values, variances, isample, icat),
            }
        )
    return modifiers


def build_workspace(
    categories: list[str],
    values: np.ndarray,
    variances: np.ndarray,
    nuisance_mode: str = "nominal",
) -> dict[str, Any]:
    channels = []
    observations = []
    bkg_idx = [SAMPLES.index(sample) for sample in BACKGROUNDS]
    for icat, category in enumerate(categories):
        samples = []
        for isample, sample in enumerate(SAMPLES):
            samples.append(
                {
                    "name": sample,
                    "data": values[isample, icat, :].tolist(),
                    "modifiers": sample_modifiers(sample, category, values, variances, isample, icat, nuisance_mode),
                }
            )
        background = np.sum(values[bkg_idx, icat, :], axis=0)
        channels.append({"name": sanitize_category(category), "samples": samples})
        observations.append({"name": sanitize_category(category), "data": background.tolist()})
    return {
        "channels": channels,
        "measurements": [
            {
                "name": "phase3_sensitivity_regression",
                "config": {
                    "poi": "mu",
                    "parameters": [{"name": "mu", "inits": [1.0], "bounds": [[0.0, 50.0]]}],
                },
            }
        ],
        "observations": observations,
        "version": "1.0.0",
    }


def model_data_for_mu(model: pyhf.pdf.Model, mu: float) -> list[float]:
    pars = model.config.suggested_init()
    pars[model.config.poi_index] = mu
    return pyhf.tensorlib.tolist(model.expected_data(pars, include_auxdata=True))


def fit_mu(model: pyhf.pdf.Model, data: list[float]) -> float:
    pars = pyhf.infer.mle.fit(
        data,
        model,
        init_pars=model.config.suggested_init(),
        par_bounds=model.config.suggested_bounds(),
        fixed_params=model.config.suggested_fixed(),
    )
    pars_list = [float(x) for x in pyhf.tensorlib.tolist(pars)]
    return float(pars_list[model.config.poi_index])


def expected_limit(model: pyhf.pdf.Model, bkg_asimov: list[float]) -> dict[str, Any]:
    from pyhf.infer.intervals import upper_limits

    scan = np.linspace(0.0, 50.0, 51)
    obs_limit, exp_limits, _ = upper_limits.upper_limit(
        bkg_asimov,
        model,
        scan=scan,
        level=0.05,
        return_results=True,
    )
    return {
        "observed_on_background_asimov": float(obs_limit),
        "expected_band_minus2_minus1_median_plus1_plus2": [float(x) for x in exp_limits],
        "scan_min": float(scan[0]),
        "scan_max": float(scan[-1]),
        "scan_points": len(scan),
    }


def discovery_z(model: pyhf.pdf.Model) -> dict[str, Any]:
    splusb = model_data_for_mu(model, 1.0)
    try:
        p_value = pyhf.infer.hypotest(0.0, splusb, model, calctype="asymptotics", test_stat="q0")
        p_float = float(pyhf.tensorlib.tolist(p_value))
        return {"status": "evaluated", "p_value": p_float, "z_value": float(norm.isf(p_float)) if p_float > 0 else float("inf")}
    except Exception as exc:  # noqa: BLE001
        return {"status": "failed", "reason": str(exc), "z_value": None}


def signal_injection(model: pyhf.pdf.Model) -> dict[str, Any]:
    rows = []
    for injected in [0.0, 1.0, 2.0, 5.0]:
        data = model_data_for_mu(model, injected)
        fitted = fit_mu(model, data)
        bias = fitted - injected
        rel_bias = 0.0 if injected == 0.0 else bias / injected
        rows.append(
            {
                "injected_mu": injected,
                "fitted_mu": float(fitted),
                "absolute_bias": float(bias),
                "relative_bias": float(rel_bias),
                "passes_20_percent_gate": bool(abs(rel_bias) <= 0.20 if injected > 0 else abs(bias) <= 1e-3),
            }
        )
    return {"rows": rows, "all_pass": all(row["passes_20_percent_gate"] for row in rows)}


def evaluate_spec(
    selected: dict[str, np.ndarray],
    spec: ModelSpec,
    weights: dict[str, float],
    nuisance_mode: str,
    include_limit: bool,
    include_injection: bool,
) -> dict[str, Any]:
    templates, values, variances = build_templates(selected, spec, weights)
    try:
        workspace = build_workspace(spec.categories, values, variances, nuisance_mode=nuisance_mode)
        model = pyhf.Workspace(workspace).model()
        bkg_asimov = model_data_for_mu(model, 0.0)
        z_payload = discovery_z(model)
        result: dict[str, Any] = {
            "spec": {
                "name": spec.name,
                "family": spec.family,
                "observable": spec.observable,
                "categories": spec.categories,
                "bin_edges": spec.bins.tolist(),
                "description": spec.description,
                "caveat": spec.caveat,
                "model_name": spec.model_name,
                "selection_role": spec.selection_role,
                "sparse_bin_handling": spec.sparse_bin_handling,
            },
            "nuisance_mode": nuisance_mode,
            "templates": templates,
            "discovery_sensitivity": z_payload,
            "pyhf": {"npars": model.config.npars, "nchannels": len(spec.categories)},
        }
        if include_limit:
            result["expected_upper_limit"] = expected_limit(model, bkg_asimov)
        if include_injection:
            result["signal_injection"] = signal_injection(model)
        return result
    except Exception as exc:  # noqa: BLE001
        return {
            "spec": {
                "name": spec.name,
                "family": spec.family,
                "observable": spec.observable,
                "categories": spec.categories,
                "bin_edges": spec.bins.tolist(),
                "description": spec.description,
                "caveat": spec.caveat,
                "model_name": spec.model_name,
                "selection_role": spec.selection_role,
                "sparse_bin_handling": spec.sparse_bin_handling,
            },
            "nuisance_mode": nuisance_mode,
            "templates": templates,
            "status": "failed",
            "reason": str(exc),
        }


def train_mva_models(selected: dict[str, np.ndarray]) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    sr_mc = (
        selected["is_signal_region"].astype(bool)
        & np.isin(selected["role"], ["signal", "background"])
        & np.isin(selected["sample"], SAMPLES)
    )
    x = np.column_stack(
        [
            np.nan_to_num(selected[name][sr_mc].astype(float), nan=-999.0, posinf=999.0, neginf=-999.0)
            for name in MVA_INPUTS
        ]
    )
    y = (selected["role"][sr_mc] == "signal").astype(int)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.35, random_state=31415, stratify=y)
    models: dict[str, Any] = {
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            max_iter=180,
            learning_rate=0.045,
            max_leaf_nodes=17,
            l2_regularization=0.05,
            random_state=2718,
        ),
        "mlp": make_pipeline(
            StandardScaler(),
            MLPClassifier(
                hidden_layer_sizes=(48, 24),
                activation="relu",
                alpha=2e-3,
                max_iter=500,
                early_stopping=True,
                random_state=1618,
            ),
        ),
    }
    if XGBClassifier is not None:
        models["xgboost"] = XGBClassifier(
            n_estimators=160,
            max_depth=3,
            learning_rate=0.045,
            subsample=0.85,
            colsample_bytree=0.85,
            min_child_weight=2.0,
            reg_lambda=2.0,
            objective="binary:logistic",
            eval_metric="logloss",
            n_jobs=2,
            random_state=57721,
        )
    full_x = np.column_stack(
        [
            np.nan_to_num(selected[name].astype(float), nan=-999.0, posinf=999.0, neginf=-999.0)
            for name in MVA_INPUTS
        ]
    )
    scores: dict[str, np.ndarray] = {}
    metadata: dict[str, Any] = {
        "status": "trained_expected_only_mc",
        "blinding": "Trained only on signal/background MC in signal-region selected events; no observed data SR distribution used.",
        "inputs": MVA_INPUTS,
        "split": {"test_size": 0.35, "random_state": 31415, "stratified": True},
        "class_counts": {"background": int(np.sum(y == 0)), "signal": int(np.sum(y == 1))},
        "models": {},
        "transformer_feasibility": transformer_feasibility(),
        "genmet_regression_feasibility": genmet_regression_feasibility(selected),
        "tau_antimuon_veto": tau_antimuon_status(),
    }
    for name, model in models.items():
        log.info("Training expected-only %s", name)
        model.fit(x_train, y_train)
        train_score = model.predict_proba(x_train)[:, 1]
        test_score = model.predict_proba(x_test)[:, 1]
        full_score = model.predict_proba(full_x)[:, 1]
        scores[name] = full_score.astype(float)
        train_auc = float(roc_auc_score(y_train, train_score))
        test_auc = float(roc_auc_score(y_test, test_score))
        metadata["models"][name] = {
            "type": type(model).__name__,
            "train_auc": train_auc,
            "test_auc": test_auc,
            "overtraining_gap_train_minus_test": float(train_auc - test_auc),
            "n_train": int(len(y_train)),
            "n_test": int(len(y_test)),
        }
    return metadata, scores


def baseline_specs(selected: dict[str, np.ndarray], scores: dict[str, np.ndarray], weights: dict[str, float]) -> list[ModelSpec]:
    baseline = assign_baseline(selected)
    specs = [
        ModelSpec(
            name="baseline_phase4a_mvis",
            family="baseline_reproduction",
            category_labels=baseline,
            categories=BASELINE_CATEGORIES,
            observable="m_vis",
            bins=BASELINE_BINS,
            description="Phase 4a visible-mass baseline with VBF, boosted, and zero-jet categories.",
        ),
        ModelSpec(
            name="baseline_addmet",
            family="observable_binning_audit",
            category_labels=baseline,
            categories=BASELINE_CATEGORIES,
            observable="m_addmet",
            bins=ADDMET_BINS,
            description="Add-MET mass with baseline categories and coarse expected-model bins.",
        ),
        ModelSpec(
            name="baseline_pt_tautau_proxy",
            family="observable_binning_audit",
            category_labels=baseline,
            categories=BASELINE_CATEGORIES,
            observable="pt_tautau_proxy",
            bins=PT_TAUTAU_BINS,
            description="Visible-plus-MET pT proxy with baseline categories.",
        ),
    ]
    refined = assign_jhep_refined(selected)
    specs.append(
        ModelSpec(
            name="jhep_refined_mvis",
            family="jhep_category_refinement",
            category_labels=refined,
            categories=categories_from_labels(refined),
            observable="m_vis",
            bins=BASELINE_BINS,
            description="Loose/tight VBF and boosted/tau-pT category refinement inspired by CMS Run 1 methods.",
            caveat="No central-jet veto branch is available in the reduced selected-event representation.",
        )
    )
    for name, score in scores.items():
        observable = f"mva_score_{name}"
        selected[observable] = score
        score_edges, score_sparse = merge_common_edges_for_background(
            selected,
            baseline,
            BASELINE_CATEGORIES,
            observable,
            MVA_SCORE_BINS,
            weights,
        )
        specs.append(
            ModelSpec(
                name=f"mva_{name}_score_baseline_categories",
                family="expected_only_mva",
                category_labels=baseline,
                categories=BASELINE_CATEGORIES,
                observable=observable,
                bins=score_edges,
                description=f"{name} classifier score templates with baseline categories.",
                caveat="Expected-only MC gain; severe input modelling caveats require Phase 4b validation before unqualified promotion.",
                model_name=name,
                selection_role="primary_candidate",
                sparse_bin_handling=score_sparse,
            )
        )
        inclusive_labels = np.where(selected["is_signal_region"].astype(bool), "inclusive_sr", "none")
        inclusive_edges, inclusive_sparse = merge_common_edges_for_background(
            selected,
            inclusive_labels,
            ["inclusive_sr"],
            observable,
            MVA_COARSE_BINS,
            weights,
        )
        specs.append(
            ModelSpec(
                name=f"mva_{name}_score_single_category",
                family="expected_only_mva",
                category_labels=inclusive_labels,
                categories=["inclusive_sr"],
                observable=observable,
                bins=inclusive_edges,
                description=f"{name} classifier score templates in a single inclusive signal-region channel.",
                caveat=(
                    "Expected-only MC comparison retained for continuity. The user-requested primary method "
                    "must preserve event categories and is therefore not selected from this inclusive candidate."
                ),
                model_name=name,
                selection_role="comparison_only_not_selected",
                sparse_bin_handling=inclusive_sparse,
            )
        )
    return specs


def grid_specs(selected: dict[str, np.ndarray]) -> list[ModelSpec]:
    specs: list[ModelSpec] = []
    for mjj_cut in [300.0, 400.0, 500.0, 650.0]:
        for detajj_cut in [2.5, 3.0, 3.5, 4.0]:
            for pttt_cut in [50.0, 75.0, 100.0, 125.0]:
                labels = assign_grid(selected, mjj_cut, detajj_cut, pttt_cut)
                specs.append(
                    ModelSpec(
                        name=f"grid_mjj{mjj_cut:.0f}_deta{detajj_cut:.1f}_pt{pttt_cut:.0f}",
                        family="jhep_category_grid",
                        category_labels=labels,
                        categories=categories_from_labels(labels),
                        observable="m_vis",
                        bins=BASELINE_BINS,
                        description=(
                            f"VBF mjj>{mjj_cut:.0f}, |deta|>{detajj_cut:.1f}; "
                            f"boosted high pT proxy>{pttt_cut:.0f}."
                        ),
                    )
                )
    for btag_cut in [0.0, 0.25, 0.5]:
        labels = assign_grid(selected, 300.0, 2.5, 75.0, tau_cut=45.0, btag_cut=btag_cut)
        specs.append(
            ModelSpec(
                name=f"btag_veto_le{btag_cut:.2f}_split",
                family="btag_top_handling",
                category_labels=labels,
                categories=categories_from_labels(labels),
                observable="m_vis",
                bins=BASELINE_BINS,
                description=f"Exploratory top suppression requiring max valid btag <= {btag_cut:.2f}.",
                caveat="Reduced Jet_btag branch has no calibrated working point in the current artifact.",
            )
        )
    for tau_cut in [35.0, 45.0, 55.0]:
        labels = assign_grid(selected, 300.0, 2.5, 75.0, tau_cut=tau_cut)
        specs.append(
            ModelSpec(
                name=f"taupt_split_{tau_cut:.0f}",
                family="boosted_tau_split",
                category_labels=labels,
                categories=categories_from_labels(labels),
                observable="m_vis",
                bins=BASELINE_BINS,
                description=f"Baseline VBF with boosted pT proxy split and zero-jet tau pT>{tau_cut:.0f} split.",
            )
        )
    return specs


def rank_key(result: dict[str, Any]) -> float:
    z_payload = result.get("discovery_sensitivity", {})
    value = z_payload.get("z_value")
    return float(value) if value is not None and np.isfinite(value) else -1.0


def is_primary_eligible(result: dict[str, Any]) -> bool:
    spec = result.get("spec", {})
    categories = spec.get("categories", [])
    return (
        spec.get("selection_role") != "comparison_only_not_selected"
        and "vbf" in categories
        and len(categories) >= 3
        and rank_key(result) >= 0.0
    )


def evaluate_all(
    selected: dict[str, np.ndarray],
    specs: list[ModelSpec],
    weights: dict[str, float],
    phase4a_baseline: dict[str, float],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for spec in specs:
        log.info("Evaluating nominal expected model %s", spec.name)
        result = evaluate_spec(selected, spec, weights, "nominal", include_limit=False, include_injection=False)
        z_value = rank_key(result)
        result["comparison_to_phase4a"] = {
            "baseline_z": phase4a_baseline["expected_z"],
            "z_improvement_factor": z_value / phase4a_baseline["expected_z"] if z_value >= 0 and phase4a_baseline["expected_z"] > 0 else None,
        }
        results.append(result)
    eligible = [result for result in results if is_primary_eligible(result)]
    provisional_best = max(eligible if eligible else results, key=rank_key)
    enrich_names = {"baseline_phase4a_mvis", provisional_best["spec"]["name"]}
    enriched_results: list[dict[str, Any]] = []
    for result in results:
        if result["spec"]["name"] in enrich_names:
            spec = next(item for item in specs if item.name == result["spec"]["name"])
            include_limit = spec.name == "baseline_phase4a_mvis" or len(spec.categories) <= 4
            log.info("Adding injection%s for %s", " and limit" if include_limit else "", spec.name)
            enriched = evaluate_spec(selected, spec, weights, "nominal", include_limit=include_limit, include_injection=True)
            z_value = rank_key(enriched)
            limit = enriched.get("expected_upper_limit", {})
            median_limit = None
            if "expected_band_minus2_minus1_median_plus1_plus2" in limit:
                median_limit = limit["expected_band_minus2_minus1_median_plus1_plus2"][2]
            enriched["comparison_to_phase4a"] = {
                "baseline_z": phase4a_baseline["expected_z"],
                "z_improvement_factor": z_value / phase4a_baseline["expected_z"] if phase4a_baseline["expected_z"] > 0 else None,
                "baseline_median_limit": phase4a_baseline["median_limit"],
                "median_limit_improvement_factor": phase4a_baseline["median_limit"] / median_limit if median_limit else None,
                "limit_evaluation": "evaluated" if include_limit else "deferred_high_category_runtime",
            }
            enriched_results.append(enriched)
        else:
            enriched_results.append(result)
    enriched_eligible = [result for result in enriched_results if is_primary_eligible(result)]
    best = max(enriched_eligible if enriched_eligible else enriched_results, key=rank_key)
    return enriched_results, best


def nuisance_audit(selected: dict[str, np.ndarray], specs: list[ModelSpec], best: dict[str, Any], weights: dict[str, float]) -> dict[str, Any]:
    chosen_names = ["baseline_phase4a_mvis", best["spec"]["name"]]
    rows = []
    for name in dict.fromkeys(chosen_names):
        spec = next(item for item in specs if item.name == name)
        mode_rows = []
        for mode in ["nominal", "no_staterror", "no_normsys", "no_nuisance", "low_nuisance_diagnostic"]:
            result = evaluate_spec(selected, spec, weights, mode, include_limit=False, include_injection=False)
            mode_rows.append(
                {
                    "nuisance_mode": mode,
                    "z_value": result.get("discovery_sensitivity", {}).get("z_value"),
                    "low_background_bins_lt5": result.get("templates", {}).get("combined", {}).get("low_background_bins_lt5"),
                }
            )
        rows.append({"model": name, "modes": mode_rows})
    return {
        "interpretation": (
            "No/low-nuisance configurations are diagnostics only. They quantify how much the Phase 4a nuisance "
            "implementation suppresses sensitivity but are not a final result without independent uncertainty justification."
        ),
        "rows": rows,
    }


def missing_component_feasibility() -> dict[str, Any]:
    manifest_path = ROOT / "phase2_exploration" / "outputs" / "local_sample_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    available_files = sorted([path.name for path in (ROOT / "mc").glob("*.root")])
    targets = {
        "QCD_multijet": ["QCD", "qcd"],
        "diboson_WW_WZ_ZZ": ["WW", "WZ", "ZZ", "Diboson", "diboson"],
        "single_top": ["SingleTop", "SingleT", "ST_", "T_t-channel", "T_s-channel", "T_tW-channel"],
        "W4_or_inclusive_W": ["W4Jets", "WJetsToLNu", "WJets"],
        "associated_H": ["WH", "ZH", "ttH"],
        "H_to_WW": ["HToWW", "HToWW2L2Nu"],
        "extra_DY_categories": ["DY1Jets", "DY2Jets", "DY3Jets", "DY4Jets"],
        "embedded_Ztautau": ["Embedded", "embedding"],
    }
    rows = []
    manifest_text = json.dumps(manifest)
    for component, patterns in targets.items():
        file_matches = [name for name in available_files if any(pattern in name for pattern in patterns)]
        manifest_mentions = [pattern for pattern in patterns if pattern in manifest_text]
        feasible_now = bool(file_matches)
        rows.append(
            {
                "component": component,
                "feasible_in_current_reduced_file_set": feasible_now,
                "local_file_matches": file_matches,
                "manifest_pattern_mentions": manifest_mentions,
                "decision": "available_for_future_modeling" if feasible_now else "unavailable_do_not_approximate",
            }
        )
    return {
        "available_mc_root_files": available_files,
        "manifest_path": str(manifest_path.relative_to(ROOT)),
        "rows": rows,
        "policy": "Unavailable components are carried as limitations; no paper-level yields or fabricated pseudo-events are introduced.",
    }


def save_figure(fig: plt.Figure, name: str) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Wrote %s", FIG / f"{name}.pdf")


def label(ax: plt.Axes, llabel: str = "Open Simulation") -> None:
    mh.label.exp_label(exp="CMS", text="", loc=0, data=True, llabel=llabel, rlabel=r"$8$ TeV", ax=ax)


def plot_variant_summary(results: list[dict[str, Any]]) -> None:
    valid = [row for row in results if rank_key(row) >= 0]
    top = sorted(valid, key=rank_key, reverse=True)[:10]
    names = [spec_display_label(row["spec"]["name"]) for row in top]
    values = [rank_key(row) for row in top]
    y = np.arange(len(top))
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.errorbar(values, y, xerr=np.zeros(len(values)), marker="o", linestyle="", color="tab:blue", label="Variant")
    ax.axvline(0.1906097504953417, color="tab:red", linestyle="--", label="Phase 4a baseline")
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_xlabel("Asimov discovery Z")
    ax.set_ylabel("Expected-only variant")
    ax.legend(fontsize="x-small", loc="lower right")
    xmin, xmax = ax.get_xlim()
    if xmax > xmin:
        ax.set_xlim(xmin, xmax * 1.10)
    label(ax)
    save_figure(fig, "sensitivity_variant_summary")


def plot_nuisance_audit(payload: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(10, 10))
    modes = ["nominal", "no_staterror", "no_normsys", "no_nuisance", "low_nuisance_diagnostic"]
    x = np.arange(len(modes), dtype=float)
    for imodel, row in enumerate(payload["rows"]):
        values_by_mode = {item["nuisance_mode"]: item["z_value"] for item in row["modes"]}
        offset = (imodel - 0.5) * 0.16
        values = [values_by_mode.get(mode, 0.0) for mode in modes]
        ax.errorbar(
            x + offset,
            values,
            yerr=np.zeros(len(values)),
            marker="o",
            linestyle="",
            label=spec_display_label(row["model"]),
        )
    ax.set_xticks(x)
    ax.set_xticklabels([NUISANCE_DISPLAY_LABELS[mode] for mode in modes], rotation=30, ha="right")
    ax.set_xlabel("Nuisance diagnostic mode")
    ax.set_ylabel("Asimov discovery Z")
    ax.legend(fontsize="x-small", loc="upper right")
    ymin, ymax = ax.get_ylim()
    if ymax > ymin:
        ax.set_ylim(ymin, ymax * 1.25)
    label(ax)
    save_figure(fig, "sensitivity_nuisance_audit")


def plot_mva_scores(selected: dict[str, np.ndarray], scores: dict[str, np.ndarray], weights: dict[str, float]) -> None:
    fig, ax = plt.subplots(figsize=(10, 10))
    bins = np.linspace(0.0, 1.0, 31)
    score = scores.get("hist_gradient_boosting")
    if score is None:
        return
    for role, color in [("signal", "tab:green"), ("background", "tab:blue")]:
        mask = (
            selected["is_signal_region"].astype(bool)
            & (selected["role"] == role)
            & np.isin(selected["sample"], SAMPLES)
        )
        hist_values = np.zeros(len(bins) - 1, dtype=float)
        hist_vars = np.zeros(len(bins) - 1, dtype=float)
        for sample in SAMPLES:
            sample_mask = mask & (selected["sample"] == sample)
            counts, _ = np.histogram(score[sample_mask], bins=bins)
            hist_values += counts * weights[sample]
            hist_vars += counts * weights[sample] * weights[sample]
        centers = 0.5 * (bins[:-1] + bins[1:])
        widths = np.diff(bins)
        ax.errorbar(
            centers,
            hist_values,
            yerr=np.sqrt(hist_vars),
            xerr=0.5 * widths,
            linestyle="",
            marker="o",
            label=role.title(),
            color=color,
        )
    ax.set_xlabel("Gradient-boosted classifier score")
    ax.set_ylabel("Expected events")
    ax.set_yscale("log")
    ymin, ymax = ax.get_ylim()
    if ymax > ymin:
        ax.set_ylim(max(ymin, 1e-3), ymax * 3.0)
    ax.legend(fontsize="x-small", loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0.0)
    label(ax)
    save_figure(fig, "mva_score_templates")


def compact_result(row: dict[str, Any]) -> dict[str, Any]:
    limit = row.get("expected_upper_limit", {})
    median_limit = None
    if "expected_band_minus2_minus1_median_plus1_plus2" in limit:
        median_limit = limit["expected_band_minus2_minus1_median_plus1_plus2"][2]
    return {
        "name": row["spec"]["name"],
        "family": row["spec"]["family"],
        "observable": row["spec"]["observable"],
        "categories": row["spec"]["categories"],
        "bin_edges": row["spec"]["bin_edges"],
        "model_name": row["spec"].get("model_name"),
        "selection_role": row["spec"].get("selection_role"),
        "sparse_bin_handling": row["spec"].get("sparse_bin_handling"),
        "z_value": row.get("discovery_sensitivity", {}).get("z_value"),
        "median_limit": median_limit,
        "signal_total": row.get("templates", {}).get("combined", {}).get("signal_total"),
        "background_total": row.get("templates", {}).get("combined", {}).get("background_total"),
        "s_over_b": row.get("templates", {}).get("combined", {}).get("s_over_b"),
        "s_over_sqrt_b": row.get("templates", {}).get("combined", {}).get("s_over_sqrt_b"),
        "low_background_bins_lt5": row.get("templates", {}).get("combined", {}).get("low_background_bins_lt5"),
        "low_background_fraction": row.get("templates", {}).get("combined", {}).get("low_background_fraction"),
        "z_improvement_factor": row.get("comparison_to_phase4a", {}).get("z_improvement_factor"),
        "median_limit_improvement_factor": row.get("comparison_to_phase4a", {}).get("median_limit_improvement_factor"),
        "caveat": row["spec"].get("caveat"),
    }


def write_selection_regression_section(best: dict[str, Any], phase4a_baseline: dict[str, float]) -> None:
    path = OUT / "SELECTION.md"
    text = path.read_text()
    marker = "\n## Sensitivity Regression Remediation\n"
    if marker in text:
        text = text.split(marker)[0].rstrip() + "\n"
    best_summary = compact_result(best)
    section = f"""
## Sensitivity Regression Remediation

A Phase 3 sensitivity regression pass was added after the Phase 4a expected
model returned `Z = {phase4a_baseline['expected_z']:.3f}` and a median expected
limit of `mu = {phase4a_baseline['median_limit']:.3f}`. The remediation uses
only MC and Asimov expectations for selection, category, binning, and
classifier choices. It does not tune on observed full-data signal-region
discriminant distributions.

The scan covers JHEP-inspired loose/tight VBF and boosted/tau-pT splits,
top/b-veto exploratory handling, `m_vis`, `m_addmet`, `pt_tautau_proxy`, and
two expected-only classifiers. Machine-readable results are written to
`sensitivity_scan.json`, `mva_sensitivity.json`,
`sensitivity_recommendation.json`, `sensitivity_selected_events.npz`, and
`missing_component_feasibility.json`.

![Expected-only sensitivity variant summary. This figure ranks the strongest
selection, category, observable, and classifier variants by Asimov discovery
sensitivity using only simulated signal and background templates. The dashed
reference line is the Phase 4a visible-mass baseline, so the comparison is an
optimization diagnostic and not an observed-data result.](figures/sensitivity_variant_summary.pdf){{#fig:p3-sensitivity-variant-summary}}

![Gradient-boosted classifier score templates. The figure shows the expected
signal and background score distributions in the signal region after applying
the official Open Data normalization inputs. The classifier was trained only on
MC, and Phase 4b must validate the score modelling before this expected-only
gain can be promoted as a primary result.](figures/mva_score_templates.pdf){{#fig:p3-mva-score-templates}}

![Sensitivity nuisance diagnostic. The figure compares the visible-mass
baseline and the strongest classifier-score candidate under nominal, reduced,
and removed nuisance-parameter configurations. These curves are diagnostic
stress tests of the expected model only; configurations with removed or
reduced nuisances are not final statistical results.](figures/sensitivity_nuisance_audit.pdf){{#fig:p3-sensitivity-nuisance-audit}}

The best expected-only variant is the {spec_display_label(best_summary['name'])} with Asimov
discovery `Z = {best_summary['z_value']:.3f}`. Its median expected CLs limit is
`{best_summary['median_limit']:.3f}` where evaluated. Relative to the Phase 4a
baseline this is a `Z` improvement factor of
`{best_summary['z_improvement_factor']:.2f}`. The expected signal and
background totals are `{best_summary['signal_total']:.3f}` and
`{best_summary['background_total']:.3f}`, with integrated `S/B =
{best_summary['s_over_b']:.4f}` and `S/sqrt(B) =
{best_summary['s_over_sqrt_b']:.3f}`.

The MVA improvement remains gated. The classifier is trained only on MC, but
Phase 3 already found severe data/background-MC input-shape disagreements for
most candidate variables. Therefore a classifier score can be carried to
Phase 4a as an expected-only candidate, but Phase 4b must validate score
modelling in control/validation regions or assign an explicit calibration
uncertainty before using it as an unqualified primary result.

The missing-component feasibility check found no current reduced ROOT files
for QCD multijet, diboson, single top, W4/inclusive W, associated H, H to WW,
extra DY jet categories, or embedded Z to tau tau. These components remain
limitations and were not approximated with paper-level yields or fabricated
templates.

Phase 4a rerun instruction: update the expected-model executor to read
`phase3_selection/outputs/sensitivity_recommendation.json` and
`phase3_selection/outputs/sensitivity_selected_events.npz`. Rebuild templates
using the recommended observable/category labels and the same official
normalization, then regenerate `expected_results.json`, `INFERENCE_EXPECTED.md`,
the analysis-note markdown, TeX, and PDF before restarting the full Phase 4a
review.
"""
    path.write_text(text.rstrip() + "\n" + section)
    log.info("Updated %s", path)


def main() -> None:
    pyhf.set_backend("numpy")
    FIG.mkdir(parents=True, exist_ok=True)
    SESSION_LOG.parent.mkdir(parents=True, exist_ok=True)
    append_markdown(SESSION_LOG, "Started expected-only sensitivity regression scan.")

    selected = load_selected()
    norm_payload = load_norm()
    weights = sample_weights(norm_payload)
    phase4a_baseline = load_phase4a_baseline()
    mva_metadata, mva_scores = train_mva_models(selected)
    for name, score in mva_scores.items():
        selected[f"mva_score_{name}"] = score

    specs = baseline_specs(selected, mva_scores, weights) + grid_specs(selected)
    results, best = evaluate_all(selected, specs, weights, phase4a_baseline)
    audit = nuisance_audit(selected, specs, best, weights)
    missing = missing_component_feasibility()

    compact = sorted([compact_result(row) for row in results], key=lambda row: row["z_value"] or -1.0, reverse=True)
    recommendation = {
        "blinding": {
            "expected_only": True,
            "observed_full_data_signal_region_used_for_optimization": False,
            "data_use": "Only existing control/validation caveats are referenced; no observed SR shape tuning.",
        },
        "phase4a_baseline": phase4a_baseline,
        "method_requirements": {
            "primary_must_preserve_event_categories": True,
            "required_categories": BASELINE_CATEGORIES,
            "simultaneous_fit": True,
            "inclusive_score_candidates_are_comparison_only": True,
        },
        "modern_model_feasibility": {
            "transformer_discriminator": transformer_feasibility(),
            "genmet_direction_regression": genmet_regression_feasibility(selected),
            "tau_antimuon_veto": tau_antimuon_status(),
        },
        "promotion_gate": {
            "z_or_limit_improvement_required": ">=30%",
            "signal_injection_required": "bias <20% for nonzero injected mu",
            "minimum_expected_background_per_bin": ">=5 or toy-validation/bin-merging required",
        },
        "best": compact_result(best),
        "best_full_result": best,
        "candidate_comparison_ranked": compact,
        "passes_30_percent_z_improvement": bool((compact_result(best)["z_improvement_factor"] or 0.0) >= 1.30),
        "residual_blockers": [
            "MVA input and output modelling must be validated in Phase 4b before unqualified use.",
            "No SVFIT mass, embedding, QCD estimate, or additional tau channels are available in this reduced pass.",
            "Low-background bins require bin merging or toy validation if a refined low-yield category is promoted.",
        ],
        "phase4a_rerun_instructions": [
            "Read sensitivity_recommendation.json and sensitivity_selected_events.npz.",
            "Use best.spec.observable and best.spec.categories/category labels for templates.",
            "Keep official L_int and N_gen weights from normalization_inputs.json.",
            "Recompute pyhf workspace, expected_results.json, signal injection, GoF, systematics, plots, AN markdown, TeX, and PDF.",
            "Restart Phase 4a 4-bot+bib review on the compiled PDF.",
        ],
    }
    scan_payload = {
        "phase": "phase3_sensitivity_regression",
        "baseline": phase4a_baseline,
        "model_count": len(results),
        "results_compact_ranked": compact,
        "results": results,
        "nuisance_audit": audit,
    }
    mva_payload = {
        **mva_metadata,
        "expected_sensitivity_results": [
            compact_result(row)
            for row in results
            if row["spec"]["family"] == "expected_only_mva"
        ],
        "modelling_caveat": (
            "Phase 3 variable_modeling.json found most MVA inputs failed data/background-MC shape gates. "
            "These MVA results quantify expected-only gain and define Phase 4b validation requirements."
        ),
    }
    write_json(OUT / "sensitivity_scan.json", scan_payload)
    write_json(OUT / "mva_sensitivity.json", mva_payload)
    write_json(OUT / "sensitivity_recommendation.json", recommendation)
    write_json(OUT / "missing_component_feasibility.json", missing)
    np.savez_compressed(
        OUT / "sensitivity_selected_events.npz",
        **selected,
        sensitivity_best_category=next(spec.category_labels for spec in specs if spec.name == best["spec"]["name"]),
    )
    log.info("Wrote %s", OUT / "sensitivity_selected_events.npz")

    plot_variant_summary(results)
    plot_mva_scores(selected, mva_scores, weights)
    plot_nuisance_audit(audit)
    write_selection_regression_section(best, phase4a_baseline)

    best_short = compact_result(best)
    append_markdown(
        SESSION_LOG,
        (
            f"Completed scan over {len(results)} expected-only variants. Best variant "
            f"`{best_short['name']}` reached Z={best_short['z_value']:.3f}, "
            f"median limit={best_short['median_limit']:.3f}."
        ),
    )
    experiment_message = (
        "Phase 3 sensitivity regression fixer ran expected-only category, observable, "
        f"MVA, nuisance, and missing-component scans. Best variant `{best_short['name']}` "
        f"reached Z={best_short['z_value']:.3f} versus Phase 4a baseline "
        f"Z={phase4a_baseline['expected_z']:.3f}; see "
        "`phase3_selection/outputs/sensitivity_recommendation.json`."
    )
    if "Phase 3 sensitivity regression fixer ran expected-only category" not in EXPERIMENT_LOG.read_text():
        append_markdown(EXPERIMENT_LOG, experiment_message)


if __name__ == "__main__":
    main()
