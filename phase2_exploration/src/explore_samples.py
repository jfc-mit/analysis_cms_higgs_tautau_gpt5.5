"""Phase 2 metadata, branch archaeology, and slice-level variable survey."""

from __future__ import annotations

import json
import logging
import math
import os
import ssl
from pathlib import Path
from urllib.request import Request, urlopen

import awkward as ak
import numpy as np
import uproot
from rich.logging import RichHandler
from sklearn.metrics import roc_auc_score

os.environ.setdefault("SSL_CERT_FILE", "/etc/ssl/certs/ca-certificates.crt")
ssl._create_default_https_context = ssl.create_default_context  # noqa: SLF001

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent
ANALYSIS_ROOT = HERE.parent.parent
OUT = HERE.parent / "outputs"
FIG = OUT / "figures"
BASE_URL = "https://root.cern.ch/files/HiggsTauTauReduced"
ENTRY_STOP = 5_000

SAMPLES = [
    {"name": "GluGluToHToTauTau", "file": "GluGluToHToTauTau.root", "role": "signal"},
    {"name": "VBF_HToTauTau", "file": "VBF_HToTauTau.root", "role": "signal"},
    {"name": "DYJetsToLL", "file": "DYJetsToLL.root", "role": "background"},
    {"name": "TTbar", "file": "TTbar.root", "role": "background"},
    {"name": "W1JetsToLNu", "file": "W1JetsToLNu.root", "role": "background"},
    {"name": "W2JetsToLNu", "file": "W2JetsToLNu.root", "role": "background"},
    {"name": "W3JetsToLNu", "file": "W3JetsToLNu.root", "role": "background"},
    {"name": "Run2012B_TauPlusX", "file": "Run2012B_TauPlusX.root", "role": "data"},
    {"name": "Run2012C_TauPlusX", "file": "Run2012C_TauPlusX.root", "role": "data"},
]

SURVEY_BRANCHES = [
    "HLT_IsoMu24_eta2p1",
    "HLT_IsoMu24",
    "HLT_IsoMu17_eta2p1_LooseIsoPFTau20",
    "PV_npvs",
    "nMuon",
    "Muon_pt",
    "Muon_eta",
    "Muon_phi",
    "Muon_mass",
    "Muon_charge",
    "Muon_pfRelIso04_all",
    "Muon_tightId",
    "nTau",
    "Tau_pt",
    "Tau_eta",
    "Tau_phi",
    "Tau_mass",
    "Tau_charge",
    "Tau_decayMode",
    "Tau_relIso_all",
    "Tau_idIsoTight",
    "Tau_idAntiMuTight",
    "MET_pt",
    "MET_phi",
    "nJet",
    "Jet_pt",
    "Jet_eta",
    "Jet_phi",
    "Jet_mass",
    "Jet_btag",
    "nGenPart",
    "GenPart_pt",
    "GenPart_eta",
    "GenPart_phi",
    "GenPart_mass",
    "GenPart_pdgId",
    "GenPart_status",
]


def ensure_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)


def head_size(url: str) -> int | None:
    req = Request(url, method="HEAD")
    try:
        with urlopen(req, timeout=30) as response:
            value = response.headers.get("content-length")
    except OSError as exc:
        log.warning("HEAD failed for %s: %s", url, exc)
        return None
    return int(value) if value is not None else None


def local_sample_path(sample: dict[str, str]) -> Path:
    directory = "data" if sample["role"] == "data" else "mc"
    return ANALYSIS_ROOT / directory / sample["file"]


def sample_source(sample: dict[str, str]) -> str:
    local_path = local_sample_path(sample)
    if local_path.exists():
        return str(local_path)
    return f"{BASE_URL}/{sample['file']}"


def open_tree(file_name: str) -> uproot.TTree:
    sample = next((item for item in SAMPLES if item["file"] == file_name), None)
    source = sample_source(sample) if sample is not None else f"{BASE_URL}/{file_name}"
    root_file = uproot.open(source)
    return root_file["Events"]


def branch_kind(name: str) -> list[str]:
    lower = name.lower()
    tags = []
    for key in (
        "weight",
        "flag",
        "hlt",
        "id",
        "iso",
        "pu",
        "pileup",
        "gen",
        "met",
        "btag",
        "charge",
        "quality",
        "filter",
    ):
        if key in lower:
            tags.append(key)
    return tags


