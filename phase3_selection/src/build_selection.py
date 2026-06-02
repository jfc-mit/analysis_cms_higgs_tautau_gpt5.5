"""Build Phase 3 mu tau_h selections, regions, and compact summaries."""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path

import awkward as ak
import numpy as np
import uproot
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = HERE.parent / "outputs"
SESSION_LOG = HERE.parent / "logs" / "executor_phase3_selection_20260602T110516Z.md"

CHUNK_SIZE = 200_000

SAMPLES = [
    {"name": "GluGluToHToTauTau", "path": ROOT / "mc" / "GluGluToHToTauTau.root", "role": "signal"},
    {"name": "VBF_HToTauTau", "path": ROOT / "mc" / "VBF_HToTauTau.root", "role": "signal"},
    {"name": "DYJetsToLL", "path": ROOT / "mc" / "DYJetsToLL.root", "role": "background"},
    {"name": "TTbar", "path": ROOT / "mc" / "TTbar.root", "role": "background"},
    {"name": "W1JetsToLNu", "path": ROOT / "mc" / "W1JetsToLNu.root", "role": "background"},
    {"name": "W2JetsToLNu", "path": ROOT / "mc" / "W2JetsToLNu.root", "role": "background"},
    {"name": "W3JetsToLNu", "path": ROOT / "mc" / "W3JetsToLNu.root", "role": "background"},
    {"name": "Run2012B_TauPlusX", "path": ROOT / "data" / "Run2012B_TauPlusX.root", "role": "data"},
    {"name": "Run2012C_TauPlusX", "path": ROOT / "data" / "Run2012C_TauPlusX.root", "role": "data"},
]

BRANCHES = [
    "run",
    "luminosityBlock",
    "event",
    "HLT_IsoMu24_eta2p1",
    "HLT_IsoMu24",
    "HLT_IsoMu17_eta2p1_LooseIsoPFTau20",
    "PV_npvs",
    "Muon_pt",
    "Muon_eta",
    "Muon_phi",
    "Muon_mass",
    "Muon_charge",
    "Muon_pfRelIso04_all",
    "Muon_tightId",
    "Tau_pt",
    "Tau_eta",
    "Tau_phi",
    "Tau_mass",
    "Tau_charge",
    "Tau_relIso_all",
    "Tau_idDecayMode",
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
]

CUTFLOW_STEPS = [
    "events",
    "trigger",
    "muon_candidate",
    "tau_candidate",
    "mu_tau_pair",
    "opposite_sign",
    "low_mt_signal_region",
]

CONFIG = {
    "muon": {
        "pt_min_gev": 20.0,
        "eta_abs_max": 2.1,
        "pfRelIso04_all_max": 0.20,
        "tight_id_required": True,
    },
    "tau": {
        "pt_min_gev": 20.0,
        "eta_abs_max": 2.3,
        "idIsoTight_required": True,
        "idAntiMuTight_required": True,
        "delta_r_mu_tau_min": 0.5,
    },
    "jet": {
        "pt_min_gev": 30.0,
        "eta_abs_max": 4.7,
        "delta_r_lepton_min": 0.5,
    },
    "regions": {
        "signal_mt_max_gev": 40.0,
        "w_cr_mt_min_gev": 80.0,
        "z_rich_mvis_min_gev": 60.0,
        "z_rich_mvis_max_gev": 120.0,
    },
    "categories": {
        "assignment_order": ["vbf", "boosted", "zero_jet"],
        "vbf_njet_min": 2,
        "vbf_mjj_min_gev": 300.0,
        "vbf_delta_eta_jj_min": 2.5,
        "boosted_njet_min": 1,
    },
    "btag": {
        "usage": "diagnostic continuous top handle only",
        "sentinel_rule": "Jet_btag < 0 is invalid and excluded from max score",
    },
}


def append_session(message: str) -> None:
    with SESSION_LOG.open("a") as handle:
        handle.write(f"\n## {message}\n")


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    log.info("Wrote %s", path)


