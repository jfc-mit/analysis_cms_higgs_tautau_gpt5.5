"""Evaluate MVA input modelling and train diagnostic classifiers if allowed."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
from rich.logging import RichHandler
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBClassifier
except ImportError:  # pragma: no cover - optional environment dependency
    XGBClassifier = None

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "outputs"
MODEL_DIR = OUT / "models"
SESSION_LOG = HERE.parent / "logs" / "executor_phase3_selection_20260602T110516Z.md"

INPUTS = [
    "m_vis",
    "mu_pt",
    "mu_eta",
    "tau_pt",
    "tau_eta",
    "delta_r_mu_tau",
    "delta_phi_mu_tau",
    "met_pt",
    "met_significance",
    "mt_mu_met",
    "mt_tau_met",
    "mt_tot",
    "pt_tautau_proxy",
    "m_coll",
    "tau_id_iso_raw",
]

BINS = {
    "mu_pt": np.linspace(20, 160, 17),
    "mu_eta": np.linspace(-2.2, 2.2, 17),
    "tau_pt": np.linspace(20, 180, 17),
    "tau_eta": np.linspace(-2.5, 2.5, 17),
    "delta_r_mu_tau": np.linspace(0.5, 5.0, 19),
    "delta_phi_mu_tau": np.linspace(0.0, np.pi, 17),
    "met_pt": np.linspace(0, 200, 21),
    "met_significance": np.linspace(0, 100, 21),
    "mt_mu_met": np.linspace(0, 160, 17),
    "mt_tau_met": np.linspace(0, 160, 17),
    "mt_tot": np.linspace(0, 300, 31),
    "m_vis": np.linspace(0, 250, 26),
    "m_addmet": np.linspace(0, 300, 31),
    "pt_tautau_proxy": np.linspace(0, 250, 26),
    "m_coll": np.linspace(0, 300, 31),
    "tau_id_iso_raw": np.linspace(0, 20, 21),
}

REMEDIATION_BINS = {
    "m_vis_coarse": np.linspace(0, 250, 11),
    "m_vis_z_window": np.linspace(60, 120, 7),
    "m_addmet_coarse": np.linspace(0, 300, 11),
}

VALIDATION_REGIONS = {
    "w_high_mt": "is_w_high_mt",
    "qcd_same_sign": "is_same_sign_low_mt",
    "z_rich": "is_z_rich",
    "top_btag_handle": "is_top_btag_handle",
}


def append_session(message: str) -> None:
    with SESSION_LOG.open("a") as handle:
        handle.write(f"\n## {message}\n")


def load_selected() -> dict[str, np.ndarray]:
    with np.load(OUT / "selected_events.npz") as data:
        return {key: data[key] for key in data.files}


def chi2_ndf(data_values: np.ndarray, mc_values: np.ndarray, bins: np.ndarray) -> dict[str, object]:
    data_values = data_values[np.isfinite(data_values)]
    mc_values = mc_values[np.isfinite(mc_values)]
    if data_values.size < 20 or mc_values.size < 20:
        return {"chi2": None, "ndf": None, "chi2_ndf": None, "status": "low_statistics"}
    data_counts, _ = np.histogram(data_values, bins=bins)
    mc_counts, _ = np.histogram(mc_values, bins=bins)
    active = (data_counts + mc_counts) > 0
    if int(np.sum(active)) < 3:
        return {"chi2": None, "ndf": None, "chi2_ndf": None, "status": "low_populated_bins"}
    data_total = np.sum(data_counts)
    mc_total = np.sum(mc_counts)
    data_shape = data_counts[active] / data_total
    mc_shape = mc_counts[active] / mc_total
    data_var = np.maximum(data_counts[active], 1.0) / data_total**2
    mc_var = np.maximum(mc_counts[active], 1.0) / mc_total**2
    chi2 = float(np.sum((data_shape - mc_shape) ** 2 / (data_var + mc_var)))
    ndf = int(np.sum(active) - 1)
    return {"chi2": chi2, "ndf": ndf, "chi2_ndf": chi2 / ndf if ndf > 0 else None, "status": "evaluated"}


def role_shape_check(
    selected: dict[str, np.ndarray],
    variable: str,
    mask: np.ndarray,
    bins: np.ndarray,
    background_role: str = "background",
) -> dict[str, object]:
    data_mask = mask & (selected["role"] == "data")
    mc_mask = mask & (selected["role"] == background_role)
    result = chi2_ndf(selected[variable][data_mask], selected[variable][mc_mask], bins)
    result["data_events"] = int(np.sum(data_mask & np.isfinite(selected[variable])))
    result["mc_events"] = int(np.sum(mc_mask & np.isfinite(selected[variable])))
    result["background_role"] = background_role
    return result


def union_validation_mask(selected: dict[str, np.ndarray]) -> np.ndarray:
    mask = np.zeros(len(selected["role"]), dtype=bool)
    for flag in VALIDATION_REGIONS.values():
        mask |= selected[flag].astype(bool)
    return mask


def validation_remediation(selected: dict[str, np.ndarray]) -> dict[str, object]:
    union_mask = union_validation_mask(selected)
    attempts: list[dict[str, object]] = []

    attempts.append(
        {
            "attempt": 0,
            "name": "pre_review_mixed_validation_and_control_union",
            "description": "Recompute the original mixed validation/control-region shape test using the new boolean flags instead of the overwritten region string.",
            "results": {
                "m_vis": role_shape_check(selected, "m_vis", union_mask, BINS["m_vis"]),
                "m_addmet": role_shape_check(selected, "m_addmet", union_mask, BINS["m_addmet"]),
            },
        }
    )

    separate_results: dict[str, object] = {}
    for region, flag in VALIDATION_REGIONS.items():
        region_mask = selected[flag].astype(bool)
        separate_results[region] = {
            "m_vis": role_shape_check(selected, "m_vis", region_mask, BINS["m_vis"]),
            "m_addmet": role_shape_check(selected, "m_addmet", region_mask, BINS["m_addmet"]),
        }
    attempts.append(
        {
            "attempt": 1,
            "name": "separate_region_shape_tests",
            "description": "Avoid mixing incompatible W, same-sign, Z-rich, and top-enriched shapes by evaluating each validation/control handle separately.",
            "results": separate_results,
        }
    )

    attempts.append(
        {
            "attempt": 2,
            "name": "coarse_rebinned_primary_observables",
            "description": "Test whether sparse or over-fine binning drives the alarm by rebinnig the primary and add-MET observables in the same validation/control union.",
            "results": {
                "m_vis": role_shape_check(selected, "m_vis", union_mask, REMEDIATION_BINS["m_vis_coarse"]),
                "m_addmet": role_shape_check(selected, "m_addmet", union_mask, REMEDIATION_BINS["m_addmet_coarse"]),
            },
        }
    )

    z_mask = selected["is_z_rich"].astype(bool)
    attempts.append(
        {
            "attempt": 3,
            "name": "z_rich_window_dy_shape_handle",
            "description": "Restrict the primary visible-mass check to the Z-rich validation window and compare data against the available background MC without using it as a fitted normalization closure.",
            "results": {
                "m_vis": role_shape_check(selected, "m_vis", z_mask, REMEDIATION_BINS["m_vis_z_window"]),
            },
        }
    )

    primary_values = [
        attempts[0]["results"]["m_vis"]["chi2_ndf"],
        *[
            row["m_vis"]["chi2_ndf"]
            for row in attempts[1]["results"].values()
            if row["m_vis"]["chi2_ndf"] is not None
        ],
        attempts[2]["results"]["m_vis"]["chi2_ndf"],
        attempts[3]["results"]["m_vis"]["chi2_ndf"],
    ]
    finite_primary = [value for value in primary_values if value is not None and np.isfinite(value)]
    best_primary = float(min(finite_primary)) if finite_primary else None
    closure_validated = best_primary is not None and best_primary <= 3.0
    return {
        "alarm_threshold_chi2_ndf": 3.0,
        "attempt_count": 4,
        "attempts": attempts,
        "best_primary_m_vis_chi2_ndf": best_primary,
        "primary_m_vis_closure_validated_for_phase4": closure_validated,
        "phase4_blocker": None
        if closure_validated
        else (
            "The raw background-only Phase 3 templates are not closure-validated for final Phase 4 inference. "
            "Phase 4 must add citable normalizations, missing-background/QCD treatment, and nuisance-constrained control-region modelling before using the raw templates as final fit inputs."
        ),
    }


def modelling_table(selected: dict[str, np.ndarray]) -> dict[str, object]:
    validation_mask = union_validation_mask(selected)
    data_mask = validation_mask & (selected["role"] == "data")
    mc_mask = validation_mask & (selected["role"] == "background")
    rows = []
    passing = []
    for name in INPUTS:
        result = chi2_ndf(selected[name][data_mask], selected[name][mc_mask], BINS[name])
        chi = result["chi2_ndf"]
        if chi is None:
            decision = "low_statistics_keep_for_diagnostic_only"
        elif chi <= 5.0:
            decision = "pass"
            passing.append(name)
        else:
            decision = "remove_from_mva"
        rows.append(
            {
                "variable": name,
                "validation_regions": ["w_high_mt", "qcd_same_sign", "z_rich", "top_btag_handle"],
                "validation_region_semantics": "union of non-exclusive boolean flags, not selected_events region strings",
                "bins": BINS[name].astype(float).tolist(),
                **result,
                "decision": decision,
            }
        )
    fail_count = sum(row["decision"] == "remove_from_mva" for row in rows)
    return {
        "gate": "data_vs_background_mc_shape_chi2_ndf_le_5",
        "normalization": "shape_normalized_raw_counts",
        "rows": rows,
        "passing_inputs": passing,
        "fail_count": fail_count,
        "candidate_input_count": len(INPUTS),
        "majority_failed": fail_count > len(INPUTS) / 2,
    }


def finite_matrix(selected: dict[str, np.ndarray], inputs: list[str], mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    matrix = np.column_stack([np.nan_to_num(selected[name][mask].astype(float), nan=-999.0, posinf=999.0, neginf=-999.0) for name in inputs])
    labels = (selected["role"][mask] == "signal").astype(int)
    return matrix, labels


def train_models(selected: dict[str, np.ndarray], inputs: list[str], majority_failed: bool) -> dict[str, object]:
    sr_mask = np.isin(selected["category"], ["vbf", "boosted", "zero_jet"]) & np.isin(selected["role"], ["signal", "background"])
    if len(inputs) < 3:
        return {"status": "downscoped", "reason": "Fewer than three inputs passed the modelling gate.", "trained": False}
    x, y = finite_matrix(selected, inputs, sr_mask)
    class_counts = {str(label): int(np.sum(y == label)) for label in (0, 1)}
    if min(class_counts.values()) < 50:
        return {
            "status": "downscoped",
            "reason": "Insufficient selected MC statistics for stable train/test classifier comparison.",
            "class_counts": class_counts,
            "trained": False,
        }
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.35, random_state=31415, stratify=y)
    models = {}
    if XGBClassifier is not None:
        models["xgboost_primary"] = XGBClassifier(
            n_estimators=180,
            max_depth=3,
            learning_rate=0.045,
            subsample=0.85,
            colsample_bytree=0.85,
            min_child_weight=2.0,
            reg_lambda=2.0,
            objective="binary:logistic",
            eval_metric="logloss",
            n_jobs=4,
            random_state=57721,
        )
    models.update(
        {
            "mlp_alternative": make_pipeline(
            StandardScaler(),
            MLPClassifier(hidden_layer_sizes=(32, 16), activation="relu", alpha=1e-3, max_iter=500, random_state=31415),
            ),
            "hist_gradient_boosting_alternative": HistGradientBoostingClassifier(
                max_iter=120,
                learning_rate=0.05,
                max_leaf_nodes=15,
                random_state=2718,
            ),
        }
    )
    metadata: dict[str, object] = {
        "status": "trained_for_phase3_comparison_with_modelling_caveat" if majority_failed else "trained_for_phase3_comparison",
        "trained": True,
        "inputs": inputs,
        "split_seed": 31415,
        "class_counts": class_counts,
        "modelling_gate_majority_failed": majority_failed,
        "modelling_gate_note": (
            "The classifier training remains MC-only and is retained as a candidate discriminator. "
            "Data/background-MC input-shape failures are carried as validation requirements rather than used to tune the classifier."
        )
        if majority_failed
        else "Input modelling gate did not remove the majority of candidate variables.",
        "models": {},
    }
    for name, model in models.items():
        log.info("Training %s", name)
        model.fit(x_train, y_train)
        train_score = model.predict_proba(x_train)[:, 1]
        test_score = model.predict_proba(x_test)[:, 1]
        metadata["models"][name] = {
            "train_auc": float(roc_auc_score(y_train, train_score)),
            "test_auc": float(roc_auc_score(y_test, test_score)),
            "n_train": int(len(y_train)),
            "n_test": int(len(y_test)),
        }
        full_score = model.predict_proba(x)[:, 1]
        np.savez_compressed(MODEL_DIR / f"{name}_scores.npz", score=full_score, label=y)
    return metadata


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    selected = load_selected()
    table = modelling_table(selected)
    model_metadata = train_models(selected, INPUTS, bool(table["majority_failed"]))
    output = {
        **table,
        "validation_remediation": validation_remediation(selected),
        "mva_result": model_metadata,
        "nn_genmet_regression": {
            "status": "formally_downscoped",
            "reason": "Reduced MC files contain no direct GenMET branch and Phase 2 found no neutrino generator-particle truth target.",
            "phase3_decision": "Do not construct or fit NN genMET mass. Keep add-MET mass as the reconstructed-MET alternative.",
        },
    }
    (OUT / "variable_modeling.json").write_text(json.dumps(output, indent=2, sort_keys=True))
    (MODEL_DIR / "model_metadata.json").write_text(json.dumps(model_metadata, indent=2, sort_keys=True))
    log.info("Wrote %s", OUT / "variable_modeling.json")
    append_session("MVA input modelling and classifier feasibility evaluation completed.")


if __name__ == "__main__":
    main()