def summarize_values(values: ak.Array | np.ndarray) -> dict[str, object]:
    flat = ak.to_numpy(ak.flatten(values, axis=None), allow_missing=True)
    flat = np.asarray(flat)
    total = int(flat.size)
    if total == 0:
        return {"entries": 0, "finite_fraction": None}
    if np.ma.isMaskedArray(flat):
        flat = flat.compressed()
    flat = flat[flat != None]  # noqa: E711
    if flat.size == 0:
        return {"entries": total, "finite_fraction": 0.0}

    if flat.dtype.kind in "bui":
        numeric = flat.astype(float)
    elif flat.dtype.kind == "f":
        numeric = flat.astype(float)
    else:
        return {"entries": total, "dtype": str(flat.dtype)}

    finite = np.isfinite(numeric)
    finite_values = numeric[finite]
    summary: dict[str, object] = {
        "entries": total,
        "finite_fraction": float(np.mean(finite)),
    }
    if finite_values.size == 0:
        return summary
    summary.update(
        {
            "min": float(np.min(finite_values)),
            "max": float(np.max(finite_values)),
            "mean": float(np.mean(finite_values)),
            "std": float(np.std(finite_values)),
        }
    )
    unique = np.unique(finite_values)
    if unique.size <= 20:
        summary["unique_values"] = [float(x) for x in unique.tolist()]
    summary["nontrivial"] = bool(unique.size > 1)
    return summary


def first_or_nan(arrays: ak.Array, prefix: str, field: str) -> np.ndarray:
    name = f"{prefix}_{field}"
    if name not in arrays.fields:
        return np.full(len(arrays), np.nan)
    padded = ak.pad_none(arrays[name], 1, clip=True)
    return ak.to_numpy(ak.fill_none(padded[:, 0], np.nan))


def scalar(arrays: ak.Array, name: str, default: float = np.nan) -> np.ndarray:
    if name not in arrays.fields:
        return np.full(len(arrays), default)
    return ak.to_numpy(ak.fill_none(arrays[name], default))


def invariant_mass(
    pt1: np.ndarray,
    eta1: np.ndarray,
    phi1: np.ndarray,
    m1: np.ndarray,
    pt2: np.ndarray,
    eta2: np.ndarray,
    phi2: np.ndarray,
    m2: np.ndarray,
) -> np.ndarray:
    px1 = pt1 * np.cos(phi1)
    py1 = pt1 * np.sin(phi1)
    pz1 = pt1 * np.sinh(eta1)
    e1 = np.sqrt(np.maximum(px1**2 + py1**2 + pz1**2 + m1**2, 0))
    px2 = pt2 * np.cos(phi2)
    py2 = pt2 * np.sin(phi2)
    pz2 = pt2 * np.sinh(eta2)
    e2 = np.sqrt(np.maximum(px2**2 + py2**2 + pz2**2 + m2**2, 0))
    mass2 = (e1 + e2) ** 2 - (px1 + px2) ** 2 - (py1 + py2) ** 2 - (pz1 + pz2) ** 2
    return np.sqrt(np.maximum(mass2, 0))


def add_met_mass(
    mu_pt: np.ndarray,
    mu_eta: np.ndarray,
    mu_phi: np.ndarray,
    mu_mass: np.ndarray,
    tau_pt: np.ndarray,
    tau_eta: np.ndarray,
    tau_phi: np.ndarray,
    tau_mass: np.ndarray,
    met_pt: np.ndarray,
    met_phi: np.ndarray,
) -> np.ndarray:
    px3 = met_pt * np.cos(met_phi)
    py3 = met_pt * np.sin(met_phi)
    e3 = met_pt
    visible = invariant_mass(mu_pt, mu_eta, mu_phi, mu_mass, tau_pt, tau_eta, tau_phi, tau_mass)
    px1 = mu_pt * np.cos(mu_phi)
    py1 = mu_pt * np.sin(mu_phi)
    pz1 = mu_pt * np.sinh(mu_eta)
    e1 = np.sqrt(np.maximum(px1**2 + py1**2 + pz1**2 + mu_mass**2, 0))
    px2 = tau_pt * np.cos(tau_phi)
    py2 = tau_pt * np.sin(tau_phi)
    pz2 = tau_pt * np.sinh(tau_eta)
    e2 = np.sqrt(np.maximum(px2**2 + py2**2 + pz2**2 + tau_mass**2, 0))
    mass2 = (e1 + e2 + e3) ** 2 - (px1 + px2 + px3) ** 2 - (py1 + py2 + py3) ** 2 - (pz1 + pz2) ** 2
    out = np.sqrt(np.maximum(mass2, 0))
    return np.where(np.isfinite(visible), out, np.nan)