def delta_phi(phi1: np.ndarray, phi2: np.ndarray) -> np.ndarray:
    return np.arctan2(np.sin(phi1 - phi2), np.cos(phi1 - phi2))


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
    e1 = np.sqrt(np.maximum(px1**2 + py1**2 + pz1**2 + m1**2, 0.0))
    px2 = pt2 * np.cos(phi2)
    py2 = pt2 * np.sin(phi2)
    pz2 = pt2 * np.sinh(eta2)
    e2 = np.sqrt(np.maximum(px2**2 + py2**2 + pz2**2 + m2**2, 0.0))
    mass2 = (e1 + e2) ** 2 - (px1 + px2) ** 2 - (py1 + py2) ** 2 - (pz1 + pz2) ** 2
    return np.sqrt(np.maximum(mass2, 0.0))


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
    px1 = mu_pt * np.cos(mu_phi)
    py1 = mu_pt * np.sin(mu_phi)
    pz1 = mu_pt * np.sinh(mu_eta)
    e1 = np.sqrt(np.maximum(px1**2 + py1**2 + pz1**2 + mu_mass**2, 0.0))
    px2 = tau_pt * np.cos(tau_phi)
    py2 = tau_pt * np.sin(tau_phi)
    pz2 = tau_pt * np.sinh(tau_eta)
    e2 = np.sqrt(np.maximum(px2**2 + py2**2 + pz2**2 + tau_mass**2, 0.0))
    px3 = met_pt * np.cos(met_phi)
    py3 = met_pt * np.sin(met_phi)
    e3 = met_pt
    mass2 = (e1 + e2 + e3) ** 2 - (px1 + px2 + px3) ** 2 - (py1 + py2 + py3) ** 2 - (pz1 + pz2) ** 2
    return np.sqrt(np.maximum(mass2, 0.0))


def first_passing(arrays: ak.Array, prefix: str, mask: ak.Array, extra_fields: tuple[str, ...] = ()) -> dict[str, np.ndarray]:
    order = ak.argsort(arrays[f"{prefix}_pt"], axis=1, ascending=False)
    sorted_mask = mask[order]
    sorted_indices = ak.local_index(mask, axis=1)[order]
    passing_indices = sorted_indices[sorted_mask]
    chosen = ak.pad_none(passing_indices, 1, clip=True)[:, 0]
    output: dict[str, np.ndarray] = {}
    for field in ("pt", "eta", "phi", "mass", "charge", *extra_fields):
        values = arrays[f"{prefix}_{field}"][order][sorted_mask]
        output[field] = ak.to_numpy(ak.fill_none(ak.firsts(values), np.nan))
    output["index"] = ak.to_numpy(ak.fill_none(chosen, -1)).astype(np.int64)
    return output


def scalar(arrays: ak.Array, name: str, default: float = np.nan) -> np.ndarray:
    if name not in arrays.fields:
        return np.full(len(arrays), default)
    return ak.to_numpy(ak.fill_none(arrays[name], default))


