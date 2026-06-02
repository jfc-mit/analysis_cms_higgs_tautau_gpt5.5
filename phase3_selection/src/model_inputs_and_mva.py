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
    "mu_pt",
    "mu_eta",
    "mu_reliso",
    "tau_pt",
    "tau_eta",
    "tau_reliso",
    "met_pt",
    "mt_mu_met",
    "m_vis",
    "m_addmet",
    "pt_tautau_proxy",
    "n_clean_jets",
    "mjj",
    "delta_eta_jj",
    "jet1_pt",
    "btag_max",
]

BINS = {
    "mu_pt": np.linspace(20, 160, 17),
    "mu_eta": np.linspace(-2.2, 2.2, 17),
    "mu_reliso": np.linspace(0, 0.25, 16),
    "tau_pt": np.linspace(20, 180, 17),
    "tau_eta": np.linspace(-2.5, 2.5, 17),
    "tau_reliso": np.linspace(0, 5, 16),
    "met_pt": np.linspace(0, 200, 21),
    "mt_mu_met": np.linspace(0, 160, 17),
    "m_vis": np.linspace(0, 250, 26),
    "m_addmet": np.linspace(0, 300, 31),
    "pt_tautau_proxy": np.linspace(0, 250, 26),
    "n_clean_jets": np.arange(-0.5, 8.5, 1),
    "mjj": np.linspace(0, 1200, 25),
    "delta_eta_jj": np.linspace(0, 8, 17),
    "jet1_pt": np.linspace(0, 250, 26),
    "btag_max": np.linspace(-1, 1, 21),
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


def modelling_table(selected: dict[str, np.ndarray]) -> dict[str, object]:
    validation_mask = np.isin(selected["region"], ["w_high_mt", "qcd_same_sign", "z_rich", "top_btag_handle"])
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
    if majority_failed:
        return {
            "status": "downscoped",
            "reason": "Majority of candidate MVA inputs failed the data/MC modelling gate in validation/control regions.",
            "trained": False,
        }
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
    models = {
        "mlp_primary": make_pipeline(
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
    metadata: dict[str, object] = {
        "status": "trained_for_phase3_comparison",
        "trained": True,
        "inputs": inputs,
        "split_seed": 31415,
        "class_counts": class_counts,
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
    model_metadata = train_models(selected, table["passing_inputs"], bool(table["majority_failed"]))
    output = {
        **table,
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
