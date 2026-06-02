"""Validate Phase 4b partial data-validation outputs."""

from __future__ import annotations

import json
import logging
from pathlib import Path

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
OUT = PHASE / "outputs"
FIG = OUT / "figures"

JSON_FILES = [
    "partial_results.json",
    "partial_yields.json",
    "wjets_highmt_scale.json",
    "data_validation.json",
    "pyhf_workspace_partial.json",
]
FIGURE_STEMS = [
    "partial_score_vbf",
    "partial_score_boosted",
    "partial_score_zero_jet",
    "w_highmt_scale",
    "partial_mvis_summary",
    "partial_pull_summary",
]


def main() -> None:
    payloads = {}
    for name in JSON_FILES:
        path = OUT / name
        if not path.exists():
            raise FileNotFoundError(path)
        payloads[name] = json.loads(path.read_text())
        log.info("Valid JSON: %s", path)
    with np.load(OUT / "partial_templates.npz", allow_pickle=False) as templates:
        required = {"samples", "categories", "bin_edges", "observable", "yields", "variances", "raw_counts", "data_counts"}
        if set(templates.files) != required:
            raise ValueError(f"Unexpected partial_templates.npz keys: {templates.files}")
        if np.any(templates["yields"] < 0) or np.any(templates["variances"] < 0) or np.any(templates["data_counts"] < 0):
            raise ValueError("Negative yield, variance, or data count in partial templates")
        log.info("Valid NPZ: %s", OUT / "partial_templates.npz")
    ws = pyhf.Workspace(payloads["pyhf_workspace_partial.json"])
    model = ws.model()
    data = ws.data(model)
    _ = model.logpdf(model.config.suggested_init(), data)
    log.info("pyhf partial workspace constructs with %s parameters", model.config.npars)
    results = payloads["partial_results.json"]
    if results["mask"]["rule"] != "(run * 1000003 + luminosityBlock * 9176 + event) % 10 == 0":
        raise ValueError("Unexpected 10% data mask rule")
    if results["blinding"]["remaining_90pct_or_full_data_signal_region_inspected"]:
        raise ValueError("Phase 4b output claims remaining/full data inspection")
    frac = results["mask"]["data_selected_fraction"]
    if not 0.08 <= frac <= 0.12:
        raise ValueError(f"Unexpected data mask fraction: {frac}")
    w_scale = payloads["wjets_highmt_scale.json"]
    if not np.isfinite(w_scale["applied_scale_factor"]) or w_scale["applied_scale_factor"] < 0:
        raise ValueError("Invalid W high-mT applied scale")
    validation = payloads["data_validation.json"]
    if validation["score_modeling_status"] not in {"pass", "flagged"}:
        raise ValueError("Invalid score modelling status")
    for stem in FIGURE_STEMS:
        for suffix in [".pdf", ".png"]:
            path = FIG / f"{stem}{suffix}"
            if not path.exists() or path.stat().st_size == 0:
                raise FileNotFoundError(path)
    for name in ["INFERENCE_PARTIAL.md", "ANALYSIS_NOTE_4b_v1.md", "ANALYSIS_NOTE_4b_v1.tex", "ANALYSIS_NOTE_4b_v1.pdf"]:
        path = OUT / name
        if not path.exists() or path.stat().st_size == 0:
            raise FileNotFoundError(path)
    artifact_text = (OUT / "INFERENCE_PARTIAL.md").read_text()
    if "remaining 90%" not in artifact_text or "No model retuning" not in artifact_text:
        raise ValueError("Artifact does not document blinding or anti-retuning boundary")
    log.info("Phase 4b validation passed")


if __name__ == "__main__":
    main()