def derived_variables(arrays: ak.Array) -> dict[str, np.ndarray]:
    mu_pt = first_or_nan(arrays, "Muon", "pt")
    mu_eta = first_or_nan(arrays, "Muon", "eta")
    mu_phi = first_or_nan(arrays, "Muon", "phi")
    mu_mass = first_or_nan(arrays, "Muon", "mass")
    mu_charge = first_or_nan(arrays, "Muon", "charge")
    mu_iso = first_or_nan(arrays, "Muon", "pfRelIso04_all")
    tau_pt = first_or_nan(arrays, "Tau", "pt")
    tau_eta = first_or_nan(arrays, "Tau", "eta")
    tau_phi = first_or_nan(arrays, "Tau", "phi")
    tau_mass = first_or_nan(arrays, "Tau", "mass")
    tau_charge = first_or_nan(arrays, "Tau", "charge")
    tau_iso = first_or_nan(arrays, "Tau", "relIso_all")
    tau_antimu = first_or_nan(arrays, "Tau", "idAntiMuTight")
    met_pt = scalar(arrays, "MET_pt")
    met_phi = scalar(arrays, "MET_phi")
    njet = scalar(arrays, "nJet", 0.0)
    jet1_pt = first_or_nan(arrays, "Jet", "pt")
    jet1_eta = first_or_nan(arrays, "Jet", "eta")
    jet1_phi = first_or_nan(arrays, "Jet", "phi")
    jet1_mass = first_or_nan(arrays, "Jet", "mass")

    jet_pt_padded = ak.pad_none(arrays["Jet_pt"], 2, clip=True) if "Jet_pt" in arrays.fields else None
    jet_eta_padded = ak.pad_none(arrays["Jet_eta"], 2, clip=True) if "Jet_eta" in arrays.fields else None
    jet_phi_padded = ak.pad_none(arrays["Jet_phi"], 2, clip=True) if "Jet_phi" in arrays.fields else None
    jet_mass_padded = ak.pad_none(arrays["Jet_mass"], 2, clip=True) if "Jet_mass" in arrays.fields else None
    if jet_pt_padded is not None:
        jet2_pt = ak.to_numpy(ak.fill_none(jet_pt_padded[:, 1], np.nan))
        jet2_eta = ak.to_numpy(ak.fill_none(jet_eta_padded[:, 1], np.nan))
        jet2_phi = ak.to_numpy(ak.fill_none(jet_phi_padded[:, 1], np.nan))
        jet2_mass = ak.to_numpy(ak.fill_none(jet_mass_padded[:, 1], np.nan))
    else:
        jet2_pt = jet2_eta = jet2_phi = jet2_mass = np.full(len(arrays), np.nan)

    m_vis = invariant_mass(mu_pt, mu_eta, mu_phi, mu_mass, tau_pt, tau_eta, tau_phi, tau_mass)
    m_addmet = add_met_mass(mu_pt, mu_eta, mu_phi, mu_mass, tau_pt, tau_eta, tau_phi, tau_mass, met_pt, met_phi)
    delta_phi = np.arctan2(np.sin(mu_phi - tau_phi), np.cos(mu_phi - tau_phi))
    delta_r = np.sqrt((mu_eta - tau_eta) ** 2 + delta_phi**2)
    mt_mu_met = np.sqrt(np.maximum(2 * mu_pt * met_pt * (1 - np.cos(mu_phi - met_phi)), 0))
    os_pair = mu_charge * tau_charge < 0
    dijet_mass = invariant_mass(jet1_pt, jet1_eta, jet1_phi, jet1_mass, jet2_pt, jet2_eta, jet2_phi, jet2_mass)
    delta_eta_jj = np.abs(jet1_eta - jet2_eta)

    has_mu_tau = np.isfinite(mu_pt) & np.isfinite(tau_pt)
    loose_accept = (
        has_mu_tau
        & (mu_pt > 20)
        & (np.abs(mu_eta) < 2.1)
        & (tau_pt > 20)
        & (np.abs(tau_eta) < 2.3)
        & (tau_antimu > 0)
    )
    baseline_os_lowmt = loose_accept & os_pair & (mt_mu_met < 40)
    high_mt = loose_accept & os_pair & (mt_mu_met > 80)
    two_jet = loose_accept & (njet >= 2)
    vbf_like = two_jet & (dijet_mass > 300) & (delta_eta_jj > 2.5)

    return {
        "mu_pt": mu_pt,
        "mu_eta": mu_eta,
        "mu_iso": mu_iso,
        "tau_pt": tau_pt,
        "tau_eta": tau_eta,
        "tau_iso": tau_iso,
        "tau_antimu_tight": tau_antimu,
        "met_pt": met_pt,
        "m_vis": m_vis,
        "m_addmet": m_addmet,
        "delta_r_mutau": delta_r,
        "mt_mu_met": mt_mu_met,
        "njet": njet,
        "dijet_mass": dijet_mass,
        "delta_eta_jj": delta_eta_jj,
        "os_pair": os_pair.astype(float),
        "loose_accept": loose_accept.astype(bool),
        "baseline_os_lowmt": baseline_os_lowmt.astype(bool),
        "high_mt": high_mt.astype(bool),
        "vbf_like": vbf_like.astype(bool),
    }


