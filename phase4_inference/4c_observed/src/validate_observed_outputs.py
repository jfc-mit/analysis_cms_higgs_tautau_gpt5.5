"""Validate Phase 4c full-data observed outputs."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import pyhf
from rich.logging import RichHandler

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent
PHASE = HERE.parent
OUT = PHASE / "outputs"
FIG = OUT / "figures"

JSON_FILES = [
    "observed_results.json",
    "visible_observed_yields.json",
    "baseline_visible_yields.json",
    "nn_score_observed_yields.json",
    "wjets_highmt_scale_full.json",
    "vbf_background_scale.json",
    "qcd_sideband_estimates.json",
    "comparison_to_4a_4b.json",
    "pyhf_workspace_baseline_visible.json",
    "pyhf_workspace_nn_score.json",
    "baseline_visible_result.json",
    "nn_score_result.json",
]
FIGURE_STEMS = [
    "observed_visible_vbf",
    "observed_visible_boosted",
    "observed_visible_zero_jet",
    "observed_nn_score_vbf",
    "observed_nn_score_boosted",
    "observed_nn_score_zero_jet",
    "observed_pull_ratio_summary",
    "w_highmt_scale_full",
    "observed_limit_significance_summary",
    "comparison_to_4a_4b",
]


def main() -> None:
    payloads = {}
    for name in JSON_FILES:
        path = OUT / name
        if not path.exists():
            raise FileNotFoundError(path)
        payloads[name] = json.loads(path.read_text())
        log.info("Valid JSON: %s", path)
    for template_name in ["visible_observed_templates.npz", "nn_score_observed_templates.npz"]:
        with np.load(OUT / template_name, allow_pickle=False) as templates:
            required = {"samples", "categories", "bin_edges", "observable", "yields", "variances", "raw_counts", "data_counts"}
            if set(templates.files) != required:
                raise ValueError(f"Unexpected {template_name} keys: {templates.files}")
            if np.any(templates["yields"] < 0) or np.any(templates["variances"] < 0) or np.any(templates["data_counts"] < 0):
                raise ValueError(f"Negative yield, variance, or data count in {template_name}")
            if int(np.sum(templates["data_counts"])) <= 1000:
                raise ValueError(f"{template_name} does not appear to use full reduced data")
            if "QCDSameSignDataDriven" not in {str(x) for x in templates["samples"]}:
                raise ValueError(f"{template_name} is missing the QCD/fake data-driven sample")
            log.info("Valid NPZ: %s", OUT / template_name)
    with np.load(OUT / "visible_observed_templates.npz", allow_pickle=False) as templates:
        if str(templates["observable"][0]) != "m_vis":
            raise ValueError("Visible baseline template is not m_vis")
    with np.load(OUT / "nn_score_observed_templates.npz", allow_pickle=False) as templates:
        if str(templates["observable"][0]) != "mva_score_xgboost":
            raise ValueError("D_NN template does not use the XGBoost score")
        if len(templates["bin_edges"]) != 21:
            raise ValueError("D_NN template does not use 20 uniform score bins")
    ws = pyhf.Workspace(payloads["pyhf_workspace_baseline_visible.json"])
    model = ws.model()
    data = ws.data(model)
    _ = model.logpdf(model.config.suggested_init(), data)
    log.info("pyhf visible baseline workspace constructs with %s parameters", model.config.npars)
    nn_ws = pyhf.Workspace(payloads["pyhf_workspace_nn_score.json"])
    nn_model = nn_ws.model()
    nn_data = nn_ws.data(nn_model)
    _ = nn_model.logpdf(nn_model.config.suggested_init(), nn_data)
    log.info("pyhf D_NN workspace constructs with %s parameters", nn_model.config.npars)
    results = payloads["observed_results.json"]
    blinding = results["blinding"]
    if "Run2012B/C TauPlusX" not in blinding["data_scope"]:
        raise ValueError("Observed outputs do not document Run2012B/C data scope")
    if blinding["post_unblinding_retuning"]:
        raise ValueError("Observed outputs claim post-unblinding retuning")
    if blinding.get("phase4b_validation_status") != "completed_before_full_signal_region_evaluation":
        raise ValueError("Observed outputs do not record Phase 4b validation status")
    if results["primary_model"] != "visible_mass_qcd_primary":
        raise ValueError("Phase 4c primary model is not the visible-mass baseline")
    baseline_result = payloads["baseline_visible_result.json"]
    if baseline_result["observable"] != "m_vis":
        raise ValueError("Baseline result does not use m_vis")
    nn_result = payloads["nn_score_result.json"]
    if nn_result["observable"] != "mva_score_xgboost":
        raise ValueError("D_NN score result does not use the XGBoost score")
    if len(nn_result["binning"]) != 21:
        raise ValueError("D_NN score result does not use 20 uniform score bins")
    if results["nn_score_result"]["workspace"] != "pyhf_workspace_nn_score.json":
        raise ValueError("observed_results.json D_NN section points to the wrong workspace")
    w_scale = payloads["wjets_highmt_scale_full.json"]
    if not np.isfinite(w_scale["applied_scale_factor"]) or w_scale["applied_scale_factor"] < 0:
        raise ValueError("Invalid full W high-mT applied scale")
    vbf_scale = payloads["vbf_background_scale.json"]
    if not np.isfinite(vbf_scale["applied_scale_factor"]) or vbf_scale["applied_scale_factor"] <= 0:
        raise ValueError("Invalid VBF background control scale")
    if not (0.2 <= vbf_scale["applied_scale_factor"] <= 0.9):
        raise ValueError("VBF background scale is outside the expected audit range")
    qcd = payloads["qcd_sideband_estimates.json"]
    for key in ["visible_mass_qcd_primary", "dnn_classifier_score_secondary"]:
        if qcd[key]["scaled_qcd_total"] <= 0:
            raise ValueError(f"QCD estimate is empty for {key}")
        if qcd[key]["transfer_sideband"]["relative_uncertainty"] <= 0:
            raise ValueError(f"QCD transfer uncertainty is invalid for {key}")
    validation = results["validation_summary"]
    if validation["score_modeling_status"] not in {"pass", "flagged"}:
        raise ValueError("Invalid primary modelling status")
    visible_validation = results["visible_mass_validation_summary"]
    if visible_validation["model_label"] != "visible_mass_qcd_primary":
        raise ValueError("Visible baseline validation summary has the wrong model label")
    fit = results["observed_fit"]
    if fit["status"] != "evaluated":
        raise ValueError(f"Observed fit did not evaluate: {fit}")
    visible_fit = results["visible_mass_observed_fit"]
    if visible_fit["status"] != "evaluated":
        raise ValueError(f"Visible baseline fit did not evaluate: {visible_fit}")
    nn_fit = results["nn_score_result"]["observed_fit"]
    if nn_fit["status"] != "evaluated":
        raise ValueError(f"D_NN fit did not evaluate: {nn_fit}")
    for stem in FIGURE_STEMS:
        for suffix in [".pdf", ".png"]:
            path = FIG / f"{stem}{suffix}"
            if not path.exists() or path.stat().st_size == 0:
                raise FileNotFoundError(path)
    for name in ["INFERENCE_OBSERVED.md", "ANALYSIS_NOTE_4c_v1.md", "ANALYSIS_NOTE_4c_v1.tex", "ANALYSIS_NOTE_4c_v1.pdf"]:
        path = OUT / name
        if not path.exists() or path.stat().st_size == 0:
            raise FileNotFoundError(path)
    artifact_text = (OUT / "INFERENCE_OBSERVED.md").read_text()
    required_phrases = ["same-sign QCD/fake", "Visible-Mass Baseline", "D_NN Result"]
    for phrase in required_phrases:
        if phrase not in artifact_text:
            raise ValueError(f"Artifact does not document required phrase: {phrase}")
    log.info("Phase 4c validation passed")


if __name__ == "__main__":
    main()
