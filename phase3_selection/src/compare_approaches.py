"""Compare Phase 3 candidate observables with a common MC-only metric."""

from __future__ import annotations

import json
import logging
from pathlib import Path

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
SESSION_LOG = HERE.parent / "logs" / "executor_phase3_selection_20260602T110516Z.md"

OBSERVABLES = {
    "visible_mass": {"variable": "m_vis", "bins": np.linspace(0, 250, 26)},
    "addmet_mass": {"variable": "m_addmet", "bins": np.linspace(0, 300, 31)},
}
CATEGORIES = ["vbf", "boosted", "zero_jet"]


def append_session(message: str) -> None:
    with SESSION_LOG.open("a") as handle:
        handle.write(f"\n## {message}\n")


def load_selected() -> dict[str, np.ndarray]:
    with np.load(OUT / "selected_events.npz") as data:
        return {key: data[key] for key in data.files}


def binned_metric(signal: np.ndarray, background: np.ndarray, bins: np.ndarray) -> dict[str, float]:
    signal = signal[np.isfinite(signal)]
    background = background[np.isfinite(background)]
    s, _ = np.histogram(signal, bins=bins)
    b, _ = np.histogram(background, bins=bins)
    raw = float(np.sum(s / np.sqrt(b + 1.0))) if np.sum(s) > 0 else 0.0
    asimov = float(np.sqrt(np.sum((s.astype(float) ** 2) / (b.astype(float) + 1.0)))) if np.sum(s) > 0 else 0.0
    return {"sum_s_over_sqrt_b_plus_1": raw, "sqrt_sum_s2_over_b_plus_1": asimov}


def main() -> None:
    selected = load_selected()
    comparison: dict[str, object] = {
        "normalization": "raw unweighted MC counts; Phase 3 ranking only",
        "metric": "MC-only binned separation over mutually exclusive categories",
        "approaches": {},
    }
    for approach, spec in OBSERVABLES.items():
        variable = spec["variable"]
        bins = spec["bins"]
        total_metric = 0.0
        category_rows = {}
        for category in CATEGORIES:
            cat = selected["category"] == category
            sig = cat & (selected["role"] == "signal")
            bkg = cat & (selected["role"] == "background")
            row = binned_metric(selected[variable][sig], selected[variable][bkg], bins)
            row["signal_events"] = int(np.sum(sig))
            row["background_events"] = int(np.sum(bkg))
            category_rows[category] = row
            total_metric += row["sqrt_sum_s2_over_b_plus_1"]
        comparison["approaches"][approach] = {
            "variable": variable,
            "categories": category_rows,
            "combined_metric_sum_over_categories": total_metric,
        }

    modelling = json.loads((OUT / "variable_modeling.json").read_text())
    if modelling["mva_result"].get("trained"):
        comparison["approaches"]["nn_classifier"] = {
            "variable": "classifier_score",
            "status": "trained_for_diagnostic_phase3_comparison",
            "models": modelling["mva_result"]["models"],
            "primary_metric": modelling["mva_result"]["models"]["mlp_primary"]["test_auc"],
            "alternative_metric": modelling["mva_result"]["models"]["hist_gradient_boosting_alternative"]["test_auc"],
            "replacement_gate": "Cannot replace visible mass in Phase 3 because full systematic template propagation and Phase 4 injection gates are not yet complete.",
        }
    else:
        comparison["approaches"]["nn_classifier"] = {
            "status": "downscoped_or_diagnostic_only",
            "reason": modelling["mva_result"].get("reason", "MVA gate did not produce a primary classifier."),
        }

    visible = comparison["approaches"]["visible_mass"]["combined_metric_sum_over_categories"]
    addmet = comparison["approaches"]["addmet_mass"]["combined_metric_sum_over_categories"]
    if addmet >= 1.10 * visible:
        recommended = "addmet_mass_for_phase4_crosscheck_with_visible_mass_retained_as_baseline"
    else:
        recommended = "visible_mass_primary"
    comparison["phase3_decision"] = {
        "recommended_primary": recommended,
        "reason": "Phase 1 [D9] requires a >=10% improvement and validation gates before replacing visible mass.",
        "genmet_regression": modelling["nn_genmet_regression"],
    }
    (OUT / "approach_comparison.json").write_text(json.dumps(comparison, indent=2, sort_keys=True))
    log.info("Wrote %s", OUT / "approach_comparison.json")
    append_session("Approach comparison completed for visible mass, add-MET mass, and classifier status.")


if __name__ == "__main__":
    main()
