"""Build Phase 4b 10% data-validation inference artifacts."""

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
EXPERIMENT_LOG = ROOT / "experiment_log.md"
P4A = ROOT / "phase4_inference" / "4a_expected" / "outputs"

SIGNALS = ["GluGluToHToTauTau", "VBF_HToTauTau"]
BACKGROUNDS = ["DYJetsToLL", "TTbar", "W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]
WJETS = ["W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]
SAMPLES = SIGNALS + BACKGROUNDS
DATA_SAMPLES = ["Run2012B_TauPlusX", "Run2012C_TauPlusX"]
MASK_EXPR = "(run * 1000003 + luminosityBlock * 9176 + event) % 10 == 0"


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


def data_10pct_mask(selected: dict[str, np.ndarray]) -> np.ndarray:
    run = selected["run"].astype(np.int64)
    lumi = selected["luminosityBlock"].astype(np.int64)
    event = selected["event"].astype(np.int64)
    return ((run * 1_000_003 + lumi * 9_176 + event) % 10) == 0


def sample_weights(norm: dict[str, Any], scale: float) -> dict[str, float]:
    return {
        sample: float(payload["absolute_weight_per_local_entry"]) * scale
        for sample, payload in norm["mc_samples"].items()
    }


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


def derive_w_scale(selected: dict[str, np.ndarray], weights: dict[str, float], data_mask: np.ndarray) -> dict[str, Any]:
    cr = selected["is_w_high_mt"].astype(bool)
    role = selected["role"]
    sample = selected["sample"]
    data_cr = (role == "data") & data_mask & cr
    n_data = int(np.sum(data_cr))
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
        "data_mask": MASK_EXPR,
        "data_events_10pct": n_data,
        "wjets_mc_yield_10pct_lumi": w_yield,
        "wjets_mc_sumw2_10pct_lumi": w_var,
        "nonw_background_mc_yield_10pct_lumi": nonw_yield,
        "nonw_background_mc_sumw2_10pct_lumi": nonw_var,
        "raw_scale_factor": raw_scale,
        "applied_scale_factor": applied,
        "absolute_uncertainty": raw_unc,
        "relative_uncertainty": rel_unc,
        "status": status,
        "nuisance": {
            "name": "wjets_high_mt_control",
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
    data_mask: np.ndarray,
    w_scale: dict[str, Any],
) -> tuple[dict[str, Any], np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    sample_array = selected["sample"]
    role = selected["role"]
    sr = selected["is_signal_region"].astype(bool)
    cat_array = selected["sensitivity_best_category"]
    sample_yields = np.zeros((len(SAMPLES), len(categories), len(edges) - 1), dtype=float)
    sample_vars = np.zeros_like(sample_yields)
    sample_counts = np.zeros_like(sample_yields, dtype=int)
    data_counts = np.zeros((len(categories), len(edges) - 1), dtype=float)
    per_sample: dict[str, Any] = {}
    for isample, sample in enumerate(SAMPLES):
        scale = w_scale["applied_scale_factor"] if sample in WJETS else 1.0
        per_sample[sample] = {"weight_10pct_lumi": weights[sample], "extra_wjets_scale": scale, "categories": {}}
        for icat, category in enumerate(categories):
            mask = sr & (cat_array == category) & (sample_array == sample)
            counts, yields, variances = weighted_hist(selected[observable][mask], weights[sample] * scale, edges)
            sample_counts[isample, icat] = counts
            sample_yields[isample, icat] = yields
            sample_vars[isample, icat] = variances
            per_sample[sample]["categories"][category] = {
                "raw_counts": counts.tolist(),
                "weighted_yields": yields.tolist(),
                "sumw2": variances.tolist(),
                "total_yield": float(np.sum(yields)),
            }
    for icat, category in enumerate(categories):
        mask = (role == "data") & data_mask & sr & (cat_array == category)
        data_counts[icat] = count_hist(selected[observable][mask], edges)
    totals: dict[str, Any] = {}
    signal_idx = [SAMPLES.index(sample) for sample in SIGNALS]
    background_idx = [SAMPLES.index(sample) for sample in BACKGROUNDS]
    for icat, category in enumerate(categories):
        signal = np.sum(sample_yields[signal_idx, icat], axis=0)
        background = np.sum(sample_yields[background_idx, icat], axis=0)
        bkg_var = np.sum(sample_vars[background_idx, icat], axis=0)
        totals[category] = {
            "data_counts": data_counts[icat].tolist(),
            "signal_bins": signal.tolist(),
            "background_bins": background.tolist(),
            "background_sumw2": bkg_var.tolist(),
            "data_total": int(np.sum(data_counts[icat])),
            "signal_total": float(np.sum(signal)),
            "background_total": float(np.sum(background)),
            "data_over_background": float(np.sum(data_counts[icat]) / np.sum(background)) if np.sum(background) > 0 else None,
        }
    yields = {
        "phase": "4b_partial",
        "blinding": {
            "real_data_signal_region_used": True,
            "data_scope": "deterministic 10% subsample only",
            "remaining_90pct_or_full_data_signal_region_inspected": False,
        },
        "mask": {
            "rule": MASK_EXPR,
            "applies_to": "rows with role == data only",
            "modulo_accept": 0,
        },
        "binning": {"observable": observable, "edges": edges.tolist()},
        "categories": categories,
        "samples": per_sample,
        "totals": totals,
    }
    return yields, sample_yields, sample_vars, sample_counts, data_counts


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


def sample_modifiers(
    sample: str,
    category: str,
    values: np.ndarray,
    variances: np.ndarray,
    isample: int,
    icat: int,
    w_scale: dict[str, Any],
) -> list[dict[str, Any]]:
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
        modifiers.append({"name": "wjets_high_mt_control", "type": "normsys", "data": w_scale["nuisance"] | {"name": None}})
        modifiers[-1]["data"].pop("name", None)
    return modifiers


def build_workspace(categories: list[str], values: np.ndarray, variances: np.ndarray, observations: np.ndarray, w_scale: dict[str, Any]) -> dict[str, Any]:
    channels = []
    obs = []
    for icat, category in enumerate(categories):
        samples = []
        for isample, sample in enumerate(SAMPLES):
            samples.append(
                {
                    "name": sample,
                    "data": values[isample, icat].tolist(),
                    "modifiers": sample_modifiers(sample, category, values, variances, isample, icat, w_scale),
                }
            )
        channels.append({"name": sanitize(category), "samples": samples})
        obs.append({"name": sanitize(category), "data": observations[icat].tolist()})
    return {
        "channels": channels,
        "measurements": [
            {
                "name": "partial_mu_tautau_10pct",
                "config": {"poi": "mu", "parameters": [{"name": "mu", "inits": [1.0], "bounds": [[0.0, 50.0]]}]},
            }
        ],
        "observations": obs,
        "version": "1.0.0",
    }


def fit_partial(workspace: dict[str, Any]) -> dict[str, Any]:
    try:
        ws = pyhf.Workspace(workspace)
        model = ws.model()
        data = ws.data(model)
        pars = pyhf.infer.mle.fit(
            data,
            model,
            init_pars=model.config.suggested_init(),
            par_bounds=model.config.suggested_bounds(),
            fixed_params=model.config.suggested_fixed(),
        )
        pars_list = [float(x) for x in pyhf.tensorlib.tolist(pars)]
        return {
            "status": "evaluated",
            "interpretation": "10pct diagnostic fit only; not a final signal-strength result",
            "mu_hat": float(pars_list[model.config.poi_index]),
            "parameters": dict(zip(model.config.par_names, pars_list, strict=True)),
            "npars": model.config.npars,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "failed",
            "interpretation": "10pct diagnostic fit only; not a final signal-strength result",
            "reason": str(exc),
        }


def visible_mass_validation(selected: dict[str, np.ndarray], weights: dict[str, float], data_mask: np.ndarray, categories: list[str]) -> dict[str, Any]:
    edges = np.asarray([0.0, 40.0, 60.0, 80.0, 100.0, 120.0, 160.0, 250.0], dtype=float)
    out: dict[str, Any] = {"observable": "m_vis", "edges": edges.tolist(), "categories": {}}
    role = selected["role"]
    sample = selected["sample"]
    sr = selected["is_signal_region"].astype(bool)
    cat_array = selected["sensitivity_best_category"]
    for category in categories:
        data = count_hist(selected["m_vis"][(role == "data") & data_mask & sr & (cat_array == category)], edges)
        bkg = np.zeros(len(edges) - 1, dtype=float)
        var = np.zeros(len(edges) - 1, dtype=float)
        for sample_name in BACKGROUNDS:
            mask = (sample == sample_name) & sr & (cat_array == category)
            _, yld, yvar = weighted_hist(selected["m_vis"][mask], weights[sample_name], edges)
            bkg += yld
            var += yvar
        variance = np.maximum(data, 1.0) + var + (0.15 * bkg) ** 2
        chi2 = float(np.sum((data - bkg) ** 2 / np.maximum(variance, 1e-12)))
        ndf = int(np.count_nonzero(bkg > 0))
        out["categories"][category] = {
            "data_counts": data.tolist(),
            "background_bins": bkg.tolist(),
            "background_sumw2": var.tolist(),
            "chi2": chi2,
            "ndf": ndf,
            "chi2_per_ndf": chi2 / ndf if ndf > 0 else math.nan,
            "data_over_background": float(np.sum(data) / np.sum(bkg)) if np.sum(bkg) > 0 else math.nan,
        }
    return out


def write_markdown_artifacts(
    yields: dict[str, Any],
    results: dict[str, Any],
    validation: dict[str, Any],
    w_scale: dict[str, Any],
) -> None:
    rows = []
    for category in yields["categories"]:
        val = validation["score_template_validation"][category]
        rows.append(
            f"| {category} | {val['data_total']:.0f} | {val['background_total']:.2f} | "
            f"{val['data_over_background']:.3f} | {val['chi2_per_ndf']:.3f} | {val['max_abs_pull']:.2f} |"
        )
    combined = validation["combined"]
    content = f"""# Phase 4b Partial Inference: 10% Data Validation

## Summary

Phase 4b validates the Phase 4a expected-primary score-template model on a
deterministic 10% collision-data subsample. The fitted observable and category
structure are unchanged from Phase 4a: `mva_score_hist_gradient_boosting` in
`vbf`, `boosted`, and `zero_jet` channels with the Phase 4a score-bin edges.
No model retuning, binning optimization, or replacement method was performed
using the 10% data.

The 10% mask applies only to data rows and is exactly:
`{MASK_EXPR}`. MC templates use all selected MC rows but their official Open
Data weights are scaled from `11.467/fb` to `1.1467/fb`. The remaining 90% and
full-data signal-region distributions are not inspected in this artifact.

## W High-mT Control Scale

The W+jets high-`mT` control scale is derived from the masked 10% data as
`(N_data_CR - nonW_MC_CR) / W_MC_CR`. The control region contains
`{w_scale['data_events_10pct']}` 10% data events, `W_MC = {w_scale['wjets_mc_yield_10pct_lumi']:.3f}`,
and `nonW_MC = {w_scale['nonw_background_mc_yield_10pct_lumi']:.3f}`. The
applied scale factor is `{w_scale['applied_scale_factor']:.4f} ± {w_scale['absolute_uncertainty']:.4f}`
with status `{w_scale['status']}`. This factor is derived outside the signal
region and is not tuned to improve the score-template agreement.

## Score-Template Validation

| Category | Data | Background | Data/background | Chi2/ndf | Max abs pull |
| --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

Combined over all score-template bins, data/background is
`{combined['data_over_background']:.3f}` with chi2/ndf
`{combined['chi2_per_ndf']:.3f}`. The score-modelling status is
`{validation['score_modeling_status']}` under the predeclared Phase 4b gate.

![10% score-template validation in the VBF category. The plot compares the
masked 10% data score distribution to MC normalized to 10% luminosity with
the W high-mT control scale applied. The ratio panel uses the same bins as the
Phase 4a pyhf workspace and does not drive any retuning.](figures/partial_score_vbf.pdf){{#fig:p4b-score-vbf}}

![10% score-template validation in the boosted category. The plot compares the
masked 10% data score distribution to MC normalized to 10% luminosity with
the W high-mT control scale applied. The ratio panel is a validation diagnostic
for the fixed Phase 4a model.](figures/partial_score_boosted.pdf){{#fig:p4b-score-boosted}}

![10% score-template validation in the zero-jet category. The plot compares
the masked 10% data score distribution to MC normalized to 10% luminosity with
the W high-mT control scale applied. This category dominates the event count
and therefore the combined ratio.](figures/partial_score_zero_jet.pdf){{#fig:p4b-score-zero}}

![W high-mT control comparison. The figure shows the observed 10% data control
count against the expected W and non-W MC components at 10% luminosity. The
derived scale is propagated to W+jets in the partial workspace as a control
region constraint.](figures/w_highmt_scale.pdf){{#fig:p4b-wcr}}

![Visible-mass validation summary. The figure provides a mass-shape cross-check
using the same masked 10% data and fixed categories. It is auxiliary to the
score-template validation and is not used to choose a new observable.](figures/partial_mvis_summary.pdf){{#fig:p4b-mvis}}

![Score-validation pull summary. The figure summarizes per-bin pulls across
the three score-template channels using the diagonal validation covariance.
It highlights the largest observed 10% deviations without changing the model.](figures/partial_pull_summary.pdf){{#fig:p4b-pulls}}

## Partial Diagnostic Fit

The partial pyhf workspace in `pyhf_workspace_partial.json` uses the masked
10% signal-region observations. The diagnostic fit status is
`{results['partial_fit']['status']}`. If evaluated, its fitted signal strength
is reported only as a 10%-data validation number and not as a final result.

## Reproduction

Run:

| Command | Purpose |
| --- | --- |
| `pixi run phase4b-results` | Build partial JSON, NPZ, workspace, and markdown outputs. |
| `pixi run phase4b-plots` | Render Phase 4b figures and compile the minimal 4b note. |
| `pixi run phase4b-validate` | Validate blinding metadata, workspace construction, and figures. |
| `pixi run phase4b-all` | Run the full Phase 4b executor chain. |
"""
    (OUT / "INFERENCE_PARTIAL.md").write_text(content)
    note = f"""---
title: "CMS Open Data H to tau tau Search: Phase 4b 10% Data Validation"
author: "Analysis my_analysis"
date: "2026-06-02"
bibliography: references.bib
---

# Change Log {{-}}

**Phase 4b v1**

- Added deterministic 10% data validation using `{MASK_EXPR}` on data rows only.
- Added the W high-mT control scale `{w_scale['applied_scale_factor']:.4f} ± {w_scale['absolute_uncertainty']:.4f}`.
- Added fixed-model score-template validation plots for `vbf`, `boosted`, and `zero_jet`.
- The remaining 90% and full-data signal-region distributions remain blinded until Phase 4c approval.

{content}

# Phase 4a Context

The Phase 4a expected model is the simultaneous pyhf score-template fit in
`vbf`, `boosted`, and `zero_jet` channels using
`mva_score_hist_gradient_boosting` with bin edges `[0.0, 0.2, 0.35, 0.5, 1.0]`.
Phase 4a reported a median expected 95% CLs upper limit of
`{results['phase4a_expected_reference']['median_expected_limit']:.3f}` and an
expected discovery diagnostic of `Z = {results['phase4a_expected_reference']['expected_discovery_z']:.3f}`.

# Unblinding Checklist

| Gate item | Phase 4b status |
| --- | --- |
| Background model validated on 10% data | `{validation['score_modeling_status']}` |
| Systematics retained | luminosity 2.6%, DY 15%, tau/open-data 15%, W high-mT control |
| Expected result physically sensible | inherited from Phase 4a expected artifacts |
| Signal injection/closure | inherited from Phase 4a expected artifacts |
| 10% partial unblinding pathologies | see score-template and W high-mT validation summaries |
| Remaining data blinded | yes |

# References {{-}}
"""
    (OUT / "ANALYSIS_NOTE_4b_v1.md").write_text(note)
    shutil.copy2(P4A / "references.bib", OUT / "references.bib")
    log.info("Wrote markdown artifacts")


def main() -> None:
    pyhf.set_backend("numpy")
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    selected = load_selected()
    norm = load_json(ROOT / "phase3_selection" / "outputs" / "normalization_inputs.json")
    p4a_yields = load_json(P4A / "nominal_yields.json")
    p4a_expected = load_json(P4A / "expected_results.json")
    p4a_systematics = load_json(P4A / "systematics.json")
    categories = [str(category) for category in p4a_yields["categories"]]
    edges = np.asarray(p4a_yields["binning"]["edges"], dtype=float)
    observable = str(p4a_yields["binning"]["observable"])
    data_mask = data_10pct_mask(selected)
    weights = sample_weights(norm, 0.1)
    w_scale = derive_w_scale(selected, weights, data_mask)
    yields, values, variances, raw_counts, data_counts = build_histograms(
        selected, weights, categories, edges, observable, data_mask, w_scale
    )
    validation = validation_metrics(yields)
    validation["visible_mass_validation"] = visible_mass_validation(selected, weights, data_mask, categories)
    workspace = build_workspace(categories, values, variances, data_counts, w_scale)
    partial_fit = fit_partial(workspace)
    mask_summary = {
        "rule": MASK_EXPR,
        "data_total_rows": int(np.sum(selected["role"] == "data")),
        "data_selected_rows": int(np.sum((selected["role"] == "data") & data_mask)),
        "data_selected_fraction": float(np.sum((selected["role"] == "data") & data_mask) / np.sum(selected["role"] == "data")),
        "data_signal_region_10pct": int(np.sum((selected["role"] == "data") & data_mask & selected["is_signal_region"].astype(bool))),
        "data_w_high_mt_10pct": int(np.sum((selected["role"] == "data") & data_mask & selected["is_w_high_mt"].astype(bool))),
    }
    results = {
        "phase": "4b_partial",
        "model": p4a_expected["model"],
        "blinding": yields["blinding"],
        "mask": mask_summary,
        "normalization": {
            "full_luminosity_fb_inv": 11.467,
            "partial_luminosity_fb_inv": 1.1467,
            "mc_weight_scale_from_full": 0.1,
            "mc_denominator_source": "official CERN Open Data distribution.number_events from phase3 normalization_inputs.json",
        },
        "wjets_high_mt_scale": w_scale,
        "validation_summary": validation,
        "partial_fit": partial_fit,
        "phase4a_expected_reference": {
            "median_expected_limit": p4a_expected["expected_upper_limit"]["expected_band_minus2_minus1_median_plus1_plus2"][2],
            "expected_discovery_z": p4a_expected["discovery_sensitivity"]["z_value"],
        },
        "systematics_retained": {
            "dy_norm_open_data": "15%",
            "tau_open_data_acceptance": "15%",
            "lumi_2012": "2.6%",
            "wjets_high_mt_control": f"{w_scale['relative_uncertainty']:.6g} relative from 10% high-mT data CR",
            "phase4a_systematics_file": str(P4A / "systematics.json"),
            "phase4a_implemented": p4a_systematics["implemented"],
        },
    }
    np.savez(
        OUT / "partial_templates.npz",
        samples=np.asarray(SAMPLES),
        categories=np.asarray(categories),
        bin_edges=edges,
        observable=np.asarray([observable]),
        yields=values,
        variances=variances,
        raw_counts=raw_counts,
        data_counts=data_counts,
    )
    write_json(OUT / "partial_yields.json", yields)
    write_json(OUT / "wjets_highmt_scale.json", w_scale)
    write_json(OUT / "data_validation.json", validation)
    write_json(OUT / "pyhf_workspace_partial.json", workspace)
    write_json(OUT / "partial_results.json", results)
    write_markdown_artifacts(yields, results, validation, w_scale)
    append_log(LOG, "Built Phase 4b 10% partial results, W high-mT scale, validation metrics, partial workspace, and markdown artifacts.")
    append_log(EXPERIMENT_LOG, f"Phase 4b executor built deterministic 10% data validation using `{MASK_EXPR}` on data rows only. W high-mT scale = {w_scale['applied_scale_factor']:.4f} ± {w_scale['absolute_uncertainty']:.4f}; score modelling status = {validation['score_modeling_status']}.")


if __name__ == "__main__":
    main()
