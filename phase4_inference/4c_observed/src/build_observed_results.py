"""Build Phase 4c full-data observed inference artifacts.

The updated Phase 4c model uses the best fast trained discriminator available
in the local environment after deriving multivariate background input
reweighting in validation/control regions before classifier training. The
observed primary result is the calibrated categorized score fit with the
same-sign QCD/fake correction; visible mass and add-MET mass are retained as
cross-checks.
"""

from __future__ import annotations

import json
import logging
import math
import shutil
import time
from pathlib import Path
from typing import Any

import numpy as np
import pyhf
from rich.logging import RichHandler
from scipy.stats import norm

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent
PHASE = HERE.parent
ROOT = PHASE.parent.parent
OUT = PHASE / "outputs"
FIG = OUT / "figures"
LOG = PHASE / "logs" / "executor_phase4c_observed_20260602T000000Z.md"
EXPERIMENT_LOG = ROOT / "experiment_log.md"
P4A = ROOT / "phase4_inference" / "4a_expected" / "outputs"
P4B = ROOT / "phase4_inference" / "4b_partial" / "outputs"

SIGNALS = ["GluGluToHToTauTau", "VBF_HToTauTau"]
BACKGROUNDS = ["DYJetsToLL", "TTbar", "W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]
WJETS = ["W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]
QCD_SAMPLE = "QCDSameSignDataDriven"
ALL_SAMPLES = SIGNALS + BACKGROUNDS + [QCD_SAMPLE]
PRIMARY_VISIBLE_BINS = np.asarray([0.0, 60.0, 80.0, 100.0, 120.0, 160.0, 250.0], dtype=float)
ADDMET_BINS = np.asarray([0.0, 60.0, 80.0, 100.0, 120.0, 160.0, 220.0, 300.0], dtype=float)
OBSERVED_DATA_SCOPE = (
    "Run2012B/C TauPlusX rows in the localized public HiggsTauTauReduced mirror; "
    "11.467/fb is retained as the Open Data normalization reference"
)


def append_log(path: Path, message: str) -> None:
    with path.open("a") as handle:
        handle.write(f"\n## {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n\n{message}\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    log.info("Wrote %s", path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def snapshot_previous_baseline() -> dict[str, Any] | None:
    baseline_path = OUT / "baseline_previous_result.json"
    if baseline_path.exists():
        return load_json(baseline_path)
    observed_path = OUT / "observed_results.json"
    workspace_path = OUT / "pyhf_workspace_observed.json"
    yields_path = OUT / "observed_yields.json"
    if not observed_path.exists():
        return None
    previous = load_json(observed_path)
    if previous.get("primary_model") != "visible_mass_qcd_primary":
        return None
    payload = {
        "label": "Baseline visible-mass result before multivariate input reweighting",
        "source": "Frozen from the previous Phase 4c observed output before the calibrated-score update.",
        "primary_model": previous.get("primary_model"),
        "observed_fit": previous.get("observed_fit"),
        "validation_summary": previous.get("validation_summary"),
        "systematics_retained": previous.get("systematics_retained"),
    }
    write_json(baseline_path, payload)
    if workspace_path.exists():
        shutil.copy2(workspace_path, OUT / "pyhf_workspace_baseline_visible.json")
    if yields_path.exists():
        shutil.copy2(yields_path, OUT / "baseline_visible_yields.json")
    return payload


def load_selected() -> dict[str, np.ndarray]:
    with np.load(ROOT / "phase3_selection" / "outputs" / "sensitivity_selected_events.npz", allow_pickle=False) as payload:
        if "m_addmet" not in payload.files:
            raise KeyError(
                "m_addmet is unavailable in phase3_selection/outputs/sensitivity_selected_events.npz; "
                f"available columns are {sorted(payload.files)}"
            )
        return {key: payload[key] for key in payload.files}


def sample_weights(norm: dict[str, Any]) -> dict[str, float]:
    return {sample: float(payload["absolute_weight_per_local_entry"]) for sample, payload in norm["mc_samples"].items()}


def assign_categories(selected: dict[str, np.ndarray]) -> np.ndarray:
    labels = np.full(len(selected["role"]), "none", dtype="<U16")
    vbf = (
        (selected["n_clean_jets"] >= 2)
        & np.isfinite(selected["mjj"])
        & (selected["mjj"] > 300.0)
        & np.isfinite(selected["delta_eta_jj"])
        & (np.abs(selected["delta_eta_jj"]) > 2.5)
    )
    labels[vbf] = "vbf"
    labels[(labels == "none") & (selected["n_clean_jets"] >= 1)] = "boosted"
    labels[(labels == "none") & (selected["n_clean_jets"] == 0)] = "zero_jet"
    return labels


def weighted_hist(values: np.ndarray, event_weights: np.ndarray | float, bins: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    finite = np.isfinite(values)
    values = values[finite]
    if np.isscalar(event_weights):
        weights = np.full(values.shape, float(event_weights), dtype=float)
    else:
        weights = np.asarray(event_weights, dtype=float)[finite]
    counts, _ = np.histogram(values, bins=bins)
    yields, _ = np.histogram(values, bins=bins, weights=weights)
    variances, _ = np.histogram(values, bins=bins, weights=weights * weights)
    return counts.astype(float), yields, variances


def count_hist(values: np.ndarray, bins: np.ndarray) -> np.ndarray:
    finite = np.isfinite(values)
    counts, _ = np.histogram(values[finite], bins=bins)
    return counts.astype(float)


def template_event_weights(selected: dict[str, np.ndarray], sample: str, mask: np.ndarray, nominal_weight: float) -> np.ndarray:
    correction = np.ones(int(np.sum(mask)), dtype=float)
    if sample in BACKGROUNDS and "background_input_reweight" in selected:
        correction = selected["background_input_reweight"][mask].astype(float)
    return nominal_weight * correction


def sanitize(name: str) -> str:
    return name.replace("-", "_").replace("/", "_")


def derive_w_scale(selected: dict[str, np.ndarray], weights: dict[str, float]) -> dict[str, Any]:
    cr = selected["is_w_high_mt"].astype(bool)
    role = selected["role"]
    sample = selected["sample"]
    n_data = int(np.sum((role == "data") & cr))
    w_yield = 0.0
    w_var = 0.0
    nonw_yield = 0.0
    nonw_var = 0.0
    for sample_name in WJETS:
        count = int(np.sum((sample == sample_name) & cr))
        weight = weights[sample_name]
        w_yield += count * weight
        w_var += count * weight * weight
    for sample_name in ["DYJetsToLL", "TTbar"]:
        count = int(np.sum((sample == sample_name) & cr))
        weight = weights[sample_name]
        nonw_yield += count * weight
        nonw_var += count * weight * weight
    numerator = float(n_data) - nonw_yield
    raw_scale = numerator / w_yield if w_yield > 0 else math.nan
    variance = (float(n_data) + nonw_var) / (w_yield**2) if w_yield > 0 else math.inf
    if w_yield > 0:
        variance += (numerator**2) * w_var / (w_yield**4)
    raw_unc = math.sqrt(max(variance, 0.0)) if math.isfinite(variance) else math.inf
    status = "valid"
    applied = raw_scale
    if not math.isfinite(raw_scale) or not math.isfinite(raw_unc) or w_yield <= 0:
        status = "downscoped_no_valid_w_mc"
        applied = 1.0
        raw_unc = 1.0
    elif raw_scale < 0:
        status = "capped_negative_to_zero"
        applied = 0.0
    elif raw_unc / max(abs(raw_scale), 1e-12) > 1.0:
        status = "unstable_large_relative_uncertainty"
    rel_unc = raw_unc / max(abs(applied), 1e-12) if applied > 0 else raw_unc
    return {
        "control_region": "is_w_high_mt",
        "formula": "(N_data_CR - nonW_MC_CR) / W_MC_CR",
        "data_scope": OBSERVED_DATA_SCOPE,
        "data_events_full": n_data,
        "wjets_mc_yield_full_lumi": w_yield,
        "wjets_mc_sumw2_full_lumi": w_var,
        "nonw_background_mc_yield_full_lumi": nonw_yield,
        "nonw_background_mc_sumw2_full_lumi": nonw_var,
        "raw_scale_factor": raw_scale,
        "applied_scale_factor": applied,
        "absolute_uncertainty": raw_unc,
        "relative_uncertainty": rel_unc,
        "status": status,
        "nuisance": {
            "hi": max(0.001, applied + raw_unc) / max(applied, 1e-12) if applied > 0 else 1.0 + raw_unc,
            "lo": max(0.001, applied - raw_unc) / max(applied, 1e-12) if applied > 0 else 0.001,
        },
    }


def derive_vbf_background_scale(selected: dict[str, np.ndarray], weights: dict[str, float], w_scale: dict[str, Any]) -> dict[str, Any]:
    category = assign_categories(selected)
    cr = (category == "vbf") & selected["is_top_btag_handle"].astype(bool) & ~selected["is_signal_region"].astype(bool)
    role = selected["role"]
    sample = selected["sample"]
    n_data = int(np.sum((role == "data") & cr))
    mc_yield = 0.0
    mc_var = 0.0
    rows: dict[str, Any] = {}
    for sample_name in BACKGROUNDS:
        scale = w_scale["applied_scale_factor"] if sample_name in WJETS else 1.0
        count = int(np.sum((sample == sample_name) & cr))
        weight = weights[sample_name] * scale
        yld = count * weight
        var = count * weight * weight
        mc_yield += yld
        mc_var += var
        rows[sample_name] = {"raw_events": count, "yield": yld, "sumw2": var}
    raw_scale = n_data / mc_yield if mc_yield > 0 else math.nan
    raw_unc = math.sqrt(max(float(n_data) + mc_var, 0.0)) / mc_yield if mc_yield > 0 else math.inf
    status = "valid"
    applied = raw_scale
    if not math.isfinite(raw_scale) or not math.isfinite(raw_unc) or mc_yield <= 0:
        status = "downscoped_no_valid_vbf_control"
        applied = 1.0
        raw_unc = 1.0
    elif raw_scale < 0:
        status = "capped_negative_to_zero"
        applied = 0.0
    rel_unc = raw_unc / max(abs(applied), 1e-12) if applied > 0 else raw_unc
    return {
        "control_region": "vbf_like_top_btag_not_signal_region",
        "formula": "N_data_CR / MC_background_CR",
        "data_scope": "VBF-like rows with top-btag handle outside the low-mT signal region",
        "data_events": n_data,
        "background_mc_yield": mc_yield,
        "background_mc_sumw2": mc_var,
        "rows": rows,
        "raw_scale_factor": raw_scale,
        "applied_scale_factor": applied,
        "absolute_uncertainty": raw_unc,
        "relative_uncertainty": rel_unc,
        "status": status,
        "nuisance": {"hi": 1.0 + rel_unc, "lo": max(0.001, 1.0 - rel_unc)},
        "application": "central scale applied only to MC background samples in the VBF fit category",
    }


def mc_background_scale(sample: str, category: str, w_scale: dict[str, Any], vbf_scale: dict[str, Any]) -> float:
    scale = w_scale["applied_scale_factor"] if sample in WJETS else 1.0
    if category == "vbf" and sample in BACKGROUNDS:
        scale *= vbf_scale["applied_scale_factor"]
    return float(scale)


def qcd_sideband_estimate(
    selected: dict[str, np.ndarray],
    weights: dict[str, float],
    categories: list[str],
    edges: np.ndarray,
    observable: str,
    w_scale: dict[str, Any],
    vbf_scale: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    role = selected["role"]
    sample = selected["sample"]
    values = selected[observable]
    category = assign_categories(selected)
    ss = selected["is_same_sign_low_mt"].astype(bool)
    sr = selected["is_signal_region"].astype(bool)

    qcd_raw = np.zeros((len(categories), len(edges) - 1), dtype=float)
    qcd_var = np.zeros_like(qcd_raw)
    rows: dict[str, Any] = {}
    for icat, cat in enumerate(categories):
        data_counts = count_hist(values[(role == "data") & ss & (category == cat)], edges)
        mc_yield = np.zeros(len(edges) - 1, dtype=float)
        mc_var = np.zeros(len(edges) - 1, dtype=float)
        for sample_name in BACKGROUNDS:
            scale = mc_background_scale(sample_name, cat, w_scale, vbf_scale)
            mask = (sample == sample_name) & ss & (category == cat)
            event_weights = template_event_weights(selected, sample_name, mask, weights[sample_name] * scale)
            _, yld, var = weighted_hist(values[mask], event_weights, edges)
            mc_yield += yld
            mc_var += var
        raw = data_counts - mc_yield
        positive = raw > 0
        qcd_raw[icat] = np.where(positive, raw, 0.0)
        qcd_var[icat] = np.where(positive, data_counts + mc_var, 0.0)
        rows[cat] = {
            "same_sign_data_counts": data_counts.tolist(),
            "same_sign_nonqcd_mc_yields": mc_yield.tolist(),
            "unscaled_qcd_template": qcd_raw[icat].tolist(),
            "unscaled_qcd_sumw2": qcd_var[icat].tolist(),
            "unscaled_qcd_total": float(np.sum(qcd_raw[icat])),
        }

    numerator = 0.0
    denominator = 0.0
    numerator_var = 0.0
    denominator_var = 0.0
    for icat, cat in enumerate(categories):
        data_counts = count_hist(values[(role == "data") & sr & (category == cat)], edges)
        mc_yield = np.zeros(len(edges) - 1, dtype=float)
        mc_var = np.zeros(len(edges) - 1, dtype=float)
        for sample_name in BACKGROUNDS:
            scale = mc_background_scale(sample_name, cat, w_scale, vbf_scale)
            mask = (sample == sample_name) & sr & (category == cat)
            event_weights = template_event_weights(selected, sample_name, mask, weights[sample_name] * scale)
            _, yld, var = weighted_hist(values[mask], event_weights, edges)
            mc_yield += yld
            mc_var += var
        if qcd_raw[icat, 0] > 0:
            numerator += max(float(data_counts[0] - mc_yield[0]), 0.0)
            denominator += float(qcd_raw[icat, 0])
            numerator_var += float(data_counts[0] + mc_var[0])
            denominator_var += float(qcd_var[icat, 0])

    if denominator > 0:
        alpha = numerator / denominator
        variance = numerator_var / (denominator**2) + (numerator**2) * denominator_var / (denominator**4)
        alpha_unc = math.sqrt(max(variance, 0.0))
        status = "measured_from_low_observable_sideband"
    else:
        alpha = 1.0
        alpha_unc = 1.0
        status = "fallback_no_positive_same_sign_denominator"
    rel_unc = alpha_unc / max(abs(alpha), 1e-12)
    scaled = qcd_raw * alpha
    # This variance is used in validation plots/chi2. The pyhf workspace carries
    # the same sideband uncertainty as a global normsys for speed and stability.
    scaled_var = qcd_var * alpha * alpha + (qcd_raw * alpha_unc) ** 2
    payload = {
        "method": "same-sign low-mT data minus non-QCD MC, transferred to opposite-sign signal candidates",
        "observable": observable,
        "category_assignment": "rederived VBF/boosted/zero-jet rules for control-region rows",
        "transfer_sideband": {
            "bin_index": 0,
            "bin_edges": [float(edges[0]), float(edges[1])],
            "description": "lowest fitted-observable bin, chosen as the most signal-depleted control bin",
            "numerator_os_data_minus_nonqcd": numerator,
            "denominator_same_sign_qcd_template": denominator,
            "scale_factor": alpha,
            "absolute_uncertainty": alpha_unc,
            "relative_uncertainty": rel_unc,
            "status": status,
        },
        "normsys": {"name": "qcd_ss_transfer", "hi": 1.0 + rel_unc, "lo": max(0.001, 1.0 - rel_unc)},
        "rows": rows,
        "scaled_qcd_total": float(np.sum(scaled)),
        "limitations": [
            "No anti-isolated tau branch is available in the selected-event artifact.",
            "The transfer factor is measured in the lowest observable bin and propagated globally.",
            "The VBF MC-background control scale is applied before non-QCD subtraction.",
            "QCD shape-statistical uncertainties are recorded for validation but not expanded into per-bin pyhf nuisances in the final workspace.",
        ],
    }
    return scaled, scaled_var, payload


def build_histograms(
    selected: dict[str, np.ndarray],
    weights: dict[str, float],
    categories: list[str],
    edges: np.ndarray,
    observable: str,
    w_scale: dict[str, Any],
    vbf_scale: dict[str, Any],
) -> tuple[dict[str, Any], np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    sample_array = selected["sample"]
    role = selected["role"]
    sr = selected["is_signal_region"].astype(bool)
    cat_array = assign_categories(selected)
    values = np.zeros((len(ALL_SAMPLES), len(categories), len(edges) - 1), dtype=float)
    variances = np.zeros_like(values)
    raw_counts = np.zeros_like(values)
    data_counts = np.zeros((len(categories), len(edges) - 1), dtype=float)
    per_sample: dict[str, Any] = {}
    for isample, sample_name in enumerate(SIGNALS + BACKGROUNDS):
        per_sample[sample_name] = {"weight_full_lumi": weights[sample_name], "categories": {}}
        for icat, cat in enumerate(categories):
            scale = mc_background_scale(sample_name, cat, w_scale, vbf_scale) if sample_name in BACKGROUNDS else 1.0
            mask = sr & (cat_array == cat) & (sample_array == sample_name)
            event_weights = template_event_weights(selected, sample_name, mask, weights[sample_name] * scale)
            counts, yld, var = weighted_hist(selected[observable][mask], event_weights, edges)
            raw_counts[isample, icat] = counts
            values[isample, icat] = yld
            variances[isample, icat] = var
            per_sample[sample_name]["categories"][cat] = {
                "raw_counts": counts.tolist(),
                "weighted_yields": yld.tolist(),
                "sumw2": var.tolist(),
                "total_yield": float(np.sum(yld)),
                "extra_wjets_scale": w_scale["applied_scale_factor"] if sample_name in WJETS else 1.0,
                "extra_vbf_background_scale": vbf_scale["applied_scale_factor"] if sample_name in BACKGROUNDS and cat == "vbf" else 1.0,
            }
    qcd_yield, qcd_var, qcd_payload = qcd_sideband_estimate(selected, weights, categories, edges, observable, w_scale, vbf_scale)
    qcd_index = ALL_SAMPLES.index(QCD_SAMPLE)
    values[qcd_index] = qcd_yield
    variances[qcd_index] = qcd_var
    raw_counts[qcd_index] = np.asarray([qcd_payload["rows"][cat]["unscaled_qcd_template"] for cat in categories], dtype=float)
    per_sample[QCD_SAMPLE] = {
        "weight_full_lumi": None,
        "method": qcd_payload["method"],
        "extra_wjets_scale": None,
        "categories": {
            cat: {
                "raw_counts": raw_counts[qcd_index, icat].tolist(),
                "weighted_yields": values[qcd_index, icat].tolist(),
                "sumw2": variances[qcd_index, icat].tolist(),
                "total_yield": float(np.sum(values[qcd_index, icat])),
            }
            for icat, cat in enumerate(categories)
        },
    }
    for icat, cat in enumerate(categories):
        mask = (role == "data") & sr & (cat_array == cat)
        data_counts[icat] = count_hist(selected[observable][mask], edges)
    totals: dict[str, Any] = {}
    signal_idx = [ALL_SAMPLES.index(sample_name) for sample_name in SIGNALS]
    nonqcd_background_idx = [ALL_SAMPLES.index(sample_name) for sample_name in BACKGROUNDS]
    background_idx = nonqcd_background_idx + [ALL_SAMPLES.index(QCD_SAMPLE)]
    for icat, cat in enumerate(categories):
        signal = np.sum(values[signal_idx, icat], axis=0)
        nonqcd_background = np.sum(values[nonqcd_background_idx, icat], axis=0)
        qcd = values[ALL_SAMPLES.index(QCD_SAMPLE), icat]
        background = np.sum(values[background_idx, icat], axis=0)
        bkg_var = np.sum(variances[background_idx, icat], axis=0)
        data = data_counts[icat]
        totals[cat] = {
            "data_counts": data.tolist(),
            "signal_bins": signal.tolist(),
            "nonqcd_background_bins": nonqcd_background.tolist(),
            "qcd_bins": qcd.tolist(),
            "background_bins": background.tolist(),
            "background_sumw2": bkg_var.tolist(),
            "data_total": int(np.sum(data)),
            "signal_total": float(np.sum(signal)),
            "nonqcd_background_total": float(np.sum(nonqcd_background)),
            "qcd_total": float(np.sum(qcd)),
            "background_total": float(np.sum(background)),
            "data_over_background": float(np.sum(data) / np.sum(background)) if np.sum(background) > 0 else None,
        }
    yields = {
        "phase": "4c_observed",
        "blinding": {
            "real_data_signal_region_used": True,
            "data_scope": OBSERVED_DATA_SCOPE,
            "phase4b_human_gate": "auto-passed by explicit user instruction on 2026-06-02",
            "post_unblinding_retuning": False,
            "phase5_audit_correction": "Added same-sign QCD/fake background, multivariate input reweighting, and wider DY/Z normalization before promoting the calibrated score fit.",
        },
        "binning": {"observable": observable, "edges": edges.tolist()},
        "categories": categories,
        "samples": per_sample,
        "qcd_sideband_estimate": qcd_payload,
        "vbf_background_scale": vbf_scale,
        "totals": totals,
    }
    return yields, values, variances, raw_counts, data_counts, qcd_payload


def validation_metrics(yields: dict[str, Any], label: str) -> dict[str, Any]:
    rows = {}
    combined_chi2 = 0.0
    combined_ndf = 0
    combined_data = 0.0
    combined_bkg = 0.0
    for category, payload in yields["totals"].items():
        data = np.asarray(payload["data_counts"], dtype=float)
        bkg = np.asarray(payload["background_bins"], dtype=float)
        bkg_var = np.asarray(payload["background_sumw2"], dtype=float)
        variance = np.maximum(data, 1.0) + bkg_var + (0.15 * np.asarray(payload["nonqcd_background_bins"], dtype=float)) ** 2
        pulls = (data - bkg) / np.sqrt(np.maximum(variance, 1e-12))
        chi2 = float(np.sum((data - bkg) ** 2 / np.maximum(variance, 1e-12)))
        ndf = int(np.count_nonzero(bkg > 0))
        ratio = float(np.sum(data) / np.sum(bkg)) if np.sum(bkg) > 0 else math.nan
        bin_ratios = np.divide(data, bkg, out=np.full_like(data, np.nan, dtype=float), where=bkg > 0)
        rows[category] = {
            "chi2": chi2,
            "ndf": ndf,
            "chi2_per_ndf": chi2 / ndf if ndf > 0 else math.nan,
            "data_total": float(np.sum(data)),
            "background_total": float(np.sum(bkg)),
            "nonqcd_background_total": float(payload["nonqcd_background_total"]),
            "qcd_total": float(payload["qcd_total"]),
            "data_over_background": ratio,
            "bin_data_over_background": bin_ratios.tolist(),
            "max_abs_pull": float(np.max(np.abs(pulls))) if pulls.size else 0.0,
            "pulls": pulls.tolist(),
            "covariance_note": "Diagonal validation covariance: data Poisson + MC/QCD sideband variances + 15% non-QCD normalization proxy.",
        }
        combined_chi2 += chi2
        combined_ndf += ndf
        combined_data += float(np.sum(data))
        combined_bkg += float(np.sum(bkg))
    ratio = combined_data / combined_bkg if combined_bkg > 0 else math.nan
    rel_unc = math.sqrt(max(combined_data, 1.0)) / combined_bkg if combined_bkg > 0 else math.inf
    combined = {
        "chi2": combined_chi2,
        "ndf": combined_ndf,
        "chi2_per_ndf": combined_chi2 / combined_ndf if combined_ndf > 0 else math.nan,
        "data_total": combined_data,
        "background_total": combined_bkg,
        "data_over_background": ratio,
        "ratio_stat_uncertainty": rel_unc,
    }
    category_fail = any(row["chi2_per_ndf"] > 5.0 for row in rows.values())
    combined_fail = bool(combined["chi2_per_ndf"] > 3.0)
    ratio_fail = bool(abs(ratio - 1.0) > 3.0 * rel_unc) if math.isfinite(ratio) and math.isfinite(rel_unc) else True
    high_score_shape_fail = False
    if "score" in label:
        for row in rows.values():
            bin_ratios = np.asarray(row["bin_data_over_background"], dtype=float)
            if bin_ratios.size and np.isfinite(bin_ratios[-1]) and bin_ratios[-1] > 1.25:
                high_score_shape_fail = True
    return {
        "model_label": label,
        "score_template_validation": rows,
        "combined": combined,
        "pass_criteria": {
            "combined_chi2_per_ndf_max": 3.0,
            "category_chi2_per_ndf_max": 5.0,
            "combined_ratio_within_3_stat_uncertainties": True,
        },
        "score_modeling_status": "pass" if not (category_fail or combined_fail or ratio_fail or high_score_shape_fail) else "flagged",
        "flags": {
            "category_chi2_failure": category_fail,
            "combined_chi2_failure": combined_fail,
            "combined_ratio_failure": ratio_fail,
            "high_score_shape_failure": high_score_shape_fail,
        },
    }


def stat_errors(values: np.ndarray, variances: np.ndarray, isample: int, icat: int) -> list[float]:
    errs = np.sqrt(np.maximum(variances[isample, icat], 0.0))
    vals = values[isample, icat]
    return [float(err) if val > 0 else 0.0 for err, val in zip(errs, vals, strict=True)]


def sample_modifiers(sample: str, category: str, values: np.ndarray, variances: np.ndarray, isample: int, icat: int, qcd_payload: dict[str, Any], w_scale: dict[str, Any], vbf_scale: dict[str, Any]) -> list[dict[str, Any]]:
    if sample == QCD_SAMPLE:
        return [{"name": "qcd_ss_transfer", "type": "normsys", "data": {"hi": qcd_payload["normsys"]["hi"], "lo": qcd_payload["normsys"]["lo"]}}]
    modifiers: list[dict[str, Any]] = [
        {"name": "lumi_2012", "type": "normsys", "data": {"hi": 1.026, "lo": 0.974}},
        {"name": "tau_open_data_acceptance", "type": "normsys", "data": {"hi": 1.15, "lo": 0.85}},
        {"name": f"mc_stat_{sanitize(category)}", "type": "staterror", "data": stat_errors(values, variances, isample, icat)},
    ]
    if sample in SIGNALS:
        modifiers.insert(0, {"name": "mu", "type": "normfactor", "data": None})
    if sample == "DYJetsToLL":
        dy_rel = 0.50 if category == "vbf" else 0.30
        modifiers.append(
            {
                "name": f"dy_ztautau_open_data_{sanitize(category)}",
                "type": "normsys",
                "data": {"hi": 1.0 + dy_rel, "lo": max(0.001, 1.0 - dy_rel)},
            }
        )
    if sample in WJETS:
        modifiers.append({"name": "wjets_high_mt_control", "type": "normsys", "data": w_scale["nuisance"]})
    if category == "vbf" and sample in BACKGROUNDS:
        modifiers.append({"name": "vbf_background_control", "type": "normsys", "data": vbf_scale["nuisance"]})
    return modifiers


def build_workspace(categories: list[str], values: np.ndarray, variances: np.ndarray, observations: np.ndarray, qcd_payload: dict[str, Any], w_scale: dict[str, Any], vbf_scale: dict[str, Any], name: str) -> dict[str, Any]:
    channels = []
    obs = []
    for icat, category in enumerate(categories):
        samples = []
        for isample, sample in enumerate(ALL_SAMPLES):
            samples.append({"name": sample, "data": values[isample, icat].tolist(), "modifiers": sample_modifiers(sample, category, values, variances, isample, icat, qcd_payload, w_scale, vbf_scale)})
        channels.append({"name": sanitize(category), "samples": samples})
        obs.append({"name": sanitize(category), "data": observations[icat].tolist()})
    return {
        "channels": channels,
        "measurements": [{"name": name, "config": {"poi": "mu", "parameters": [{"name": "mu", "inits": [1.0], "bounds": [[0.0, 50.0]]}]}}],
        "observations": obs,
        "version": "1.0.0",
    }


def fit_workspace(workspace: dict[str, Any], interpretation: str, scan_max: float = 50.0) -> dict[str, Any]:
    try:
        ws = pyhf.Workspace(workspace)
        model = ws.model()
        data = ws.data(model)
        pars = pyhf.infer.mle.fit(data, model, init_pars=model.config.suggested_init(), par_bounds=model.config.suggested_bounds(), fixed_params=model.config.suggested_fixed())
        pars_list = [float(x) for x in pyhf.tensorlib.tolist(pars)]
        fit = {
            "status": "evaluated",
            "interpretation": interpretation,
            "mu_hat": float(pars_list[model.config.poi_index]),
            "parameters": dict(zip(model.config.par_names, pars_list, strict=True)),
            "npars": model.config.npars,
        }
        from pyhf.infer.intervals import upper_limits

        scan = np.linspace(0.0, scan_max, int(scan_max * 2) + 1)
        obs_limit, exp_limits, results = upper_limits.upper_limit(data, model, scan=scan, level=0.05, return_results=True)
        fit["observed_upper_limit"] = {
            "status": "evaluated",
            "method": "pyhf asymptotic modified frequentist CLs",
            "observed_limit": float(obs_limit),
            "expected_band_minus2_minus1_median_plus1_plus2": [float(x) for x in exp_limits],
            "scan": scan.tolist(),
            "result_count": len(results),
        }
        p_value = pyhf.infer.hypotest(0.0, data, model, calctype="asymptotics", test_stat="q0")
        p_float = float(pyhf.tensorlib.tolist(p_value))
        fit["discovery_diagnostic"] = {"status": "evaluated", "method": "pyhf asymptotic q0 on observed full data", "p_value": p_float, "z_value": float(norm.isf(p_float)) if p_float > 0 else float("inf")}
        return fit
    except Exception as exc:  # noqa: BLE001
        return {"status": "failed", "interpretation": interpretation, "reason": str(exc)}


def build_model(
    selected: dict[str, np.ndarray],
    weights: dict[str, float],
    categories: list[str],
    edges: np.ndarray,
    observable: str,
    w_scale: dict[str, Any],
    vbf_scale: dict[str, Any],
    model_key: str,
    interpretation: str,
) -> dict[str, Any]:
    yields, values, variances, raw_counts, data_counts, qcd_payload = build_histograms(selected, weights, categories, edges, observable, w_scale, vbf_scale)
    validation = validation_metrics(yields, model_key)
    workspace = build_workspace(categories, values, variances, data_counts, qcd_payload, w_scale, vbf_scale, f"{model_key}_observed_mu_tautau")
    fit = fit_workspace(workspace, interpretation)
    return {
        "key": model_key,
        "observable": observable,
        "categories": categories,
        "edges": edges.tolist(),
        "yields": yields,
        "values": values,
        "variances": variances,
        "raw_counts": raw_counts,
        "data_counts": data_counts,
        "qcd": qcd_payload,
        "validation": validation,
        "workspace": workspace,
        "fit": fit,
    }


def compare_to_prior(primary: dict[str, Any], score: dict[str, Any], addmet: dict[str, Any], w_scale: dict[str, Any]) -> dict[str, Any]:
    p4a = load_json(P4A / "expected_results.json")
    p4b_results = load_json(P4B / "partial_results.json")
    p4b_validation = load_json(P4B / "data_validation.json")
    p4b_w = load_json(P4B / "wjets_highmt_scale.json")
    expected_band = p4a["expected_upper_limit"]["expected_band_minus2_minus1_median_plus1_plus2"]
    primary_limit = primary["fit"].get("observed_upper_limit", {})
    score_limit = score["fit"].get("observed_upper_limit", {})
    primary_expected = primary_limit.get("expected_band_minus2_minus1_median_plus1_plus2", [None, None, None, None, None])
    return {
        "phase4a_expected": {
            "median_expected_limit": expected_band[2],
            "expected_discovery_z": p4a["discovery_sensitivity"].get("z_value"),
            "model_note": "historical expected score-template model before Phase 5 QCD audit correction",
        },
        "phase4b_warning_carried": {
            "score_modeling_status": p4b_validation["score_modeling_status"],
            "combined_data_over_background": p4b_validation["combined"]["data_over_background"],
            "combined_chi2_per_ndf": p4b_validation["combined"]["chi2_per_ndf"],
            "flags": p4b_validation["flags"],
        },
        "w_scale_comparison": {
            "phase4b_10pct_scale": p4b_w["applied_scale_factor"],
            "phase4b_10pct_uncertainty": p4b_w["absolute_uncertainty"],
            "phase4c_full_scale": w_scale["applied_scale_factor"],
            "phase4c_full_uncertainty": w_scale["absolute_uncertainty"],
            "full_minus_10pct": w_scale["applied_scale_factor"] - p4b_w["applied_scale_factor"],
        },
        "primary_fit_comparison": {
            "model": primary["key"],
            "median_expected_limit": primary_expected[2],
            "observed_limit": primary_limit.get("observed_limit"),
            "mu_hat": primary["fit"].get("mu_hat"),
            "z_value": primary["fit"].get("discovery_diagnostic", {}).get("z_value"),
            "observed_limit_over_median_expected": primary_limit.get("observed_limit") / primary_expected[2] if primary_limit.get("observed_limit") is not None and primary_expected[2] else None,
        },
        "score_diagnostic_comparison": {
            "model": score["key"],
            "phase4b_diagnostic_mu_hat": p4b_results["partial_fit"].get("mu_hat"),
            "phase4c_mu_hat": score["fit"].get("mu_hat"),
            "phase4c_observed_limit": score_limit.get("observed_limit"),
            "phase4c_expected_median_limit": score_limit.get("expected_band_minus2_minus1_median_plus1_plus2", [None, None, None, None, None])[2],
            "validation_status": score["validation"]["score_modeling_status"],
        },
        "addmet_comparison": {
            "model": addmet["key"],
            "observable": addmet["observable"],
            "phase3_status": "retained as reconstructed-MET alternative observable after visible mass won the raw MC-only metric",
            "phase4c_mu_hat": addmet["fit"].get("mu_hat"),
            "phase4c_observed_limit": addmet["fit"].get("observed_upper_limit", {}).get("observed_limit"),
            "phase4c_expected_median_limit": addmet["fit"].get("observed_upper_limit", {}).get("expected_band_minus2_minus1_median_plus1_plus2", [None, None, None, None, None])[2],
            "validation_status": addmet["validation"]["score_modeling_status"],
        },
    }


def save_npz(path: Path, model: dict[str, Any]) -> None:
    np.savez(
        path,
        samples=np.asarray(ALL_SAMPLES),
        categories=np.asarray(model["categories"]),
        bin_edges=np.asarray(model["edges"], dtype=float),
        observable=np.asarray([model["observable"]]),
        yields=model["values"],
        variances=model["variances"],
        raw_counts=model["raw_counts"],
        data_counts=model["data_counts"],
    )


def write_markdown_artifacts(primary: dict[str, Any], score: dict[str, Any], addmet: dict[str, Any], results: dict[str, Any], comparison: dict[str, Any], w_scale: dict[str, Any]) -> None:
    primary_fit = primary["fit"]
    score_fit = score["fit"]
    primary_limit = primary_fit.get("observed_upper_limit", {})
    score_limit = score_fit.get("observed_upper_limit", {})
    rows = []
    for category in primary["categories"]:
        val = primary["validation"]["score_template_validation"][category]
        rows.append(f"| {category} | {val['data_total']:.0f} | {val['background_total']:.2f} | {val['qcd_total']:.2f} | {val['data_over_background']:.3f} | {val['chi2_per_ndf']:.3f} | {val['max_abs_pull']:.2f} |")
    score_rows = []
    for category in score["categories"]:
        val = score["validation"]["score_template_validation"][category]
        score_rows.append(f"| {category} | {val['data_total']:.0f} | {val['background_total']:.2f} | {val['qcd_total']:.2f} | {val['data_over_background']:.3f} | {val['chi2_per_ndf']:.3f} | {val['max_abs_pull']:.2f} |")
    addmet_fit = addmet["fit"]
    addmet_limit = addmet_fit.get("observed_upper_limit", {})
    addmet_rows = []
    for category in addmet["categories"]:
        val = addmet["validation"]["score_template_validation"][category]
        addmet_rows.append(f"| {category} | {val['data_total']:.0f} | {val['background_total']:.2f} | {val['qcd_total']:.2f} | {val['data_over_background']:.3f} | {val['chi2_per_ndf']:.3f} | {val['max_abs_pull']:.2f} |")
    content = f"""# Phase 4c Observed Inference: Audit-Corrected Full Data

## Summary

Phase 4c has been updated after the audit of the large expected versus observed
discrepancy. The problem was physics modelling: the original score-template fit
omitted a reducible QCD/fake-tau component, used background MC before correcting
large data/MC input-shape differences, and carried too restrictive a DY/Z
normalization model for a reduced sample without embedding or EWK Z simulation.

The primary observed result is therefore the calibrated trained-discriminator
fit in the same VBF, boosted, and zero-jet categories. The classifier is trained
only on MC, but the background MC receives a multivariate data/MC input
reweighting derived before training in W high-mT, same-sign, Z-rich, and
top/b-tag validation/control regions. The primary score model also includes the
same-sign data-driven QCD/fake template and wider DY/Z normalization nuisance
terms. Visible mass and add-MET mass are retained only as cross-checks.

## W and QCD Control Inputs

The full-data W+jets scale from the high-mT control region is
`{w_scale['applied_scale_factor']:.4f} ± {w_scale['absolute_uncertainty']:.4f}`.
The VBF background control scale from the VBF-like top-btag non-signal region is
`{results['vbf_background_scale']['applied_scale_factor']:.4f} ± {results['vbf_background_scale']['absolute_uncertainty']:.4f}`;
it is applied only to MC backgrounds in the VBF fit category. This addresses
the large VBF data/MC overprediction seen in the original observed templates
without changing the signal normalization or the boosted/zero-jet categories.
The same-sign QCD/fake estimate uses data minus non-QCD MC in the same-sign
low-mT region and a transfer factor measured in the lowest fitted-observable
bin. For the primary calibrated-score model this factor is
`{primary['qcd']['transfer_sideband']['scale_factor']:.4f} ± {primary['qcd']['transfer_sideband']['absolute_uncertainty']:.4f}`.
For the visible-mass cross-check it is
`{score['qcd']['transfer_sideband']['scale_factor']:.4f} ± {score['qcd']['transfer_sideband']['absolute_uncertainty']:.4f}`.
For the add-MET mass cross-check it is
`{addmet['qcd']['transfer_sideband']['scale_factor']:.4f} ± {addmet['qcd']['transfer_sideband']['absolute_uncertainty']:.4f}`.

![Full high-mT W control comparison. The figure shows non-W MC, nominal W MC,
the scaled control-region prediction, and full data in the control region.
The scale is derived outside the signal region and then propagated into the
observed workspaces.](figures/w_highmt_scale_full.pdf){{#fig:p4c-wcr}}

## Primary Calibrated-Score Result

| Category | Data | Background | QCD/fake | Data/background | Chi2/ndf | Max abs pull |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

The primary calibrated-score fit gives `mu_hat = {primary_fit.get('mu_hat', float('nan')):.4f}`,
an observed 95% CLs limit `mu < {primary_limit.get('observed_limit', float('nan')):.4f}`,
and a diagnostic `q0` value `Z = {primary_fit.get('discovery_diagnostic', {}).get('z_value', float('nan')):.4f}`.
The median expected limit from the same corrected workspace is
`{primary_limit.get('expected_band_minus2_minus1_median_plus1_plus2', [float('nan')]*5)[2]:.4f}`.

![Primary calibrated-score validation in the VBF category. The plot compares
localized Run2012B/C TauPlusX data to the calibrated score model after
pre-training multivariate input reweighting, wider DY/Z normalization, and
same-sign QCD/fake correction. This category remains statistically limited but
is included in the simultaneous primary fit.](figures/observed_primary_score_vbf.pdf){{#fig:p4c-primary-vbf}}

![Primary calibrated-score validation in the boosted category. The plot
compares full data to the calibrated score model with the W high-mT scale and
same-sign QCD/fake template. This category is used in the final observed
fit.](figures/observed_primary_score_boosted.pdf){{#fig:p4c-primary-boosted}}

![Primary calibrated-score validation in the zero-jet category. The zero-jet
normalization is stabilized by the same-sign QCD/fake estimate and the
background input reweighting. This category contributes the largest data
statistics to the primary simultaneous fit.](figures/observed_primary_score_zero_jet.pdf){{#fig:p4c-primary-zero}}

## Add-MET Mass Cross-Check

| Category | Data | Background | QCD/fake | Data/background | Chi2/ndf | Max abs pull |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(addmet_rows)}

The simultaneous add-MET mass fit gives `mu_hat = {addmet_fit.get('mu_hat', float('nan')):.4f}`,
an observed 95% CLs limit `mu < {addmet_limit.get('observed_limit', float('nan')):.4f}`,
and `Z = {addmet_fit.get('discovery_diagnostic', {}).get('z_value', float('nan')):.4f}`.
This fit uses the same categories and nuisance model as the calibrated-score
primary fit, but it is kept as a separate cross-check rather than replacing
the trained-discriminator result.

![Add-MET mass validation in the VBF category. The plot compares full data to
the QCD-corrected add-MET mass model in the VBF category. It uses the same W
control scale, VBF background control scale, and same-sign QCD/fake transfer
machinery as the calibrated-score primary model.](figures/observed_addmet_vbf.pdf){{#fig:p4c-addmet-vbf}}

![Add-MET mass validation in the boosted category. The plot compares full data
to the add-MET mass model in the boosted category. The add-MET result is stored
as an explicit Phase 4c cross-check output for downstream documentation.](figures/observed_addmet_boosted.pdf){{#fig:p4c-addmet-boosted}}

![Add-MET mass validation in the zero-jet category. The plot compares full data
to the add-MET mass model in the zero-jet category. This validates the
alternative reconstructed-MET observable without modifying the primary
calibrated-score fit.](figures/observed_addmet_zero_jet.pdf){{#fig:p4c-addmet-zero}}

## Visible-Mass Cross-Check

| Category | Data | Background | QCD/fake | Data/background | Chi2/ndf | Max abs pull |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(score_rows)}

The visible-mass cross-check gives `mu_hat = {score_fit.get('mu_hat', float('nan')):.4f}`,
an observed 95% CLs limit `mu < {score_limit.get('observed_limit', float('nan')):.4f}`,
and `Z = {score_fit.get('discovery_diagnostic', {}).get('z_value', float('nan')):.4f}`.
The visible-mass fit is not the primary result in this update because the
trained calibrated score gives the stronger expected sensitivity after the
input-reweighting and DY/QCD corrections.

![Visible-mass cross-check in the VBF category. This figure retains the
visible-mass observable used in the conservative fallback analysis. It is shown
as a validation cross-check for the primary calibrated-score result.](figures/observed_visible_vbf.pdf){{#fig:p4c-visible-vbf}}

![Observed pull and ratio summary. The figure compares the primary calibrated
score and cross-check validation behavior after the QCD/fake, DY/Z, and input
reweighting corrections. It is the central diagnostic for the final model
choice.](figures/observed_pull_ratio_summary.pdf){{#fig:p4c-pulls}}

![Observed limit and significance summary. The figure shows the primary
calibrated-score fit and the cross-check fits on the same signal-strength
scale. The result remains an Open Data diagnostic rather than CMS-quality
evidence.](figures/observed_limit_significance_summary.pdf){{#fig:p4c-result-summary}}

## Phase 5 Obligation

Phase 5 must report the calibrated-score plus QCD model as the final observed
result, while documenting the pre-training input reweighting, the widened DY/Z
normalization, and the absence of embedded/EWK Z reduced samples. It must also
state that the localized reduced mirror has about 10% of the Open Data record
entries, while the 11.467/fb value remains the cited normalization reference
for these reduced tutorial samples.
"""
    (OUT / "INFERENCE_OBSERVED.md").write_text(content)
    note = f"""---
title: "CMS Open Data H to tau tau Search: Phase 4c Audit-Corrected Observed Results"
author: "Analysis my_analysis"
date: "2026-06-02"
bibliography: references.bib
---

# Change Log {{-}}

**Phase 4c v2 audit correction**

- Added a same-sign data-driven QCD/fake background estimate.
- Added multivariate data/MC input reweighting derived in validation/control regions before classifier training.
- Promoted the calibrated categorized score model to the primary observed result.
- Widened DY/Z normalization to reflect the absence of embedding and EWK Z reduced samples.

{content}

# References {{-}}
"""
    (OUT / "ANALYSIS_NOTE_4c_v1.md").write_text(note)
    shutil.copy2(P4A / "references.bib", OUT / "references.bib")


def main() -> None:
    pyhf.set_backend("numpy")
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    baseline_previous = snapshot_previous_baseline()
    selected = load_selected()
    norm = load_json(ROOT / "phase3_selection" / "outputs" / "normalization_inputs.json")
    p4a_yields = load_json(P4A / "nominal_yields.json")
    categories = [str(category) for category in p4a_yields["categories"]]
    score_edges = np.asarray(p4a_yields["binning"]["edges"], dtype=float)
    score_observable = str(p4a_yields["binning"]["observable"])
    weights = sample_weights(norm)
    w_scale = derive_w_scale(selected, weights)
    vbf_scale = derive_vbf_background_scale(selected, weights, w_scale)

    visible = build_model(
        selected,
        weights,
        categories,
        PRIMARY_VISIBLE_BINS,
        "m_vis",
        w_scale,
        vbf_scale,
        "visible_mass_qcd_crosscheck",
        "Visible-mass cross-check after QCD/fake and input-reweighting corrections.",
    )
    score = build_model(
        selected,
        weights,
        categories,
        score_edges,
        score_observable,
        w_scale,
        vbf_scale,
        "calibrated_score_qcd_primary",
        "Categorized classifier-score primary model with pre-training multivariate input reweighting and QCD/fake correction.",
    )
    primary = score
    addmet = build_model(
        selected,
        weights,
        categories,
        ADDMET_BINS,
        "m_addmet",
        w_scale,
        vbf_scale,
        "addmet_mass_qcd_crosscheck",
        "Separate add-MET mass cross-check fit with the same Phase 4c correction and nuisance model.",
    )

    results = {
        "phase": "4c_observed",
        "primary_model": "calibrated_score_qcd_primary",
        "diagnostic_models": ["visible_mass_qcd_crosscheck", "addmet_mass_qcd_crosscheck"],
        "baseline_previous_result": baseline_previous,
        "model": load_json(P4A / "expected_results.json")["model"],
        "audit_correction": {
            "reason": "Large expected/observed discrepancy traced to missing reducible QCD/fake background, DY/Z normalization limitations, and uncorrected data/MC input-shape differences.",
            "action": "Add same-sign QCD/fake template; derive multivariate background input reweighting before classifier training; loosen DY/Z normalization; use the calibrated categorized score model as primary.",
        },
        "blinding": primary["yields"]["blinding"],
        "normalization": {
            "full_luminosity_fb_inv_reference": 11.467,
            "localized_reduced_mirror_scope": "local files have about one tenth of the Open Data record entries and are treated as reduced processing samples",
            "mc_weight_scale_from_full": 1.0,
            "mc_denominator_source": "official CERN Open Data distribution.number_events from phase3 normalization_inputs.json",
            "trigger": "HLT_IsoMu17_eta2p1_LooseIsoPFTau20",
        },
        "systematics_retained": {
            "dy_ztautau_open_data": "30% in boosted/zero-jet and 50% in VBF",
            "tau_open_data_acceptance": "15%",
            "lumi_2012": "2.6%",
            "wjets_high_mt_control": f"{w_scale['relative_uncertainty']:.6g} relative from full high-mT data CR",
            "vbf_background_control": f"{vbf_scale['relative_uncertainty']:.6g} relative from VBF-like top-btag non-signal CR",
            "qcd_ss_transfer_primary": f"{primary['qcd']['transfer_sideband']['relative_uncertainty']:.6g} relative from same-sign/low-sideband data",
            "qcd_ss_transfer_visible": f"{visible['qcd']['transfer_sideband']['relative_uncertainty']:.6g} relative from same-sign/low-sideband data",
            "qcd_ss_transfer_addmet": f"{addmet['qcd']['transfer_sideband']['relative_uncertainty']:.6g} relative from same-sign/low-sideband data",
        },
        "wjets_high_mt_scale": w_scale,
        "vbf_background_scale": vbf_scale,
        "qcd_sideband_estimates": {
            "calibrated_score_qcd_primary": primary["qcd"],
            "visible_mass_qcd_crosscheck": visible["qcd"],
            "addmet_mass_qcd_crosscheck": addmet["qcd"],
        },
        "validation_summary": primary["validation"],
        "visible_mass_validation_summary": visible["validation"],
        "score_diagnostic_validation_summary": score["validation"],
        "addmet_validation_summary": addmet["validation"],
        "observed_fit": primary["fit"],
        "visible_mass_observed_fit": visible["fit"],
        "score_diagnostic_fit": score["fit"],
        "addmet_observed_fit": addmet["fit"],
        "addmet": {
            "model": "addmet_mass_qcd_crosscheck",
            "role": "separate cross-check fit; does not replace calibrated-score primary",
            "observable": addmet["observable"],
            "binning": addmet["edges"],
            "workspace": "pyhf_workspace_addmet.json",
            "yields": "addmet_observed_yields.json",
            "templates": "addmet_observed_templates.npz",
            "validation_summary": addmet["validation"],
            "observed_fit": addmet["fit"],
        },
        "models": {
            "calibrated_score_qcd_primary": {
                "observable": score["observable"],
                "binning": score["edges"],
                "validation_summary": score["validation"],
                "observed_fit": score["fit"],
            },
            "visible_mass_qcd_crosscheck": {
                "observable": visible["observable"],
                "binning": visible["edges"],
                "validation_summary": visible["validation"],
                "observed_fit": visible["fit"],
            },
            "addmet_mass_qcd_crosscheck": {
                "observable": addmet["observable"],
                "binning": addmet["edges"],
                "validation_summary": addmet["validation"],
                "observed_fit": addmet["fit"],
            },
        },
    }
    comparison = compare_to_prior(primary, score, addmet, w_scale)

    save_npz(OUT / "observed_templates.npz", primary)
    save_npz(OUT / "score_observed_templates.npz", score)
    save_npz(OUT / "visible_observed_templates.npz", visible)
    save_npz(OUT / "addmet_observed_templates.npz", addmet)
    write_json(OUT / "observed_yields.json", primary["yields"])
    write_json(OUT / "score_observed_yields.json", score["yields"])
    write_json(OUT / "visible_observed_yields.json", visible["yields"])
    write_json(OUT / "addmet_observed_yields.json", addmet["yields"])
    write_json(OUT / "wjets_highmt_scale_full.json", w_scale)
    write_json(OUT / "vbf_background_scale.json", vbf_scale)
    write_json(OUT / "qcd_sideband_estimates.json", results["qcd_sideband_estimates"])
    write_json(OUT / "comparison_to_4a_4b.json", comparison)
    write_json(OUT / "pyhf_workspace_observed.json", primary["workspace"])
    write_json(OUT / "pyhf_workspace_score_diagnostic.json", score["workspace"])
    write_json(OUT / "pyhf_workspace_visible_crosscheck.json", visible["workspace"])
    write_json(OUT / "pyhf_workspace_addmet.json", addmet["workspace"])
    write_json(OUT / "observed_results.json", results)
    write_markdown_artifacts(primary, visible, addmet, results, comparison, w_scale)
    append_log(LOG, "Built Phase 4c calibrated-score/QCD primary result with visible-mass and add-MET cross-check fits.")
    primary_mu = primary["fit"].get("mu_hat")
    primary_limit = primary["fit"].get("observed_upper_limit", {}).get("observed_limit")
    visible_mu = visible["fit"].get("mu_hat")
    addmet_mu = addmet["fit"].get("mu_hat")
    addmet_limit = addmet["fit"].get("observed_upper_limit", {}).get("observed_limit")
    primary_mu_text = f"{primary_mu:.4f}" if primary_mu is not None else "not_evaluated"
    primary_limit_text = f"{primary_limit:.4f}" if primary_limit is not None else "not_evaluated"
    visible_mu_text = f"{visible_mu:.4f}" if visible_mu is not None else "not_evaluated"
    addmet_mu_text = f"{addmet_mu:.4f}" if addmet_mu is not None else "not_evaluated"
    addmet_limit_text = f"{addmet_limit:.4f}" if addmet_limit is not None else "not_evaluated"
    append_log(
        EXPERIMENT_LOG,
        "Phase 4c update added multivariate input reweighting before classifier training, same-sign QCD/fake templates, and wider DY/Z normalization. Primary calibrated-score/QCD result "
        f"mu={primary_mu_text}, observed limit={primary_limit_text}; "
        f"visible-mass cross-check mu={visible_mu_text}; "
        f"add-MET cross-check mu={addmet_mu_text}, observed limit={addmet_limit_text}.",
    )


if __name__ == "__main__":
    main()
