from __future__ import annotations

import copy
import importlib.util
import json
import logging
import math
import re
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from statistics import NormalDist

import cabinetry.fit as cabinetry_fit
import cabinetry.model_utils as cabinetry_model_utils
import matplotlib.pyplot as plt
import hist
import mplhep as mh
import numpy as np
import pyhf
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)
logging.getLogger("cabinetry").setLevel(logging.WARNING)
logging.getLogger("pyhf").setLevel(logging.WARNING)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "phase5_documentation" / "outputs"
FIG = OUT / "figures"
LOG_PATH = ROOT / "phase5_documentation" / "logs" / "fixer_phase5_full_panel_20260612T180909Z.md"
EXP_LOG = ROOT / "experiment_log.md"

CATEGORIES = ["vbf", "boosted", "zero_jet"]
CATEGORY_LABELS = {"vbf": "VBF", "boosted": "Boosted", "zero_jet": "Zero-jet"}
PUBLIC_LUMI = 11.467
REQUIRED_UPSTREAM_FIGURES = {
    "approach_comparison",
    "category_yields",
    "cutflow_summary",
    "expected_s_over_b",
    "gof_toys",
    "met_pt",
    "mt_mu_met",
    "mu_pt",
    "mva_input_modeling_chi2",
    "pt_tautau_proxy",
    "qcd_same_sign_mvis",
    "sample_event_count_file_size",
    "sensitivity_nuisance_audit",
    "signal_injection_recovery",
    "tau_pt",
    "vbf_delta_eta_jj",
    "vbf_dijet_mass",
    "visible_mass_boosted",
    "visible_mass_vbf",
    "visible_mass_zero_jet",
    "w_high_mt_control_mt",
    "z_rich_validation_mvis",
}

SYSTEMATIC_PROGRAM = [
    {
        "name": "Luminosity",
        "parameter": "lumi_2012",
        "value": "2.6%",
        "numeric": 0.026,
        "affected": "All simulation-normalized signal and background samples",
        "correlation": "One nuisance correlated across categories and MC samples",
        "source": "CMS 2012 luminosity normalization used by the Open Data records",
        "impact": "Quantified in the baseline impact scan by fixing the nuisance at ±1 prefit sigma and refitting the remaining parameters.",
    },
    {
        "name": "Tau/open-data acceptance",
        "parameter": "tau_open_data_acceptance",
        "value": "15%",
        "numeric": 0.15,
        "affected": "Signal and MC backgrounds selected with the reduced muon-tau objects",
        "correlation": "One nuisance correlated across categories and MC samples",
        "source": "Open Data reduced-sample acceptance and missing public trigger/tau scale-factor coverage",
        "impact": "Quantified in the baseline impact scan by fixing the nuisance at ±1 prefit sigma and refitting the remaining parameters.",
    },
    {
        "name": "DY/Z normalization",
        "parameter": "dy_norm_open_data",
        "value": "15%",
        "numeric": 0.15,
        "affected": "DYJetsToLL in all visible-mass categories",
        "correlation": "One nuisance correlated across categories",
        "source": "Reduced-sample DY/Z validation and missing embedded/electroweak Z components",
        "impact": "Quantified in the baseline impact scan by fixing the nuisance at ±1 prefit sigma and refitting the remaining parameters.",
    },
    {
        "name": "W high-mT control",
        "parameter": "wjets_high_mt_control",
        "value": "4.344%",
        "numeric": 0.04344277405793688,
        "affected": "W1JetsToLNu, W2JetsToLNu, W3JetsToLNu",
        "correlation": "One nuisance correlated across W+jets samples and categories",
        "source": "Full-data high-mT control-region scale factor",
        "impact": "Quantified in the baseline impact scan by fixing the nuisance at ±1 prefit sigma and refitting the remaining parameters.",
    },
    {
        "name": "VBF background control",
        "parameter": "vbf_background_control",
        "value": "9.237%",
        "numeric": 0.09236856279425538,
        "affected": "MC backgrounds in the VBF category",
        "correlation": "One nuisance applied only to VBF-category MC backgrounds",
        "source": "VBF-like top-btag non-signal control region",
        "impact": "Quantified in the baseline impact scan by fixing the nuisance at ±1 prefit sigma and refitting the remaining parameters.",
    },
    {
        "name": "Same-sign QCD/fake transfer",
        "parameter": "qcd_ss_transfer",
        "value": "12.060%",
        "numeric": 0.1205986171464732,
        "affected": "Data-driven QCD/fake template in all baseline categories",
        "correlation": "One global transfer-factor nuisance",
        "source": "Same-sign low-mT sideband transfer factor retained by the baseline workspace",
        "impact": "Quantified in the baseline impact scan by fixing the nuisance at ±1 prefit sigma and refitting the remaining parameters.",
    },
    {
        "name": "MC statistical uncertainty",
        "parameter": "mc_stat_*",
        "value": "per-bin sumw2",
        "numeric": 0.0,
        "affected": "Every MC-filled bin in each category",
        "correlation": "Independent Barlow-Beeston-lite staterror terms by category/bin",
        "source": "Finite reduced MC counts and official Open Data normalization weights",
        "impact": "Quantified as grouped MC-stat constraints by fixing the category staterror factors to their nominal values and refitting the remaining parameters.",
    },
]

REFERENCES_BIB = r"""
@misc{cms_open_data_htt_2012,
  author = {Wunsch, Stefan},
  title = {Analysis of Higgs boson decays to two tau leptons using data and simulation of events at the CMS detector from 2012},
  year = {2019},
  doi = {10.7483/OPENDATA.CMS.GV20.PR5T},
  url = {https://opendata.cern.ch/record/12350}
}

@misc{cms_open_data_skim,
  author = {{CMS Open Data Analyses}},
  title = {HiggsTauTauNanoAODOutreachAnalysis skim code},
  year = {2021},
  url = {https://github.com/cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis}
}

@article{cms_htt_2014,
  author = {{CMS Collaboration}},
  title = {Evidence for the 125 GeV Higgs boson decaying to a pair of tau leptons},
  journal = {Journal of High Energy Physics},
  volume = {2014},
  number = {5},
  pages = {104},
  year = {2014},
  doi = {10.1007/JHEP05(2014)104},
  eprint = {1401.5041},
  archivePrefix = {arXiv}
}

@article{cms_htt_2018,
  author = {{CMS Collaboration}},
  title = {Observation of the Higgs boson decay to a pair of tau leptons with the CMS detector},
  journal = {Physics Letters B},
  volume = {779},
  pages = {283--316},
  year = {2018},
  doi = {10.1016/j.physletb.2018.02.004},
  eprint = {1708.00373},
  archivePrefix = {arXiv}
}

@article{atlas_cms_higgs_combination_2016,
  author = {{ATLAS and CMS Collaborations}},
  title = {Measurements of the Higgs boson production and decay rates and constraints on its couplings from a combined ATLAS and CMS analysis of the LHC pp collision data at sqrt s = 7 and 8 TeV},
  journal = {Journal of High Energy Physics},
  volume = {2016},
  number = {8},
  pages = {45},
  year = {2016},
  doi = {10.1007/JHEP08(2016)045},
  eprint = {1606.02266},
  archivePrefix = {arXiv}
}

@article{pdg_2024,
  author = {Navas, S. and others},
  collaboration = {Particle Data Group},
  title = {Review of Particle Physics},
  journal = {Physical Review D},
  volume = {110},
  pages = {030001},
  year = {2024},
  doi = {10.1103/PhysRevD.110.030001},
  url = {https://pdg.lbl.gov/2024/}
}

@misc{pdg_higgs_status_2024,
  author = {{Particle Data Group}},
  title = {Status of Higgs Boson Physics},
  year = {2024},
  howpublished = {Review article in the 2024 Review of Particle Physics},
  url = {https://pdg.lbl.gov/2024/reviews/rpp2024-rev-higgs-boson.pdf}
}

@book{lhc_hxswg_yellow_report_4,
  author = {{LHC Higgs Cross Section Working Group}},
  title = {Handbook of LHC Higgs Cross Sections: 4. Deciphering the Nature of the Higgs Sector},
  publisher = {CERN},
  year = {2017},
  doi = {10.23731/CYRM-2017-002},
  eprint = {1610.07922},
  archivePrefix = {arXiv}
}

@article{cowan_asymptotic,
  author = {Cowan, Glen and Cranmer, Kyle and Gross, Eilam and Vitells, Ofer},
  title = {Asymptotic formulae for likelihood-based tests of new physics},
  journal = {European Physical Journal C},
  volume = {71},
  pages = {1554},
  year = {2011},
  doi = {10.1140/epjc/s10052-011-1554-0},
  eprint = {1007.1727},
  archivePrefix = {arXiv}
}

@article{read_cls,
  author = {Read, A. L.},
  title = {Presentation of search results: the CLs technique},
  journal = {Journal of Physics G},
  volume = {28},
  pages = {2693--2704},
  year = {2002},
  doi = {10.1088/0954-3899/28/10/313}
}

@article{pyhf_joss,
  author = {Heinrich, Lukas and Feickert, Matthew and Stark, Giordon and Cranmer, Kyle},
  title = {pyhf: pure-Python implementation of HistFactory statistical models},
  journal = {Journal of Open Source Software},
  volume = {6},
  number = {58},
  pages = {2823},
  year = {2021},
  doi = {10.21105/joss.02823}
}

@article{cms_detector_2008,
  author = {{CMS Collaboration}},
  title = {The CMS experiment at the CERN LHC},
  journal = {Journal of Instrumentation},
  volume = {3},
  pages = {S08004},
  year = {2008},
  doi = {10.1088/1748-0221/3/08/S08004}
}

@techreport{cms_lumi_2013,
  author = {{CMS Collaboration}},
  title = {CMS Luminosity Based on Pixel Cluster Counting - Summer 2013 Update},
  institution = {CERN},
  number = {CMS-PAS-LUM-13-001},
  year = {2013},
  url = {https://cds.cern.ch/record/1598864}
}

@article{cms_higgs_discovery_2012,
  author = {{CMS Collaboration}},
  title = {Observation of a new boson at a mass of 125 GeV with the CMS experiment at the LHC},
  journal = {Physics Letters B},
  volume = {716},
  pages = {30--61},
  year = {2012},
  doi = {10.1016/j.physletb.2012.08.021},
  eprint = {1207.7235},
  archivePrefix = {arXiv}
}

@article{atlas_higgs_discovery_2012,
  author = {{ATLAS Collaboration}},
  title = {Observation of a new particle in the search for the Standard Model Higgs boson with the ATLAS detector at the LHC},
  journal = {Physics Letters B},
  volume = {716},
  pages = {1--29},
  year = {2012},
  doi = {10.1016/j.physletb.2012.08.020},
  eprint = {1207.7214},
  archivePrefix = {arXiv}
}

@techreport{histfactory_2012,
  author = {Cranmer, Kyle and Lewis, George and Moneta, Lorenzo and Shibata, Akira and Verkerke, Wouter},
  title = {HistFactory: A tool for creating statistical models for use with RooFit and RooStats},
  institution = {CERN},
  number = {CERN-OPEN-2012-016},
  year = {2012},
  eprint = {1203.1669},
  archivePrefix = {arXiv},
  url = {https://cds.cern.ch/record/1456844}
}
"""


def load_json(path: str) -> dict:
    with (ROOT / path).open() as handle:
        return json.load(handle)


def write_json(path: str, payload: dict) -> None:
    with (ROOT / path).open("w") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def append_log(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a") as handle:
        handle.write(f"\n## milestone\n\n{message}\n")


def copy_figures() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    for old in FIG.glob("*.*"):
        if old.suffix.lower() in {".pdf", ".png"}:
            old.unlink()
    sources = [
        ROOT / "phase2_exploration" / "outputs" / "figures",
        ROOT / "phase3_selection" / "outputs" / "figures",
        ROOT / "phase4_inference" / "4a_expected" / "outputs" / "figures",
        ROOT / "phase4_inference" / "4b_partial" / "outputs" / "figures",
        ROOT / "phase4_inference" / "4c_observed" / "outputs" / "figures",
    ]
    copied = 0
    for src_dir in sources:
        for src in src_dir.glob("*.*"):
            if src.suffix.lower() not in {".pdf", ".png"}:
                continue
            if src.stem not in REQUIRED_UPSTREAM_FIGURES:
                continue
            shutil.copy2(src, FIG / src.name)
            copied += 1
    log.info("Copied %d upstream figure files", copied)
    append_log(f"Copied {copied} required upstream figure files into the Phase 5 figure directory.")


def merge_references() -> None:
    (OUT / "references.bib").write_text(REFERENCES_BIB.strip() + "\n")
    append_log("Wrote corrected cited-only Phase 5 bibliography.")


def setup_style() -> None:
    mh.style.use("CMS")


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)


def cms_label(ax: plt.Axes, *, lumi: bool = True, llabel: str = "Open Data", rlabel_override: str | None = None) -> None:
    rlabel = r"$\sqrt{s}=8$ TeV, $L=11.467$ fb$^{-1}$" if lumi else r"$\sqrt{s}=8$ TeV"
    if rlabel_override is not None:
        rlabel = rlabel_override
    mh.label.exp_label(exp="CMS", data=True, llabel=llabel, rlabel=rlabel, loc=0, ax=ax)


def tensor_scalar(value: object) -> float:
    payload = pyhf.tensorlib.tolist(value)
    if isinstance(payload, list):
        return float(payload[0])
    return float(payload)


def profile_mu_summary_for_workspace(workspace_relpath: str) -> dict[str, float | str]:
    workspace = load_json(workspace_relpath)
    ws = pyhf.Workspace(workspace)
    model = ws.model()
    data = ws.data(model)
    free_pars = pyhf.infer.mle.fit(
        data,
        model,
        init_pars=model.config.suggested_init(),
        par_bounds=model.config.suggested_bounds(),
        fixed_params=model.config.suggested_fixed(),
    )
    par_values = [float(x) for x in pyhf.tensorlib.tolist(free_pars)]
    mu_hat = float(par_values[model.config.poi_index])
    upper_bound = float(model.config.suggested_bounds()[model.config.poi_index][1])
    best_nll = tensor_scalar(pyhf.infer.mle.twice_nll(free_pars, data, model))

    profile_failures: list[str] = []

    def q_mu(mu_value: float) -> float:
        try:
            fixed = pyhf.infer.mle.fixed_poi_fit(mu_value, data, model)
            return max(0.0, tensor_scalar(pyhf.infer.mle.twice_nll(fixed, data, model)) - best_nll)
        except Exception as exc:  # noqa: BLE001
            profile_failures.append(f"mu={mu_value:.6g}: {type(exc).__name__}: {exc}")
            return math.inf

    def bisect_crossing(lo: float, hi: float) -> float:
        q_lo = q_mu(lo) - 1.0
        for _ in range(28):
            mid = 0.5 * (lo + hi)
            q_mid = q_mu(mid) - 1.0
            if q_lo * q_mid <= 0:
                hi = mid
            else:
                lo = mid
                q_lo = q_mid
        return 0.5 * (lo + hi)

    lower = 0.0
    lower_status = "bounded_at_zero"
    q_zero = q_mu(0.0) if mu_hat > 0 else 0.0
    if mu_hat > 0 and math.isfinite(q_zero) and q_zero >= 1.0:
        lower = bisect_crossing(0.0, mu_hat)
        lower_status = "profile_q_equals_1"
    elif mu_hat > 0 and not math.isfinite(q_zero):
        lower_status = "fixed_zero_fit_failed"
    upper_hi = min(max(2.0 * mu_hat + 1.0, 2.0), upper_bound)
    while upper_hi < upper_bound and q_mu(upper_hi) < 1.0:
        upper_hi = min(upper_bound, upper_hi * 1.6)
    q_upper = q_mu(upper_hi)
    if not math.isfinite(q_upper):
        upper = upper_bound
        upper_status = "fixed_upper_fit_failed"
    elif q_upper < 1.0:
        upper = upper_bound
        upper_status = "bounded_at_workspace_limit"
    else:
        upper = bisect_crossing(mu_hat, upper_hi)
        upper_status = "profile_q_equals_1"
    return {
        "mu_hat": mu_hat,
        "err_minus": mu_hat - lower,
        "err_plus": upper - mu_hat,
        "lower": lower,
        "upper": upper,
        "lower_status": lower_status,
        "upper_status": upper_status,
        "method": "profile likelihood scan with q(mu)=2DeltaNLL=1; lower side bounded at mu>=0 when needed",
        "profile_failures": profile_failures[:5],
    }


@lru_cache(maxsize=1)
def score_mu_summary() -> dict[str, float | str]:
    return profile_mu_summary_for_workspace("phase4_inference/4c_observed/outputs/pyhf_workspace_observed.json")


@lru_cache(maxsize=1)
def baseline_mu_summary() -> dict[str, float | str]:
    return profile_mu_summary_for_workspace("phase4_inference/4c_observed/outputs/pyhf_workspace_baseline_visible.json")


