"""Validate Phase 4a expected inference outputs."""

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
    "nominal_yields.json",
    "pyhf_workspace.json",
    "expected_results.json",
    "systematics.json",
    "signal_injection.json",
    "gof_validation.json",
    "limitations_downscope.json",
]

FIGURES = [
    "expected_mva_score_inclusive_sr",
    "expected_s_over_b",
    "expected_nuisance_summary",
    "signal_injection_recovery",
    "gof_toys",
]


def main() -> None:
    payloads = {}
    for name in JSON_FILES:
        path = OUT / name
        if not path.exists():
            raise FileNotFoundError(path)
        payloads[name] = json.loads(path.read_text())
        log.info("Valid JSON: %s", path)
    templates_path = OUT / "templates.npz"
    if not templates_path.exists():
        raise FileNotFoundError(templates_path)
    with np.load(templates_path, allow_pickle=False) as templates:
        required = {"samples", "categories", "bin_edges", "yields", "variances"}
        if set(templates.files) != required:
            raise ValueError(f"Unexpected templates keys: {templates.files}")
        if np.any(templates["yields"] < 0) or np.any(templates["variances"] < 0):
            raise ValueError("Negative template yield or variance")
        log.info("Valid NPZ: %s", templates_path)
    ws = pyhf.Workspace(payloads["pyhf_workspace.json"])
    model = ws.model()
    data = ws.data(model)
    _ = model.logpdf(model.config.suggested_init(), data)
    log.info("pyhf workspace constructs with %s parameters", model.config.npars)
    expected = payloads["expected_results.json"]
    if expected["blinding"]["real_data_signal_region_used"]:
        raise ValueError("Phase 4a expected result claims real data signal-region use")
    if expected["model"]["status"] != "expected-primary candidate pending Phase 4b score-modelling validation/calibration":
        raise ValueError("Expected MVA caveat/status missing from expected_results.json")
    min_background = min(
        row["min_background_bin"]
        for row in payloads["nominal_yields.json"]["totals"].values()
    )
    if min_background < 5.0:
        raise ValueError(f"Low-background bin remains after merging: {min_background}")
    if not payloads["signal_injection.json"]["all_pass"]:
        raise ValueError("Signal injection gate failed")
    if not payloads["gof_validation.json"]["combined"]["passes"]:
        raise ValueError("GoF validation did not pass")
    for stem in FIGURES:
        for suffix in [".pdf", ".png"]:
            path = FIG / f"{stem}{suffix}"
            if not path.exists() or path.stat().st_size == 0:
                raise FileNotFoundError(path)
    artifact = OUT / "INFERENCE_EXPECTED.md"
    if not artifact.exists():
        raise FileNotFoundError(artifact)
    text = artifact.read_text()
    if "real data signal-region" not in text:
        raise ValueError("Artifact does not state the blinding boundary")
    log.info("Phase 4a validation passed")


if __name__ == "__main__":
    main()