def histogram(values: np.ndarray, bins: np.ndarray) -> dict[str, list[float]]:
    finite = values[np.isfinite(values)]
    counts, edges = np.histogram(finite, bins=bins)
    return {"counts": counts.astype(float).tolist(), "edges": edges.astype(float).tolist()}


def build_inventory() -> dict[str, object]:
    inventory: dict[str, object] = {"base_url": BASE_URL, "samples": {}}
    for sample in SAMPLES:
        log.info("Inventory %s", sample["file"])
        url = f"{BASE_URL}/{sample['file']}"
        tree = open_tree(sample["file"])
        branches = tree.keys()
        inventory["samples"][sample["name"]] = {
            "file": sample["file"],
            "role": sample["role"],
            "url": url,
            "source_used": sample_source(sample),
            "local_path": str(local_sample_path(sample)),
            "local_exists": local_sample_path(sample).exists(),
            "size_bytes": head_size(url),
            "trees": {"Events": {"entries": int(tree.num_entries)}},
            "branch_count": len(branches),
            "branches": [
                {
                    "name": name,
                    "typename": tree[name].typename,
                    "interpretation": str(tree[name].interpretation),
                    "tags": branch_kind(name),
                }
                for name in branches
            ],
            "feature_flags": {
                "has_genpart": "GenPart_pdgId" in branches,
                "has_direct_genmet": any("genmet" in b.lower() or b.lower().startswith("genmet") for b in branches),
                "has_pileup_weight": any("pu" in b.lower() and "weight" in b.lower() for b in branches),
                "has_pv_npvs": "PV_npvs" in branches,
                "has_tau_antimu_tight": "Tau_idAntiMuTight" in branches,
                "has_btag": "Jet_btag" in branches,
                "has_met_covariance": all(b in branches for b in ["MET_CovXX", "MET_CovXY", "MET_CovYY"]),
                "has_event_weight": any("weight" in b.lower() for b in branches),
            },
        }
    return inventory


def branch_diagnostics(inventory: dict[str, object]) -> dict[str, object]:
    diagnostics: dict[str, object] = {"entry_stop": ENTRY_STOP, "samples": {}}
    for sample in SAMPLES:
        tree = open_tree(sample["file"])
        branches = [
            b["name"]
            for b in inventory["samples"][sample["name"]]["branches"]
            if b["tags"] or b["name"].startswith(("nMuon", "nTau", "nJet"))
        ]
        branches = sorted(set(branches))
        log.info("Branch diagnostics %s (%d branches)", sample["name"], len(branches))
        arrays = tree.arrays(branches, entry_stop=min(ENTRY_STOP, tree.num_entries), library="ak")
        diagnostics["samples"][sample["name"]] = {
            branch: summarize_values(arrays[branch]) for branch in branches
        }
    return diagnostics