def clean_jet_variables(arrays: ak.Array, mu: dict[str, np.ndarray], tau: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    jet_pt = arrays["Jet_pt"]
    jet_eta = arrays["Jet_eta"]
    jet_phi = arrays["Jet_phi"]
    jet_mass = arrays["Jet_mass"]
    jet_btag = arrays["Jet_btag"]
    dr_mu = np.sqrt((jet_eta - ak.Array(mu["eta"])[:, None]) ** 2 + delta_phi(jet_phi, ak.Array(mu["phi"])[:, None]) ** 2)
    dr_tau = np.sqrt((jet_eta - ak.Array(tau["eta"])[:, None]) ** 2 + delta_phi(jet_phi, ak.Array(tau["phi"])[:, None]) ** 2)
    clean = (
        (jet_pt > CONFIG["jet"]["pt_min_gev"])
        & (abs(jet_eta) < CONFIG["jet"]["eta_abs_max"])
        & (dr_mu > CONFIG["jet"]["delta_r_lepton_min"])
        & (dr_tau > CONFIG["jet"]["delta_r_lepton_min"])
    )
    clean_pt = jet_pt[clean]
    clean_eta = jet_eta[clean]
    clean_phi = jet_phi[clean]
    clean_mass = jet_mass[clean]
    clean_btag = jet_btag[clean]
    n_clean = ak.to_numpy(ak.num(clean_pt, axis=1)).astype(np.int64)

    padded_pt = ak.pad_none(clean_pt, 2, clip=True)
    padded_eta = ak.pad_none(clean_eta, 2, clip=True)
    padded_phi = ak.pad_none(clean_phi, 2, clip=True)
    padded_mass = ak.pad_none(clean_mass, 2, clip=True)
    jet1_pt = ak.to_numpy(ak.fill_none(padded_pt[:, 0], np.nan))
    jet1_eta = ak.to_numpy(ak.fill_none(padded_eta[:, 0], np.nan))
    jet1_phi = ak.to_numpy(ak.fill_none(padded_phi[:, 0], np.nan))
    jet1_mass = ak.to_numpy(ak.fill_none(padded_mass[:, 0], np.nan))
    jet2_pt = ak.to_numpy(ak.fill_none(padded_pt[:, 1], np.nan))
    jet2_eta = ak.to_numpy(ak.fill_none(padded_eta[:, 1], np.nan))
    jet2_phi = ak.to_numpy(ak.fill_none(padded_phi[:, 1], np.nan))
    jet2_mass = ak.to_numpy(ak.fill_none(padded_mass[:, 1], np.nan))
    mjj = invariant_mass(jet1_pt, jet1_eta, jet1_phi, jet1_mass, jet2_pt, jet2_eta, jet2_phi, jet2_mass)
    detajj = np.abs(jet1_eta - jet2_eta)
    valid_btag = clean_btag[clean_btag >= 0]
    btag_max = ak.to_numpy(ak.fill_none(ak.max(valid_btag, axis=1), -1.0))
    return {
        "n_clean_jets": n_clean,
        "mjj": np.where(n_clean >= 2, mjj, np.nan),
        "delta_eta_jj": np.where(n_clean >= 2, detajj, np.nan),
        "jet1_pt": jet1_pt,
        "btag_max": btag_max,
        "has_positive_btag_score": btag_max > 0.0,
    }


def process_chunk(arrays: ak.Array) -> dict[str, np.ndarray]:
    trigger = (
        (scalar(arrays, "HLT_IsoMu24_eta2p1", 0.0) > 0)
        | (scalar(arrays, "HLT_IsoMu24", 0.0) > 0)
        | (scalar(arrays, "HLT_IsoMu17_eta2p1_LooseIsoPFTau20", 0.0) > 0)
    )
    mu_iso = arrays["Muon_pfRelIso04_all"]
    mu_mask = (
        (arrays["Muon_pt"] > CONFIG["muon"]["pt_min_gev"])
        & (abs(arrays["Muon_eta"]) < CONFIG["muon"]["eta_abs_max"])
        & (arrays["Muon_tightId"] > 0)
        & (mu_iso >= 0)
        & (mu_iso < CONFIG["muon"]["pfRelIso04_all_max"])
    )
    mu = first_passing(arrays, "Muon", mu_mask, ("pfRelIso04_all",))
    has_muon = mu["index"] >= 0

    tau_iso = arrays["Tau_relIso_all"]
    tau_pre_mask = (
        (arrays["Tau_pt"] > CONFIG["tau"]["pt_min_gev"])
        & (abs(arrays["Tau_eta"]) < CONFIG["tau"]["eta_abs_max"])
        & (arrays["Tau_idDecayMode"] > 0)
        & (arrays["Tau_idIsoTight"] > 0)
        & (arrays["Tau_idAntiMuTight"] > 0)
        & (tau_iso >= 0)
    )
    tau_dr_mu = np.sqrt(
        (arrays["Tau_eta"] - ak.Array(mu["eta"])[:, None]) ** 2
        + delta_phi(arrays["Tau_phi"], ak.Array(mu["phi"])[:, None]) ** 2
    )
    tau_mask = tau_pre_mask & (tau_dr_mu > CONFIG["tau"]["delta_r_mu_tau_min"])
    tau = first_passing(arrays, "Tau", tau_mask, ("relIso_all",))
    has_tau = tau["index"] >= 0

    met_pt = scalar(arrays, "MET_pt")
    met_phi = scalar(arrays, "MET_phi")
    mt = np.sqrt(np.maximum(2.0 * mu["pt"] * met_pt * (1.0 - np.cos(delta_phi(mu["phi"], met_phi))), 0.0))
    mvis = invariant_mass(mu["pt"], mu["eta"], mu["phi"], mu["mass"], tau["pt"], tau["eta"], tau["phi"], tau["mass"])
    maddmet = add_met_mass(mu["pt"], mu["eta"], mu["phi"], mu["mass"], tau["pt"], tau["eta"], tau["phi"], tau["mass"], met_pt, met_phi)
    px_vismet = mu["pt"] * np.cos(mu["phi"]) + tau["pt"] * np.cos(tau["phi"]) + met_pt * np.cos(met_phi)
    py_vismet = mu["pt"] * np.sin(mu["phi"]) + tau["pt"] * np.sin(tau["phi"]) + met_pt * np.sin(met_phi)
    pt_tautau_proxy = np.sqrt(px_vismet**2 + py_vismet**2)
    os_pair = mu["charge"] * tau["charge"] < 0
    pair = trigger & has_muon & has_tau
    os = pair & os_pair
    ss = pair & ~os_pair
    low_mt = os & (mt < CONFIG["regions"]["signal_mt_max_gev"])
    high_mt = os & (mt > CONFIG["regions"]["w_cr_mt_min_gev"])
    qcd_ss = ss & (mt < CONFIG["regions"]["signal_mt_max_gev"])
    z_rich = low_mt & (mvis >= CONFIG["regions"]["z_rich_mvis_min_gev"]) & (mvis <= CONFIG["regions"]["z_rich_mvis_max_gev"])

    jets = clean_jet_variables(arrays, mu, tau)
    vbf = (
        low_mt
        & (jets["n_clean_jets"] >= CONFIG["categories"]["vbf_njet_min"])
        & (jets["mjj"] > CONFIG["categories"]["vbf_mjj_min_gev"])
        & (jets["delta_eta_jj"] > CONFIG["categories"]["vbf_delta_eta_jj_min"])
    )
    boosted = low_mt & ~vbf & (jets["n_clean_jets"] >= CONFIG["categories"]["boosted_njet_min"])
    zero_jet = low_mt & ~vbf & ~boosted
    top_handle = pair & jets["has_positive_btag_score"] & (jets["n_clean_jets"] >= 1)

    category = np.full(len(arrays), "none", dtype="<U12")
    category[vbf] = "vbf"
    category[boosted] = "boosted"
    category[zero_jet] = "zero_jet"

    region = np.full(len(arrays), "other", dtype="<U16")
    region[low_mt] = "signal_region"
    region[high_mt] = "w_high_mt"
    region[qcd_ss] = "qcd_same_sign"

    region_exclusive = np.full(len(arrays), "other", dtype="<U20")
    region_exclusive[low_mt] = "signal_other"
    region_exclusive[high_mt] = "w_high_mt"
    region_exclusive[qcd_ss] = "qcd_same_sign"
    region_exclusive[top_handle] = "top_btag_handle"
    region_exclusive[z_rich] = "z_rich"

    keep_summary = pair | low_mt | high_mt | qcd_ss | z_rich | top_handle
    return {
        "run": scalar(arrays, "run", 0.0).astype(np.int64),
        "luminosityBlock": scalar(arrays, "luminosityBlock", 0.0).astype(np.int64),
        "event": scalar(arrays, "event", 0.0).astype(np.int64),
        "trigger": trigger,
        "has_muon": has_muon,
        "has_tau": has_tau,
        "pair": pair,
        "opposite_sign": os,
        "low_mt": low_mt,
        "is_signal_region": low_mt,
        "w_high_mt": high_mt,
        "is_w_high_mt": high_mt,
        "qcd_same_sign": qcd_ss,
        "is_same_sign": ss,
        "is_same_sign_low_mt": qcd_ss,
        "z_rich": z_rich,
        "is_z_rich": z_rich,
        "top_btag_handle": top_handle,
        "is_top_btag_handle": top_handle,
        "category": category,
        "region": region,
        "region_exclusive": region_exclusive,
        "mu_pt": mu["pt"],
        "mu_eta": mu["eta"],
        "mu_phi": mu["phi"],
        "mu_reliso": mu["pfRelIso04_all"],
        "tau_pt": tau["pt"],
        "tau_eta": tau["eta"],
        "tau_phi": tau["phi"],
        "tau_reliso": tau["relIso_all"],
        "met_pt": met_pt,
        "mt_mu_met": mt,
        "m_vis": mvis,
        "m_addmet": maddmet,
        "pt_tautau_proxy": pt_tautau_proxy,
        "n_clean_jets": jets["n_clean_jets"],
        "mjj": jets["mjj"],
        "delta_eta_jj": jets["delta_eta_jj"],
        "jet1_pt": jets["jet1_pt"],
        "btag_max": jets["btag_max"],
        "keep_summary": keep_summary,
    }


def init_nested(keys: list[str]) -> dict[str, dict[str, int]]:
    return {key: {} for key in keys}


def increment(mapping: dict[str, int], key: str, value: int) -> None:
    mapping[key] = mapping.get(key, 0) + int(value)


def process_sample(sample: dict[str, object]) -> tuple[dict[str, int], dict[str, int], list[dict[str, np.ndarray]]]:
    name = str(sample["name"])
    path = Path(sample["path"])
    log.info("Processing %s", name)
    tree = uproot.open(path)["Events"]
    available = [branch for branch in BRANCHES if branch in tree.keys()]
    cutflow = {step: 0 for step in CUTFLOW_STEPS}
    counts = {"signal": 0, "w_high_mt": 0, "qcd_same_sign": 0, "z_rich": 0, "top_btag_handle": 0}
    counts.update({"category_vbf": 0, "category_boosted": 0, "category_zero_jet": 0, "category_none": 0})
    chunks = []
    for arrays in tree.iterate(available, step_size=CHUNK_SIZE, library="ak"):
        derived = process_chunk(arrays)
        cutflow["events"] += len(arrays)
        cutflow["trigger"] += int(np.sum(derived["trigger"]))
        cutflow["muon_candidate"] += int(np.sum(derived["trigger"] & derived["has_muon"]))
        cutflow["tau_candidate"] += int(np.sum(derived["trigger"] & derived["has_muon"] & derived["has_tau"]))
        cutflow["mu_tau_pair"] += int(np.sum(derived["pair"]))
        cutflow["opposite_sign"] += int(np.sum(derived["opposite_sign"]))
        cutflow["low_mt_signal_region"] += int(np.sum(derived["low_mt"]))
        for region in ("signal", "w_high_mt", "qcd_same_sign", "z_rich", "top_btag_handle"):
            increment(counts, region, np.sum(derived[region] if region != "signal" else derived["low_mt"]))
        for category in ("vbf", "boosted", "zero_jet", "none"):
            increment(counts, f"category_{category}", np.sum(derived["category"] == category))
        keep = derived["keep_summary"]
        summary = {key: value[keep] for key, value in derived.items() if key != "keep_summary"}
        n_keep = int(np.sum(keep))
        summary["sample"] = np.full(n_keep, name, dtype="<U32")
        summary["role"] = np.full(n_keep, str(sample["role"]), dtype="<U16")
        chunks.append(summary)
    return cutflow, counts, chunks


def concatenate_chunks(chunks: list[dict[str, np.ndarray]]) -> dict[str, np.ndarray]:
    keys = sorted(chunks[0]) if chunks else []
    return {key: np.concatenate([chunk[key] for chunk in chunks]) for key in keys}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "models").mkdir(parents=True, exist_ok=True)
    cutflow: dict[str, object] = {"steps": CUTFLOW_STEPS, "samples": {}}
    region_yields: dict[str, object] = {"samples": {}}
    all_chunks: list[dict[str, np.ndarray]] = []
    for sample in SAMPLES:
        sample_cutflow, counts, chunks = process_sample(sample)
        cutflow["samples"][sample["name"]] = {"role": sample["role"], "counts": sample_cutflow}
        region_yields["samples"][sample["name"]] = {"role": sample["role"], "raw_counts": counts}
        all_chunks.extend(chunks)
    selected = concatenate_chunks(all_chunks)
    np.savez_compressed(OUT / "selected_events.npz", **selected)
    category_yields = {"categories": ["vbf", "boosted", "zero_jet"], "samples": {}}
    for sample in SAMPLES:
        mask = selected["sample"] == sample["name"]
        category_yields["samples"][sample["name"]] = {
            "role": sample["role"],
            "raw_counts": {
                category: int(np.sum(mask & (selected["category"] == category))) for category in category_yields["categories"]
            },
        }
    normalization = {
        "status": "blocking_for_phase4_absolute_templates",
        "resolved_in_phase3": False,
        "reason": "Reduced ROOT files contain no event or generator weights, pileup weights, embedded luminosity, or cross-section metadata.",
        "available_phase3_outputs": [
            "raw selected counts",
            "shape-normalized templates",
            "control-region raw yields for W high-mT normalization preparation",
        ],
        "integrated_luminosity": {
            "status": "unresolved_blocking_input",
            "no_circular_derivation": True,
            "phase3_action": (
                "Checked analysis-local reduced-file metadata and public CMS/CERN Open Data provenance records; "
                "did not compute luminosity from selected event counts, generated MC counts, or data/MC back-calculation."
            ),
            "checked_sources": [
                {
                    "source": "CERN Open Data record 12350",
                    "url": "https://opendata.cern.ch/record/12350",
                    "finding": "Identifies the CMS 2012 H to tau tau reduced outreach sample set and Run2012 TauPlusX inputs, but not an exact integrated luminosity for the localized Run2012B/C reduced ROOT files.",
                },
                {
                    "source": "Run2012B_TauPlusX reduced ROOT file from the HiggsTauTauReduced mirror",
                    "url": "https://root.cern.ch/files/HiggsTauTauReduced/Run2012B_TauPlusX.root",
                    "finding": "The reduced Events tree has run and luminosityBlock identifiers but no embedded integrated-luminosity metadata.",
                },
                {
                    "source": "Run2012C_TauPlusX reduced ROOT file from the HiggsTauTauReduced mirror",
                    "url": "https://root.cern.ch/files/HiggsTauTauReduced/Run2012C_TauPlusX.root",
                    "finding": "The reduced Events tree has run and luminosityBlock identifiers but no embedded integrated-luminosity metadata.",
                },
            ],
            "required_for_phase4": (
                "An official CMS Open Data luminosity record, luminosity JSON plus brilcalc-equivalent evaluation, "
                "or another citable CMS source for the exact certified Run2012B/C TauPlusX data subset represented by these reduced files."
            ),
            "impact": "Phase 4 cannot quote luminosity-normalized yields, cross sections, or production-normalized MC expectations until this input is sourced.",
        },
        "missing_citable_inputs": [
            "TauPlusX Run2012B/Run2012C effective integrated luminosity for the localized reduced files",
            "ggH and VBF 8 TeV production cross sections and branching fraction applicable to the reduced samples",
            "DYJetsToLL, TTbar, and W1/W2/W3 jet-bin cross sections",
            "W+jets exclusive jet-bin stitching prescription for W1/W2/W3 without inclusive WJets or W4",
            "official trigger, muon, tau, b-tag, and pileup scale-factor prescriptions for these reduced files",
        ],
        "anti_tuning_statement": "No MC sample has been manually scaled to data in Phase 3.",
    }
    write_json(OUT / "cutflow.json", cutflow)
    write_json(OUT / "region_yields.json", region_yields)
    write_json(OUT / "category_yields.json", category_yields)
    write_json(OUT / "normalization_inputs.json", normalization)
    write_json(OUT / "selection_config.json", CONFIG)
    append_session("Selection processing completed and machine-readable summaries were written.")


if __name__ == "__main__":
    main()