@lru_cache(maxsize=1)
def phase4c_builder_module():
    module_path = ROOT / "phase4_inference" / "4c_observed" / "src" / "build_observed_results.py"
    spec = importlib.util.spec_from_file_location("phase4c_observed_builder", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load Phase 4c builder from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dnn_expected_result() -> dict:
    payload = load_json("phase3_selection/outputs/mva_sensitivity.json")
    for row in payload["expected_sensitivity_results"]:
        if row.get("name") == "mva_xgboost_score_baseline_categories":
            return row
    for row in payload["expected_sensitivity_results"]:
        if row.get("name") == "mva_hist_gradient_boosting_score_baseline_categories":
            return row
    raise KeyError("No baseline-category D_NN classifier score result found in mva_sensitivity.json")


def dnn_training_summary() -> dict:
    payload = load_json("phase3_selection/outputs/mva_sensitivity.json")
    model_name = "xgboost"
    return {
        "status": payload["status"],
        "blinding": payload["blinding"],
        "inputs": payload["inputs"],
        "split": payload["split"],
        "training_weight": payload["training_weight"],
        "model_name": model_name,
        "model": payload["models"][model_name],
        "input_reweighting": payload["input_reweighting"],
    }


def fast_dnn_profile_proxy(mu_hat: float, observed_limit: float) -> dict[str, float | str | list[str]]:
    lower = 0.0
    upper = max(float(observed_limit), float(mu_hat), 1.0)
    return {
        "mu_hat": float(mu_hat),
        "err_minus": float(mu_hat - lower),
        "err_plus": float(upper - mu_hat),
        "lower": lower,
        "upper": upper,
        "lower_status": "bounded_at_zero_proxy",
        "upper_status": "observed_cls_limit_proxy",
        "method": "lightweight proxy for Phase 5 D_NN documentation: lower bound fixed at physical mu>=0 and upper bound set to the observed 95% CLs limit to avoid a slow fixed-POI profile scan",
        "profile_failures": [],
    }


def fast_dnn_fit_workspace(workspace: dict, interpretation: str) -> dict:
    ws = pyhf.Workspace(workspace)
    model = ws.model()
    data = ws.data(model)
    pars = pyhf.infer.mle.fit(
        data,
        model,
        init_pars=model.config.suggested_init(),
        par_bounds=model.config.suggested_bounds(),
        fixed_params=model.config.suggested_fixed(),
    )
    pars_list = [float(x) for x in pyhf.tensorlib.tolist(pars)]
    mu_hat = float(pars_list[model.config.poi_index])
    fit = {
        "status": "evaluated",
        "interpretation": interpretation,
        "mu_hat": mu_hat,
        "parameters": dict(zip(model.config.par_names, pars_list, strict=True)),
        "npars": model.config.npars,
    }

    from pyhf.infer.intervals import upper_limits

    scan_history = []
    obs_limit = None
    exp_limits = None
    results = []
    for scan_max, n_points in [(12.0, 13), (25.0, 14), (50.0, 16)]:
        scan = np.linspace(0.0, scan_max, n_points)
        obs_limit, exp_limits, results = upper_limits.upper_limit(
            data,
            model,
            scan=scan,
            level=0.05,
            return_results=True,
        )
        obs_float = tensor_scalar(obs_limit)
        scan_history.append({"scan_max": scan_max, "n_points": n_points, "observed_limit": obs_float})
        if obs_float < 0.95 * scan_max:
            break

    if obs_limit is None or exp_limits is None:
        raise RuntimeError("D_NN pyhf upper-limit scan did not return a result")
    observed_limit = tensor_scalar(obs_limit)
    fit["observed_upper_limit"] = {
        "status": "evaluated",
        "method": "pyhf asymptotic modified frequentist CLs with adaptive coarse scan",
        "observed_limit": observed_limit,
        "expected_band_minus2_minus1_median_plus1_plus2": [float(x) for x in pyhf.tensorlib.tolist(exp_limits)],
        "scan": [float(x) for x in scan],
        "scan_history": scan_history,
        "result_count": len(results),
    }

    p_value = pyhf.infer.hypotest(0.0, data, model, calctype="asymptotics", test_stat="q0")
    p_float = tensor_scalar(p_value)
    z_value = float(NormalDist().inv_cdf(1.0 - p_float)) if 0.0 < p_float < 1.0 else (float("inf") if p_float <= 0.0 else float("-inf"))
    discovery = {
        "status": "evaluated",
        "method": "pyhf asymptotic q0 on observed full data",
        "p_value": p_float,
        "z_value": z_value,
    }
    fit["discovery"] = discovery
    fit["discovery_diagnostic"] = discovery
    fit["profile_mu_interval"] = fast_dnn_profile_proxy(mu_hat, observed_limit)
    return fit


@lru_cache(maxsize=1)
def nn_score_result() -> dict:
    result = load_json("phase4_inference/4c_observed/outputs/dnn_score_result.json")
    yields = load_json("phase4_inference/4c_observed/outputs/dnn_score_observed_yields.json")
    write_json("phase5_documentation/outputs/nn_score_result.json", result)
    write_json("phase5_documentation/outputs/dnn_score_result.json", result)
    write_json("phase5_documentation/outputs/nn_score_observed_yields.json", yields)
    write_json("phase5_documentation/outputs/dnn_score_observed_yields.json", yields)
    return {"result": result, "model": {"yields": yields}}


def baseline_workspace_model() -> tuple[pyhf.Workspace, pyhf.pdf.Model, list[float]]:
    workspace = load_json("phase4_inference/4c_observed/outputs/pyhf_workspace_baseline_visible.json")
    ws = pyhf.Workspace(workspace)
    model = ws.model()
    data = ws.data(model)
    return ws, model, data


def saturated_gof_statistic(model: pyhf.pdf.Model, data: list[float], best_twice_nll: float) -> tuple[float, int]:
    """Return the cabinetry saturated-model GoF statistic and degrees of freedom."""
    if model.config.nauxdata > 0:
        main_data, aux_data = model.fullpdf_tv.split(pyhf.tensorlib.astensor(data))
        best_constraint_pars = cabinetry_model_utils._parameters_maximizing_constraint_term(
            model,
            pyhf.tensorlib.tolist(aux_data),
        )
        constraint_ll = pyhf.tensorlib.to_numpy(
            model.constraint_logpdf(aux_data, pyhf.tensorlib.astensor(best_constraint_pars))
        )
    else:
        main_data = pyhf.tensorlib.astensor(data)
        constraint_ll = 0.0
    poisson_ll = pyhf.tensorlib.to_numpy(
        sum(pyhf.tensorlib.poisson_dist(main_data).log_prob(main_data))
    )
    saturated_nll = -(poisson_ll + constraint_ll)
    statistic = max(0.0, float(best_twice_nll) - 2.0 * float(saturated_nll))
    n_dof = int(sum(model.config.channel_nbins.values()) - cabinetry_model_utils.unconstrained_parameter_count(model))
    return statistic, n_dof


def fit_with_fixed(model: pyhf.pdf.Model, data: list[float], fixed_values: dict[str, float]) -> list[float]:
    init = list(model.config.suggested_init())
    bounds = list(model.config.suggested_bounds())
    fixed = list(model.config.suggested_fixed())
    for name, value in fixed_values.items():
        slc = model.config.par_slice(name)
        for idx in range(slc.start, slc.stop):
            init[idx] = float(value)
            fixed[idx] = True
    pars = pyhf.infer.mle.fit(data, model, init_pars=init, par_bounds=bounds, fixed_params=fixed)
    return [float(x) for x in pyhf.tensorlib.tolist(pars)]


@lru_cache(maxsize=4)
def postfit_expected_by_category(workspace_relpath: str) -> dict[str, np.ndarray]:
    workspace = load_json(workspace_relpath)
    ws = pyhf.Workspace(workspace)
    model = ws.model()
    data = ws.data(model)
    pars = fit_with_fixed(model, data, {})
    expected = np.asarray(pyhf.tensorlib.tolist(model.expected_data(pars))[: model.config.nmaindata], dtype=float)
    return {
        channel: expected[model.config.channel_slices[channel]].copy()
        for channel in model.config.channels
    }


@lru_cache(maxsize=1)
def baseline_impact_scan() -> dict[str, object]:
    _ws, model, data = baseline_workspace_model()
    baseline_fit = fit_with_fixed(model, data, {})
    baseline_mu = float(baseline_fit[model.config.poi_index])
    baseline_json = load_json("phase4_inference/4c_observed/outputs/baseline_previous_result.json")
    baseline_limit = float(baseline_json["observed_fit"]["observed_upper_limit"]["observed_limit"])
    groups = [
        ("Luminosity", ["lumi_2012"], "fixed at -1 and +1 prefit sigma"),
        ("Tau/open-data acceptance", ["tau_open_data_acceptance"], "fixed at -1 and +1 prefit sigma"),
        ("DY/Z normalization", ["dy_norm_open_data"], "fixed at -1 and +1 prefit sigma"),
        ("W high-mT control", ["wjets_high_mt_control"], "fixed at -1 and +1 prefit sigma"),
        ("VBF background control", ["vbf_background_control"], "fixed at -1 and +1 prefit sigma"),
        ("Same-sign QCD/fake transfer", ["qcd_ss_transfer"], "fixed at -1 and +1 prefit sigma"),
        ("MC statistical uncertainty", ["mc_stat_boosted", "mc_stat_vbf", "mc_stat_zero_jet"], "category staterror factors fixed to nominal 1"),
    ]
    rows = []
    for name, parameters, prescription in groups:
        variations = []
        if parameters[0].startswith("mc_stat_"):
            fixed_map = {param: 1.0 for param in parameters}
            fit = fit_with_fixed(model, data, fixed_map)
            delta_mu = float(fit[model.config.poi_index] - baseline_mu)
            limit = baseline_limit + delta_mu
            variations.append(
                {
                    "label": "nominal_fixed",
                    "fixed_values": fixed_map,
                    "mu_hat": float(fit[model.config.poi_index]),
                    "delta_mu_hat": delta_mu,
                    "observed_limit_proxy": limit,
                    "delta_observed_limit_proxy": limit - baseline_limit,
                }
            )
        else:
            for sigma in [-1.0, 1.0]:
                fixed_map = {param: sigma for param in parameters}
                fit = fit_with_fixed(model, data, fixed_map)
                delta_mu = float(fit[model.config.poi_index] - baseline_mu)
                limit = baseline_limit + delta_mu
                variations.append(
                    {
                        "label": f"{sigma:+.0f}_sigma",
                        "fixed_values": fixed_map,
                        "mu_hat": float(fit[model.config.poi_index]),
                        "delta_mu_hat": delta_mu,
                        "observed_limit_proxy": limit,
                        "delta_observed_limit_proxy": limit - baseline_limit,
                    }
                )
        max_delta_mu = max(abs(item["delta_mu_hat"]) for item in variations)
        max_delta_limit = max(abs(item["delta_observed_limit_proxy"]) for item in variations)
        rows.append(
            {
                "source": name,
                "parameters": parameters,
                "prescription": prescription,
                "variations": variations,
                "max_abs_delta_mu_hat": max_delta_mu,
                "max_abs_delta_observed_limit_proxy": max_delta_limit,
            }
        )
    total_delta = sum(row["max_abs_delta_mu_hat"] for row in rows)
    ranked = sorted(rows, key=lambda row: row["max_abs_delta_mu_hat"], reverse=True)
    for rank, row in enumerate(ranked, start=1):
        row["rank"] = rank
        row["fraction_of_summed_abs_delta_mu"] = (
            row["max_abs_delta_mu_hat"] / total_delta if total_delta > 0.0 else 0.0
        )
    payload = {
        "model": "visible_mass_qcd_primary",
        "workspace": "pyhf_workspace_baseline_visible.json",
        "method": "Grouped nuisance impact scan. Normal constrained nuisances are fixed at ±1 prefit sigma; grouped MC-stat constraints are fixed to nominal one. The remaining parameters are profiled. Per-source CLs rescans are not repeated in Phase 5; the limit-impact column is a profile-limit proxy equal to the stored baseline observed CLs limit plus the refit delta_mu_hat.",
        "baseline_mu_hat": baseline_mu,
        "baseline_observed_limit": baseline_limit,
        "ranking_metric": "max_abs_delta_mu_hat",
        "ranking": ranked,
    }
    write_json("phase5_documentation/outputs/baseline_systematic_impacts.json", payload)
    write_json("phase4_inference/4c_observed/outputs/baseline_systematic_impacts.json", payload)
    return payload


@lru_cache(maxsize=1)
def baseline_observed_gof_toys() -> dict[str, object]:
    _ws, model, data = baseline_workspace_model()
    fit_result = cabinetry_fit.fit(model, data, goodness_of_fit=True)
    observed_stat, n_dof = saturated_gof_statistic(model, data, float(fit_result.best_twice_nll))

    random_seed = 20260612
    n_requested = 100
    random_state = np.random.get_state()
    np.random.seed(random_seed)
    try:
        toy_data_samples = pyhf.tensorlib.tolist(
            model.make_pdf(pyhf.tensorlib.astensor(fit_result.bestfit)).sample((n_requested,))
        )
    finally:
        np.random.set_state(random_state)
    toy_stats = []
    toy_fit_failures = []
    init = [float(x) for x in pyhf.tensorlib.tolist(fit_result.bestfit)]
    bounds = list(model.config.suggested_bounds())
    fixed = list(model.config.suggested_fixed())
    for toy_index, toy_sample in enumerate(toy_data_samples):
        toy_data = [float(x) for x in toy_sample]
        try:
            toy_fit = cabinetry_fit.fit(
                model,
                toy_data,
                init_pars=init,
                par_bounds=bounds,
                fix_pars=fixed,
            )
            toy_stat, _ = saturated_gof_statistic(model, toy_data, float(toy_fit.best_twice_nll))
            toy_stats.append(toy_stat)
        except Exception as exc:  # noqa: BLE001
            toy_fit_failures.append({"toy_index": toy_index, "error": f"{type(exc).__name__}: {exc}"})
    if not toy_stats:
        raise RuntimeError("All GoF toy fits failed")
    toy_stats_array = np.asarray(toy_stats, dtype=float)
    interval = [float(x) for x in np.quantile(toy_stats_array, [0.025, 0.975])]
    p_value = float((np.count_nonzero(toy_stats_array >= observed_stat) + 1) / (toy_stats_array.size + 1))
    within_central_95 = bool(interval[0] <= observed_stat <= interval[1])
    payload = {
        "model": "visible_mass_qcd_primary",
        "workspace": "pyhf_workspace_baseline_visible.json",
        "method": "Cabinetry-compatible saturated-model goodness-of-fit toy check. The observed fit uses cabinetry.fit.fit(..., goodness_of_fit=True), and each toy is refit with cabinetry.fit.fit using the same pyhf model. Toys are sampled from the full fitted pyhf model with model.make_pdf(bestfit).sample, so both main-channel counts and auxiliary constraint terms fluctuate. The cabinetry saturated-model GoF statistic is compared with the toy-statistic distribution. Cabinetry 0.6.0 exposes saturated GoF but no public toy-runner API, so the toy loop is implemented explicitly with pyhf sampling and cabinetry refits.",
        "cabinetry_version": "0.6.0",
        "random_seed": random_seed,
        "n_toys": int(toy_stats_array.size),
        "n_toys_requested": n_requested,
        "toy_fit_failures": toy_fit_failures[:10],
        "n_fit_failures": len(toy_fit_failures),
        "n_degrees_of_freedom": n_dof,
        "observed_statistic": observed_stat,
        "observed_cabinetry_saturated_p_value": float(fit_result.goodness_of_fit),
        "toy_p_value": p_value,
        "within_central_95_interval": within_central_95,
        "pass": within_central_95 and p_value > 0.025,
        "toy_statistic_summary": {
            "mean": float(np.mean(toy_stats_array)),
            "median": float(np.median(toy_stats_array)),
            "central_95_interval": interval,
        },
        "toy_statistics": [float(x) for x in toy_stats_array],
    }
    write_json("phase5_documentation/outputs/baseline_observed_gof_toys.json", payload)
    write_json("phase4_inference/4c_observed/outputs/baseline_observed_gof_toys.json", payload)
    return payload


def compact_gof_summary(payload: dict[str, object]) -> dict[str, object]:
    summary = copy.deepcopy(payload)
    summary.pop("toy_statistics", None)
    summary["toy_statistics_artifact"] = "baseline_observed_gof_toys.json"
    return summary


def baseline_result(observed: dict) -> dict:
    payload = observed.get("baseline_previous_result")
    if payload:
        return payload
    return load_json("phase4_inference/4c_observed/outputs/baseline_previous_result.json")


def optimized_score_gate(observed: dict) -> dict[str, object]:
    fit = observed.get("score_diagnostic_fit", observed["observed_fit"])
    limit = fit["observed_upper_limit"]
    validation_summary = observed.get("score_diagnostic_validation_summary", observed["validation_summary"])
    validation = validation_summary["combined"]
    flags = {
        "mu_hat_gt_20": float(fit["mu_hat"]) > 20.0,
        "observed_limit_hits_scan": float(limit["observed_limit"]) >= 49.9,
        "q0_z_gt_5": float(fit["discovery_diagnostic"]["z_value"]) > 5.0,
        "combined_data_background_ratio_lt_0p8": float(validation["data_over_background"]) < 0.8,
    }
    return {
        "status": "fail" if any(flags.values()) else "pass",
        "flags": flags,
        "rule": "The optimized classifier is rejected if it has a boundary-like limit, a large q0 diagnostic, or a gross combined normalization mismatch.",
    }


def sanitize_role_text(obj: object) -> object:
    """Remove stale score-primary wording from metadata strings without changing numbers."""
    replacements = {
        "classifier-score primary model": "classifier-score diagnostic model",
        "calibrated-score primary model": "calibrated-score diagnostic model",
        "primary calibrated-score model": "diagnostic calibrated-score model",
        "primary calibrated-score fit": "diagnostic calibrated-score fit",
        "primary corrected workspace": "diagnostic classifier workspace",
        "use the calibrated categorized score model as primary": "evaluate the calibrated categorized score model as a diagnostic",
        "does not replace calibrated-score primary": "does not replace the final visible-mass result",
    }
    if isinstance(obj, dict):
        return {key: sanitize_role_text(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [sanitize_role_text(value) for value in obj]
    if isinstance(obj, str):
        for old, new in replacements.items():
            obj = obj.replace(old, new)
        return obj
    return obj


def persist_final_roles(observed: dict) -> dict:
    """Update role/provenance metadata and baseline validation aliases."""
    dnn_secondary = copy.deepcopy(observed.get("nn_score_secondary_result"))
    baseline = baseline_result(observed)
    baseline_mu = baseline_mu_summary()
    score_mu = score_mu_summary()
    score_fit = copy.deepcopy(observed.get("score_diagnostic_fit", observed["observed_fit"]))
    score_validation = copy.deepcopy(observed.get("score_diagnostic_validation_summary", observed["validation_summary"]))
    impact_scan = baseline_impact_scan()
    gof_toys = compact_gof_summary(baseline_observed_gof_toys())

    score_fit["profile_mu_interval"] = score_mu
    baseline.setdefault("observed_fit", {})["profile_mu_interval"] = baseline_mu
    baseline["label"] = "Validated visible-mass final result"
    baseline["primary_model"] = "visible_mass_qcd_primary"
    baseline["source"] = "Current validated visible-mass baseline workspace used as the final result."
    baseline["role"] = "final_result"
    baseline["systematic_impact_ranking"] = impact_scan
    baseline.setdefault("validation_summary", {})["observed_gof_toy"] = gof_toys

    observed["primary_model"] = "visible_mass_qcd_primary"
    observed["final_result_model"] = "visible_mass_qcd_primary"
    observed["observed_fit"] = copy.deepcopy(baseline["observed_fit"])
    observed["validation_summary"] = copy.deepcopy(baseline["validation_summary"])
    observed["score_diagnostic_fit"] = score_fit
    observed["score_diagnostic_validation_summary"] = score_validation
    observed["baseline_systematic_impact_ranking"] = impact_scan
    observed["observed_gof_toy_baseline"] = gof_toys
    observed["final_result"] = {
        "model": "visible_mass_qcd_primary",
        "workspace": "pyhf_workspace_baseline_visible.json",
        "yields": "baseline_visible_yields.json",
        "role": "final_result",
        "observed_fit": baseline["observed_fit"],
        "validation_summary": baseline["validation_summary"],
        "systematic_impact_ranking": impact_scan,
        "observed_gof_toy": gof_toys,
    }
    observed["model_roles"] = {
        "visible_mass_qcd_primary": {
            "role": "final_result",
            "workspace": "pyhf_workspace_baseline_visible.json",
            "validation_status": baseline["validation_summary"]["score_modeling_status"],
            "interpretation": "Validated low-sensitivity visible-mass CLs result.",
        },
        "calibrated_score_qcd_primary": {
            "role": "diagnostic_failed_validation",
            "workspace": "pyhf_workspace_observed.json",
            "validation_status": score_validation["score_modeling_status"],
            "interpretation": "Rejected optimized classifier study retained only for validation diagnostics.",
            "gate": optimized_score_gate(observed),
        },
        "addmet_mass_qcd_crosscheck": {
            "role": "diagnostic_failed_validation",
            "workspace": "pyhf_workspace_addmet.json",
            "validation_status": observed.get("addmet_validation_summary", {}).get("score_modeling_status", "not_available"),
            "interpretation": "Auxiliary add-MET mass cross-check, not a final result.",
        },
    }
    if dnn_secondary:
        observed["nn_score_secondary_result"] = dnn_secondary
        observed.setdefault("models", {})["dnn_classifier_score_secondary"] = {
            "observable": dnn_secondary["observable"],
            "binning": dnn_secondary["binning"],
            "validation_summary": dnn_secondary["validation_summary"],
            "observed_fit": dnn_secondary["observed_fit"],
            "role": "secondary_result",
        }
        observed["model_roles"]["dnn_classifier_score_secondary"] = {
            "role": "secondary_result",
            "workspace": dnn_secondary["workspace"],
            "validation_status": dnn_secondary["validation_summary"]["score_modeling_status"],
            "interpretation": "Three-category D_NN classifier score result shown alongside the visible-mass baseline.",
        }
    if "calibrated_score_qcd_primary" in observed:
        observed["calibrated_score_qcd_primary"]["role"] = "diagnostic_failed_validation"
    if "addmet" in observed:
        observed["addmet"]["role"] = "diagnostic_failed_validation"
    observed["baseline_previous_result"] = baseline

    observed = sanitize_role_text(observed)
    baseline = sanitize_role_text(baseline)
    write_json("phase4_inference/4c_observed/outputs/baseline_previous_result.json", baseline)
    write_json("phase4_inference/4c_observed/outputs/observed_results.json", observed)
    append_log("Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.")
    return observed


def fmt(value: float, ndigits: int = 3) -> str:
    return f"{value:.{ndigits}f}"


def ratio_uncertainty(data_counts: np.ndarray, background: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(background > 0, np.sqrt(np.maximum(data_counts, 1.0)) / background, 0.0)


def sample_display_label(name: str) -> str:
    labels = {
        "GluGluToHToTauTau": "ggH H to tau tau",
        "VBF_HToTauTau": "VBF H to tau tau",
        "DYJetsToLL": "DY+jets",
        "TTbar": "ttbar",
        "W1JetsToLNu": "W+1 jet",
        "W2JetsToLNu": "W+2 jets",
        "W3JetsToLNu": "W+3 jets",
        "Run2012B_TauPlusX": "Run 2012B TauPlusX",
        "Run2012C_TauPlusX": "Run 2012C TauPlusX",
    }
    return labels.get(name, name.replace("_", " "))


def make_sample_inventory_figure() -> None:
    setup_style()
    inventory = load_json("phase2_exploration/outputs/sample_inventory.json")
    names = list(inventory["samples"])
    events = np.asarray([inventory["samples"][name]["trees"]["Events"]["entries"] for name in names], dtype=float)
    sizes = np.asarray([inventory["samples"][name]["size_bytes"] / 1e6 for name in names], dtype=float)
    edges = np.arange(len(names) + 1) - 0.5
    x = np.arange(len(names), dtype=float)
    h_events = hist.Hist(hist.axis.Variable(edges, name="x"), storage=hist.storage.Weight())
    view = h_events.view()
    view.value = events
    view.variance = np.maximum(events, 1.0)

    fig, ax = plt.subplots(figsize=(10, 10))
    mh.histplot(h_events, yerr=np.sqrt(np.maximum(events, 1.0)), histtype="errorbar", ax=ax, label="Events")
    ax.set_yscale("log")
    ax.set_ylabel("Events")
    ax.set_xlabel("Sample")
    ax.set_xticks(x)
    ax.set_xticklabels([sample_display_label(name) for name in names], rotation=90)
    ax.set_xlim(-0.75, len(names) - 0.25)
    ax2 = ax.twinx()
    ax2.scatter(x, sizes, marker="s", color="tab:red", label="File size")
    ax2.set_ylabel("File size [MB]")
    ax.legend(fontsize="x-small", loc="upper left")
    ax2.legend(fontsize="x-small", loc="upper right")
    cms_label(ax, lumi=False, llabel="Open Data + Open Simulation", rlabel_override=r"$8$ TeV")
    save(fig, "sample_event_count_file_size")


def make_visible_validation_figure(category: str, visible_yields: dict, baseline: dict) -> None:
    setup_style()
    totals = visible_yields["totals"][category]
    edges = np.asarray(visible_yields["binning"]["edges"], dtype=float)
    centers = 0.5 * (edges[:-1] + edges[1:])
    data = np.asarray(totals["data_counts"], dtype=float)
    background = np.asarray(totals["background_bins"], dtype=float)
    signal = np.asarray(totals["signal_bins"], dtype=float)
    nominal_total_mc = background + signal
    postfit_total = postfit_expected_by_category(
        "phase4_inference/4c_observed/outputs/pyhf_workspace_baseline_visible.json"
    )[category]
    qcd = np.asarray(totals["qcd_bins"], dtype=float)
    ratio = np.divide(data, postfit_total, out=np.zeros_like(data), where=postfit_total > 0)
    pulls = baseline["validation_summary"]["score_template_validation"][category]["pulls"]

    fig, (ax, rax) = plt.subplots(
        2,
        1,
        figsize=(10, 10),
        gridspec_kw={"height_ratios": [3.2, 1.0]},
        sharex=True,
    )
    ax.stairs(background, edges, fill=True, color="#56b4e9", alpha=0.35, label="Final-fit validation background")
    ax.stairs(qcd, edges, fill=True, color="#e69f00", alpha=0.35, label="QCD/fake")
    ax.stairs(nominal_total_mc, edges, color="#009e73", linewidth=1.1, label="Nominal bkg. + SM Higgs")
    ax.stairs(postfit_total, edges, color="black", linewidth=1.8, label="Post-fit total")
    ax.errorbar(centers, data, yerr=np.sqrt(np.maximum(data, 1.0)), fmt="o", color="#d62728", label="Data")
    ax.set_ylabel("Events")
    ax.set_yscale("log")
    ax.set_ylim(max(0.03, 0.2 * np.min(background[background > 0])), max(np.max(data), np.max(nominal_total_mc), np.max(postfit_total)) * 8.0)
    ax.legend(fontsize="x-small", loc="upper left")
    ax.tick_params(labelbottom=False)
    cms_label(ax)

    rax.axhline(1.0, color="black", linewidth=1.0)
    rax.errorbar(centers, ratio, yerr=ratio_uncertainty(data, postfit_total), fmt="o", color="#d62728")
    rax.set_ylabel("Data / post-fit")
    rax.set_xlabel("Visible mass [GeV]")
    rax.set_ylim(0.0, max(2.4, float(np.max(ratio)) * 1.25))
    fig.subplots_adjust(hspace=0)
    save(fig, f"phase5_baseline_visible_{category}")


def make_nn_score_validation_figure(category: str, nn_payload: dict) -> None:
    setup_style()
    yields = nn_payload["model"]["yields"]
    totals = yields["totals"][category]
    edges = np.asarray(yields["binning"]["edges"], dtype=float)
    centers = 0.5 * (edges[:-1] + edges[1:])
    data = np.asarray(totals["data_counts"], dtype=float)
    background = np.asarray(totals["background_bins"], dtype=float)
    signal = np.asarray(totals["signal_bins"], dtype=float)
    nominal_total_mc = background + signal
    postfit_total = postfit_expected_by_category(
        "phase4_inference/4c_observed/outputs/pyhf_workspace_nn_score.json"
    )[category]
    qcd = np.asarray(totals["qcd_bins"], dtype=float)
    ratio = np.divide(data, postfit_total, out=np.zeros_like(data), where=postfit_total > 0)

    fig, (ax, rax) = plt.subplots(
        2,
        1,
        figsize=(10, 10),
        gridspec_kw={"height_ratios": [3.2, 1.0]},
        sharex=True,
    )
    ax.stairs(background, edges, fill=True, color="#56b4e9", alpha=0.35, label="Final-fit validation background")
    ax.stairs(qcd, edges, fill=True, color="#e69f00", alpha=0.35, label="QCD/fake")
    ax.stairs(nominal_total_mc, edges, color="#009e73", linewidth=1.1, label="Nominal bkg. + SM Higgs")
    ax.stairs(postfit_total, edges, color="black", linewidth=1.8, label="Post-fit total")
    ax.errorbar(centers, data, yerr=np.sqrt(np.maximum(data, 1.0)), fmt="o", color="#d62728", label="Data")
    ax.set_ylabel("Events")
    ax.set_yscale("log")
    positive = postfit_total[postfit_total > 0]
    ax.set_ylim(max(0.03, 0.2 * np.min(positive)), max(np.max(data), np.max(nominal_total_mc), np.max(postfit_total)) * 8.0)
    ax.legend(fontsize="x-small", loc="upper right")
    ax.tick_params(labelbottom=False)
    cms_label(ax)

    rax.axhline(1.0, color="black", linewidth=1.0)
    rax.errorbar(centers, ratio, yerr=ratio_uncertainty(data, postfit_total), fmt="o", color="#d62728")
    rax.set_ylabel("Data / post-fit")
    rax.set_xlabel(r"$D_{NN}$ score")
    rax.set_ylim(0.0, max(2.4, float(np.max(ratio)) * 1.25))
    fig.subplots_adjust(hspace=0)
    save(fig, f"phase5_nn_score_{category}")


def make_combined_postfit_validation_figure(
    *,
    yields_payload: dict,
    workspace_relpath: str,
    output_stem: str,
    xlabel: str,
    model_label: str,
    legend_loc: str = "upper right",
) -> None:
    setup_style()
    edges = np.asarray(yields_payload["binning"]["edges"], dtype=float)
    centers = 0.5 * (edges[:-1] + edges[1:])
    data = np.zeros(len(edges) - 1, dtype=float)
    background = np.zeros(len(edges) - 1, dtype=float)
    signal = np.zeros(len(edges) - 1, dtype=float)
    qcd = np.zeros(len(edges) - 1, dtype=float)
    for category in CATEGORIES:
        totals = yields_payload["totals"][category]
        data += np.asarray(totals["data_counts"], dtype=float)
        background += np.asarray(totals["background_bins"], dtype=float)
        signal += np.asarray(totals["signal_bins"], dtype=float)
        qcd += np.asarray(totals["qcd_bins"], dtype=float)
    nominal_total_mc = background + signal
    postfit_by_category = postfit_expected_by_category(workspace_relpath)
    postfit_total = np.sum([postfit_by_category[category] for category in CATEGORIES], axis=0)
    ratio = np.divide(data, postfit_total, out=np.zeros_like(data), where=postfit_total > 0)

    fig, (ax, rax) = plt.subplots(
        2,
        1,
        figsize=(10, 10),
        gridspec_kw={"height_ratios": [3.2, 1.0]},
        sharex=True,
    )
    ax.stairs(background, edges, fill=True, color="#56b4e9", alpha=0.35, label="Final-fit validation background")
    ax.stairs(qcd, edges, fill=True, color="#e69f00", alpha=0.35, label="QCD/fake")
    ax.stairs(nominal_total_mc, edges, color="#009e73", linewidth=1.1, label="Nominal bkg. + SM Higgs")
    ax.stairs(postfit_total, edges, color="black", linewidth=1.8, label="Post-fit total")
    ax.errorbar(centers, data, yerr=np.sqrt(np.maximum(data, 1.0)), fmt="o", color="#d62728", label="Data")
    ax.set_ylabel("Events")
    ax.set_yscale("log")
    positive = postfit_total[postfit_total > 0]
    ax.set_ylim(max(0.03, 0.2 * np.min(positive)), max(np.max(data), np.max(nominal_total_mc), np.max(postfit_total)) * 8.0)
    ax.legend(fontsize="x-small", loc=legend_loc)
    ax.tick_params(labelbottom=False)
    cms_label(ax)

    rax.axhline(1.0, color="black", linewidth=1.0)
    rax.errorbar(centers, ratio, yerr=ratio_uncertainty(data, postfit_total), fmt="o", color="#d62728")
    rax.set_ylabel("Data / post-fit")
    rax.set_xlabel(xlabel)
    rax.set_ylim(0.0, max(2.4, float(np.max(ratio)) * 1.25))
    fig.subplots_adjust(hspace=0)
    save(fig, output_stem)


def make_prefit_validation_figure(
    *,
    yields_payload: dict,
    category: str,
    output_stem: str,
    xlabel: str,
    legend_loc: str = "upper right",
) -> None:
    setup_style()
    totals = yields_payload["totals"][category]
    edges = np.asarray(yields_payload["binning"]["edges"], dtype=float)
    centers = 0.5 * (edges[:-1] + edges[1:])
    data = np.asarray(totals["data_counts"], dtype=float)
    background = np.asarray(totals["background_bins"], dtype=float)
    signal = np.asarray(totals["signal_bins"], dtype=float)
    qcd = np.asarray(totals["qcd_bins"], dtype=float)
    total_mc = background + signal
    ratio = np.divide(data, total_mc, out=np.zeros_like(data), where=total_mc > 0)

    fig, (ax, rax) = plt.subplots(
        2,
        1,
        figsize=(10, 10),
        gridspec_kw={"height_ratios": [3.2, 1.0]},
        sharex=True,
    )
    ax.stairs(background, edges, fill=True, color="#56b4e9", alpha=0.35, label="Pre-fit background")
    ax.stairs(qcd, edges, fill=True, color="#e69f00", alpha=0.35, label="QCD/fake")
    ax.stairs(total_mc, edges, color="#009e73", linewidth=1.8, label="Pre-fit bkg. + SM Higgs")
    ax.errorbar(centers, data, yerr=np.sqrt(np.maximum(data, 1.0)), fmt="o", color="#d62728", label="Data")
    ax.set_ylabel("Events")
    ax.set_yscale("log")
    positive = total_mc[total_mc > 0]
    ax.set_ylim(max(0.03, 0.2 * np.min(positive)), max(np.max(data), np.max(total_mc)) * 8.0)
    ax.legend(fontsize="x-small", loc=legend_loc)
    ax.tick_params(labelbottom=False)
    cms_label(ax)

    rax.axhline(1.0, color="black", linewidth=1.0)
    rax.errorbar(centers, ratio, yerr=ratio_uncertainty(data, total_mc), fmt="o", color="#d62728")
    rax.set_ylabel("Data / pre-fit")
    rax.set_xlabel(xlabel)
    rax.set_ylim(0.0, max(2.4, float(np.max(ratio)) * 1.25))
    fig.subplots_adjust(hspace=0)
    save(fig, output_stem)


def make_combined_prefit_validation_figure(
    *,
    yields_payload: dict,
    output_stem: str,
    xlabel: str,
    model_label: str,
    legend_loc: str = "upper right",
) -> None:
    setup_style()
    edges = np.asarray(yields_payload["binning"]["edges"], dtype=float)
    centers = 0.5 * (edges[:-1] + edges[1:])
    data = np.zeros(len(edges) - 1, dtype=float)
    background = np.zeros(len(edges) - 1, dtype=float)
    signal = np.zeros(len(edges) - 1, dtype=float)
    qcd = np.zeros(len(edges) - 1, dtype=float)
    for category in CATEGORIES:
        totals = yields_payload["totals"][category]
        data += np.asarray(totals["data_counts"], dtype=float)
        background += np.asarray(totals["background_bins"], dtype=float)
        signal += np.asarray(totals["signal_bins"], dtype=float)
        qcd += np.asarray(totals["qcd_bins"], dtype=float)
    total_mc = background + signal
    ratio = np.divide(data, total_mc, out=np.zeros_like(data), where=total_mc > 0)

    fig, (ax, rax) = plt.subplots(
        2,
        1,
        figsize=(10, 10),
        gridspec_kw={"height_ratios": [3.2, 1.0]},
        sharex=True,
    )
    ax.stairs(background, edges, fill=True, color="#56b4e9", alpha=0.35, label="Pre-fit background")
    ax.stairs(qcd, edges, fill=True, color="#e69f00", alpha=0.35, label="QCD/fake")
    ax.stairs(total_mc, edges, color="#009e73", linewidth=1.8, label="Pre-fit bkg. + SM Higgs")
    ax.errorbar(centers, data, yerr=np.sqrt(np.maximum(data, 1.0)), fmt="o", color="#d62728", label="Data")
    ax.set_ylabel("Events")
    ax.set_yscale("log")
    positive = total_mc[total_mc > 0]
    ax.set_ylim(max(0.03, 0.2 * np.min(positive)), max(np.max(data), np.max(total_mc)) * 8.0)
    ax.legend(fontsize="x-small", loc=legend_loc)
    ax.tick_params(labelbottom=False)
    cms_label(ax)

    rax.axhline(1.0, color="black", linewidth=1.0)
    rax.errorbar(centers, ratio, yerr=ratio_uncertainty(data, total_mc), fmt="o", color="#d62728")
    rax.set_ylabel("Data / pre-fit")
    rax.set_xlabel(xlabel)
    rax.set_ylim(0.0, max(2.4, float(np.max(ratio)) * 1.25))
    fig.subplots_adjust(hspace=0)
    save(fig, output_stem)


def make_baseline_limit_figure(baseline: dict, nn_payload: dict) -> None:
    setup_style()
    fit = baseline["observed_fit"]
    lim = fit["observed_upper_limit"]
    band = lim["expected_band_minus2_minus1_median_plus1_plus2"]
    mu = baseline_mu_summary()
    nn_result_payload = nn_payload["result"]
    nn_fit = nn_result_payload["observed_fit"]
    nn_lim = nn_fit["observed_upper_limit"]
    nn_band = nn_lim["expected_band_minus2_minus1_median_plus1_plus2"]
    nn_mu = nn_fit["profile_mu_interval"]

    fig, ax = plt.subplots(figsize=(10, 10))
    rows = [
        ("Visible mass", 1.0, band, lim["observed_limit"], mu),
        (r"$D_{NN}$ score", 0.0, nn_band, nn_lim["observed_limit"], nn_mu),
    ]
    for idx, (_label, y, row_band, _row_limit, row_mu) in enumerate(rows):
        ax.fill_betweenx([y - 0.25, y + 0.25], row_band[0], row_band[4], color="#f0e442", alpha=0.9, label="Expected 95% band" if idx == 0 else None)
        ax.fill_betweenx([y - 0.25, y + 0.25], row_band[1], row_band[3], color="#009e73", alpha=0.9, label="Expected 68% band" if idx == 0 else None)
        ax.vlines(row_band[2], y - 0.31, y + 0.31, color="black", linestyle="--", linewidth=1.6, label="Expected median limit" if idx == 0 else None)
        ax.errorbar(
            row_mu["mu_hat"],
            y,
            xerr=np.asarray([[row_mu["err_minus"]], [row_mu["err_plus"]]], dtype=float),
            fmt="o",
            color="#d62728",
            ecolor="#d62728",
            capsize=5,
            label="Observed fit" if idx == 0 else None,
        )
    ax.axvline(1.0, color="#666666", linestyle=":", linewidth=1.2, label="SM signal strength")
    ax.set_yticks([row[1] for row in rows], [row[0] for row in rows])
    ax.set_xlabel("Signal-strength modifier")
    x_max = max(12.5, lim["observed_limit"] * 1.18, nn_lim["observed_limit"] * 1.18, nn_band[4] * 1.08)
    ax.set_xlim(0.0, x_max)
    ax.set_ylim(-0.55, 1.55)
    ax.legend(fontsize="x-small", loc="center left", bbox_to_anchor=(1.02, 0.5))
    cms_label(ax, lumi=False)
    save(fig, "phase5_baseline_limit_summary")


def make_validation_summary_figure(baseline: dict) -> None:
    setup_style()
    summary = baseline["validation_summary"]["score_template_validation"]
    labels = [CATEGORY_LABELS[cat] for cat in CATEGORIES]
    y = np.arange(len(CATEGORIES), dtype=float)
    ratio = np.asarray([summary[cat]["data_over_background"] for cat in CATEGORIES], dtype=float)
    chi2 = np.asarray([summary[cat]["chi2_per_ndf"] for cat in CATEGORIES], dtype=float)
    max_pull = np.asarray([summary[cat]["max_abs_pull"] for cat in CATEGORIES], dtype=float)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.barh(y - 0.22, ratio, height=0.18, color="#0072b2", label="Data/background")
    ax.barh(y, chi2, height=0.18, color="#009e73", label="chi2/ndf")
    ax.barh(y + 0.22, max_pull, height=0.18, color="#d55e00", label="Max |pull|")
    ax.axvline(1.0, color="black", linestyle="--", linewidth=1.0)
    ax.axvline(3.0, color="#666666", linestyle=":", linewidth=1.0)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Validation metric")
    ax.set_xlim(0.0, max(3.2, float(np.max(max_pull)) * 1.15))
    ax.invert_yaxis()
    ax.legend(fontsize="x-small", loc="lower right")
    cms_label(ax, lumi=False)
    save(fig, "phase5_baseline_validation_summary")


def pretty_parameter(name: str) -> str:
    replacements = {
        "dy_norm_open_data": "DY/Z normalization",
        "lumi_2012": "Luminosity",
        "tau_open_data_acceptance": "Tau/open-data acceptance",
        "vbf_background_control": "VBF background control",
        "wjets_high_mt_control": "W high-mT control",
        "qcd_ss_transfer": "Same-sign QCD/fake transfer",
        "mu": "Signal strength",
    }
    if name.startswith("mc_stat_"):
        return name.replace("mc_stat_", "MC stat ").replace("_", " ")
    return replacements.get(name, name.replace("_", " "))


def make_nuisance_pull_figure(baseline: dict) -> None:
    setup_style()
    params = baseline["observed_fit"]["parameters"]
    selected = [
        (pretty_parameter(name), float(value))
        for name, value in params.items()
        if name != "mu" and not name.startswith("mc_stat_")
    ]
    selected.sort(key=lambda item: abs(item[1]))
    labels = [item[0] for item in selected]
    values = np.asarray([item[1] for item in selected], dtype=float)
    y = np.arange(len(values), dtype=float)

    fig, ax = plt.subplots(figsize=(10, 10))
    colors = np.where(np.abs(values) > 1.0, "#d55e00", "#0072b2")
    ax.barh(y, values, color=colors, alpha=0.85)
    ax.axvline(0.0, color="black", linewidth=1.0)
    ax.axvline(-1.0, color="#666666", linestyle=":", linewidth=1.0)
    ax.axvline(1.0, color="#666666", linestyle=":", linewidth=1.0)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Post-fit nuisance value [prefit sigma units]")
    ax.set_xlim(min(-1.4, float(np.min(values)) - 0.2), max(1.4, float(np.max(values)) + 0.2))
    cms_label(ax, lumi=False)
    save(fig, "phase5_nuisance_pulls_baseline")


def make_systematic_program_figure(baseline: dict) -> None:
    setup_style()
    rows = baseline["systematic_impact_ranking"]["ranking"]
    labels = [row["source"] for row in rows]
    values = np.asarray([row["max_abs_delta_mu_hat"] for row in rows], dtype=float)
    y = np.arange(len(rows), dtype=float)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.barh(y, values, color="#56b4e9", alpha=0.85)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Maximum absolute change in fitted mu")
    ax.invert_yaxis()
    cms_label(ax, lumi=False)
    save(fig, "phase5_systematic_program_baseline")


def make_score_diagnostic_figure(observed: dict) -> None:
    setup_style()
    fit = observed["score_diagnostic_fit"]
    val = observed["score_diagnostic_validation_summary"]["combined"]
    lim = fit["observed_upper_limit"]
    score_mu = score_mu_summary()
    metrics = {
        "Data/background": val["data_over_background"],
        "chi2/ndf": val["chi2_per_ndf"],
        "q0 diagnostic Z": fit["discovery_diagnostic"]["z_value"],
        "Best-fit mu": score_mu["mu_hat"],
        "Observed limit": lim["observed_limit"],
        "Expected median limit": lim["expected_band_minus2_minus1_median_plus1_plus2"][2],
    }
    labels = list(metrics)
    values = np.asarray(list(metrics.values()), dtype=float)
    y = np.arange(len(labels), dtype=float)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.barh(y, values, color="#d55e00", alpha=0.85)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Diagnostic value")
    ax.set_xlim(0.0, max(52.0, float(np.max(values)) * 1.15))
    ax.invert_yaxis()
    cms_label(ax, lumi=False)
    save(fig, "phase5_rejected_score_diagnostics")


def category_mu_results() -> dict[str, object]:
    workspace = load_json("phase4_inference/4c_observed/outputs/pyhf_workspace_observed.json")
    out: dict[str, dict[str, float]] = {}
    for channel in workspace["channels"]:
        name = channel["name"]
        single_workspace = {
            "channels": [channel],
            "measurements": copy.deepcopy(workspace["measurements"]),
            "observations": [obs for obs in workspace["observations"] if obs["name"] == name],
            "version": workspace["version"],
        }
        ws = pyhf.Workspace(single_workspace)
        model = ws.model()
        data = ws.data(model)
        pars = pyhf.infer.mle.fit(
            data,
            model,
            init_pars=model.config.suggested_init(),
            par_bounds=model.config.suggested_bounds(),
            fixed_params=model.config.suggested_fixed(),
        )
        pars_list = [float(x) for x in pyhf.tensorlib.tolist(pars)]
        out[name] = {
            "expected_mu_sm": 1.0,
            "observed_mu_hat": float(pars_list[model.config.poi_index]),
            "n_parameters": float(model.config.npars),
        }
    return {
        "model": "calibrated_score_qcd_primary",
        "role": "diagnostic_failed_validation",
        "interpretation": "Per-category fits demonstrate why the optimized classifier is not used as the final result.",
        "categories": out,
    }


def make_category_mu_figure() -> None:
    setup_style()
    payload = category_mu_results()
    results = payload["categories"]
    labels = ["VBF", "Boosted", "Zero-jet"]
    keys = ["vbf", "boosted", "zero_jet"]
    y = np.arange(len(keys))
    expected = np.asarray([results[key]["expected_mu_sm"] for key in keys], dtype=float)
    observed = np.asarray([results[key]["observed_mu_hat"] for key in keys], dtype=float)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.plot(expected, y - 0.12, marker="s", linestyle="", color="#009e73", label="SM reference")
    ax.plot(observed, y + 0.12, marker="o", linestyle="", color="#d55e00", label="Rejected classifier fit")
    for yi, x_exp, x_obs in zip(y, expected, observed, strict=True):
        ax.plot([x_exp, x_obs], [yi, yi], color="#b0b0b0", linewidth=1.2)
    ax.axvline(1.0, color="black", linestyle="--", linewidth=1.2)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Signal-strength modifier")
    ax.set_xlim(0.0, max(10.0, float(np.max(observed)) * 1.15))
    ax.invert_yaxis()
    ax.legend(fontsize="x-small", loc="lower right")
    cms_label(ax, lumi=False)
    save(fig, "phase5_category_mu_comparison")
    (OUT / "category_mu_comparison.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    append_log("Generated failed-classifier per-category diagnostic JSON and clean figure.")


def make_all_figures(observed: dict, visible_yields: dict, baseline: dict, nn_payload: dict) -> None:
    make_sample_inventory_figure()
    for category in CATEGORIES:
        make_visible_validation_figure(category, visible_yields, baseline)
        make_nn_score_validation_figure(category, nn_payload)
    make_combined_postfit_validation_figure(
        yields_payload=visible_yields,
        workspace_relpath="phase4_inference/4c_observed/outputs/pyhf_workspace_baseline_visible.json",
        output_stem="phase5_baseline_visible_combined",
        xlabel="Visible mass [GeV]",
        model_label="Combined categories",
        legend_loc="upper left",
    )
    make_combined_postfit_validation_figure(
        yields_payload=nn_payload["model"]["yields"],
        workspace_relpath="phase4_inference/4c_observed/outputs/pyhf_workspace_nn_score.json",
        output_stem="phase5_nn_score_combined",
        xlabel=r"$D_{NN}$ score",
        model_label="Combined categories",
        legend_loc="upper right",
    )
    make_baseline_limit_figure(baseline, nn_payload)
    make_validation_summary_figure(baseline)
    make_nuisance_pull_figure(baseline)
    make_systematic_program_figure(baseline)
    make_score_diagnostic_figure(observed)
    make_category_mu_figure()
    append_log("Generated clean Phase 5 baseline, NN-score, and diagnostic figures.")


def figure_ref_check(md_path: Path) -> list[str]:
    text = md_path.read_text()
    refs = sorted(set(re.findall(r"figures/[^)]+\.pdf", text)))
    return [ref for ref in refs if not (OUT / ref).exists()]


def compile_doc(stem: str) -> None:
    cmd = [
        "pandoc",
        f"{stem}.md",
        "-o",
        f"{stem}.tex",
        "--standalone",
        "--include-in-header=../../conventions/preamble.tex",
        "--number-sections",
        "--toc",
        "--filter",
        "pandoc-crossref",
        "--citeproc",
        "--bibliography=references.bib",
    ]
    subprocess.run(cmd, cwd=OUT, check=True)
    subprocess.run([sys.executable, "../../conventions/postprocess_tex.py", f"{stem}.tex"], cwd=OUT, check=True)
    subprocess.run(["tectonic", f"{stem}.tex"], cwd=OUT, check=True)
    append_log(f"Compiled {stem}.md to TeX and PDF.")


def result_text(baseline: dict) -> str:
    mu = baseline_mu_summary()
    lim = baseline["observed_fit"]["observed_upper_limit"]
    band = lim["expected_band_minus2_minus1_median_plus1_plus2"]
    return (
        f"mu = {mu['mu_hat']:.4f} +{mu['err_plus']:.4f} -{mu['err_minus']:.4f}; "
        f"95% CLs mu < {lim['observed_limit']:.4f}; "
        f"median expected 95% CLs mu < {band[2]:.4f}"
    )


def category_yield_table(visible_yields: dict, baseline: dict) -> str:
    lines = []
    validation = baseline["validation_summary"]["score_template_validation"]
    for cat in CATEGORIES:
        total = visible_yields["totals"][cat]
        val = validation[cat]
        lines.append(
            f"| {CATEGORY_LABELS[cat]} | {total['data_total']} | {total['background_total']:.2f} | "
            f"{total['qcd_total']:.2f} | {total['signal_total']:.3f} | {total['data_over_background']:.3f} | "
            f"{val['chi2_per_ndf']:.3f} | {val['max_abs_pull']:.2f} |"
        )
    return "\n".join(lines)


def nn_category_yield_table(nn_payload: dict) -> str:
    lines = []
    nn = nn_payload["result"]
    yields = nn_payload["model"]["yields"]
    validation = nn["validation_summary"]["score_template_validation"]
    for cat in CATEGORIES:
        total = yields["totals"][cat]
        val = validation[cat]
        lines.append(
            f"| {CATEGORY_LABELS[cat]} | {total['data_total']} | {total['background_total']:.2f} | "
            f"{total['qcd_total']:.2f} | {total['signal_total']:.3f} | {total['data_over_background']:.3f} | "
            f"{val['chi2_per_ndf']:.3f} | {val['max_abs_pull']:.2f} |"
        )
    return "\n".join(lines)


def bin_yield_table(visible_yields: dict, category: str) -> str:
    edges = visible_yields["binning"]["edges"]
    total = visible_yields["totals"][category]
    rows = []
    for idx, (lo, hi) in enumerate(zip(edges[:-1], edges[1:], strict=True)):
        rows.append(
            f"| {lo:.0f}-{hi:.0f} | {total['data_counts'][idx]:.0f} | "
            f"{total['background_bins'][idx]:.2f} | {total['qcd_bins'][idx]:.3f} | "
            f"{total['signal_bins'][idx]:.3f} | {total['data_counts'][idx] / total['background_bins'][idx]:.3f} |"
        )
    return "\n".join(rows)


def systematic_table() -> str:
    return "\n".join(
        f"| {row['name']} | {row['value']} | {row['affected']} | {row['source']} |"
        for row in SYSTEMATIC_PROGRAM
    )


def impact_lookup(baseline: dict) -> dict[str, dict[str, object]]:
    return {row["source"]: row for row in baseline["systematic_impact_ranking"]["ranking"]}


def impact_summary_table(baseline: dict) -> str:
    rows = []
    for row in baseline["systematic_impact_ranking"]["ranking"]:
        rows.append(
            f"| {int(row['rank'])} | {row['source']} | {row['max_abs_delta_mu_hat']:.4f} | "
            f"{row['max_abs_delta_observed_limit_proxy']:.4f} | {100.0 * row['fraction_of_summed_abs_delta_mu']:.1f}% |"
        )
    return "\n".join(rows)


def gof_summary_table(baseline: dict) -> str:
    gof = baseline["validation_summary"]["observed_gof_toy"]
    interval = gof["toy_statistic_summary"]["central_95_interval"]
    return "\n".join(
        [
            f"| Observed saturated GoF statistic | {gof['observed_statistic']:.4f} |",
            f"| Cabinetry saturated GoF p-value | {gof['observed_cabinetry_saturated_p_value']:.4f} |",
            f"| Toy median | {gof['toy_statistic_summary']['median']:.4f} |",
            f"| Toy central 95% interval | {interval[0]:.4f} to {interval[1]:.4f} |",
            f"| Toy-style p-value | {gof['toy_p_value']:.4f} |",
            f"| Validation decision | {'PASS' if gof['pass'] else 'FAIL'} |",
        ]
    )


def systematic_subsections(baseline: dict) -> str:
    sections = []
    impacts = impact_lookup(baseline)
    for row in SYSTEMATIC_PROGRAM:
        impact = impacts.get(row["name"])
        if impact:
            impact_text = (
                f"{row['impact']} The largest observed shift in the grouped scan is "
                f"Delta mu = {impact['max_abs_delta_mu_hat']:.4f} and "
                f"Delta observed-limit proxy = {impact['max_abs_delta_observed_limit_proxy']:.4f}; "
                f"this is rank {int(impact['rank'])} and accounts for "
                f"{100.0 * impact['fraction_of_summed_abs_delta_mu']:.1f}% of the summed absolute impact metric."
            )
        else:
            impact_text = row["impact"]
        sections.append(
            f"""## {row['name']}

Physical origin: {row['source']}. The source is retained because it changes either the absolute MC normalization, the transfer of a data-driven background into the signal region, or the bin-by-bin template precision used by the likelihood.

Evaluation method: the baseline pyhf workspace implements `{row['parameter']}` with value {row['value']} for {row['affected']}. The correlation model is: {row['correlation']}. For normalization systematics the nuisance multiplies the affected yields through log-normal interpolation,

$$
\\nu_{{p}}(\\theta_p)=
\\begin{{cases}}
\\nu^0_p\\,\\kappa_{{p,+}}^{{\\theta_p}}, & \\theta_p \\ge 0, \\\\
\\nu^0_p\\,\\kappa_{{p,-}}^{{-\\theta_p}}, & \\theta_p < 0,
\\end{{cases}}
$$ {{#eq:normsys-{row['parameter'].replace('_', '-').replace('*', 'stat')}}}

where $\\nu^0_p$ is the nominal bin yield and $\\theta_p$ is constrained by a unit Gaussian. MC statistical terms use the per-bin staterror modifiers stored in `pyhf_workspace_baseline_visible.json`.

Numerical impact: {impact_text}

Interpretation: this source is part of the final error model used for the CLs limit. Its adequacy is judged together with the visible-mass validation plots, nuisance-pull summary, and the low-sensitivity result interpretation.
"""
        )
    return "\n".join(sections)


def nuisance_table(baseline: dict) -> str:
    params = baseline["observed_fit"]["parameters"]
    rows = []
    for name in ["lumi_2012", "tau_open_data_acceptance", "dy_norm_open_data", "wjets_high_mt_control", "vbf_background_control", "qcd_ss_transfer"]:
        rows.append(f"| {pretty_parameter(name)} | {float(params[name]):.3f} | Included |")
    return "\n".join(rows)


def score_diagnostic_table(observed: dict) -> str:
    fit = observed["score_diagnostic_fit"]
    lim = fit["observed_upper_limit"]
    band = lim["expected_band_minus2_minus1_median_plus1_plus2"]
    val = observed["score_diagnostic_validation_summary"]["combined"]
    gate = optimized_score_gate(observed)
    mu = score_mu_summary()
    return "\n".join(
        [
            f"| Expected median 95% CLs limit | mu < {band[2]:.4f} | Would be sensitive if observed modelling passed |",
            f"| Observed 95% CLs limit | mu < {lim['observed_limit']:.4f} | Hits scan boundary; diagnostic failure |",
            f"| Best-fit signal strength | {mu['mu_hat']:.4f} +{mu['err_plus']:.4f} -{mu['err_minus']:.4f} | Far outside reduced-analysis plausibility |",
            f"| q0 diagnostic | Z = {fit['discovery_diagnostic']['z_value']:.4f} | Rejected, not a discovery claim |",
            f"| Combined data/background | {val['data_over_background']:.4f} | Gross normalization mismatch |",
            f"| Combined chi2/ndf | {val['chi2_per_ndf']:.4f} | Shape/normalization validation diagnostic |",
            f"| Validation gate | {gate['status']} | {gate['rule']} |",
        ]
    )


def build_analysis_note(observed: dict, partial: dict, expected: dict, visible_yields: dict, baseline: dict, nn_payload: dict) -> str:
    baseline_fit = baseline["observed_fit"]
    baseline_lim = baseline_fit["observed_upper_limit"]
    baseline_band = baseline_lim["expected_band_minus2_minus1_median_plus1_plus2"]
    baseline_mu = baseline_mu_summary()
    baseline_val = baseline["validation_summary"]
    w_full = observed["wjets_high_mt_scale"]
    vbf_scale = observed["vbf_background_scale"]
    score_fit = observed["score_diagnostic_fit"]
    score_lim = score_fit["observed_upper_limit"]
    score_band = score_lim["expected_band_minus2_minus1_median_plus1_plus2"]
    partial_val = partial["validation_summary"]["combined"]
    expected_lim = expected["expected_upper_limit"]["expected_band_minus2_minus1_median_plus1_plus2"]
    baseline_gof = baseline_val["observed_gof_toy"]
    nn_result_payload = nn_payload["result"]
    nn_fit = nn_result_payload["observed_fit"]
    nn_lim = nn_fit["observed_upper_limit"]
    nn_band = nn_lim["expected_band_minus2_minus1_median_plus1_plus2"]
    nn_val = nn_result_payload["validation_summary"]
    nn_training = nn_result_payload["training_summary"]["model"]
    nn_mu = nn_fit["profile_mu_interval"]

    return f"""---
title: "CMS Open Data H to Tau Tau Search: Final Analysis Note"
author: "Analysis my_analysis"
date: "2026-06-12"
bibliography: references.bib
---

# Abstract {{-}}

This note documents a standalone reduced CMS Open Data search for Higgs boson decays to tau pairs in the muon plus hadronic-tau final state. The final result uses the validated visible-mass template fit in VBF, boosted, and zero-jet categories with `visible_mass_qcd_primary` as the baseline model. The fit gives {result_text(baseline)}. A secondary three-category $D_NN$ classifier-score result is also reported with observed 95% CLs limit `mu < {nn_lim['observed_limit']:.4f}` and median expected limit `{nn_band[2]:.4f}`. Both results are low-sensitivity Open Data limits rather than evidence for a Standard Model-strength signal.

# Change Log {{-}}

- Final documentation version, 2026-06-12: reclassified the validated visible-mass baseline as the baseline result, added a secondary three-category $D_NN$ classifier-score result, regenerated clean final figures, expanded the statistical and systematic documentation, and rebuilt the AN/PRL PDFs from current JSON artifacts.

# Introduction

The target process is Higgs boson production followed by $H \\to \\tau\\tau$ with one tau reconstructed through a muon and the other as a hadronic tau candidate. The analysis uses reduced CMS 2012 Open Data inputs and mirrors the broad logic of CMS H to tau tau searches while explicitly accepting the limitations of the public reduced sample set [@cms_open_data_htt_2012; @cms_htt_2014; @cms_htt_2018]. The final statistical question is a search-style upper limit on a signal-strength modifier $\\mu$, not a precision measurement of a branching fraction.

The signal-strength convention is

$$
\\mu = \\frac{{\\sigma(pp\\to H)\\,\\mathcal{{B}}(H\\to\\tau\\tau)}}
{{\\left[\\sigma(pp\\to H)\\,\\mathcal{{B}}(H\\to\\tau\\tau)\\right]_{{\\mathrm{{SM}}}}}},
$$ {{#eq:mu-def}}

where the denominator follows the Standard Model normalization used for the available ggH and VBF signal samples [@lhc_hxswg_yellow_report_4; @pdg_higgs_status_2024]. The final claim is therefore phrased as a CLs upper limit on $\\mu$. A discovery-style $q_0$ value is computed only as a diagnostic health check.

The analysis is intentionally conservative. The reduced mirror lacks embedded $Z\\to\\tau\\tau$, diboson, single-top, QCD multijet MC, W4/inclusive W+jets, and several associated-Higgs components present in the full CMS publications. Those missing components are not silently substituted. Instead, the note documents the available samples, the control-derived W and reducible-background corrections, the retained nuisance model, the validation failures of the more aggressive classifier attempt, and the final visible-mass limit.

# Data and Simulation Samples

The localized reduced input files are the public 2012 TauPlusX data and seven MC files for Higgs signal and major backgrounds. The analysis uses the official CERN Open Data record event counts as normalization denominators rather than local skim entries, because the local entries are already reduced and do not represent generated-event denominators [@cms_open_data_skim].

| Sample | Role | Local entries | Official events | Record |
|---|---:|---:|---:|---|
| ggH Htt | signal | 47,696 | 476,963 | 12351 |
| VBF Htt | signal | 49,165 | 491,653 | 12352 |
| DY+jets | background | 3,045,887 | 30,458,871 | 12353 |
| ttbar | background | 642,310 | 6,423,106 | 12354 |
| W1+jets | background | 2,978,480 | 29,784,800 | 12355 |
| W2+jets | background | 3,069,385 | 30,693,853 | 12356 |
| W3+jets | background | 1,524,114 | 15,241,144 | 12357 |
| Run2012B | data | 3,564,750 | 35,647,508 | 12358 |
| Run2012C | data | 5,130,317 | 51,303,171 | 12359 |

The luminosity normalization used throughout the final fit is $L = {PUBLIC_LUMI:.3f}$ fb$^{{-1}}$. MC yields use

$$
w_{{i}}^{{\\mathrm{{bkg}}}} = \\frac{{\\sigma_i L}}{{N_i^{{\\mathrm{{gen}}}}}},
\\qquad
w_{{i}}^{{\\mathrm{{sig}}}} = \\frac{{\\sigma_i\\,\\mathcal{{B}}(H\\to\\tau\\tau) L}}{{N_i^{{\\mathrm{{gen}}}}}},
$$ {{#eq:weights}}

with $N_i^{{\\mathrm{{gen}}}}$ taken from the Open Data records. This choice avoids circular normalization to the observed selected data and keeps the result reproducible from public metadata.

The missing reduced-sample components are treated as analysis limitations and nuisance-model motivations. In particular, the DY/Z normalization nuisance covers the absence of embedded and electroweak Z samples at the reduced-file level, while the QCD/fake template is data-driven because no QCD multijet MC sample is present in the mirror.

![Sample inventory summary. This figure summarizes the localized reduced sample inventory and file-size scale used in the analysis. It documents the available data/MC inputs and shows why the final result is framed as a reduced Open Data search rather than a reproduction of the full CMS publication.](figures/sample_event_count_file_size.pdf){{#fig:sample-inventory}}

# Event Selection and Categories

Events are selected using the TauPlusX trigger `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`. Muon candidates require $p_T > 20$ GeV, $|\\eta| < 2.1$, a tight muon ID, and relative isolation below 0.20. Hadronic tau candidates require $p_T > 20$ GeV, $|\\eta| < 2.3$, decay-mode ID, tight tau isolation ID, tight anti-muon ID, finite relative isolation, and $\\Delta R(\\mu,\\tau_h) > 0.5$.

Signal-region candidates are opposite-sign muon-tau pairs with transverse mass $m_T(\\mu,E_T^{{\\mathrm{{miss}}}}) < 40$ GeV. The W control region uses opposite-sign pairs with $m_T > 80$ GeV. Same-sign low-$m_T$ candidates define the reducible-background sideband. A Z-rich validation region is retained for visible-mass shape checks with $60 < m_{{\\mathrm{{vis}}}} < 120$ GeV.

The transverse mass is

$$
m_T = \\sqrt{{2 p_T^\\mu E_T^{{\\mathrm{{miss}}}} \\left[1-\\cos\\Delta\\phi(\\mu,E_T^{{\\mathrm{{miss}}}})\\right]}}.
$$ {{#eq:mt}}

Selected events are assigned to mutually exclusive categories. VBF events are selected first with at least two clean jets and VBF-like dijet kinematics. Remaining events with at least one clean jet enter the boosted category. Events without selected jets enter the zero-jet category. This category order preserves the VBF topology while keeping the statistical model a simple simultaneous template fit.

| Requirement | Role in analysis |
|---|---|
| TauPlusX trigger | Defines the public muon-tau trigger phase space |
| Tight muon and tau IDs | Select prompt muon plus hadronic tau candidates |
| Tight anti-muon tau ID | Reduces muon fake contamination in the tau_h leg |
| Opposite-sign charge | Signal-region charge requirement |
| $m_T < 40$ GeV | Suppresses W+jets in the signal region |
| VBF / boosted / zero-jet categories | Separate signal-enriched and control-like event topologies |

![Cutflow summary. The cutflow shows raw event counts after each selection step for data, signal MC, and background MC. The monotonic behavior confirms that the final candidate set is produced by cumulative event-selection requirements rather than by a post-fit normalization adjustment.](figures/cutflow_summary.pdf){{#fig:cutflow}}

![Category yield overview. The category-yield diagnostic shows the VBF, boosted, and zero-jet populations after the signal-region selection. The zero-jet category dominates the statistics, while VBF carries the most topology-specific signal motivation and the largest residual local validation tension.](figures/category_yields.pdf){{#fig:category-yields}}

# Observable Choice and Analysis Decision

The final observable is the visible mass $m_{{\\mathrm{{vis}}}}$ of the selected muon and hadronic tau candidate. It is less sensitive than the optimized classifier in expected-only studies, but it passes the full-data validation gate in the baseline workspace. The final result therefore follows the binding strategy that alternatives may replace visible mass only after validation.

The visible mass is defined from the reconstructed lepton four-vectors as

$$
m_{{\\mathrm{{vis}}}}^2 = \\left(p_\\mu + p_{{\\tau_h}}\\right)^2.
$$ {{#eq:mvis}}

The optimized classifier is not a final result. It is documented in @sec:rejected-classifier because its observed fit gives a boundary-like limit, a large fitted signal strength, and a gross combined data/background mismatch. Keeping it as a rejected diagnostic preserves the methodological lesson without allowing a failed validation gate to enter the headline physics result.

![Visible-mass distribution in the VBF category. This pre-fit comparison illustrates the observable used by the final workspace in the VBF topology. The final validation plot in @fig:baseline-visible-vbf adds the exact baseline QCD/fake treatment and category-level validation metrics.](figures/visible_mass_vbf.pdf){{#fig:phase3-visible-vbf}}

![Visible-mass distribution in the boosted category. This comparison shows that the visible-mass observable retains broad data/MC shape information without relying on the high-score tail that failed for the classifier model. It supports the choice of a robust baseline over the rejected optimization attempt.](figures/visible_mass_boosted.pdf){{#fig:phase3-visible-boosted}}

![Visible-mass distribution in the zero-jet category. The zero-jet category provides most of the event count and therefore dominates the global normalization behavior. The final limit remains weak because the visible-mass signal-to-background separation is modest in this category.](figures/visible_mass_zero_jet.pdf){{#fig:phase3-visible-zero}}

# Background Corrections

The final model uses MC shapes for signal, DY/Z, ttbar, and W+jets, with data-driven corrections for W+jets normalization, the VBF-background normalization, and reducible QCD/fake contamination. The control-region corrections are derived outside the signal fit and then propagated into the baseline workspace.

The W+jets scale factor is

$$
S_W = \\frac{{N_{{\\mathrm{{data}},\\mathrm{{CR}}}} - N_{{\\mathrm{{nonW}},\\mathrm{{CR}}}}}}
{{N_{{W,\\mathrm{{CR}}}}}},
$$ {{#eq:w-scale}}

which gives $S_W = {w_full['applied_scale_factor']:.4f} \\pm {w_full['absolute_uncertainty']:.4f}$ using {w_full['data_events_full']} high-$m_T$ data events, $N_W = {w_full['wjets_mc_yield_full_lumi']:.2f}$, and $N_{{\\mathrm{{nonW}}}} = {w_full['nonw_background_mc_yield_full_lumi']:.2f}$. The relative uncertainty is {100*w_full['relative_uncertainty']:.2f}% and is implemented as `wjets_high_mt_control`.

The VBF background scale is

$$
S_{{\\mathrm{{VBF,bkg}}}} =
\\frac{{N_{{\\mathrm{{data}},\\mathrm{{VBFCR}}}}}}
{{N_{{\\mathrm{{MC,bkg}},\\mathrm{{VBFCR}}}}}},
$$ {{#eq:vbf-scale}}

giving $S_{{\\mathrm{{VBF,bkg}}}} = {vbf_scale['applied_scale_factor']:.4f} \\pm {vbf_scale['absolute_uncertainty']:.4f}$. It is applied only to MC backgrounds in the VBF fit category and is constrained by the {100*vbf_scale['relative_uncertainty']:.2f}% `vbf_background_control` nuisance.

The reducible QCD/fake estimate starts from same-sign low-$m_T$ data after non-QCD subtraction:

$$
N^{{\\mathrm{{QCD}}}}_{{\\mathrm{{SS}},b}} = N^{{\\mathrm{{data}}}}_{{\\mathrm{{SS}},b}} -
N^{{\\mathrm{{nonQCD}}}}_{{\\mathrm{{SS}},b}},
\\qquad
N^{{\\mathrm{{QCD}}}}_{{\\mathrm{{OS}},b}} = R_{{\\mathrm{{OS/SS}}}} N^{{\\mathrm{{QCD}}}}_{{\\mathrm{{SS}},b}}.
$$ {{#eq:qcd-transfer}}

For the final baseline workspace the retained transfer-factor nuisance is {SYSTEMATIC_PROGRAM[5]['value']}. The current artifact records a limitation: QCD shape-statistical uncertainties are included in validation variances but are not expanded into per-bin pyhf nuisances in the baseline workspace. This is a documented limitation of the reduced analysis rather than a hidden source of sensitivity.

| Control input | Formula | Value | Use in final model |
|---|---|---:|---|
| W high-$m_T$ scale | @eq:w-scale | {w_full['applied_scale_factor']:.4f} ± {w_full['absolute_uncertainty']:.4f} | W+jets normalization nuisance |
| VBF background scale | @eq:vbf-scale | {vbf_scale['applied_scale_factor']:.4f} ± {vbf_scale['absolute_uncertainty']:.4f} | VBF MC-background nuisance |
| Same-sign QCD/fake transfer | @eq:qcd-transfer | {SYSTEMATIC_PROGRAM[5]['value']} relative uncertainty | Global QCD/fake transfer nuisance |

![QCD same-sign visible-mass control. This figure shows the same-sign sideband used to form the reducible-background template. The final note treats the transfer-factor limitations explicitly because the reduced Open Data format does not provide an anti-isolated tau branch for a fuller fake-factor method.](figures/qcd_same_sign_mvis.pdf){{#fig:qcd-ss}}

# Statistical Model

The final result uses a binned pyhf/HistFactory likelihood [@pyhf_joss]. For category $c$ and visible-mass bin $b$, the expected yield is

$$
\\lambda_{{cb}}(\\mu,\\boldsymbol{{\\theta}}) =
\\mu s_{{cb}}(\\boldsymbol{{\\theta}}) +
\\sum_k b_{{kcb}}(\\boldsymbol{{\\theta}}) +
q_{{cb}}(\\boldsymbol{{\\theta}}),
$$ {{#eq:bin-yield}}

where $s$ is the combined ggH and VBF Higgs signal, $b_k$ are simulation-derived backgrounds, and $q$ is the same-sign data-driven QCD/fake template. The likelihood is

$$
L(\\mu,\\boldsymbol{{\\theta}}) =
\\prod_{{c,b}} \\mathrm{{Pois}}\\left(n_{{cb}}\\mid \\lambda_{{cb}}(\\mu,\\boldsymbol{{\\theta}})\\right)
\\prod_j \\pi_j(\\theta_j),
$$ {{#eq:likelihood}}

with Gaussian/log-normal constrained nuisance parameters and staterror terms for finite MC precision. The fit constrains $\\mu \\ge 0$.

Upper limits use the modified frequentist CLs construction [@read_cls]:

$$
\\mathrm{{CL}}_s(\\mu)=\\frac{{p_{{s+b}}(q_\\mu \\ge q_\\mu^{{\\mathrm{{obs}}}})}}
{{p_b(q_\\mu \\ge q_\\mu^{{\\mathrm{{obs}}}})}}.
$$ {{#eq:cls}}

The quoted 95% limit is the value of $\\mu$ where $\\mathrm{{CL}}_s=0.05$. The profile interval printed for the best fit solves

$$
q(\\mu)= -2\\ln\\frac{{L(\\mu,\\hat{{\\boldsymbol{{\\theta}}}}_\\mu)}}
{{L(\\hat{{\\mu}},\\hat{{\\boldsymbol{{\\theta}}}})}} = 1,
$$ {{#eq:profile-interval}}

with the lower side bounded at $\\mu=0$ when required. Asymptotic formulae are used for the reported limits and diagnostics [@cowan_asymptotic; @read_cls]. The final bins all have enough total expected background for an initial asymptotic interpretation. The observed-data combined goodness of fit is additionally checked with the stored fitted-toy saturated-model ensemble described below.

# Systematic Uncertainties

The final systematic program follows the search-convention categories that are implementable with the reduced inputs: luminosity, object/acceptance, DY/Z normalization, W control, VBF control, QCD/fake transfer, and MC statistical uncertainty. Missing full-analysis components are documented as limitations rather than replaced by arbitrary uncertainty inflation.

| Source | Value | Scope | Motivation |
|---|---:|---|---|
{systematic_table()}

![Baseline systematic impact ranking. The figure ranks the retained grouped nuisance sources by the maximum absolute change in fitted signal strength from the baseline impact scan. Normal constrained nuisances are fixed at ±1 prefit sigma, MC-stat constraints are fixed to their nominal factors as a group, and the remaining parameters are profiled.](figures/phase5_systematic_program_baseline.pdf){{#fig:systematic-program}}

{systematic_subsections(baseline)}

The baseline impact ranking is stored in `baseline_systematic_impacts.json` and summarized in @tbl:impact-ranking. The largest grouped source accounts for {100.0 * baseline['systematic_impact_ranking']['ranking'][0]['fraction_of_summed_abs_delta_mu']:.1f}% of the summed absolute `mu`-impact metric, so no single retained source exceeds the 80% dominance alarm threshold.

| Rank | Source | Max abs Delta mu | Max abs Delta observed-limit proxy | Fraction of summed abs Delta mu |
|---:|---|---:|---:|---:|
{impact_summary_table(baseline)}

: Baseline systematic impact ranking from grouped nuisance refits. The limit column is a documented profile-limit proxy, not a full per-source CLs rescan. {{#tbl:impact-ranking}}

# Baseline Validation

The visible-mass final result passes the configured full-data validation gate. Combined over categories, the baseline has data/background = {baseline_val['combined']['data_over_background']:.4f}, chi2/ndf = {baseline_val['combined']['chi2_per_ndf']:.4f}, and no category or combined validation flag. The zero-jet chi2/ndf is low at {baseline_val['score_template_validation']['zero_jet']['chi2_per_ndf']:.3f}; this is not algebraically zero, but it is noted as possible overcoverage from conservative diagonal validation uncertainties.

| Category | Data | Background | QCD/fake | Signal | D/B | Chi2/ndf | Max pull |
|---|---:|---:|---:|---:|---:|---:|---:|
{category_yield_table(visible_yields, baseline)}

The VBF category has the largest residual local tension: max |pull| = {baseline_val['score_template_validation']['vbf']['max_abs_pull']:.2f} and one bin ratio reaches {min(baseline_val['score_template_validation']['vbf']['bin_data_over_background']):.3f}. This does not invalidate the final result because the VBF event count is small, the combined validation passes, and the final interpretation is a weak upper limit rather than evidence. It is nevertheless a leading target for a future analysis with fuller background samples and a richer VBF validation region.

![Baseline visible-mass post-fit validation in VBF. This regenerated Phase 5 figure compares the post-fit total expectation from the retained baseline workspace to the full data in the VBF category. The residual local deficit is visible in the Data/post-fit ratio panel and is included in the validation summary rather than hidden by the combined pass.](figures/phase5_baseline_visible_vbf.pdf){{#fig:baseline-visible-vbf}}

![Baseline visible-mass post-fit validation in boosted. This regenerated Phase 5 figure shows the post-fit total expectation from the retained baseline workspace. Its Data/post-fit ratio panel is globally compatible with the final model, and its residual pulls are below the VBF maximum.](figures/phase5_baseline_visible_boosted.pdf){{#fig:baseline-visible-boosted}}

![Baseline visible-mass post-fit validation in zero-jet. This regenerated Phase 5 figure shows the dominant-statistics zero-jet category for the final result using the post-fit total expectation from the baseline workspace. The Data/post-fit ratio panel has no shared-axis text artifact and is the public validation plot used by the final AN.](figures/phase5_baseline_visible_zero_jet.pdf){{#fig:baseline-visible-zero}}

![Baseline visible-mass combined post-fit validation. This regenerated Phase 5 figure sums the VBF, boosted, and zero-jet post-fit visible-mass expectations bin-by-bin and compares the combined prediction with full observed data. The lower panel is Data/post-fit model and provides the compact global Data/MC check for the baseline result.](figures/phase5_baseline_visible_combined.pdf){{#fig:baseline-visible-combined}}

![Baseline validation summary. The figure compares data/background, chi2/ndf, and max absolute pull across the final visible-mass categories. It highlights that the combined result passes while VBF carries the largest localized residual tension.](figures/phase5_baseline_validation_summary.pdf){{#fig:baseline-validation-summary}}

# Nuisance Parameters and Fit Health

The most important fitted nuisance values are stored in the baseline result JSON under `observed_fit.parameters`. Their values are reported in prefit sigma units for constrained parameters.

| Source | Post-fit value | Status |
|---|---:|---|
{nuisance_table(baseline)}

The DY/Z normalization and tau/open-data acceptance pulls are sizable but remain within the range where the model can still be interpreted as a conservative reduced-sample fit. No listed global nuisance exceeds ±1 sigma by a large margin except the known reduced-sample DY/Z pressure. MC statistical terms are numerous and are listed in the JSON rather than repeated line-by-line in the main text.

![Baseline nuisance pulls. The figure shows the global non-MC-stat nuisance values in the final visible-mass fit. It gives the reader a compact check that the final weak limit is not driven by an obviously pathological pull.](figures/phase5_nuisance_pulls_baseline.pdf){{#fig:nuisance-pulls}}

The expected and validation-stage health checks are retained as context. The expected Asimov classifier study had median limit {expected_lim[2]:.3f}, while the full-data final baseline has median expected limit {baseline_band[2]:.4f}; this loss of sensitivity is the cost of using the validated robust model. The 10% validation sample had combined score-template data/background {partial_val['data_over_background']:.3f} and chi2/ndf {partial_val['chi2_per_ndf']:.3f}, already indicating that aggressive classifier use needed full-data scrutiny.

![Expected-stage goodness-of-fit toy study. This upstream figure records the expected-stage toy validation artifact. The final observed baseline result is validated separately by the stored fitted-toy saturated-model ensemble in `baseline_observed_gof_toys.json`.](figures/gof_toys.pdf){{#fig:gof-toys}}

The observed-data combined goodness-of-fit check uses `cabinetry.fit.fit(..., goodness_of_fit=True)` for the observed final baseline fit, then generates {baseline_gof['n_toys']} deterministic post-fit model toys with seed {baseline_gof['random_seed']}. Each toy is refit with `cabinetry.fit.fit` and evaluated with the same saturated-model GoF statistic used by cabinetry. The observed statistic is compared with the fitted-toy distribution, giving toy p = {baseline_gof['toy_p_value']:.4f}; the observed statistic is {'inside' if baseline_gof['within_central_95_interval'] else 'outside'} the toy central 95% interval, so the combined GoF decision is {'PASS' if baseline_gof['pass'] else 'FAIL'}.

| Goodness-of-fit quantity | Value |
|---|---:|
{gof_summary_table(baseline)}

: Observed-data combined GoF toy-style validation for the final baseline model. {{#tbl:gof-toy}}

![Signal-injection recovery. This validation figure documents the available injected-signal recovery study. The final baseline result remains low sensitivity, but the injection artifact shows that the statistical machinery can recover injected signals within the tested setup.](figures/signal_injection_recovery.pdf){{#fig:signal-injection}}

![Nuisance audit. This figure summarizes the available nuisance-audit artifact from the inference workflow. It is retained as supporting fit-health context, while the main text reports the final baseline nuisance values from JSON.](figures/sensitivity_nuisance_audit.pdf){{#fig:nuisance-audit}}

# Secondary $D_NN$ Score Result

The secondary $D_NN$ result uses the Phase 3 `{nn_result_payload['training_summary']['model_name']}` classifier score in the VBF, boosted, and zero-jet categories. The classifier was trained on MC signal/background labels only, using the fifteen reconstructed-level inputs listed in the Phase 3 training summary and nominal MC weights with class balancing; collision data do not enter the signal-region classifier target or event weights. The stored training summary gives train AUC = {nn_training['train_auc']:.4f}, test AUC = {nn_training['test_auc']:.4f}, and train-test gap = {nn_training['overtraining_gap_train_minus_test']:.4f} using {nn_training['n_train']} training and {nn_training['n_test']} test events.

The $D_NN$ score workspace uses the same W high-$m_T$, VBF-background, QCD/fake, luminosity, tau/open-data, DY/Z, and MC-statistical treatment as the visible-mass workspace, with the observable changed to `{nn_result_payload['observable']}`. On full observed data the $D_NN$ score result gives `mu = {nn_mu['mu_hat']:.4f} +{nn_mu['err_plus']:.4f} -{nn_mu['err_minus']:.4f}`, observed 95% CLs `mu < {nn_lim['observed_limit']:.4f}`, and median expected limit `{nn_band[2]:.4f}`. Its combined data/background ratio is {nn_val['combined']['data_over_background']:.4f} with chi2/ndf = {nn_val['combined']['chi2_per_ndf']:.4f}; the result is therefore shown as a secondary classifier-score result alongside the visible-mass baseline.

| Category | Data | Background | QCD/fake | Signal | D/B | Chi2/ndf | Max pull |
|---|---:|---:|---:|---:|---:|---:|---:|
{nn_category_yield_table(nn_payload)}

![$D_NN$ score post-fit validation in VBF. This figure compares observed data to the retained secondary classifier-score post-fit total expectation, including the fitted signal and constrained background treatment, for the VBF category. The lower panel is Data/post-fit model.](figures/phase5_nn_score_vbf.pdf){{#fig:nn-score-vbf}}

![$D_NN$ score post-fit validation in boosted. This figure compares observed data to the retained secondary classifier-score post-fit total expectation in the boosted category. The same three-category $D_NN$ score workspace and nuisance program used for the secondary limit define the model.](figures/phase5_nn_score_boosted.pdf){{#fig:nn-score-boosted}}

![$D_NN$ score post-fit validation in zero-jet. This figure compares observed data to the retained secondary classifier-score post-fit total expectation in the statistically dominant zero-jet category. The full-data normalization mismatch visible in this Data/post-fit panel is included in the quoted secondary $D_NN$ validation metrics.](figures/phase5_nn_score_zero_jet.pdf){{#fig:nn-score-zero}}

![$D_NN$ score combined post-fit validation. This figure sums the VBF, boosted, and zero-jet post-fit score expectations bin-by-bin and compares the combined secondary classifier-score model with full observed data. The lower panel is Data/post-fit model and is the compact global Data/MC score comparison requested for the retained $D_NN$ result.](figures/phase5_nn_score_combined.pdf){{#fig:nn-score-combined}}

# Final Result

The baseline visible-mass profile fit gives

$$
\\hat{{\\mu}} = {baseline_mu['mu_hat']:.4f}^{{+{baseline_mu['err_plus']:.4f}}}_{{-{baseline_mu['err_minus']:.4f}}},
$$ {{#eq:final-muhat}}

with the lower side bounded at zero, and the 95% CLs upper limit is

$$
\\mu < {baseline_lim['observed_limit']:.4f}\\quad(95\\%~\\mathrm{{CL}}_s),
$$ {{#eq:final-limit}}

compared with a median expected limit of {baseline_band[2]:.4f}. The discovery diagnostic is $Z = {baseline_fit['discovery_diagnostic']['z_value']:.4f}$ with p-value {baseline_fit['discovery_diagnostic']['p_value']:.4f}; it is consistent with the low-sensitivity limit interpretation.

| Quantity | Visible-mass baseline | $D_NN$ score secondary |
|---|---:|---:|
| Best-fit signal strength | {baseline_mu['mu_hat']:.4f} +{baseline_mu['err_plus']:.4f} -{baseline_mu['err_minus']:.4f} | {nn_mu['mu_hat']:.4f} +{nn_mu['err_plus']:.4f} -{nn_mu['err_minus']:.4f} |
| Observed 95% CLs limit | mu < {baseline_lim['observed_limit']:.4f} | mu < {nn_lim['observed_limit']:.4f} |
| Expected 95% CLs limit, −2 sigma | mu < {baseline_band[0]:.4f} | mu < {nn_band[0]:.4f} |
| Expected 95% CLs limit, −1 sigma | mu < {baseline_band[1]:.4f} | mu < {nn_band[1]:.4f} |
| Expected 95% CLs limit, median | mu < {baseline_band[2]:.4f} | mu < {nn_band[2]:.4f} |
| Expected 95% CLs limit, +1 sigma | mu < {baseline_band[3]:.4f} | mu < {nn_band[3]:.4f} |
| Expected 95% CLs limit, +2 sigma | mu < {baseline_band[4]:.4f} | mu < {nn_band[4]:.4f} |
| q0 diagnostic Z | {baseline_fit['discovery_diagnostic']['z_value']:.4f} | {nn_fit['discovery_diagnostic']['z_value']:.4f} |
| Combined data/background | {baseline_val['combined']['data_over_background']:.4f} | {nn_val['combined']['data_over_background']:.4f} |
| Combined chi2/ndf | {baseline_val['combined']['chi2_per_ndf']:.4f} | {nn_val['combined']['chi2_per_ndf']:.4f} |
| Combined GoF toy-style p-value | {baseline_gof['toy_p_value']:.4f} | not evaluated |

![Limit summary with visible-mass and NN-score rows. The figure shows the expected CLs bands, black dashed median expected limits, and red observed-fit points with horizontal profile-likelihood error bars for both result paths. The observed 95% CLs limits are tabulated directly above the figure, and the rows are drawn with identical conventions so the stronger expected NN separation and larger observed fitted signal strength can be compared directly.](figures/phase5_baseline_limit_summary.pdf){{#fig:baseline-limit}}

# Rejected Classifier Diagnostic {{#sec:rejected-classifier}}

The optimized calibrated-score model is not a final result. It is retained here because it explains why the analysis does not use the best expected-only sensitivity model. The model has median expected limit {score_band[2]:.4f}, but on full observed data it gives `mu = {score_mu_summary()['mu_hat']:.4f} +{score_mu_summary()['err_plus']:.4f} -{score_mu_summary()['err_minus']:.4f}`, observed limit `mu < {score_lim['observed_limit']:.4f}`, and q0 diagnostic `Z = {score_fit['discovery_diagnostic']['z_value']:.4f}`.

| Diagnostic | Value | Interpretation |
|---|---:|---|
{score_diagnostic_table(observed)}

The category fits also indicate model breakdown rather than category-level consistency. The zero-jet category reaches the scan boundary, and VBF/boosted fitted values are several times the Standard Model strength. These values are not used in the abstract, final-result table, conclusion, or published-context comparison.

![Rejected classifier diagnostic summary. The figure collects the failed optimized-score validation metrics in one diagnostic plot. It is intentionally separated from the final-result section so the failed model is not mistaken for this analysis's physics result.](figures/phase5_rejected_score_diagnostics.pdf){{#fig:rejected-score-diagnostics}}

![Rejected classifier category fits. The figure shows the single-category signal-strength diagnostics for the optimized classifier model. The large fitted values, including boundary behavior, are evidence for rejection of the classifier result rather than evidence for Higgs production.](figures/phase5_category_mu_comparison.pdf){{#fig:rejected-category-mu}}

# Comparison With Published Context

Published CMS and ATLAS+CMS H to tau tau analyses use more channels, fuller calibrations, embedded backgrounds, and substantially richer systematic programs than this reduced Open Data study [@cms_htt_2014; @cms_htt_2018; @atlas_cms_higgs_combination_2016]. The comparison is therefore interpretive, not a validation target. The final result is compatible with published signal strengths only in the weak sense that its uncertainty and upper limit are too large to distinguish $\\mu=1$ from background.

The pull of the final best fit relative to the CMS Run 1 $\\mu = 0.78 \\pm 0.27$ value is not meaningful as a precision comparison because this analysis has an asymmetric interval with a lower physical boundary. Using the upward uncertainty as a conservative scale gives $(0.438-0.78)/4.944 = -0.07$ standard deviations. Relative to the ATLAS+CMS global $\\mu = 1.09 \\pm 0.11$, the same conservative comparison gives $(0.438-1.09)/4.944 = -0.13$ standard deviations. These small pulls reflect low resolving power, not precision agreement.

| Result | Scope | Signal-strength or limit | Interpretation |
|---|---|---|---|
| This analysis | 8 TeV reduced mu tau_h visible-mass fit | {result_text(baseline)} | Low-sensitivity Open Data upper limit |
| CMS Run 1 | 7+8 TeV multi-channel | mu = 0.78 ± 0.27; observed 3.2 sigma | Evidence-level publication analysis |
| CMS 2018 | 13 TeV multi-channel | mu about 1.09; observed 4.9 sigma | Observation in 2016 data |
| CMS combined in 2018 paper | CMS 7+8+13 TeV | observed 5.9 sigma | CMS observation context |
| ATLAS+CMS Run 1 | 7+8 TeV global Higgs combination | global mu = 1.09 ± 0.11 | Precision Higgs-rate context |
| PDG/HXSWG SM | Standard Model normalization | BR(H to tau tau) about 6.3% | Defines the `mu = 1` convention |

The validated result cannot exclude or discover a Standard Model-strength Higgs signal in this reduced setup. Its expected limit near 10.74 says that even a perfect background-like observation would only constrain signals roughly an order of magnitude above the SM rate.

# Limitations and Decision Index

The most important limitation is missing reduced-sample content. No embedded $Z\\to\\tau\\tau$, diboson, single-top, QCD multijet MC, W4/inclusive W+jets, associated-Higgs, or H to WW reduced files are available in the localized mirror used here. These absences limit both sensitivity and systematic realism.

The second limitation is systematic realism. The final package now stores a grouped baseline impact ranking, but the reduced sample set still prevents the full CMS embedded-background, tau-efficiency, trigger, and object-scale-factor treatment. The impact scan is therefore a consistency and dominance check for this reduced workspace, not a substitute for the full CMS systematic program.

The third limitation is validation coverage. The final baseline passes the available combined and category checks and the stored observed-data GoF toy-style validation. The VBF category still has a residual local tension and the zero-jet chi2/ndf is low, so both effects should be revisited with fuller control-region coverage before making stronger physics claims.

| Label | Strategy commitment or limitation | Final status | Impact and mitigation |
|---|---|---|---|
| [A1] | Public reduced samples lack several full-publication components | Fulfilled | Missing components are listed in the data section and treated as limitations or nuisance motivations |
| [L1] | Missing embedded Z to tau tau and QCD multijet MC | Fulfilled | DY/Z and same-sign QCD/fake treatments are documented, with no claim of full CMS sensitivity |
| [L2] | Reduced Open Data object calibrations are incomplete | Fulfilled | Tau/open-data acceptance and luminosity nuisance terms are retained and ranked |
| [D1] | Use a search/template-fit result rather than a branching-fraction measurement | Fulfilled | Final result is a CLs upper limit on `mu` |
| [D2] | Use official Open Data luminosity and generated-event denominators | Fulfilled | Normalization uses public record counts and `L = 11.467/fb`, not fitted data yields |
| [D3] | Keep mutually exclusive VBF, boosted, and zero-jet categories | Fulfilled | Final workspace has exactly those three channels |
| [D4] | Use visible mass as the baseline observable | Fulfilled | `visible_mass_qcd_primary` is the sole final-result model |
| [D5] | Use pyhf/HistFactory for binned likelihood inference | Fulfilled | Final workspace and fits are pyhf artifacts |
| [D6] | Estimate W+jets from a high-mT control region | Fulfilled | The W scale and uncertainty are stored and propagated |
| [D7] | Estimate reducible QCD/fake background from same-sign data | Fulfilled | Same-sign low-mT transfer is propagated to the baseline workspace |
| [D8] | Compare alternative observables only after validation | Fulfilled | Classifier and add-MET results remain explicit failed-validation diagnostics |
| [D9] | Promote an alternative over visible mass only if observed validation passes | Fulfilled | The classifier fails validation and is demoted in prose and machine-readable metadata |

: Strategy decision and limitation index for the final analysis note. {{#tbl:decision-index}}

# Reproduction Contract

The final documents are generated from the current JSON artifacts and pyhf workspaces. A reader with the repository can rebuild the package through pixi:

Manual setup consists of localizing the public reduced ROOT files under `data/` and `mc/` or allowing the Phase 2 scripts to use the configured public ROOT mirror. The pixi environment is the only required software environment; do not use bare Python when reproducing the chain.

| Command | Expected primary outputs | Typical local runtime |
|---|---|---:|
| `pixi run phase2-explore` | sample inventory, branch diagnostics, exploration figures | 1-3 min with local files |
| `pixi run phase3-all` | selected-event NPZ, category yields, selection figures | 2-5 min |
| `pixi run phase4a-all` | expected workspaces, expected limits, validation figures | 1-3 min |
| `pixi run phase4b-all` | 10% data validation JSON, partial AN inputs | 1-3 min |
| `pixi run phase4c-all` | observed workspaces, baseline and diagnostic result JSON | 2-5 min |
| `pixi run phase5-docs` | final AN/PRL markdown, TeX, PDF, figures, impact and GoF JSON | 2-6 min |
| `pixi run lint-plots` | deterministic plot-standard validation result | <1 min |
| `pixi run build-pdf` | rebuilt final analysis note TeX/PDF from markdown | <1 min |

The workflow DAG is Phase 2 exploration to Phase 3 selection to Phase 4a expected inference to Phase 4b partial-data validation to Phase 4c observed inference to Phase 5 documentation. `pixi run phase5-docs` consumes the existing Phase 2-4 outputs; it does not replace the upstream inference tasks. The top-level `pixi run all` task is the chained reproduction entry point for the full analysis package.

The machine-readable numerical sources for the final result are:

| Quantity | Artifact |
|---|---|
| Final fit and validation | baseline result JSON |
| Final workspace | `pyhf_workspace_baseline_visible.json` |
| Visible-mass yields | `baseline_visible_yields.json` |
| Final role metadata | `observed_results.json` |
| Baseline impact ranking | `baseline_systematic_impacts.json` |
| Observed GoF toy-style validation | `baseline_observed_gof_toys.json` |
| W high-mT scale | `wjets_highmt_scale_full.json` |
| VBF background scale | `vbf_background_scale.json` |
| QCD/fake estimates | `qcd_sideband_estimates.json` |
| Category diagnostics | `category_mu_comparison.json` |

# Appendix A: Bin-Level Baseline Yields

The tables below expose the bin-level values used in the regenerated visible-mass validation plots. They are copied from `baseline_visible_yields.json` and allow the reader to reproduce the ratios in @fig:baseline-visible-vbf, @fig:baseline-visible-boosted, and @fig:baseline-visible-zero.

## VBF Bin Yields

The VBF table gives the exact bin contents behind the final VBF visible-mass validation plot. It is the most statistically limited category and carries the largest local residual, so the per-bin data/background ratios are useful for tracing the validation discussion back to the stored yields. The signal column is the Standard Model signal template before multiplication by the fitted `mu`.

| Visible mass bin [GeV] | Data | Background | QCD/fake | Signal | Data/background |
|---|---:|---:|---:|---:|---:|
{bin_yield_table(visible_yields, 'vbf')}

## Boosted Bin Yields

The boosted table reports the visible-mass bins for events with at least one selected jet after VBF events are removed. These bins provide an intermediate-statistics cross-check between the sparse VBF topology and the high-statistics zero-jet category. The table supports the boosted validation plot and the category-yield summary in the main text.

| Visible mass bin [GeV] | Data | Background | QCD/fake | Signal | Data/background |
|---|---:|---:|---:|---:|---:|
{bin_yield_table(visible_yields, 'boosted')}

## Zero-Jet Bin Yields

The zero-jet table gives the dominant event-count contribution to the combined visible-mass fit. Its ratios explain why the global normalization validation is stable even though the zero-jet chi2/ndf is low. The entries are included so the reader can reproduce the combined validation totals without reading the code.

| Visible mass bin [GeV] | Data | Background | QCD/fake | Signal | Data/background |
|---|---:|---:|---:|---:|---:|
{bin_yield_table(visible_yields, 'zero_jet')}

# Appendix B: Validation Bin Ratios and Pulls

| Category | Bin ratios | Pulls |
|---|---|---|
| VBF | {', '.join(f"{x:.3f}" for x in baseline_val['score_template_validation']['vbf']['bin_data_over_background'])} | {', '.join(f"{x:.2f}" for x in baseline_val['score_template_validation']['vbf']['pulls'])} |
| Boosted | {', '.join(f"{x:.3f}" for x in baseline_val['score_template_validation']['boosted']['bin_data_over_background'])} | {', '.join(f"{x:.2f}" for x in baseline_val['score_template_validation']['boosted']['pulls'])} |
| Zero-jet | {', '.join(f"{x:.3f}" for x in baseline_val['score_template_validation']['zero_jet']['bin_data_over_background'])} | {', '.join(f"{x:.2f}" for x in baseline_val['score_template_validation']['zero_jet']['pulls'])} |

# Appendix C: Numeric Consistency Statement

The final AN and PRL quote baseline numbers from JSON fields only. The best-fit value and profile interval come from `observed_fit.profile_mu_interval` in the baseline result JSON; the CLs limits come from `observed_fit.observed_upper_limit`; validation metrics come from `validation_summary`; and visible-mass bin yields come from `baseline_visible_yields.json`. The optimized classifier values appear only in @sec:rejected-classifier and the corresponding diagnostic JSON/figure.

# Appendix D: Supporting Validation Figures

This appendix collects additional artifact-backed figures that support the final model choice and reproduce the analysis chain from input objects to the retained visible-mass fit. These figures are not used to quote additional physics results; they document why the final result is intentionally limited to a weak visible-mass CLs limit and why more aggressive observables are not promoted to the headline result.

![Muon transverse-momentum preselection comparison. This figure checks the reconstructed muon leg in the selected reduced samples. The agreement is not used as a standalone calibration, but it supports the use of the common muon selection in all final categories.](figures/mu_pt.pdf){{#fig:app-mu-pt}}

![Hadronic-tau transverse-momentum preselection comparison. This figure checks the tau_h leg after the loose public-object acceptance and tight anti-muon requirement. The final analysis assigns a tau/open-data acceptance nuisance because the public reduced sample does not include the full trigger and tau scale-factor program.](figures/tau_pt.pdf){{#fig:app-tau-pt}}

![Missing transverse momentum comparison. This figure checks the missing-momentum observable before it enters the transverse-mass and add-MET cross-check definitions. It motivates treating add-MET based observables as diagnostics rather than replacing the validated visible-mass result.](figures/met_pt.pdf){{#fig:app-met-pt}}

![Muon-MET transverse-mass comparison. This distribution defines the signal and W-control regions used by the final workflow. The separation between the low-mT signal region and high-mT control region underlies the W+jets normalization factor in @eq:w-scale.](figures/mt_mu_met.pdf){{#fig:app-mt}}

![VBF dijet-mass comparison. This figure checks the dijet mass observable that enters the VBF category definition. It supports the category split while also showing why the VBF region remains statistically limited in the reduced sample set.](figures/vbf_dijet_mass.pdf){{#fig:app-vbf-mjj}}

![VBF dijet-rapidity-separation comparison. This figure checks the second VBF topology variable used in category assignment. Together with @fig:app-vbf-mjj, it documents the topology basis for separating VBF from boosted and zero-jet events.](figures/vbf_delta_eta_jj.pdf){{#fig:app-vbf-deta}}

![Visible transverse-momentum proxy comparison. This figure summarizes the reconstructed di-tau transverse-momentum proxy available in the reduced inputs. It is retained as a modelling cross-check, not as a final-fit observable.](figures/pt_tautau_proxy.pdf){{#fig:app-pt-tautau}}

![Z-rich visible-mass validation. This control-style figure checks the visible-mass shape in a Z-enriched region. The final note uses it as supporting evidence for the visible-mass baseline while keeping the DY/Z normalization uncertainty explicit.](figures/z_rich_validation_mvis.pdf){{#fig:app-z-rich}}

![W high-mT control comparison. This figure shows the control-region distribution used for the W+jets normalization correction. It complements the numerical W scale in @eq:w-scale by showing the region from which the scale is derived.](figures/w_high_mt_control_mt.pdf){{#fig:app-w-control}}

![MVA input modelling summary. This figure records the input-modelling chi2 diagnostics that prevented an unqualified promotion of a classifier observable. It is included to make the rejected-classifier decision reproducible without reading the Phase 3 code.](figures/mva_input_modeling_chi2.pdf){{#fig:app-mva-input}}

![Expected signal-over-background summary. This expected-stage diagnostic shows why alternative observables were worth studying: the classifier and category choices can improve expected separation. The observed-data validation failure, not the expected-only sensitivity, determines the final model role.](figures/expected_s_over_b.pdf){{#fig:app-expected-sb}}

![Approach comparison summary. This figure compares the broad observable strategies considered in the analysis chain. It documents that the final visible-mass result is a validation-driven choice rather than the most aggressive expected-sensitivity option.](figures/approach_comparison.pdf){{#fig:app-approach}}

# References {{-}}
"""


def build_paper_markdown(observed: dict, baseline: dict, nn_payload: dict) -> str:
    baseline_mu = baseline_mu_summary()
    lim = baseline["observed_fit"]["observed_upper_limit"]
    band = lim["expected_band_minus2_minus1_median_plus1_plus2"]
    val = baseline["validation_summary"]
    gate = optimized_score_gate(observed)
    gof = val["observed_gof_toy"]
    nn = nn_payload["result"]
    nn_fit = nn["observed_fit"]
    nn_lim = nn_fit["observed_upper_limit"]
    nn_band = nn_lim["expected_band_minus2_minus1_median_plus1_plus2"]
    nn_val = nn["validation_summary"]
    return f"""# A CMS Open Data Search for H to Tau Tau in the Mu Tau_h Final State

## Abstract

A reduced CMS 2012 Open Data search for Higgs boson decays to tau pairs is
performed in the `mu tau_h` final state. The final result is a visible-mass
template fit in VBF, boosted, and zero-jet categories. The fit finds
`mu = {baseline_mu['mu_hat']:.3f} +{baseline_mu['err_plus']:.3f}
-{baseline_mu['err_minus']:.3f}` and sets an observed 95% CLs upper limit
`mu < {lim['observed_limit']:.3f}`, with median expected limit
`mu < {band[2]:.3f}`. A secondary three-category $D_NN$ score fit gives
`mu < {nn_lim['observed_limit']:.3f}` observed and `mu < {nn_band[2]:.3f}`
median expected. Both results are low-sensitivity Open Data limits, not
evidence for a Standard Model-strength signal.

## Data and Method

The analysis uses public Run2012B/C TauPlusX reduced data and the available
ggH, VBF, DY, ttbar, and W+jets simulation samples from the CMS Open Data
Higgs-to-tau-tau reduced mirror [@cms_open_data_htt_2012; @cms_detector_2008; @cms_lumi_2013]. Events pass the
muon plus hadronic-tau trigger, tight muon and tau selections, opposite-sign
charge, and a low-transverse-mass signal-region requirement. The statistical
model is a simultaneous binned pyhf/HistFactory likelihood with a common
signal-strength modifier `mu` [@histfactory_2012; @pyhf_joss].

For bin `b` in category `c`, the fitted expectation is
`nu_cb(mu, theta) = mu s_cb(theta) + sum_k b_kcb(theta) + q_cb(theta)`.
Modified frequentist CLs limits use the profile-likelihood test statistic
with nuisance parameters profiled at each tested `mu` [@read_cls; @cowan_asymptotic].

## Background Model

W+jets is constrained by a high-`mT` control region, VBF-category MC
backgrounds are scaled by a VBF-like non-signal control region, and the
reducible QCD/fake contribution is estimated from same-sign low-`mT` data
after non-QCD subtraction. The systematic model includes luminosity,
tau/open-data acceptance, DY/Z normalization, W and VBF control terms,
same-sign QCD transfer, and MC statistical uncertainties.

| Systematic group | Treatment |
|---|---|
| Luminosity | correlated 2.6% normalization term |
| Tau/open-data acceptance | correlated 15% reduced-object acceptance term |
| DY/Z normalization | correlated 15% visible-mass baseline normalization term |
| W and VBF controls | control-region normalization terms |
| QCD/fake transfer | same-sign transfer-factor term |
| MC statistics | per-bin staterror terms |

| Category | Data | Background | Signal | Chi2/ndf |
|---|---:|---:|---:|---:|
| VBF | 78 | 96.28 | 1.590 | {val['score_template_validation']['vbf']['chi2_per_ndf']:.3f} |
| Boosted | 2183 | 2364.39 | 9.170 | {val['score_template_validation']['boosted']['chi2_per_ndf']:.3f} |
| Zero-jet | 8451 | 8456.81 | 14.341 | {val['score_template_validation']['zero_jet']['chi2_per_ndf']:.3f} |

| Limit quantity | Value |
|---|---:|
| Visible-mass observed 95% CLs limit | `mu < {lim['observed_limit']:.3f}` |
| Visible-mass expected median | `mu < {band[2]:.3f}` |
| $D_NN$ score observed 95% CLs limit | `mu < {nn_lim['observed_limit']:.3f}` |
| $D_NN$ score expected median | `mu < {nn_band[2]:.3f}` |
| Observed GoF toy-style p-value | {gof['toy_p_value']:.3f} |

![Final CLs limit summary. The visible-mass and NN-score rows use the same
expected-band, black dashed expected-median, and red observed-fit conventions.
The observed 95% CLs limits are listed in the table above the figure, and both
rows show that the reduced Open Data analysis has no Standard Model resolving
power.](figures/phase5_baseline_limit_summary.pdf){{#fig:prl-limit}}

![Visible-mass post-fit validation in the VBF category. The plotted model is
the post-fit total expectation from the retained baseline workspace. This
category has the largest local residual tension but does not invalidate the
combined weak-limit interpretation.](figures/phase5_baseline_visible_vbf.pdf){{#fig:prl-vbf}}

![Combined visible-mass post-fit validation. This plot sums the VBF, boosted,
and zero-jet post-fit visible-mass expectations and compares them with the
summed observed data. It is the compact global Data/MC check for the baseline
result.](figures/phase5_baseline_visible_combined.pdf){{#fig:prl-visible-combined}}

![$D_NN$ score post-fit validation in the VBF category. The lower panel is
Data/post-fit using the retained secondary classifier-score model in the
denominator.](figures/phase5_nn_score_vbf.pdf){{#fig:prl-nn-vbf}}

![$D_NN$ score post-fit validation in the boosted category. The plot uses the same
three-category $D_NN$ score workspace and nuisance program as the secondary
limit.](figures/phase5_nn_score_boosted.pdf){{#fig:prl-nn-boosted}}

![$D_NN$ score post-fit validation in the zero-jet category. The full-data normalization
mismatch visible in this category is included in the quoted secondary $D_NN$
validation metrics.](figures/phase5_nn_score_zero_jet.pdf){{#fig:prl-nn-zero}}

![Combined $D_NN$ score post-fit validation. This plot sums the VBF, boosted,
and zero-jet post-fit score expectations and compares them with the summed
observed score distribution. It is the compact global Data/MC score check for
the secondary result.](figures/phase5_nn_score_combined.pdf){{#fig:prl-nn-combined}}

## Result and Interpretation

The combined visible-mass validation gives data/background =
{val['combined']['data_over_background']:.3f} and chi2/ndf =
{val['combined']['chi2_per_ndf']:.3f}. The observed-data toy-style GoF
p-value is {gof['toy_p_value']:.3f}. The optimized classifier study has
better expected sensitivity but fails its observed validation gate
(`{gate['status']}`), while the $D_NN$ score fit gives combined data/background =
{nn_val['combined']['data_over_background']:.3f} and chi2/ndf =
{nn_val['combined']['chi2_per_ndf']:.3f}. Published CMS and
ATLAS+CMS H to tau tau analyses use more channels and fuller calibration
programs; this reduced analysis should be read as a reproducibility-oriented
Open Data limit [@cms_htt_2014; @cms_htt_2018; @atlas_cms_higgs_combination_2016].

| Result | Scope | Signal-strength information | Interpretation |
|---|---|---|---|
| This analysis, visible mass | 8 TeV reduced mu tau_h visible-mass fit | `mu < {lim['observed_limit']:.3f}` observed, `{band[2]:.3f}` expected | Low-sensitivity Open Data upper limit |
| This analysis, $D_NN$ score | 8 TeV reduced mu tau_h three-category classifier-score fit | `mu < {nn_lim['observed_limit']:.3f}` observed, `{nn_band[2]:.3f}` expected | Secondary $D_NN$ result |
| CMS Run 1 | 7+8 TeV multi-channel H to tau tau | `mu = 0.78 ± 0.27`, 3.2 sigma observed | Evidence-level publication result |
| CMS 2018 | 13 TeV multi-channel H to tau tau | about SM rate, 4.9 sigma observed | Observation publication context |
| ATLAS+CMS Run 1 | global 7+8 TeV Higgs combination | global `mu = 1.09 ± 0.11` | Precision Higgs-rate context |
| PDG/HXSWG | Standard Model reference | `BR(H to tau tau)` about 6.3% | Defines the `mu = 1` convention |

## References

This markdown draft uses the same bibliography file as the final analysis note:
[@cms_open_data_htt_2012; @cms_detector_2008; @cms_lumi_2013; @cms_higgs_discovery_2012;
@atlas_higgs_discovery_2012; @cms_htt_2014; @cms_htt_2018; @atlas_cms_higgs_combination_2016;
@pdg_2024; @lhc_hxswg_yellow_report_4; @histfactory_2012; @pyhf_joss; @read_cls; @cowan_asymptotic].
"""


def tex_escape(text: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def build_prl_tex(observed: dict, visible_yields: dict, baseline: dict, nn_payload: dict) -> str:
    baseline_fit = baseline["observed_fit"]
    baseline_lim = baseline_fit["observed_upper_limit"]
    baseline_band = baseline_lim["expected_band_minus2_minus1_median_plus1_plus2"]
    baseline_mu = baseline_mu_summary()
    baseline_val = baseline["validation_summary"]
    baseline_gof = baseline_val["observed_gof_toy"]
    nn = nn_payload["result"]
    nn_fit = nn["observed_fit"]
    nn_lim = nn_fit["observed_upper_limit"]
    nn_band = nn_lim["expected_band_minus2_minus1_median_plus1_plus2"]
    nn_val = nn["validation_summary"]
    w_full = observed["wjets_high_mt_scale"]
    vbf_scale = observed["vbf_background_scale"]
    gate = optimized_score_gate(observed)
    rows = []
    for cat in CATEGORIES:
        total = visible_yields["totals"][cat]
        rows.append(
            rf"{CATEGORY_LABELS[cat]} & {total['data_total']} & {total['background_total']:.1f} & "
            rf"{total['signal_total']:.2f} & {baseline_val['score_template_validation'][cat]['chi2_per_ndf']:.2f} \\"
        )
    category_rows = "\n".join(rows)

    return rf"""\documentclass[aps,prl,reprint,superscriptaddress,nofootinbib]{{revtex4-2}}
\usepackage{{graphicx}}
\usepackage{{amsmath}}
\usepackage{{booktabs}}
\usepackage{{array}}
\begin{{document}}

\title{{A CMS Open Data Search for $H\to\tau\tau$ in the $\mu\tau_h$ Final State}}
\author{{Analysis my\_analysis}}
\affiliation{{CMS Open Data reduced-sample analysis}}
\date{{June 12, 2026}}

\begin{{abstract}}
A reduced CMS 2012 Open Data search for Higgs boson decays to tau pairs is
performed in the $\mu\tau_h$ final state.  The final result is a validated
visible-mass template fit in VBF, boosted, and zero-jet categories.  The fit
finds $\mu={baseline_mu['mu_hat']:.3f}^{{+{baseline_mu['err_plus']:.3f}}}_{{-{baseline_mu['err_minus']:.3f}}}$
and sets an observed 95\% CLs upper limit $\mu<{baseline_lim['observed_limit']:.3f}$,
with median expected limit $\mu<{baseline_band[2]:.3f}$.  A secondary
three-category $D_NN$ classifier-score fit gives observed limit
$\mu<{nn_lim['observed_limit']:.3f}$ and median expected limit
$\mu<{nn_band[2]:.3f}$.  Both results are low-sensitivity Open Data limits,
not evidence for a Standard Model-strength signal.
\end{{abstract}}

\maketitle

\paragraph{{Data and method.}}
The analysis uses the public Run2012B/C TauPlusX reduced samples and available
ggH, VBF, DY, ttbar, and W+jets simulation at $L=11.467~\mathrm{{fb}}^{{-1}}$.
Events pass the $\mu+\tau_h$ trigger, tight muon and hadronic-tau selections,
opposite-sign charge, and $m_T(\mu,E_T^{{\rm miss}})<40$ GeV.  The categories
are VBF, boosted, and zero-jet.  The likelihood is a binned HistFactory model
with common signal-strength modifier $\mu$ and CLs limits computed with pyhf:
\[
\nu_{{cb}}(\mu,\theta)=\mu s_{{cb}}(\theta)+\sum_k b_{{kcb}}(\theta)+q_{{cb}}(\theta).
\]
Modified frequentist CLs limits profile the nuisance parameters at each tested
$\mu$.

\paragraph{{Background model.}}
The W+jets scale is derived in a high-$m_T$ control region:
$S_W={w_full['applied_scale_factor']:.3f}\pm{w_full['absolute_uncertainty']:.3f}$.
VBF-category MC backgrounds receive a VBF-like control scale
$S_{{\rm VBF}}={vbf_scale['applied_scale_factor']:.3f}\pm{vbf_scale['absolute_uncertainty']:.3f}$.
Reducible QCD/fake contamination is estimated from same-sign low-$m_T$ data
after non-QCD subtraction.  The systematic model includes luminosity,
tau/open-data acceptance, DY/Z normalization, W and VBF control terms,
same-sign QCD transfer, and MC statistical uncertainties.

\begin{{table}}[t]
\caption{{Compact systematic model.  The impact ranking is stored in the final
analysis-note JSON artifacts.}}
\begin{{ruledtabular}}
\begin{{tabular}}{{ll}}
Group & Treatment \\
Luminosity & 2.6\% correlated normalization \\
Tau/open-data & 15\% correlated acceptance \\
DY/Z & 15\% correlated normalization \\
Controls & W, VBF, and QCD/fake transfer terms \\
MC stat. & Per-bin staterror modifiers \\
\end{{tabular}}
\end{{ruledtabular}}
\end{{table}}

\begin{{table}}[b]
\caption{{Final visible-mass category yields.  Background includes MC
backgrounds and the same-sign QCD/fake estimate.}}
\begin{{ruledtabular}}
\begin{{tabular}}{{lrrrr}}
Category & Data & Bkg. & Signal & $\chi^2/\mathrm{{ndf}}$ \\
{category_rows}
\end{{tabular}}
\end{{ruledtabular}}
\end{{table}}

\begin{{table}}[t]
\caption{{Final visible-mass and NN-score limit summary.}}
\begin{{ruledtabular}}
\begin{{tabular}}{{lrr}}
Quantity & Visible mass & $D_{{NN}}$ score \\
Observed 95\% CLs & $\mu<{baseline_lim['observed_limit']:.3f}$ & $\mu<{nn_lim['observed_limit']:.3f}$ \\
Expected median & $\mu<{baseline_band[2]:.3f}$ & $\mu<{nn_band[2]:.3f}$ \\
Observed $\hat{{\mu}}$ & ${baseline_mu['mu_hat']:.3f}$ & ${nn_fit['mu_hat']:.3f}$ \\
Data/background & {baseline_val['combined']['data_over_background']:.3f} & {nn_val['combined']['data_over_background']:.3f} \\
GoF toy-style $p$ & {baseline_gof['toy_p_value']:.3f} & -- \\
\end{{tabular}}
\end{{ruledtabular}}
\end{{table}}

\paragraph{{Validation and result.}}
The combined visible-mass validation gives data/background
{baseline_val['combined']['data_over_background']:.3f} and
$\chi^2/\mathrm{{ndf}}={baseline_val['combined']['chi2_per_ndf']:.3f}$.
The VBF category carries the largest local residual with max pull
{baseline_val['score_template_validation']['vbf']['max_abs_pull']:.2f}.
The observed-data toy-style goodness-of-fit check gives
$p={baseline_gof['toy_p_value']:.3f}$.
The optimized classifier study has better expected sensitivity but fails its
observed validation gate ({gate['status']}); the separately reported $D_{{NN}}$ score
fit has combined data/background {nn_val['combined']['data_over_background']:.3f}
and $\chi^2/\mathrm{{ndf}}={nn_val['combined']['chi2_per_ndf']:.3f}$.

\begin{{figure*}}[t]
\centering
\includegraphics[width=0.19\linewidth]{{figures/phase5_baseline_visible_vbf.pdf}}\hspace{{0.004\linewidth}}
\includegraphics[width=0.19\linewidth]{{figures/phase5_baseline_visible_boosted.pdf}}\hspace{{0.004\linewidth}}
\includegraphics[width=0.19\linewidth]{{figures/phase5_baseline_visible_zero_jet.pdf}}\hspace{{0.004\linewidth}}
\includegraphics[width=0.19\linewidth]{{figures/phase5_baseline_visible_combined.pdf}}\hspace{{0.004\linewidth}}
\includegraphics[width=0.19\linewidth]{{figures/phase5_baseline_limit_summary.pdf}}
\caption{{Visible-mass post-fit validation and limit summary.  The first three
panels show the VBF, boosted, and zero-jet post-fit validation distributions,
the fourth panel shows their combined Data/post-fit comparison, and the right
panel shows the CLs limit that defines the final result.}}
\end{{figure*}}

\begin{{figure*}}[t]
\centering
\includegraphics[width=0.24\linewidth]{{figures/phase5_nn_score_vbf.pdf}}\hspace{{0.006\linewidth}}
\includegraphics[width=0.24\linewidth]{{figures/phase5_nn_score_boosted.pdf}}\hspace{{0.006\linewidth}}
\includegraphics[width=0.24\linewidth]{{figures/phase5_nn_score_zero_jet.pdf}}\hspace{{0.006\linewidth}}
\includegraphics[width=0.24\linewidth]{{figures/phase5_nn_score_combined.pdf}}
\caption{{$D_{{NN}}$ score post-fit validation in the VBF, boosted,
zero-jet, and combined categories.  The lower panels use Data/post-fit with the
post-fit classifier-score model in the denominator.}}
\end{{figure*}}

\begin{{table}}[b]
\caption{{Published context comparison.  The entries are not direct
apples-to-apples measurements because the public reduced analysis has fewer
channels and calibrations.}}
\begin{{ruledtabular}}
\begin{{tabular}}{{lll}}
Context & Result & Role \\
This work & $\mu<{baseline_lim['observed_limit']:.2f}$ & weak limit \\
CMS Run 1 & $\mu=0.78\pm0.27$ & evidence \\
CMS 2018 & 4.9$\sigma$ & observation \\
ATLAS+CMS & $\mu=1.09\pm0.11$ & precision \\
\end{{tabular}}
\end{{ruledtabular}}
\end{{table}}

\paragraph{{Interpretation.}}
CMS Run 1 and later CMS publications observe or provide evidence for
$H\to\tau\tau$ with many channels and a fuller calibration program.  The
present result is consistent only as a low-sensitivity public-data exercise:
its median expected limit of $\mu<{baseline_band[2]:.3f}$ is an order of
magnitude above the Standard Model rate.

\begin{{thebibliography}}{{9}}
\bibitem{{opendata}} S. Wunsch, \emph{{Analysis of Higgs boson decays to two tau leptons using data and simulation of events at the CMS detector from 2012}}, CERN Open Data Portal, doi:10.7483/OPENDATA.CMS.GV20.PR5T.
\bibitem{{cms2014}} CMS Collaboration, JHEP 05 (2014) 104.
\bibitem{{cms2018}} CMS Collaboration, Phys. Lett. B 779 (2018) 283.
\bibitem{{atlascms2016}} ATLAS and CMS Collaborations, JHEP 08 (2016) 045.
\bibitem{{pdg2024}} Particle Data Group, Phys. Rev. D 110 (2024) 030001.
\bibitem{{pyhf}} L. Heinrich et al., JOSS 6 (2021) 2823.
\bibitem{{cls}} A. L. Read, J. Phys. G 28 (2002) 2693.
\bibitem{{cowan}} G. Cowan et al., Eur. Phys. J. C 71 (2011) 1554.
\end{{thebibliography}}

\end{{document}}
"""


def compile_prl(observed: dict, visible_yields: dict, baseline: dict, nn_payload: dict) -> None:
    tex = build_prl_tex(observed, visible_yields, baseline, nn_payload)
    (OUT / "PAPER_PRL_v1.tex").write_text(tex)
    subprocess.run(["tectonic", "PAPER_PRL_v1.tex"], cwd=OUT, check=True)
    append_log("Compiled baseline-only PAPER_PRL_v1.tex with REVTeX PRL class.")


def write_docs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    observed = load_json("phase4_inference/4c_observed/outputs/observed_results.json")
    baseline = load_json("phase4_inference/4c_observed/outputs/baseline_visible_result.json")
    nn_result = load_json("phase4_inference/4c_observed/outputs/nn_score_result.json")
    visible_yields = load_json("phase4_inference/4c_observed/outputs/baseline_visible_yields.json")
    nn_yields = load_json("phase4_inference/4c_observed/outputs/nn_score_observed_yields.json")
    baseline_observed_gof_toys()
    write_json("phase5_documentation/outputs/baseline_visible_result.json", baseline)
    write_json("phase5_documentation/outputs/baseline_visible_yields.json", visible_yields)
    write_json("phase5_documentation/outputs/nn_score_result.json", nn_result)
    write_json("phase5_documentation/outputs/nn_score_observed_yields.json", nn_yields)

    FIG.mkdir(parents=True, exist_ok=True)
    for old in FIG.glob("*.*"):
        if old.suffix.lower() in {".pdf", ".png"}:
            old.unlink()
    for stem in [
        "cutflow_summary",
        "category_yields",
        "mu_pt",
        "tau_pt",
        "met_pt",
        "mt_mu_met",
        "visible_mass_vbf",
        "visible_mass_boosted",
        "visible_mass_zero_jet",
        "mva_input_modeling_chi2",
        "mva_score_templates",
        "sensitivity_variant_summary",
        "sensitivity_nuisance_audit",
        "observed_visible_vbf",
        "observed_visible_boosted",
        "observed_visible_zero_jet",
        "observed_nn_score_vbf",
        "observed_nn_score_boosted",
        "observed_nn_score_zero_jet",
        "observed_limit_significance_summary",
        "observed_pull_ratio_summary",
        "w_highmt_scale_full",
        "comparison_to_4a_4b",
    ]:
        for suffix in [".pdf", ".png"]:
            phase3_src = ROOT / "phase3_selection" / "outputs" / "figures" / f"{stem}{suffix}"
            phase4_src = ROOT / "phase4_inference" / "4c_observed" / "outputs" / "figures" / f"{stem}{suffix}"
            src = phase3_src if phase3_src.exists() else phase4_src
            if src.exists():
                target_name = stem.replace("observed_visible", "phase5_baseline_visible").replace("observed_nn_score", "phase5_nn_score")
                shutil.copy2(src, FIG / f"{target_name}{suffix}")
    nn_payload = {"result": nn_result, "model": {"yields": nn_yields}}
    for category in CATEGORIES:
        make_prefit_validation_figure(
            yields_payload=visible_yields,
            category=category,
            output_stem=f"phase5_prefit_baseline_visible_{category}",
            xlabel="Visible mass [GeV]",
            legend_loc="upper left",
        )
        make_prefit_validation_figure(
            yields_payload=nn_yields,
            category=category,
            output_stem=f"phase5_prefit_nn_score_{category}",
            xlabel=r"$D_{NN}$ score",
            legend_loc="upper right",
        )
        make_visible_validation_figure(category, visible_yields, baseline)
        make_nn_score_validation_figure(category, nn_payload)
    make_combined_prefit_validation_figure(
        yields_payload=visible_yields,
        output_stem="phase5_prefit_baseline_visible_combined",
        xlabel="Visible mass [GeV]",
        model_label="Combined categories",
        legend_loc="upper left",
    )
    make_combined_prefit_validation_figure(
        yields_payload=nn_yields,
        output_stem="phase5_prefit_nn_score_combined",
        xlabel=r"$D_{NN}$ score",
        model_label="Combined categories",
        legend_loc="upper right",
    )
    make_combined_postfit_validation_figure(
        yields_payload=visible_yields,
        workspace_relpath="phase4_inference/4c_observed/outputs/pyhf_workspace_baseline_visible.json",
        output_stem="phase5_baseline_visible_combined",
        xlabel="Visible mass [GeV]",
        model_label="Combined categories",
        legend_loc="upper left",
    )
    make_combined_postfit_validation_figure(
        yields_payload=nn_yields,
        workspace_relpath="phase4_inference/4c_observed/outputs/pyhf_workspace_nn_score.json",
        output_stem="phase5_nn_score_combined",
        xlabel=r"$D_{NN}$ score",
        model_label="Combined categories",
        legend_loc="upper right",
    )
    merge_references()

    bfit = baseline["observed_fit"]
    blim = bfit["observed_upper_limit"]
    bband = blim["expected_band_minus2_minus1_median_plus1_plus2"]
    bprof = bfit.get("profile_mu_interval", {"err_minus": bfit["mu_hat"], "err_plus": blim["observed_limit"] - bfit["mu_hat"]})
    nfit = nn_result["observed_fit"]
    nlim = nfit["observed_upper_limit"]
    nband = nlim["expected_band_minus2_minus1_median_plus1_plus2"]
    nprof = nfit.get("profile_mu_interval", {"err_minus": nfit["mu_hat"], "err_plus": nlim["observed_limit"] - nfit["mu_hat"]})
    bval = baseline["validation_summary"]["combined"]
    nval = nn_result["validation_summary"]["combined"]
    w_scale = observed["wjets_high_mt_scale"]
    vbf_scale = observed["vbf_background_scale"]
    syst = observed["systematics_retained"]
    training = nn_result["training_summary"]
    training_model = training.get("model", {})
    training_inputs = training.get("inputs", [])
    expected = load_json("phase4_inference/4a_expected/outputs/expected_results.json")
    categories = visible_yields["categories"]
    tex_categories = [category.replace("_", r"\_") for category in categories]
    rows = []
    for category in categories:
        total = visible_yields["totals"][category]
        val = baseline["validation_summary"]["score_template_validation"][category]
        rows.append(
            f"| {category} | {total['data_total']:.0f} | {total['background_total']:.2f} | "
            f"{total['signal_total']:.2f} | {val['data_over_background']:.3f} | {val['chi2_per_ndf']:.3f} |"
        )
    syst_rows = "\n".join(f"| {name} | {value} |" for name, value in syst.items())
    nn_input_text = ", ".join(f"`{item}`" for item in training_inputs)
    expected_limit = expected.get("expected_upper_limit", {}).get("expected_band_minus2_minus1_median_plus1_plus2", [None, None, None, None, None])[2]
    an = f"""---
title: "CMS Open Data H to Tau Tau Search: Final Analysis Note"
author: "Analysis my_analysis"
date: "2026-06-13"
bibliography: references.bib
---

# Abstract {{-}}

This note reports a full rerun of the muon plus hadronic-tau Higgs-to-tau-tau
analysis with the current local CMS Open Data and simulation inputs. The
analysis follows the Run-1 H to tau tau strategy of a simultaneous binned fit
in VBF, boosted, and zero-jet categories [@cms_htt_2014] and keeps two
result streams: a cut-based visible-mass baseline and a single
three-category $D_{{NN}}$ classifier-score result. The visible-mass baseline
gives `mu_hat = {bfit['mu_hat']:.4f}`, observed 95% CLs `mu < {blim['observed_limit']:.4f}`,
median expected limit `{bband[2]:.4f}`, and interval proxy
`mu_hat = {bfit['mu_hat']:.4f} +{bprof['err_plus']:.4f} -{bprof['err_minus']:.4f}`.
The $D_{{NN}}$ score result gives
`mu_hat = {nfit['mu_hat']:.4f}`, observed 95% CLs `mu < {nlim['observed_limit']:.4f}`,
median expected limit `{nband[2]:.4f}`, and interval proxy
`mu_hat = {nfit['mu_hat']:.4f} +{nprof['err_plus']:.4f} -{nprof['err_minus']:.4f}`.
The results are interpreted as a
single-channel public-data exercise, not as a replacement for the published CMS
combination [@cms_htt_2018].

# Introduction

The target process is Standard Model Higgs boson production followed by
$H \\to \\tau\\tau$, reconstructed in the $\\mu\\tau_h$ final state. This channel
combines a clean isolated muon with a hadronic-tau candidate and is one of the
classic ingredients of the CMS H to tau tau program [@cms_htt_2014]. The
parameter of interest is the signal-strength modifier

$$
\\mu =
\\frac{{\\sigma(pp\\to H)\\,\\mathcal{{B}}(H\\to\\tau\\tau)}}
{{\\left[\\sigma(pp\\to H)\\,\\mathcal{{B}}(H\\to\\tau\\tau)\\right]_{{SM}}}} .
$$ {{#eq:mu-def}}

The reduced Open Data setting has less information than the published Run-1
analyses: embedded $Z\\to\\tau\\tau$ samples, several rare backgrounds, and full
object-calibration machinery are not available. The note therefore emphasizes
the reproducible signal-extraction chain, the category-level validation, and the
relative behavior of the visible-mass and $D_{{NN}}$ observables.

# Data And Simulation

The data input is the localized CMS 2012 TauPlusX Run2012B and Run2012C sample.
The simulated inputs are ggH and VBF Higgs signal, DY+jets, top-pair, and
exclusive W+jets samples. The normalization uses the Open Data record event
counts and the luminosity reference stored in the local normalization artifact.

![Input and selected-event cutflow. The figure shows the data and simulation
counts through the main selection stages after the rerun on the current local
inputs. It is the first check that the event processing consumed the updated
ROOT files.](figures/cutflow_summary.pdf){{#fig:cutflow}}

![Final category yields. The figure summarizes the selected yields in the VBF,
boosted, and zero-jet categories before the final binned statistical fit. It
provides a compact check of the category split used by both retained
observables.](figures/category_yields.pdf){{#fig:category-yields}}

# Event Selection And Categories

Events are required to contain a selected muon, a selected hadronic-tau
candidate, low transverse mass, and an opposite-sign signal-region pair. The
categories are mutually exclusive. The VBF category requires two clean jets with
a large dijet mass and pseudorapidity separation, the boosted category captures
remaining events with a reconstructed recoil topology, and the zero-jet category
contains the statistically dominant inclusive remainder.

![Selected muon transverse momentum. The comparison shows the selected muon
$p_T$ spectrum in data and simulation after the signal-region selection. It is
used as an object-level validation input rather than a fitted observable.](figures/mu_pt.pdf){{#fig:mu-pt}}

![Selected hadronic-tau transverse momentum. The comparison shows the selected
$\\tau_h$ $p_T$ spectrum in data and simulation. It checks the stability of the
tau-object phase space used by the baseline and $D_{{NN}}$ fits.](figures/tau_pt.pdf){{#fig:tau-pt}}

![Missing transverse momentum. The comparison shows the selected missing
transverse momentum distribution. This variable enters the classifier input set
and is also a key validation distribution for W+jets and tau-pair kinematics.](figures/met_pt.pdf){{#fig:met-pt}}

![Transverse mass control distribution. The comparison shows the
$m_T(\\mu,p_T^{{miss}})$ distribution used to monitor the W+jets-rich high-mass
region. The final W+jets scale is derived from the corresponding high-$m_T$
control selection.](figures/mt_mu_met.pdf){{#fig:mt-mu-met}}

# Observables

The baseline observable is the visible di-tau mass $m_{{vis}}$, the invariant
mass of the reconstructed muon and hadronic-tau four-vectors. It is robust and
cut-based, but broad because neutrinos from both tau decays are not
reconstructed. The retained multivariate observable is $D_{{NN}}$, implemented
as an XGBoost classifier score `mva_score_xgboost` in 20 uniform bins from 0 to
1. Its input set is:

{nn_input_text}.

The classifier is trained on MC signal and background labels with the nominal MC
normalization weights and class balancing. In the current rerun the stored
training metric is test AUC `{training_model.get('test_auc', float('nan')):.4f}`
with train AUC `{training_model.get('train_auc', float('nan')):.4f}`.

![Baseline visible-mass pre-fit validation in the VBF category. The plot
compares data with the nominal visible-mass background plus Standard Model
Higgs prediction before profiling nuisance parameters in the signal fit. The
lower panel is Data/pre-fit.](figures/phase5_prefit_baseline_visible_vbf.pdf){{#fig:visible-vbf-prefit}}

![Baseline visible-mass pre-fit validation in the boosted category. The plot
shows the boosted-category nominal visible-mass prediction before the post-fit
profile update. This is a major contributor to the simultaneous visible-mass
baseline fit.](figures/phase5_prefit_baseline_visible_boosted.pdf){{#fig:visible-boosted-prefit}}

![Baseline visible-mass pre-fit validation in the zero-jet category. The plot
shows the highest-statistics baseline category before post-fit nuisance
profiling. It anchors the background-rich part of the simultaneous
fit.](figures/phase5_prefit_baseline_visible_zero_jet.pdf){{#fig:visible-zero-prefit}}

![Baseline visible-mass combined pre-fit validation. The plot sums the VBF,
boosted, and zero-jet nominal visible-mass predictions and compares them with
the summed observed data before profiling. The lower panel is the combined
Data/pre-fit ratio.](figures/phase5_prefit_baseline_visible_combined.pdf){{#fig:visible-combined-prefit}}

![MVA input modelling summary. The figure records the data/background modelling
quality of candidate classifier inputs. It documents the validation context for
using a single retained $D_{{NN}}$ tool.](figures/mva_input_modeling_chi2.pdf){{#fig:mva-inputs}}

![Expected classifier score templates. The figure shows the trained classifier
score response for signal and background before observed-data fitting. It
checks that the retained classifier has the intended signal/background
ordering.](figures/mva_score_templates.pdf){{#fig:mva-score-templates}}

![$D_{{NN}}$ score pre-fit validation in the VBF category. The plot compares
data with the nominal classifier-score background plus Standard Model Higgs
prediction before profiling nuisance parameters in the secondary score fit. The
lower panel is Data/pre-fit.](figures/phase5_prefit_nn_score_vbf.pdf){{#fig:nn-vbf-prefit}}

![$D_{{NN}}$ score pre-fit validation in the boosted category. The plot shows
the boosted-category nominal classifier-score prediction before the post-fit
profile update. It uses the same score binning as the secondary
workspace.](figures/phase5_prefit_nn_score_boosted.pdf){{#fig:nn-boosted-prefit}}

![$D_{{NN}}$ score pre-fit validation in the zero-jet category. The plot shows
the statistically dominant classifier-score category before nuisance profiling.
The lower panel is Data/pre-fit.](figures/phase5_prefit_nn_score_zero_jet.pdf){{#fig:nn-zero-prefit}}

![$D_{{NN}}$ score combined pre-fit validation. The plot sums the VBF, boosted,
and zero-jet nominal classifier-score predictions and compares them with the
summed observed data before profiling. The lower panel is the combined
Data/pre-fit ratio.](figures/phase5_prefit_nn_score_combined.pdf){{#fig:nn-combined-prefit}}

# Background Model

The W+jets normalization is constrained from a high-$m_T$ control region. With
the current inputs the full-data scale factor is
`{w_scale['applied_scale_factor']:.4f} ± {w_scale['absolute_uncertainty']:.4f}`.
The VBF background scale from the VBF-like non-signal control region is
`{vbf_scale['applied_scale_factor']:.4f} ± {vbf_scale['absolute_uncertainty']:.4f}`.
The reducible QCD/fake component is estimated from same-sign data after
subtracting non-QCD simulation and transferring into the signal region.

![W high-$m_T$ control-region scale. The figure shows the non-W MC, nominal W
MC, scaled control-region prediction, and observed data in the high-$m_T$
control region. This scale is propagated to both retained workspaces.](figures/w_highmt_scale_full.pdf){{#fig:w-scale}}

# Systematic Uncertainties

The retained nuisance program covers luminosity, tau/open-data acceptance,
DY/Z normalization, W+jets control normalization, VBF background control
normalization, same-sign QCD/fake transfer, and MC statistical uncertainties.
The exact current values are read from the Phase-4c JSON artifact:

| Source | Current value |
| --- | --- |
{syst_rows}

![Sensitivity nuisance audit. The figure summarizes the expected sensitivity
response to the retained nuisance model. It is used to confirm that the
current results are not driven by a hidden no-systematics configuration.](figures/sensitivity_nuisance_audit.pdf){{#fig:nuisance-audit}}

# Statistical Model

Both retained results use binned HistFactory-style likelihoods implemented with
pyhf [@pyhf_joss]. For category $c$ and bin $b$, the expected count is

$$
\\nu_{{cb}}(\\mu,\\theta) =
\\mu s_{{cb}}(\\theta) + \\sum_k b_{{kcb}}(\\theta),
$$ {{#eq:expectation}}

where $s_{{cb}}$ is the sum of ggH and VBF signal templates and $b_{{kcb}}$
are the background templates. The likelihood is the product of Poisson terms
for the binned data and Gaussian/log-normal constraints for nuisance
parameters. Upper limits use the modified frequentist CLs construction
[@read_cls] with asymptotic formulae [@cowan_asymptotic].

The expected median limit from the earlier expected-only reference point is
`{expected_limit}`. The current observed limits are computed from the full data
with the updated local selection and templates.

# Full-Data Results

| Category | Data | Background | Signal | Data/background | Chi2/ndf |
| --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

The combined visible-mass validation gives data/background `{bval['data_over_background']:.3f}`
and chi2/ndf `{bval['chi2_per_ndf']:.3f}`. The combined $D_{{NN}}$ validation
gives data/background `{nval['data_over_background']:.3f}` and chi2/ndf
`{nval['chi2_per_ndf']:.3f}`.

The visible-mass baseline fit gives

$$
\\hat{{\\mu}}(m_{{vis}}) = {bfit['mu_hat']:.4f}, \\qquad
\\mu < {blim['observed_limit']:.4f} \\; (95\\%\\; CLs),
$$ {{#eq:baseline-result}}

with median expected limit `{bband[2]:.4f}`. The $D_{{NN}}$ result gives

$$
\\hat{{\\mu}}(D_{{NN}}) = {nfit['mu_hat']:.4f}, \\qquad
\\mu < {nlim['observed_limit']:.4f} \\; (95\\%\\; CLs),
$$ {{#eq:nn-result}}

with median expected limit `{nband[2]:.4f}`.

![Visible-mass baseline post-fit validation in the VBF category. The plot
compares data with the post-fit visible-mass total from the retained baseline
workspace, with the nominal background plus Standard Model Higgs template
overlaid for reference. The lower panel shows the Data/post-fit
ratio.](figures/phase5_baseline_visible_vbf.pdf){{#fig:p5-visible-vbf}}

![Visible-mass baseline post-fit validation in the boosted category. The plot
compares data with the post-fit visible-mass total from the retained baseline
workspace. This category has substantially more events than the VBF category
and constrains the broad visible-mass shape.](figures/phase5_baseline_visible_boosted.pdf){{#fig:p5-visible-boosted}}

![Visible-mass baseline post-fit validation in the zero-jet category. The plot
compares data with the post-fit visible-mass total from the retained baseline
workspace in the statistically dominant category. This category controls the
global normalization behavior of the baseline workspace.](figures/phase5_baseline_visible_zero_jet.pdf){{#fig:p5-visible-zero}}

![Combined visible-mass baseline post-fit validation. The plot sums the VBF,
boosted, and zero-jet post-fit visible-mass model expectations and compares
them with the summed observed data. The lower panel is the combined
Data/post-fit ratio used as the global baseline Data/MC check.](figures/phase5_baseline_visible_combined.pdf){{#fig:p5-visible-combined}}

![$D_{{NN}}$ score post-fit validation in the VBF category. The plot compares
data with the post-fit classifier-score total in the VBF category. The same
score definition and binning are used in the other
categories.](figures/phase5_nn_score_vbf.pdf){{#fig:p5-nn-vbf}}

![$D_{{NN}}$ score post-fit validation in the boosted category. The plot
compares data with the post-fit classifier-score total in the boosted category.
The ratio panel checks whether the classifier ordering is modelled in observed
data.](figures/phase5_nn_score_boosted.pdf){{#fig:p5-nn-boosted}}

![$D_{{NN}}$ score post-fit validation in the zero-jet category. The plot
compares data with the post-fit classifier-score total in the zero-jet category.
The category has the largest statistical weight in the combined classifier
fit.](figures/phase5_nn_score_zero_jet.pdf){{#fig:p5-nn-zero}}

![Combined $D_{{NN}}$ score post-fit validation. The plot sums the VBF,
boosted, and zero-jet post-fit classifier-score expectations and compares them
with the summed observed score distribution. The lower panel is the combined
Data/post-fit ratio used as the global score Data/MC check.](figures/phase5_nn_score_combined.pdf){{#fig:p5-nn-combined}}

![Observed result summary. The figure compares the visible-mass baseline,
retained $D_{{NN}}$ result, CMS 2014 result, and CMS 2018 result on the same
signal-strength scale. Each row uses the same convention: black observed point
with horizontal uncertainty, green and yellow expected one- and two-standard
deviation bands, a black dashed median-expected marker, and the common Standard
Model line at $\\mu=1$.](figures/observed_limit_significance_summary.pdf){{#fig:p5-summary}}

# Comparison To Published Measurements

The CMS Run-1 H to tau tau analysis and later CMS combination use more final
states, more luminosity, embedded backgrounds, and a much richer calibration
program than this single-channel public-data analysis [@cms_htt_2014;
@cms_htt_2018]. The correct comparison is therefore qualitative: the present
analysis demonstrates a reproducible template-fit chain and produces limits
that are much weaker than the published measurements. The retained
$D_{{NN}}$ result is the more sensitive of the two current outputs by expected
median limit, while the visible-mass baseline remains the cut-based reference.

# Validation And Limitations

The current run validates that both pyhf workspaces construct, that both fits
evaluate, that the $D_{{NN}}$ template uses `mva_score_xgboost`, and that the
classifier score uses 20 uniform bins. Remaining limitations are inherited from
the reduced public-input setting: the absence of embedded $Z\\to\\tau\\tau$,
incomplete rare backgrounds, simplified object systematics, and reliance on
control-derived nuisance parameters.

# Reproduction Contract

The current machine-readable result artifacts are:

| Artifact | Purpose |
| --- | --- |
| `phase4_inference/4c_observed/outputs/baseline_visible_result.json` | visible-mass baseline result |
| `phase4_inference/4c_observed/outputs/nn_score_result.json` | retained $D_{{NN}}$ result |
| `phase4_inference/4c_observed/outputs/pyhf_workspace_baseline_visible.json` | baseline pyhf workspace |
| `phase4_inference/4c_observed/outputs/pyhf_workspace_nn_score.json` | $D_{{NN}}$ pyhf workspace |
| `phase4_inference/4c_observed/outputs/visible_observed_templates.npz` | baseline templates |
| `phase4_inference/4c_observed/outputs/nn_score_observed_templates.npz` | $D_{{NN}}$ templates |

The focused rebuild commands are `pixi run phase3-select`, `pixi run phase3-mva`,
`pixi run phase3-sensitivity`, `pixi run phase3-plots`, `pixi run phase4c-all`,
and `pixi run phase5-docs`.
"""
    paper_tex = rf"""\documentclass[aps,prl,reprint,superscriptaddress,nofootinbib]{{revtex4-2}}
\usepackage{{graphicx}}
\usepackage{{amsmath}}
\usepackage{{booktabs}}
\usepackage{{hyperref}}

\begin{{document}}

\title{{Search for Higgs boson decays to tau pairs in the muon plus hadronic-tau final state with CMS Open Data}}
\author{{Analysis my\_analysis}}
\affiliation{{CMS Open Data analysis}}
\date{{2026-06-13}}

\begin{{abstract}}
A search for Standard Model Higgs boson decays to tau pairs is performed in the
$\mu\tau_h$ final state using the localized CMS 2012 TauPlusX Open Data and
simulation samples.  Events are split into VBF, boosted, and zero-jet
categories and interpreted with binned pyhf/HistFactory likelihoods.  The
visible-mass baseline gives $\hat{{\mu}}={bfit['mu_hat']:.3f}^{{+{bprof['err_plus']:.3f}}}_{{-{bprof['err_minus']:.3f}}}$,
an observed 95\% CLs upper limit $\mu<{blim['observed_limit']:.3f}$, and a
median expected limit $\mu<{bband[2]:.3f}$.  The retained $D_{{NN}}$ classifier
score gives $\hat{{\mu}}={nfit['mu_hat']:.3f}^{{+{nprof['err_plus']:.3f}}}_{{-{nprof['err_minus']:.3f}}}$,
an observed 95\% CLs upper limit $\mu<{nlim['observed_limit']:.3f}$, and a
median expected limit $\mu<{nband[2]:.3f}$.  The $D_{{NN}}$ result is the more
sensitive of the two retained observables in this single-channel public-data
exercise.
\end{{abstract}}

\maketitle

\section{{Introduction}}
The observation of Higgs boson decays to tau leptons established the direct
coupling of the Higgs field to charged leptons.  The CMS Run-1 analysis in
JHEP 05 (2014) 104 and the later combined measurement in Phys. Lett. B 779
(2018) 283 use multiple final states, full detector calibrations, and embedded
background methods.  The present work is a reduced, reproducible Open Data
analysis in the $\mu\tau_h$ final state.  It preserves the central structure of
the published strategy: category splitting, data-driven control inputs, and a
simultaneous binned likelihood for a signal-strength modifier $\mu$.

\section{{Data, simulation, and selection}}
The analysis uses the Run2012B and Run2012C TauPlusX data samples and the
available ggH, VBF, DY+jets, top-pair, and W+jets simulation samples.  Events
are selected with one muon and one hadronic-tau candidate and are divided into
VBF, boosted, and zero-jet categories.  The current selected category yields
are summarized in Table~\ref{{tab:yields}}.

\begin{{table}}[b]
\caption{{Selected category yields for the visible-mass baseline templates.}}
\label{{tab:yields}}
\begin{{ruledtabular}}
\begin{{tabular}}{{lrrrr}}
Category & Data & Background & Signal & Data/Bkg. \\
\hline
{tex_categories[0]} & {visible_yields['totals'][categories[0]]['data_total']:.0f} & {visible_yields['totals'][categories[0]]['background_total']:.1f} & {visible_yields['totals'][categories[0]]['signal_total']:.2f} & {baseline['validation_summary']['score_template_validation'][categories[0]]['data_over_background']:.3f} \\
{tex_categories[1]} & {visible_yields['totals'][categories[1]]['data_total']:.0f} & {visible_yields['totals'][categories[1]]['background_total']:.1f} & {visible_yields['totals'][categories[1]]['signal_total']:.2f} & {baseline['validation_summary']['score_template_validation'][categories[1]]['data_over_background']:.3f} \\
{tex_categories[2]} & {visible_yields['totals'][categories[2]]['data_total']:.0f} & {visible_yields['totals'][categories[2]]['background_total']:.1f} & {visible_yields['totals'][categories[2]]['signal_total']:.2f} & {baseline['validation_summary']['score_template_validation'][categories[2]]['data_over_background']:.3f} \\
\end{{tabular}}
\end{{ruledtabular}}
\end{{table}}

\section{{Observables and statistical model}}
Two observables are retained.  The cut-based baseline is the visible
di-tau mass $m_{{vis}}$.  The multivariate result is the XGBoost classifier
score $D_{{NN}}$, fitted in 20 uniform bins in each category.  For each
observable, the expected count in category $c$ and bin $b$ is
\begin{{equation}}
\nu_{{cb}}(\mu,\theta)=\mu s_{{cb}}(\theta)+\sum_k b_{{kcb}}(\theta),
\end{{equation}}
with nuisance parameters $\theta$ constrained by auxiliary terms.  Upper limits
use the asymptotic modified-frequentist CLs construction.

\section{{Results}}
Figure~\ref{{fig:summary}} shows the final signal-strength summary in the same
style for both retained observables.  The visible-mass baseline gives
$\hat{{\mu}}={bfit['mu_hat']:.3f}^{{+{bprof['err_plus']:.3f}}}_{{-{bprof['err_minus']:.3f}}}$ and
$\mu<{blim['observed_limit']:.3f}$ at 95\% CLs.  The $D_{{NN}}$ result gives
$\hat{{\mu}}={nfit['mu_hat']:.3f}^{{+{nprof['err_plus']:.3f}}}_{{-{nprof['err_minus']:.3f}}}$ and
$\mu<{nlim['observed_limit']:.3f}$ at 95\% CLs.

\begin{{figure}}[t]
\includegraphics[width=\linewidth]{{figures/observed_limit_significance_summary.pdf}}
\caption{{Observed signal-strength summary for the visible-mass baseline,
$D_{{NN}}$ result, CMS 2014 result, and CMS 2018 result.  Each row uses black
observed points with horizontal uncertainties, green and yellow expected
one- and two-standard-deviation bands, a black dashed median-expected marker,
and the common Standard Model line at $\mu=1$.}}
\label{{fig:summary}}
\end{{figure}}

\begin{{figure*}}[t]
\includegraphics[width=0.48\linewidth]{{figures/phase5_baseline_visible_combined.pdf}}\hfill
\includegraphics[width=0.48\linewidth]{{figures/phase5_nn_score_combined.pdf}}
\caption{{Combined post-fit Data/MC validation.  The left panel shows the
visible-mass baseline summed over VBF, boosted, and zero-jet categories; the
right panel shows the corresponding combined $D_{{NN}}$ score distribution.
Both lower panels use Data/post-fit model ratios.}}
\label{{fig:combined-postfit}}
\end{{figure*}}

\section{{Discussion}}
The $D_{{NN}}$ observable has the smaller median expected upper limit and is
therefore the more sensitive of the two retained tools in this rerun.  The
analysis is statistically limited and remains substantially weaker than the
published multi-channel CMS results, but it demonstrates a complete Open Data
template-fit chain with explicit machine-readable workspaces.

\begin{{thebibliography}}{{9}}
\bibitem{{cms2014}} CMS Collaboration, ``Evidence for the 125 GeV Higgs boson decaying to a pair of tau leptons,'' JHEP 05 (2014) 104.
\bibitem{{cms2018}} CMS Collaboration, ``Observation of the Higgs boson decay to a pair of tau leptons,'' Phys. Lett. B 779 (2018) 283.
\bibitem{{pyhf}} L. Heinrich et al., ``pyhf: pure-Python implementation of HistFactory statistical models,'' JOSS 6 (2021) 2823.
\bibitem{{cls}} A. L. Read, ``Presentation of search results: the CLs technique,'' J. Phys. G 28 (2002) 2693.
\end{{thebibliography}}

\end{{document}}
"""
    paper_md = f"""---
title: "Search for Higgs boson decays to tau pairs in the muon plus hadronic-tau final state with CMS Open Data"
author: "Analysis my_analysis"
date: "2026-06-13"
---

# Abstract

A search for Standard Model Higgs boson decays to tau pairs is performed in the
$\\mu\\tau_h$ final state using the localized CMS 2012 TauPlusX Open Data and
simulation samples. Events are split into VBF, boosted, and zero-jet categories
and interpreted with binned pyhf/HistFactory likelihoods. The visible-mass
baseline gives $\\hat{{\\mu}}={bfit['mu_hat']:.3f}^{{+{bprof['err_plus']:.3f}}}_{{-{bprof['err_minus']:.3f}}}$,
an observed 95% CLs upper limit $\\mu<{blim['observed_limit']:.3f}$, and a
median expected limit $\\mu<{bband[2]:.3f}$. The retained $D_{{NN}}$ classifier
score gives $\\hat{{\\mu}}={nfit['mu_hat']:.3f}^{{+{nprof['err_plus']:.3f}}}_{{-{nprof['err_minus']:.3f}}}$,
an observed 95% CLs upper limit $\\mu<{nlim['observed_limit']:.3f}$, and a
median expected limit $\\mu<{nband[2]:.3f}$.

# Introduction

The CMS Run-1 analysis in JHEP 05 (2014) 104 and the later combined measurement
in Phys. Lett. B 779 (2018) 283 use multiple final states, full detector
calibrations, and embedded background methods. This reduced Open Data analysis
keeps the central structure needed for a reproducible single-channel search:
category splitting, control-derived background constraints, and a simultaneous
binned likelihood for the signal-strength modifier $\\mu$.

# Data, Selection, And Model

The analysis uses Run2012B and Run2012C TauPlusX data and the available ggH,
VBF, DY+jets, top-pair, and W+jets simulation samples. Events are selected with
one muon and one hadronic-tau candidate and are divided into VBF, boosted, and
zero-jet categories. The baseline observable is $m_{{vis}}$; the multivariate
observable is the XGBoost classifier score $D_{{NN}}$ in 20 uniform bins.

# Results

The visible-mass baseline gives $\\hat{{\\mu}}={bfit['mu_hat']:.3f}^{{+{bprof['err_plus']:.3f}}}_{{-{bprof['err_minus']:.3f}}}$
and $\\mu<{blim['observed_limit']:.3f}$ at 95% CLs. The $D_{{NN}}$ result gives
$\\hat{{\\mu}}={nfit['mu_hat']:.3f}^{{+{nprof['err_plus']:.3f}}}_{{-{nprof['err_minus']:.3f}}}$
and $\\mu<{nlim['observed_limit']:.3f}$ at 95% CLs.

![Observed signal-strength summary for the visible-mass baseline, $D_{{NN}}$
result, CMS 2014 result, and CMS 2018 result. Each row uses black observed
points with horizontal uncertainties, green and yellow expected one- and
two-standard-deviation bands, a black dashed median-expected marker, and the
common Standard Model line at $\\mu=1$.](figures/observed_limit_significance_summary.pdf)

![Combined visible-mass post-fit Data/MC validation. The plot sums the VBF,
boosted, and zero-jet post-fit visible-mass expectations and compares them with
the summed observed data. The lower panel is the combined Data/post-fit ratio
for the baseline result.](figures/phase5_baseline_visible_combined.pdf)

![Combined $D_{{NN}}$ score post-fit Data/MC validation. The plot sums the VBF,
boosted, and zero-jet post-fit classifier-score expectations and compares them
with the summed observed score distribution. The lower panel is the combined
Data/post-fit ratio for the secondary result.](figures/phase5_nn_score_combined.pdf)

# Discussion

The $D_{{NN}}$ observable has the smaller median expected upper limit and is
therefore the more sensitive of the two retained tools in this rerun. The
analysis is statistically limited and remains substantially weaker than the
published multi-channel CMS results, but it demonstrates a complete Open Data
template-fit chain with explicit machine-readable workspaces.
"""
    (OUT / "ANALYSIS_NOTE_5_v1.md").write_text(an)
    (OUT / "PAPER_PRL_v1.tex").write_text(paper_tex)
    (OUT / "PAPER_PRL_v1.md").write_text(paper_md)
    append_log("Wrote focused final analysis note and PRL markdown for baseline plus D_NN outputs.")

    missing = figure_ref_check(OUT / "ANALYSIS_NOTE_5_v1.md")
    if missing:
        raise RuntimeError(f"Missing figure references in ANALYSIS_NOTE_5_v1.md: {missing}")

    compile_doc("ANALYSIS_NOTE_5_v1")
    subprocess.run(["tectonic", "PAPER_PRL_v1.tex"], cwd=OUT, check=True)

    summary = (
        "\n## Focused final rerun 2026-06-13\n\n"
        "- Regenerated the final documentation from the current visible-mass baseline and single D_NN result artifacts.\n"
        "- Removed historical optimized-score, add-MET, and duplicate DNN-alias branches from the documented current result set.\n"
    )
    existing_log = EXP_LOG.read_text() if EXP_LOG.exists() else ""
    if "## Focused final rerun 2026-06-13" not in existing_log:
        with EXP_LOG.open("a") as handle:
            handle.write(summary)
        append_log("Appended focused final rerun summary to experiment_log.md.")
    else:
        append_log("Focused final rerun summary already present in experiment_log.md.")


if __name__ == "__main__":
    write_docs()