def survey_variables() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    bins = {
        "mu_pt": np.linspace(0, 160, 41),
        "mu_eta": np.linspace(-2.5, 2.5, 41),
        "tau_pt": np.linspace(0, 160, 41),
        "tau_eta": np.linspace(-2.5, 2.5, 41),
        "met_pt": np.linspace(0, 200, 41),
        "m_vis": np.linspace(0, 250, 51),
        "m_addmet": np.linspace(0, 300, 61),
        "mt_mu_met": np.linspace(0, 200, 41),
        "njet": np.arange(-0.5, 10.5, 1),
        "dijet_mass": np.linspace(0, 1000, 51),
        "delta_eta_jj": np.linspace(0, 8, 41),
        "delta_r_mutau": np.linspace(0, 6, 41),
    }
    histograms: dict[str, object] = {"entry_stop": ENTRY_STOP, "bins": {k: v.tolist() for k, v in bins.items()}, "samples": {}}
    yields: dict[str, object] = {"entry_stop": ENTRY_STOP, "samples": {}}
    separation_values: dict[str, list[np.ndarray]] = {}
    labels: list[np.ndarray] = []

    for sample in SAMPLES:
        tree = open_tree(sample["file"])
        available = [b for b in SURVEY_BRANCHES if b in tree.keys()]
        log.info(
            "Variable survey %s (%d branches, %d events)",
            sample["name"],
            len(available),
            min(ENTRY_STOP, tree.num_entries),
        )
        arrays = tree.arrays(available, entry_stop=min(ENTRY_STOP, tree.num_entries), library="ak")
        derived = derived_variables(arrays)
        role = sample["role"]
        histograms["samples"][sample["name"]] = {
            "role": role,
            "histograms": {name: histogram(derived[name], edges) for name, edges in bins.items()},
        }
        n = len(arrays)
        yields["samples"][sample["name"]] = {
            "role": role,
            "slice_events": int(n),
            "full_events": int(tree.num_entries),
            "has_mu_tau": int(np.sum(np.isfinite(derived["mu_pt"]) & np.isfinite(derived["tau_pt"]))),
            "loose_accept": int(np.sum(derived["loose_accept"])),
            "baseline_os_lowmt": int(np.sum(derived["baseline_os_lowmt"])),
            "high_mt_w_cr": int(np.sum(derived["high_mt"])),
            "vbf_like": int(np.sum(derived["vbf_like"])),
            "same_sign_loose": int(
                np.sum(derived["loose_accept"] & np.isfinite(derived["os_pair"]) & (derived["os_pair"] < 0.5))
            ),
        }
        if role in {"signal", "background"}:
            mask = derived["loose_accept"] & np.isfinite(derived["m_vis"])
            sample_label = np.ones(np.sum(mask), dtype=int) if role == "signal" else np.zeros(np.sum(mask), dtype=int)
            labels.append(sample_label)
            for name in bins:
                separation_values.setdefault(name, []).append(derived[name][mask])

    sep_rows = []
    y = np.concatenate(labels) if labels else np.array([])
    for name, parts in separation_values.items():
        x = np.concatenate(parts) if parts else np.array([])
        finite = np.isfinite(x) & np.isfinite(y)
        if np.sum(finite) > 10 and len(np.unique(y[finite])) == 2:
            auc = float(roc_auc_score(y[finite], x[finite]))
            sep_rows.append(
                {
                    "variable": name,
                    "auc": auc,
                    "separation_from_random": abs(auc - 0.5),
                    "events_used": int(np.sum(finite)),
                }
            )
    sep_rows.sort(key=lambda row: row["separation_from_random"], reverse=True)
    separation = {"entry_stop": ENTRY_STOP, "method": "single-variable ROC AUC on loose-accept MC slice", "ranking": sep_rows}
    return histograms, yields, separation


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    log.info("Wrote %s", path)


def main() -> None:
    ensure_dirs()
    inventory = build_inventory()
    write_json(OUT / "sample_inventory.json", inventory)
    diagnostics = branch_diagnostics(inventory)
    write_json(OUT / "branch_diagnostics.json", diagnostics)
    histograms, yields, separation = survey_variables()
    write_json(OUT / "variable_histograms.json", histograms)
    write_json(OUT / "preselection_yields.json", yields)
    write_json(OUT / "variable_separation.json", separation)


if __name__ == "__main__":
    main()
