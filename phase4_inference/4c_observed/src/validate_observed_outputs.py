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
    "wjets_highmt_scale_full.json",
    "comparison_to_4a_4b.json",
    "pyhf_workspace_observed.json",
]
FIGURE_STEMS = [
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
    with np.load(OUT / "observed_templates.npz", allow_pickle=False) as templates:
        required = {"samples", "categories", "bin_edges", "observable", "yields", "variances", "raw_counts", "data_counts"}
        if set(templates.files) != required:
            raise ValueError(f"Unexpected observed_templates.npz keys: {templates.files}")
        if np.any(templates["yields"] < 0) or np.any(templates["variances"] < 0) or np.any(templates["data_counts"] < 0):
            raise ValueError("Negative yield, variance, or data count in observed templates")
        if int(np.sum(templates["data_counts"])) <= 1000:
            raise ValueError("Observed template does not appear to use full data")
        log.info("Valid NPZ: %s", OUT / "observed_templates.npz")
    ws = pyhf.Workspace(payloads["pyhf_workspace_observed.json"])
    model = ws.model()
    data = ws.data(model)
    _ = model.logpdf(model.config.suggested_init(), data)
    log.info("pyhf observed workspace constructs with %s parameters", model.config.npars)
    results = payloads["observed_results.json"]
    blinding = results["blinding"]
    if "all Run2012B/C TauPlusX" not in blinding["data_scope"]:
        raise ValueError("Observed outputs do not document full Run2012B/C data scope")
    if blinding["post_unblinding_retuning"]:
        raise ValueError("Observed outputs claim post-unblinding retuning")
    if "auto-passed" not in blinding["phase4b_human_gate"]:
        raise ValueError("Observed outputs do not record Phase 4b gate auto-pass")
    w_scale = payloads["wjets_highmt_scale_full.json"]
    if not np.isfinite(w_scale["applied_scale_factor"]) or w_scale["applied_scale_factor"] < 0:
        raise ValueError("Invalid full W high-mT applied scale")
    validation = results["validation_summary"]
    if validation["score_modeling_status"] not in {"pass", "flagged"}:
        raise ValueError("Invalid full score modelling status")
    comparison = payloads["comparison_to_4a_4b.json"]
    p4b_warning = comparison["phase4b_warning_carried"]
    if p4b_warning["score_modeling_status"] != "flagged":
        raise ValueError("Phase 4b score-modeling warning was not preserved")
    if not p4b_warning["flags"]["combined_ratio_failure"]:
        raise ValueError("Phase 4b combined-ratio warning flag was not preserved")
    fit = results["observed_fit"]
    if fit["status"] != "evaluated":
        raise ValueError(f"Observed fit did not evaluate: {fit}")
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
    required_phrases = ["No full-data retuning", "Phase 4b score-template warning", "Phase 5 paper must state"]
    for phrase in required_phrases:
        if phrase not in artifact_text:
            raise ValueError(f"Artifact does not document required phrase: {phrase}")
    log.info("Phase 4c validation passed")


if __name__ == "__main__":
    main()
