"""Build Phase 4c full-data observed inference artifacts."""

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
SAMPLES = SIGNALS + BACKGROUNDS
OBSERVED_DATA_SCOPE = "all Run2012B/C TauPlusX rows in phase3 sensitivity_selected_events.npz"


def append_log(path: Path, message: str) -> None:
    with path.open("a") as handle:
        handle.write(f"\n## {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n\n{message}\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    log.info("Wrote %s", path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def load_selected() -> dict[str, np.ndarray]:
    with np.load(ROOT / "phase3_selection" / "outputs" / "sensitivity_selected_events.npz", allow_pickle=False) as payload:
        return {key: payload[key] for key in payload.files}


def sample_weights(norm: dict[str, Any]) -> dict[str, float]:
    return {sample: float(payload["absolute_weight_per_local_entry"]) for sample, payload in norm["mc_samples"].items()}


def weighted_hist(values: np.ndarray, weight: float, bins: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    finite = np.isfinite(values)
    counts, _ = np.histogram(values[finite], bins=bins)
    yields = counts.astype(float) * weight
    variances = counts.astype(float) * weight * weight
    return counts.astype(int), yields, variances


def count_hist(values: np.ndarray, bins: np.ndarray) -> np.ndarray:
    finite = np.isfinite(values)
    counts, _ = np.histogram(values[finite], bins=bins)
    return counts.astype(float)


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


def build_histograms(
    selected: dict[str, np.ndarray],
    weights: dict[str, float],
    categories: list[str],
    edges: np.ndarray,
    observable: str,
    w_scale: dict[str, Any],
) -> tuple[dict[str, Any], np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    sample_array = selected["sample"]
    role = selected["role"]
    sr = selected["is_signal_region"].astype(bool)
    cat_array = selected["sensitivity_best_category"]
    values = np.zeros((len(SAMPLES), len(categories), len(edges) - 1), dtype=float)
    variances = np.zeros_like(values)
    raw_counts = np.zeros_like(values, dtype=int)
    data_counts = np.zeros((len(categories), len(edges) - 1), dtype=float)
    per_sample: dict[str, Any] = {}
    for isample, sample in enumerate(SAMPLES):
        scale = w_scale["applied_scale_factor"] if sample in WJETS else 1.0
        per_sample[sample] = {"weight_full_lumi": weights[sample], "extra_wjets_scale": scale, "categories": {}}
        for icat, category in enumerate(categories):
            mask = sr & (cat_array == category) & (sample_array == sample)
            counts, yld, var = weighted_hist(selected[observable][mask], weights[sample] * scale, edges)
            raw_counts[isample, icat] = counts
            values[isample, icat] = yld
            variances[isample, icat] = var
            per_sample[sample]["categories"][category] = {
                "raw_counts": counts.tolist(),
                "weighted_yields": yld.tolist(),
                "sumw2": var.tolist(),
                "total_yield": float(np.sum(yld)),
            }
    for icat, category in enumerate(categories):
        mask = (role == "data") & sr & (cat_array == category)
        data_counts[icat] = count_hist(selected[observable][mask], edges)
    totals: dict[str, Any] = {}
    signal_idx = [SAMPLES.index(sample) for sample in SIGNALS]
    background_idx = [SAMPLES.index(sample) for sample in BACKGROUNDS]
    for icat, category in enumerate(categories):
        signal = np.sum(values[signal_idx, icat], axis=0)
        background = np.sum(values[background_idx, icat], axis=0)
        bkg_var = np.sum(variances[background_idx, icat], axis=0)
        data = data_counts[icat]
        totals[category] = {
            "data_counts": data.tolist(),
            "signal_bins": signal.tolist(),
            "background_bins": background.tolist(),
            "background_sumw2": bkg_var.tolist(),
            "data_total": int(np.sum(data)),
            "signal_total": float(np.sum(signal)),
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
        },
        "binning": {"observable": observable, "edges": edges.tolist()},
        "categories": categories,
        "samples": per_sample,
        "totals": totals,
    }
    return yields, values, variances, raw_counts, data_counts


def validation_metrics(yields: dict[str, Any]) -> dict[str, Any]:
    rows = {}
    combined_chi2 = 0.0
    combined_ndf = 0
    combined_data = 0.0
    combined_bkg = 0.0
    for category, payload in yields["totals"].items():
        data = np.asarray(payload["data_counts"], dtype=float)
        bkg = np.asarray(payload["background_bins"], dtype=float)
        bkg_var = np.asarray(payload["background_sumw2"], dtype=float)
        variance = np.maximum(data, 1.0) + bkg_var + (0.15 * bkg) ** 2
        pulls = (data - bkg) / np.sqrt(np.maximum(variance, 1e-12))
        chi2 = float(np.sum((data - bkg) ** 2 / np.maximum(variance, 1e-12)))
        ndf = int(np.count_nonzero(bkg > 0))
        ratio = float(np.sum(data) / np.sum(bkg)) if np.sum(bkg) > 0 else math.nan
        rows[category] = {
            "chi2": chi2,
            "ndf": ndf,
            "chi2_per_ndf": chi2 / ndf if ndf > 0 else math.nan,
            "data_total": float(np.sum(data)),
            "background_total": float(np.sum(bkg)),
            "data_over_background": ratio,
            "max_abs_pull": float(np.max(np.abs(pulls))) if pulls.size else 0.0,
            "pulls": pulls.tolist(),
            "covariance_note": "Diagonal validation covariance: data Poisson + MC stat + 15% background normalization proxy.",
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
    return {
        "score_template_validation": rows,
        "combined": combined,
        "pass_criteria": {
            "combined_chi2_per_ndf_max": 3.0,
            "category_chi2_per_ndf_max": 5.0,
            "combined_ratio_within_3_stat_uncertainties": True,
        },
        "score_modeling_status": "pass" if not (category_fail or combined_fail or ratio_fail) else "flagged",
        "flags": {
            "category_chi2_failure": category_fail,
            "combined_chi2_failure": combined_fail,
            "combined_ratio_failure": ratio_fail,
        },
    }


def stat_errors(values: np.ndarray, variances: np.ndarray, isample: int, icat: int) -> list[float]:
    errs = np.sqrt(np.maximum(variances[isample, icat], 0.0))
    vals = values[isample, icat]
    return [float(err) if val > 0 else 0.0 for err, val in zip(errs, vals, strict=True)]


def sample_modifiers(sample: str, category: str, values: np.ndarray, variances: np.ndarray, isample: int, icat: int, w_scale: dict[str, Any]) -> list[dict[str, Any]]:
    modifiers: list[dict[str, Any]] = [
        {"name": "lumi_2012", "type": "normsys", "data": {"hi": 1.026, "lo": 0.974}},
        {"name": "tau_open_data_acceptance", "type": "normsys", "data": {"hi": 1.15, "lo": 0.85}},
        {"name": f"mc_stat_{sanitize(category)}", "type": "staterror", "data": stat_errors(values, variances, isample, icat)},
    ]
    if sample in SIGNALS:
        modifiers.insert(0, {"name": "mu", "type": "normfactor", "data": None})
    if sample == "DYJetsToLL":
        modifiers.append({"name": "dy_norm_open_data", "type": "normsys", "data": {"hi": 1.15, "lo": 0.85}})
    if sample in WJETS:
        modifiers.append({"name": "wjets_high_mt_control", "type": "normsys", "data": w_scale["nuisance"]})
    return modifiers


def build_workspace(categories: list[str], values: np.ndarray, variances: np.ndarray, observations: np.ndarray, w_scale: dict[str, Any]) -> dict[str, Any]:
    channels = []
    obs = []
    for icat, category in enumerate(categories):
        samples = []
        for isample, sample in enumerate(SAMPLES):
            samples.append({"name": sample, "data": values[isample, icat].tolist(), "modifiers": sample_modifiers(sample, category, values, variances, isample, icat, w_scale)})
        channels.append({"name": sanitize(category), "samples": samples})
        obs.append({"name": sanitize(category), "data": observations[icat].tolist()})
    return {
        "channels": channels,
        "measurements": [{"name": "observed_mu_tautau_full", "config": {"poi": "mu", "parameters": [{"name": "mu", "inits": [1.0], "bounds": [[0.0, 50.0]]}]}}],
        "observations": obs,
        "version": "1.0.0",
    }


def fit_workspace(workspace: dict[str, Any]) -> dict[str, Any]:
    try:
        ws = pyhf.Workspace(workspace)
        model = ws.model()
        data = ws.data(model)
        pars = pyhf.infer.mle.fit(data, model, init_pars=model.config.suggested_init(), par_bounds=model.config.suggested_bounds(), fixed_params=model.config.suggested_fixed())
        pars_list = [float(x) for x in pyhf.tensorlib.tolist(pars)]
        fit = {"status": "evaluated", "mu_hat": float(pars_list[model.config.poi_index]), "parameters": dict(zip(model.config.par_names, pars_list, strict=True)), "npars": model.config.npars}
        from pyhf.infer.intervals import upper_limits

        scan = np.linspace(0.0, 50.0, 101)
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
        return {"status": "failed", "reason": str(exc)}


def compare_to_prior(validation: dict[str, Any], fit: dict[str, Any], w_scale: dict[str, Any]) -> dict[str, Any]:
    p4a = load_json(P4A / "expected_results.json")
    p4b_results = load_json(P4B / "partial_results.json")
    p4b_validation = load_json(P4B / "data_validation.json")
    p4b_w = load_json(P4B / "wjets_highmt_scale.json")
    expected_band = p4a["expected_upper_limit"]["expected_band_minus2_minus1_median_plus1_plus2"]
    observed_limit = fit.get("observed_upper_limit", {}).get("observed_limit")
    mu_hat = fit.get("mu_hat")
    return {
        "phase4a_expected": {
            "median_expected_limit": expected_band[2],
            "expected_discovery_z": p4a["discovery_sensitivity"].get("z_value"),
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
        "score_validation_comparison": {
            "phase4b_combined_data_over_background": p4b_validation["combined"]["data_over_background"],
            "phase4c_combined_data_over_background": validation["combined"]["data_over_background"],
            "phase4b_combined_chi2_per_ndf": p4b_validation["combined"]["chi2_per_ndf"],
            "phase4c_combined_chi2_per_ndf": validation["combined"]["chi2_per_ndf"],
            "phase4c_score_modeling_status": validation["score_modeling_status"],
        },
        "fit_comparison": {
            "phase4a_median_expected_limit": expected_band[2],
            "phase4b_diagnostic_mu_hat": p4b_results["partial_fit"].get("mu_hat"),
            "phase4c_mu_hat": mu_hat,
            "phase4c_observed_limit": observed_limit,
            "observed_limit_over_phase4a_median_expected": observed_limit / expected_band[2] if observed_limit is not None else None,
        },
    }


def write_markdown_artifacts(yields: dict[str, Any], results: dict[str, Any], validation: dict[str, Any], w_scale: dict[str, Any], comparison: dict[str, Any]) -> None:
    rows = []
    for category in yields["categories"]:
        val = validation["score_template_validation"][category]
        rows.append(f"| {category} | {val['data_total']:.0f} | {val['background_total']:.2f} | {val['data_over_background']:.3f} | {val['chi2_per_ndf']:.3f} | {val['max_abs_pull']:.2f} |")
    combined = validation["combined"]
    fit = results["observed_fit"]
    limit = fit.get("observed_upper_limit", {})
    discovery = fit.get("discovery_diagnostic", {})
    p4b_warn = comparison["phase4b_warning_carried"]
    content = f"""# Phase 4c Observed Inference: Full Data

## Summary

Phase 4c applies the frozen Phase 4a/4b score-template model to all available
Run2012B/C TauPlusX data in `phase3_selection/outputs/sensitivity_selected_events.npz`.
No full-data retuning of the selection, classifier, categories, score bins, or
statistical model was performed. The Phase 4b human gate is recorded as
auto-passed by explicit user instruction.

The fitted observable remains `mva_score_hist_gradient_boosting` in the
`vbf`, `boosted`, and `zero_jet` channels with bin edges `[0.0, 0.2, 0.35,
0.5, 1.0]`. The Phase 4b score-template warning is not removed: the 10%
combined data/MC ratio was `{p4b_warn['combined_data_over_background']:.3f}`,
chi2/ndf was `{p4b_warn['combined_chi2_per_ndf']:.3f}`, and the status was
`{p4b_warn['score_modeling_status']}` with flags `{p4b_warn['flags']}`.

## W High-mT Control Scale

The full-data W+jets scale is derived only from the high-`mT` control region
using `(N_data_CR - nonW_MC_CR) / W_MC_CR`. The full control region contains
`{w_scale['data_events_full']}` data events, `W_MC = {w_scale['wjets_mc_yield_full_lumi']:.3f}`,
and `nonW_MC = {w_scale['nonw_background_mc_yield_full_lumi']:.3f}`. The
applied full-data scale is `{w_scale['applied_scale_factor']:.4f} ± {w_scale['absolute_uncertainty']:.4f}`
with status `{w_scale['status']}`. The 10% Phase 4b scale was
`{comparison['w_scale_comparison']['phase4b_10pct_scale']:.4f} ± {comparison['w_scale_comparison']['phase4b_10pct_uncertainty']:.4f}`.

![Full high-mT W control comparison. The figure shows non-W MC, nominal W MC,
the scaled control-region prediction, and full data in the control region.
The scale is derived outside the signal region and then propagated into the
observed workspace.](figures/w_highmt_scale_full.pdf){{#fig:p4c-wcr}}

## Full-Data Score-Template Validation

| Category | Data | Background | Data/background | Chi2/ndf | Max abs pull |
| --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

Combined over all score-template bins, data/background is
`{combined['data_over_background']:.3f}` with chi2/ndf
`{combined['chi2_per_ndf']:.3f}`. The full-data score-modelling status is
`{validation['score_modeling_status']}` under the same diagnostic criteria as
Phase 4b.

![Full-data score-template validation in the VBF category. The plot compares
all available Run2012B/C TauPlusX data to the frozen MC template model with
the full high-mT W scale applied. The ratio panel is a diagnostic and does not
drive any post-unblinding retuning.](figures/observed_score_vbf.pdf){{#fig:p4c-score-vbf}}

![Full-data score-template validation in the boosted category. The plot
compares full data to the frozen Phase 4a/4b score-template model. This is an
observed-result diagnostic with the Phase 4b score-modeling warning still
carried forward.](figures/observed_score_boosted.pdf){{#fig:p4c-score-boosted}}

![Full-data score-template validation in the zero-jet category. The zero-jet
channel dominates the full observed event count and therefore the combined
data/MC ratio. The model was not retuned after unblinding.](figures/observed_score_zero_jet.pdf){{#fig:p4c-score-zero}}

![Observed pull and ratio summary. The figure summarizes per-category
data/background ratios and maximum score-bin pulls for full data. It compares
the observed validation behavior to the Phase 4b 10% validation and Phase 4a
expected reference.](figures/observed_pull_ratio_summary.pdf){{#fig:p4c-pulls}}

## Observed Fit Result

The observed pyhf workspace is written to `pyhf_workspace_observed.json`.
Fit status is `{fit['status']}`. The fitted signal strength is
`{fit.get('mu_hat', float('nan')):.4f}`. The observed 95% CLs upper limit
status is `{limit.get('status', 'not_evaluated')}` and the observed limit is
`{limit.get('observed_limit', float('nan')):.4f}` if evaluated. The observed
discovery diagnostic status is `{discovery.get('status', 'not_evaluated')}`;
its `q0` significance is `Z = {discovery.get('z_value', float('nan')):.4f}` if
evaluated.

![Observed limit and significance summary. The figure shows the full-data
fitted signal strength, observed upper limit, Phase 4a expected median limit,
and observed discovery diagnostic where available. These numbers are a
simplified open-data result and must be interpreted with the documented
score-modeling caveat.](figures/observed_limit_significance_summary.pdf){{#fig:p4c-result-summary}}

![Comparison to Phase 4a expected and Phase 4b validation. The figure compares
the Phase 4a expected limit, Phase 4b diagnostic fit, full-data observed fit,
and the 10% versus full W high-mT scale factors. It is intended to make the
unblinding evolution explicit for Phase 5.](figures/comparison_to_4a_4b.pdf){{#fig:p4c-comparison}}

## Phase 5 Obligation

The Phase 5 paper must state that the score-modeling validation was flagged in
Phase 4b and remains a limitation of the simplified open-data result. The
result should not claim a clean CMS-quality score-template model, nor should
it describe the W+jets scale as signal-region tuned.
"""
    (OUT / "INFERENCE_OBSERVED.md").write_text(content)
    note = f"""---
title: "CMS Open Data H to tau tau Search: Phase 4c Full Observed Results"
author: "Analysis my_analysis"
date: "2026-06-02"
bibliography: references.bib
---

# Change Log {{-}}

**Phase 4c v1**

- Applied the frozen Phase 4a/4b score-template method to full Run2012B/C TauPlusX data.
- Derived the full high-mT W+jets scale `{w_scale['applied_scale_factor']:.4f} ± {w_scale['absolute_uncertainty']:.4f}`.
- Preserved the Phase 4b score-modeling warning in the observed result.
- Recorded that the 4b human gate was auto-passed by explicit user instruction.

{content}

# References {{-}}
"""
    (OUT / "ANALYSIS_NOTE_4c_v1.md").write_text(note)
    shutil.copy2(P4A / "references.bib", OUT / "references.bib")


def main() -> None:
    pyhf.set_backend("numpy")
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    selected = load_selected()
    norm = load_json(ROOT / "phase3_selection" / "outputs" / "normalization_inputs.json")
    p4a_yields = load_json(P4A / "nominal_yields.json")
    categories = [str(category) for category in p4a_yields["categories"]]
    edges = np.asarray(p4a_yields["binning"]["edges"], dtype=float)
    observable = str(p4a_yields["binning"]["observable"])
    weights = sample_weights(norm)
    w_scale = derive_w_scale(selected, weights)
    yields, values, variances, raw_counts, data_counts = build_histograms(selected, weights, categories, edges, observable, w_scale)
    validation = validation_metrics(yields)
    workspace = build_workspace(categories, values, variances, data_counts, w_scale)
    observed_fit = fit_workspace(workspace)
    results = {
        "phase": "4c_observed",
        "model": load_json(P4A / "expected_results.json")["model"],
        "blinding": yields["blinding"],
        "normalization": {
            "full_luminosity_fb_inv": 11.467,
            "mc_weight_scale_from_full": 1.0,
            "mc_denominator_source": "official CERN Open Data distribution.number_events from phase3 normalization_inputs.json",
            "trigger": "HLT_IsoMu17_eta2p1_LooseIsoPFTau20",
        },
        "systematics_retained": {
            "dy_norm_open_data": "15%",
            "tau_open_data_acceptance": "15%",
            "lumi_2012": "2.6%",
            "wjets_high_mt_control": f"{w_scale['relative_uncertainty']:.6g} relative from full high-mT data CR",
        },
        "wjets_high_mt_scale": w_scale,
        "validation_summary": validation,
        "observed_fit": observed_fit,
    }
    comparison = compare_to_prior(validation, observed_fit, w_scale)
    np.savez(
        OUT / "observed_templates.npz",
        samples=np.asarray(SAMPLES),
        categories=np.asarray(categories),
        bin_edges=edges,
        observable=np.asarray([observable]),
        yields=values,
        variances=variances,
        raw_counts=raw_counts,
        data_counts=data_counts,
    )
    write_json(OUT / "observed_yields.json", yields)
    write_json(OUT / "wjets_highmt_scale_full.json", w_scale)
    write_json(OUT / "comparison_to_4a_4b.json", comparison)
    write_json(OUT / "pyhf_workspace_observed.json", workspace)
    write_json(OUT / "observed_results.json", results)
    write_markdown_artifacts(yields, results, validation, w_scale, comparison)
    append_log(LOG, "Built Phase 4c full observed results, full high-mT W scale, observed workspace, comparisons, and markdown artifacts.")
    append_log(EXPERIMENT_LOG, f"Phase 4c executor used all available Run2012B/C TauPlusX data from `sensitivity_selected_events.npz` with no post-unblinding retuning. Full high-mT W scale = {w_scale['applied_scale_factor']:.4f} ± {w_scale['absolute_uncertainty']:.4f}; full score modelling status = {validation['score_modeling_status']}. Phase 4b warning remains carried to Phase 5.")


if __name__ == "__main__":
    main()
