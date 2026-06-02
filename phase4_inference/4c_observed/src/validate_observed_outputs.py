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
    "observed_yields.json",
    "score_observed_yields.json",
    "addmet_observed_yields.json",
    "wjets_highmt_scale_full.json",
    "vbf_background_scale.json",
    "qcd_sideband_estimates.json",
    "comparison_to_4a_4b.json",
    "pyhf_workspace_observed.json",
    "pyhf_workspace_score_diagnostic.json",
    "pyhf_workspace_addmet.json",
]
FIGURE_STEMS = [
    "observed_mvis_vbf",
    "observed_mvis_boosted",
    "observed_mvis_zero_jet",
    "observed_addmet_vbf",
    "observed_addmet_boosted",
    "observed_addmet_zero_jet",
    "observed_score_vbf",
    "observed_score_boosted",
    "observed_score_zero_jet",
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
    for template_name in ["observed_templates.npz", "score_observed_templates.npz", "addmet_observed_templates.npz"]:
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
    with np.load(OUT / "observed_templates.npz", allow_pickle=False) as templates:
        required = {"samples", "categories", "bin_edges", "observable", "yields", "variances", "raw_counts", "data_counts"}
        if set(templates.files) != required:
            raise ValueError(f"Unexpected observed_templates.npz keys: {templates.files}")
        if str(templates["observable"][0]) != "m_vis":
            raise ValueError("Primary observed template is not the visible-mass fallback")
    with np.load(OUT / "addmet_observed_templates.npz", allow_pickle=False) as templates:
        if str(templates["observable"][0]) != "m_addmet":
            raise ValueError("Add-MET observed template does not use m_addmet")
        if len(templates["categories"]) != 3:
            raise ValueError("Add-MET fit does not retain the three exclusive categories")
    ws = pyhf.Workspace(payloads["pyhf_workspace_observed.json"])
    model = ws.model()
    data = ws.data(model)
    _ = model.logpdf(model.config.suggested_init(), data)
    log.info("pyhf observed workspace constructs with %s parameters", model.config.npars)
    score_ws = pyhf.Workspace(payloads["pyhf_workspace_score_diagnostic.json"])
    score_model = score_ws.model()
    score_data = score_ws.data(score_model)
    _ = score_model.logpdf(score_model.config.suggested_init(), score_data)
    log.info("pyhf score diagnostic workspace constructs with %s parameters", score_model.config.npars)
    addmet_ws = pyhf.Workspace(payloads["pyhf_workspace_addmet.json"])
    addmet_model = addmet_ws.model()
    addmet_data = addmet_ws.data(addmet_model)
    _ = addmet_model.logpdf(addmet_model.config.suggested_init(), addmet_data)
    log.info("pyhf add-MET workspace constructs with %s parameters", addmet_model.config.npars)
    results = payloads["observed_results.json"]
    blinding = results["blinding"]
    if "Run2012B/C TauPlusX" not in blinding["data_scope"]:
        raise ValueError("Observed outputs do not document Run2012B/C data scope")
    if blinding["post_unblinding_retuning"]:
        raise ValueError("Observed outputs claim post-unblinding retuning")
    if "auto-passed" not in blinding["phase4b_human_gate"]:
        raise ValueError("Observed outputs do not record Phase 4b gate auto-pass")
    if results["primary_model"] != "visible_mass_qcd_primary":
        raise ValueError("Phase 4c audit correction did not promote visible-mass/QCD primary model")
    if results["addmet"]["observable"] != "m_addmet":
        raise ValueError("observed_results.json addmet section does not document m_addmet")
    if results["addmet"]["workspace"] != "pyhf_workspace_addmet.json":
        raise ValueError("observed_results.json addmet section points to the wrong workspace")
    if "addmet_mass_qcd_crosscheck" not in results["diagnostic_models"]:
        raise ValueError("Add-MET cross-check is not listed as a diagnostic model")
    w_scale = payloads["wjets_highmt_scale_full.json"]
    if not np.isfinite(w_scale["applied_scale_factor"]) or w_scale["applied_scale_factor"] < 0:
        raise ValueError("Invalid full W high-mT applied scale")
    vbf_scale = payloads["vbf_background_scale.json"]
    if not np.isfinite(vbf_scale["applied_scale_factor"]) or vbf_scale["applied_scale_factor"] <= 0:
        raise ValueError("Invalid VBF background control scale")
    if not (0.2 <= vbf_scale["applied_scale_factor"] <= 0.9):
        raise ValueError("VBF background scale is outside the expected audit range")
    qcd = payloads["qcd_sideband_estimates.json"]
    for key in ["visible_mass_qcd_primary", "hgb_score_qcd_diagnostic", "addmet_mass_qcd_crosscheck"]:
        if qcd[key]["scaled_qcd_total"] <= 0:
            raise ValueError(f"QCD estimate is empty for {key}")
        if qcd[key]["transfer_sideband"]["relative_uncertainty"] <= 0:
            raise ValueError(f"QCD transfer uncertainty is invalid for {key}")
    validation = results["validation_summary"]
    if validation["score_modeling_status"] not in {"pass", "flagged"}:
        raise ValueError("Invalid primary modelling status")
    score_validation = results["score_diagnostic_validation_summary"]
    if score_validation["score_modeling_status"] != "flagged":
        raise ValueError("Score diagnostic should remain flagged after audit correction")
    addmet_validation = results["addmet_validation_summary"]
    if addmet_validation["model_label"] != "addmet_mass_qcd_crosscheck":
        raise ValueError("Add-MET validation summary has the wrong model label")
    comparison = payloads["comparison_to_4a_4b.json"]
    p4b_warning = comparison["phase4b_warning_carried"]
    if p4b_warning["score_modeling_status"] != "flagged":
        raise ValueError("Phase 4b score-modeling warning was not preserved")
    if not p4b_warning["flags"]["combined_ratio_failure"]:
        raise ValueError("Phase 4b combined-ratio warning flag was not preserved")
    fit = results["observed_fit"]
    if fit["status"] != "evaluated":
        raise ValueError(f"Observed fit did not evaluate: {fit}")
    score_fit = results["score_diagnostic_fit"]
    if score_fit["status"] != "evaluated":
        raise ValueError(f"Score diagnostic fit did not evaluate: {score_fit}")
    addmet_fit = results["addmet_observed_fit"]
    if addmet_fit["status"] != "evaluated":
        raise ValueError(f"Add-MET fit did not evaluate: {addmet_fit}")
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
    required_phrases = ["same-sign QCD/fake", "visible-mass fit", "score fit is diagnostic", "Add-MET Mass Cross-Check"]
    for phrase in required_phrases:
        if phrase not in artifact_text:
            raise ValueError(f"Artifact does not document required phrase: {phrase}")
    log.info("Phase 4c validation passed")


if __name__ == "__main__":
    main()
