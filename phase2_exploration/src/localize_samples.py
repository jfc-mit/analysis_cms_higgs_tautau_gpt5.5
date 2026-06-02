"""Build and validate the Phase 2 local sample manifest."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from urllib.request import Request, urlopen

import uproot
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "phase2_exploration" / "outputs"
BASE_URL = "https://root.cern.ch/files/HiggsTauTauReduced"
ROOT_INDEX = "https://root.cern.ch/files/HiggsTauTauReduced/"
WORKSHOP_SOURCE = "https://cms-opendata-workshop.github.io/workshop-lesson-id-selection/"
CMS_2014 = "CMS JHEP 05 (2014) 104, DOI:10.1007/JHEP05(2014)104, arXiv:1401.5041"
CMS_2018 = "CMS Phys. Lett. B 779 (2018) 283, DOI:10.1016/j.physletb.2018.02.004, arXiv:1708.00373"
AN_CONTEXT = "phase1_strategy/outputs/STRATEGY.md and phase2_exploration/outputs/EXPLORATION.md"

CONFIRMED = [
    ("Run2012B_TauPlusX", "2012 TauPlusX collision data", "data", "Run2012B_TauPlusX.root"),
    ("Run2012C_TauPlusX", "2012 TauPlusX collision data", "data", "Run2012C_TauPlusX.root"),
    ("GluGluToHToTauTau", "ggH H to tau tau signal", "signal", "GluGluToHToTauTau.root"),
    ("VBF_HToTauTau", "VBF H to tau tau signal", "signal", "VBF_HToTauTau.root"),
    ("DYJetsToLL", "Drell-Yan Z/gamma* to ll background", "background", "DYJetsToLL.root"),
    ("TTbar", "ttbar background", "background", "TTbar.root"),
    ("W1JetsToLNu", "W+1 jet background", "background", "W1JetsToLNu.root"),
    ("W2JetsToLNu", "W+2 jets background", "background", "W2JetsToLNu.root"),
    ("W3JetsToLNu", "W+3 jets background", "background", "W3JetsToLNu.root"),
]

PAPER_LEVEL = [
    (
        "Run2012A_TauPlusX",
        "2012 TauPlusX collision data, other eras",
        "data",
        "deferred-AOD-conversion",
        "Not listed in the reduced mirror. If the CMS Open Data portal has full AOD for additional TauPlusX eras, later phases should add them through an explicit AOD-to-reduced conversion rather than downloading AOD blindly.",
    ),
    (
        "Run2012D_TauPlusX",
        "2012 TauPlusX collision data, other eras",
        "data",
        "deferred-AOD-conversion",
        "Not listed in the reduced mirror. Later phases can add full-open-data TauPlusX eras only after confirming trigger/luminosity compatibility and a maintained conversion path.",
    ),
    (
        "DYJetsToTauTau_embedded",
        "embedded Z to tau tau dominant irreducible background",
        "background",
        "missing-reduced",
        "CMS JHEP 05 (2014) 104 models the dominant Z to tau tau contribution with embedded samples; no embedded reduced ROOT file is present in the ROOT mirror.",
    ),
    (
        "DYJets_ZToMuMu_EE_fakes",
        "Z to mumu/ee lepton-to-tau fake components",
        "background",
        "missing-reduced",
        "The reduced DYJetsToLL file is present, but no separate reduced fake-component files are listed. Phase 3 can derive components from DYJetsToLL generator/object matching if supported.",
    ),
    (
        "QCD_Multijet",
        "QCD multijet jet-to-tau fake background",
        "background",
        "missing-reduced",
        "CMS papers estimate QCD from data control regions. No reduced QCD ROOT sample is present in the mirror; this should remain a data-driven same-sign/anti-isolation estimate.",
    ),
    (
        "WW",
        "diboson background",
        "background",
        "deferred-AOD-conversion",
        "CMS papers include diboson backgrounds from simulation. No WW reduced file is present in the mirror; use AOD conversion only if needed.",
    ),
    (
        "WZ",
        "diboson background",
        "background",
        "deferred-AOD-conversion",
        "CMS papers include diboson backgrounds from simulation. No WZ reduced file is present in the mirror; use AOD conversion only if needed.",
    ),
    (
        "ZZ",
        "diboson background",
        "background",
        "deferred-AOD-conversion",
        "CMS papers include diboson backgrounds from simulation. No ZZ reduced file is present in the mirror; use AOD conversion only if needed.",
    ),
    (
        "SingleTop",
        "single top background",
        "background",
        "deferred-AOD-conversion",
        "CMS papers include single-top-quark production from simulation. No reduced single-top file is present in the mirror; use AOD conversion only if needed.",
    ),
    (
        "W4JetsToLNu",
        "W+4 jet background",
        "background",
        "missing-reduced",
        "The mirror provides W1/W2/W3 jet bins only. Later phases should determine whether W4/AOD is needed for jet-bin stitching or whether W3 is the available reduced endpoint.",
    ),
    (
        "WJetsToLNu_inclusive",
        "inclusive W+jets background",
        "background",
        "missing-reduced",
        "The mirror provides exclusive W1/W2/W3 reduced files but no inclusive WJetsToLNu file.",
    ),
    (
        "DYJets_jet_binned_or_mass_binned",
        "additional DY categories",
        "background",
        "missing-reduced",
        "The mirror provides only DYJetsToLL.root. Paper-level DY refinements must be derived from that file or deferred to AOD conversion.",
    ),
    (
        "WH_HToTauTau",
        "associated-production H to tau tau signal",
        "signal",
        "deferred-AOD-conversion",
        "CMS JHEP 05 (2014) 104 includes associated WH/ZH production in the broader analysis. The mirror has no WH reduced file; it is not required for the current mu tau_h baseline unless later categories target associated production.",
    ),
    (
        "ZH_HToTauTau",
        "associated-production H to tau tau signal",
        "signal",
        "deferred-AOD-conversion",
        "CMS JHEP 05 (2014) 104 includes associated WH/ZH production in the broader analysis. The mirror has no ZH reduced file; it is not required for the current mu tau_h baseline unless later categories target associated production.",
    ),
    (
        "ttH_HToTauTau",
        "ttH H to tau tau signal",
        "signal",
        "deferred-AOD-conversion",
        "CMS JHEP 05 (2014) 104 names ttH signal generation in the full MC program. The mirror has no ttH reduced file; it is not required for the current baseline categories.",
    ),
    (
        "HToWW",
        "H to WW background or coupling-study signal component",
        "background",
        "deferred-AOD-conversion",
        "CMS papers discuss H to WW contributions in some channels and coupling scans. No reduced HToWW file is present, and this mu tau_h baseline treats it as deferred.",
    ),
]


def head_size(url: str) -> int | None:
    try:
        with urlopen(Request(url, method="HEAD"), timeout=30) as response:
            value = response.headers.get("content-length")
    except OSError:
        return None
    return int(value) if value is not None else None


def confirmed_entry(name: str, process: str, role: str, file_name: str) -> dict[str, object]:
    local_dir = "data" if role == "data" else "mc"
    path = ROOT / local_dir / file_name
    url = f"{BASE_URL}/{file_name}"
    expected_size = head_size(url)
    exists = path.exists()
    size = path.stat().st_size if exists else 0
    status = "missing-reduced"
    events = None
    validation = {"events_tree_open": False}
    if exists:
        if expected_size is None or size == expected_size:
            try:
                tree = uproot.open(path)["Events"]
                events = int(tree.num_entries)
                validation["events_tree_open"] = True
                status = "downloaded"
            except OSError as exc:
                status = "failed"
                validation["error"] = str(exc)
        else:
            status = "failed"
            validation["error"] = f"local size {size} does not match expected {expected_size}"
    return {
        "sample": name,
        "process": process,
        "role": role,
        "source_urls": [url, ROOT_INDEX, WORKSHOP_SOURCE],
        "local_path": str(path.relative_to(ROOT)),
        "size_bytes": size,
        "expected_size_bytes": expected_size,
        "status": status,
        "source_citation": "ROOT reduced sample index; CMS Open Data workshop object ID page; CERN Open Data reduced H to tau tau context.",
        "analysis_blocking": status == "failed",
        "notes": "Downloaded reduced ROOT sample for current Phase 2/3 use." if status == "downloaded" else "Reduced file is listed but local validation did not pass.",
        "validation": validation,
        "events": events,
    }


def paper_entry(
    name: str,
    process: str,
    role: str,
    status: str,
    notes: str,
) -> dict[str, object]:
    return {
        "sample": name,
        "process": process,
        "role": role,
        "source_urls": [
            ROOT_INDEX,
            "https://doi.org/10.1007/JHEP05(2014)104",
            "https://doi.org/10.1016/j.physletb.2018.02.004",
        ],
        "local_path": None,
        "size_bytes": None,
        "expected_size_bytes": None,
        "status": status,
        "source_citation": f"{CMS_2014}; {CMS_2018}; {AN_CONTEXT}",
        "notes": notes,
        "analysis_blocking": False,
        "downstream_final_an_obligation": (
            "The final analysis note and final summary must name this unavailable "
            "paper-level component, state that no corresponding reduced 2012 CMS "
            "Open Data sample or suitable substitute was used, and discuss the "
            "limitation or expected impact on the reduced-sample analysis."
        ),
        "validation": {"events_tree_open": False},
        "events": None,
    }


def build_manifest() -> dict[str, object]:
    samples = [confirmed_entry(*item) for item in CONFIRMED]
    samples.extend(paper_entry(*item) for item in PAPER_LEVEL)
    return {
        "schema_version": 1,
        "analysis": "higgs_tautau",
        "created_utc": "2026-06-02",
        "policy": "Use all currently available reduced 2012 CMS Open Data samples relevant to the mu tau_h H to tau tau analysis; defer full AOD conversion until a later phase explicitly needs it.",
        "sources": {
            "root_reduced_index": ROOT_INDEX,
            "cms_open_data_workshop": WORKSHOP_SOURCE,
            "cms_2014": CMS_2014,
            "cms_2018": CMS_2018,
        },
        "samples": samples,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest()
    path = OUT / "local_sample_manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    failed = [item["sample"] for item in manifest["samples"] if item["status"] == "failed"]
    downloaded = [item["sample"] for item in manifest["samples"] if item["status"] == "downloaded"]
    log.info("Wrote %s", path)
    log.info("Validated %d local reduced samples", len(downloaded))
    if failed:
        raise SystemExit(f"Local sample validation failed for: {', '.join(failed)}")


if __name__ == "__main__":
    main()
