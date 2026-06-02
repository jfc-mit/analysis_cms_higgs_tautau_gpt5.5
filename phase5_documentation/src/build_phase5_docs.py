from __future__ import annotations

import json
import logging
import copy
import re
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import matplotlib.pyplot as plt
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

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "phase5_documentation" / "outputs"
FIG = OUT / "figures"
LOG_PATH = ROOT / "phase5_documentation" / "logs" / "executor_phase5_documentation_20260602T162932Z.md"
EXP_LOG = ROOT / "experiment_log.md"

def load_json(path: str) -> dict:
    with (ROOT / path).open() as handle:
        return json.load(handle)


def append_log(message: str) -> None:
    with LOG_PATH.open("a") as handle:
        handle.write(f"\n## milestone\n\n{message}\n")


def copy_figures() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
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
            shutil.copy2(src, FIG / src.name)
            copied += 1
    log.info("Copied %d upstream figure files", copied)
    append_log(f"Copied {copied} upstream figure files into the Phase 5 figure directory.")


def merge_references() -> None:
    refs = (ROOT / "phase4_inference" / "4c_observed" / "outputs" / "references.bib").read_text()
    if "pdg_higgs_status_2024" not in refs:
        refs += """

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
"""
    (OUT / "references.bib").write_text(refs)
    append_log("Merged Phase 4c references into the Phase 5 bibliography.")


def setup_style() -> None:
    mh.style.use("CMS")


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)


def exp_label(ax: plt.Axes, label_text: str = "Open Data diagnostic") -> None:
    mh.label.exp_label(
        exp="CMS",
        data=True,
        llabel=label_text,
        rlabel=r"$\sqrt{s}=8$ TeV, $L=11.467$ fb$^{-1}$ ref.",
        loc=0,
        ax=ax,
    )


def exp_label_no_lumi(ax: plt.Axes, label_text: str = "Open Data diagnostic") -> None:
    mh.label.exp_label(
        exp="CMS",
        data=True,
        llabel=label_text,
        rlabel=r"$\sqrt{s}=8$ TeV",
        loc=0,
        ax=ax,
    )


def tensor_scalar(value: object) -> float:
    payload = pyhf.tensorlib.tolist(value)
    if isinstance(payload, list):
        return float(payload[0])
    return float(payload)


@lru_cache(maxsize=1)
def profile_mu_summary() -> dict[str, float | str]:
    workspace = load_json("phase4_inference/4c_observed/outputs/pyhf_workspace_observed.json")
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
    best_nll = tensor_scalar(pyhf.infer.mle.twice_nll(free_pars, data, model))

    def q_mu(mu_value: float) -> float:
        fixed = pyhf.infer.mle.fixed_poi_fit(mu_value, data, model)
        return max(0.0, tensor_scalar(pyhf.infer.mle.twice_nll(fixed, data, model)) - best_nll)

    def bisect_crossing(lo: float, hi: float) -> float:
        q_lo = q_mu(lo) - 1.0
        q_hi = q_mu(hi) - 1.0
        for _ in range(28):
            mid = 0.5 * (lo + hi)
            q_mid = q_mu(mid) - 1.0
            if q_lo * q_mid <= 0:
                hi = mid
                q_hi = q_mid
            else:
                lo = mid
                q_lo = q_mid
        return 0.5 * (lo + hi)

    lower = 0.0
    lower_status = "bounded_at_zero"
    if mu_hat > 0 and q_mu(0.0) >= 1.0:
        lower = bisect_crossing(0.0, mu_hat)
        lower_status = "profile_q_equals_1"
    upper_hi = max(2.0 * mu_hat + 1.0, 2.0)
    while q_mu(upper_hi) < 1.0 and upper_hi < 50.0:
        upper_hi *= 1.6
    upper = bisect_crossing(mu_hat, upper_hi)
    return {
        "mu_hat": mu_hat,
        "err_minus": mu_hat - lower,
        "err_plus": upper - mu_hat,
        "lower": lower,
        "upper": upper,
        "lower_status": lower_status,
        "method": "profile likelihood scan with q(mu)=2DeltaNLL=1; lower side bounded at mu>=0 when needed",
    }


def make_comparison_figures(observed: dict) -> None:
    setup_style()
    primary = observed["observed_fit"]
    primary_limit = primary["observed_upper_limit"]
    primary_band = primary_limit["expected_band_minus2_minus1_median_plus1_plus2"]
    mu_summary = profile_mu_summary()

    fig, ax = plt.subplots(figsize=(10, 10))
    rows = {
        "This analysis\n11.467 fb$^{-1}$": 0.0,
        "CMS Run 1 mu\n4.9+19.7 fb$^{-1}$": 1.0,
        "CMS 2018 mu\n35.9 fb$^{-1}$": 2.0,
        "ATLAS+CMS Run 1 global\nRun 1 per experiment": 3.0,
    }
    this_row = rows["This analysis\n11.467 fb$^{-1}$"]
    ax.fill_betweenx([this_row - 0.22, this_row + 0.22], primary_band[0], primary_band[4], color="#f0e442", alpha=0.9, label="Expected 95% band")
    ax.fill_betweenx([this_row - 0.22, this_row + 0.22], primary_band[1], primary_band[3], color="#009e73", alpha=0.9, label="Expected 68% band")
    ax.plot(primary_band[2], this_row, marker="s", color="#d55e00", linestyle="", label="Expected median limit")
    ax.plot(primary_limit["observed_limit"], this_row, marker="o", color="black", linestyle="", label="Observed limit")
    ax.errorbar(
        mu_summary["mu_hat"],
        this_row + 0.16,
        xerr=np.asarray([[mu_summary["err_minus"]], [mu_summary["err_plus"]]], dtype=float),
        fmt="D",
        color="#0072b2",
        capsize=5,
        label="Observed fitted mu",
    )

    ax.errorbar(0.78, rows["CMS Run 1 mu\n4.9+19.7 fb$^{-1}$"], xerr=0.27, fmt="o", color="#202020", capsize=5)
    ax.errorbar(1.09, rows["CMS 2018 mu\n35.9 fb$^{-1}$"], xerr=0.27, fmt="o", color="#202020", capsize=5)
    ax.errorbar(1.09, rows["ATLAS+CMS Run 1 global\nRun 1 per experiment"], xerr=0.11, fmt="o", color="#202020", capsize=5)
    ax.axvspan(1.0 - 0.016, 1.0 + 0.016, color="#6a3d9a", alpha=0.18, label="PDG SM H to tau tau BR rel. unc.")
    ax.axvline(1.0, color="black", linestyle="--", linewidth=1.2, label="SM mu=1")
    ax.set_yticks(list(rows.values()), list(rows.keys()))
    ax.set_xlabel("Signal-strength scale mu")
    ax.set_xlim(0, 30.0)
    ax.invert_yaxis()
    ax.legend(fontsize="x-small", loc="lower right")
    exp_label_no_lumi(ax)
    save(fig, "phase5_mu_limit_comparison")

    fig, ax = plt.subplots(figsize=(10, 10))
    labels = ["This analysis", "CMS Run 1 obs.", "CMS Run 1 exp.", "CMS 2018 obs.", "CMS 2018 exp.", "CMS 2018 combined", "ATLAS+CMS Run 1 H to tau tau"]
    z_values = [
        primary["discovery_diagnostic"]["z_value"],
        3.2,
        3.7,
        4.9,
        4.7,
        5.9,
        5.5,
    ]
    colors = ["#0072b2", "#7a7a7a", "#b0b0b0", "#202020", "#909090", "#404040", "#606060"]
    y = np.arange(len(labels))
    ax.barh(y, z_values, color=colors, alpha=0.88, height=0.55)
    ax.axvline(3.0, color="black", linestyle="--", linewidth=1.2)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Local significance diagnostic [standard deviations]")
    ax.set_xlim(0, 5.5)
    ax.invert_yaxis()
    exp_label(ax)
    save(fig, "phase5_significance_comparison")
    append_log("Generated CMS-style expected/observed signal-strength and significance comparison figures.")


def category_mu_results() -> dict[str, dict[str, float]]:
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
    return out


def make_category_mu_figure() -> None:
    setup_style()
    results = category_mu_results()
    labels = ["VBF", "Boosted", "Zero-jet"]
    keys = ["vbf", "boosted", "zero_jet"]
    y = np.arange(len(keys))
    expected = np.asarray([results[key]["expected_mu_sm"] for key in keys], dtype=float)
    observed = np.asarray([results[key]["observed_mu_hat"] for key in keys], dtype=float)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.plot(expected, y - 0.12, marker="s", linestyle="", color="#d55e00", label="Expected SM")
    ax.plot(observed, y + 0.12, marker="o", linestyle="", color="black", label="Observed fit")
    for yi, x_exp, x_obs in zip(y, expected, observed, strict=True):
        ax.plot([x_exp, x_obs], [yi, yi], color="#b0b0b0", linewidth=1.2)
    ax.axvline(1.0, color="black", linestyle="--", linewidth=1.2)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Signal strength mu")
    ax.set_xlim(0.0, max(10.0, float(np.max(observed)) * 1.15))
    ax.invert_yaxis()
    ax.legend(fontsize="x-small", loc="lower right")
    exp_label(ax)
    save(fig, "phase5_category_mu_comparison")
    write_json = json.dumps({"categories": results}, indent=2, sort_keys=True) + "\n"
    (OUT / "category_mu_comparison.json").write_text(write_json)
    append_log("Generated per-category expected-vs-observed mu comparison for the primary visible-mass model.")


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


def fmt(value: float, ndigits: int = 3) -> str:
    return f"{value:.{ndigits}f}"


def build_analysis_note(observed: dict, partial: dict, expected: dict, comparison: dict, yields: dict) -> str:
    primary = observed["observed_fit"]
    primary_lim = primary["observed_upper_limit"]
    primary_band = primary_lim["expected_band_minus2_minus1_median_plus1_plus2"]
    mu_summary = profile_mu_summary()
    obs_val = observed["validation_summary"]
    pval = partial["validation_summary"]
    w_full = observed["wjets_high_mt_scale"]
    w_10 = partial["wjets_high_mt_scale"]
    vbf_scale = observed["vbf_background_scale"]
    qcd_primary = observed["qcd_sideband_estimates"]["visible_mass_qcd_primary"]
    exp_lim = expected["expected_upper_limit"]
    exp_z = expected["discovery_sensitivity"]["z_value"]

    category_rows = []
    for cat in ["vbf", "boosted", "zero_jet"]:
        total = yields["totals"][cat]
        category_rows.append(
            f"| {cat} | {total['data_total']} | {total['background_total']:.2f} | "
            f"{total['qcd_total']:.2f} | {total['signal_total']:.3f} | {total['data_over_background']:.3f} |"
        )
    category_table = "\n".join(category_rows)

    return f"""---
title: "CMS Open Data H to tau tau Search: Final Analysis Note"
author: "Analysis my_analysis"
date: "2026-06-02"
bibliography: references.bib
---

# Abstract {{-}}

This note documents a reduced CMS 2012 Open Data search for Higgs boson decays
to tau pairs in the mu tau_h final state. The final result uses visible mass in
VBF, boosted, and zero-jet categories with a same-sign data-driven QCD/fake
template. It gives `mu = {mu_summary['mu_hat']:.4f} +{mu_summary['err_plus']:.4f} -{mu_summary['err_minus']:.4f}`
from a profile-likelihood scan and an observed 95% CLs limit
`mu < {primary_lim['observed_limit']:.4f}`.

# Change Log {{-}}

Phase 5 v2 responds to the observed-versus-expected audit. It adds a same-sign
QCD/fake estimate, changes the primary full-data result to the visible-mass
fallback, removes alternative-method presentation from the final result per the
latest user instruction, adds category-level `mu` diagnostics for the primary
method, and compiles the paper with REVTeX PRL formatting.

# Data And Simulation

The data are Run2012B and Run2012C TauPlusX reduced samples from the public
HiggsTauTauReduced mirror, using the CMS Open Data H to tau tau luminosity
reference of 11.467/fb [@cms_open_data_htt_2012; @cms_open_data_skim]. The
localized mirror files contain about one tenth of the event entries listed in
the Open Data records; this is treated as the public reduced processing sample
scope, while MC weights continue to use the official record denominators
specified in `normalization_inputs.json`, as required by the sample provenance.

The available MC set contains ggH and VBF H to tau tau, DYJetsToLL, TTbar, and
W1/W2/W3JetsToLNu. QCD multijet, diboson, single top, embedded Z to tau tau,
W4/inclusive W+jets, associated Higgs, and H to WW remain unavailable as
reduced samples and are not silently substituted.

![Sample inventory. The figure summarizes local reduced ROOT entries and file
sizes for the public H to tau tau files used in the analysis. The entries are
processing entries, while normalization uses official Open Data record
denominators and the cited luminosity reference.](figures/sample_event_count_file_size.pdf){{#fig:an-samples}}

# Event Selection And Categories

Events are required to pass `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`. Muons have
pt > 20 GeV and |eta| < 2.1 with tight identification and isolation. Hadronic
tau candidates have pt > 20 GeV, |eta| < 2.3, decay-mode ID, tight isolation
ID, and tight anti-muon ID. The signal region uses opposite-sign mu tau_h pairs
with muon-MET transverse mass below 40 GeV. The W control region uses high
transverse mass, and the QCD/fake estimate uses same-sign low-mT events.

The fit categories are mutually exclusive VBF, boosted, and zero-jet. VBF
requires at least two clean jets, leading-dijet mass above 300 GeV, and
leading-dijet |Delta eta| above 2.5. Boosted events have at least one clean jet
after failing VBF, and zero-jet events have no clean jets.

| Category | Data | Background | QCD/fake | Signal | Data/background |
|---|---:|---:|---:|---:|---:|
{category_table}

![Cutflow summary. This plot shows raw event counts after each selection step
for data, signal MC, and background MC. It verifies that the selection chain is
monotonic and that the reduced samples remain populated after trigger, object,
charge, and transverse-mass requirements.](figures/cutflow_summary.pdf){{#fig:an-cutflow}}

# QCD And W Control Corrections

The W+jets normalization is measured in the high-mT control region as
`{w_full['applied_scale_factor']:.4f} ± {w_full['absolute_uncertainty']:.4f}`.
The 10% validation value was `{w_10['applied_scale_factor']:.4f} ± {w_10['absolute_uncertainty']:.4f}`.
The values agree within the larger 10% uncertainty and support the W-control
arithmetic.

The VBF category originally had a large MC overprediction. Tightening the VBF
cuts and applying a simple b-tag veto did not solve it, so a disjoint VBF-like
top-btag control region outside the low-mT signal region was used to calibrate
the MC-background rate in the VBF category. The resulting VBF background scale
is `{vbf_scale['applied_scale_factor']:.4f} ± {vbf_scale['absolute_uncertainty']:.4f}`;
it is applied only to MC backgrounds in VBF and not to the signal or QCD/fake
template.

The same-sign QCD/fake estimate subtracts non-QCD MC from same-sign low-mT data
and transfers the resulting template to opposite-sign signal candidates. For
the primary visible-mass model, the OS/SS transfer factor measured in the lowest
visible-mass bin is `{qcd_primary['transfer_sideband']['scale_factor']:.4f} ± {qcd_primary['transfer_sideband']['absolute_uncertainty']:.4f}`.

![Full high-mT W control comparison. The figure shows the derivation inputs for
the full-data W+jets control scale. The control region is outside the low-mT
signal region and the scale is propagated to the observed workspace without
signal-region tuning.](figures/w_highmt_scale_full.pdf){{#fig:an-wscale}}

# Primary Visible-Mass Result

The primary statistical model is a binned pyhf profile likelihood in visible
mass, with one signal-strength parameter `mu`, the W high-mT scale, the
same-sign QCD/fake transfer uncertainty, luminosity, DY and tau/open-data
normalization terms, and MC statistical terms [@pyhf_joss; @read_cls;
@cowan_asymptotic].

| Quantity | Value | Interpretation |
|---|---:|---|
| Primary median expected 95% CLs limit | mu < {primary_band[2]:.4f} | corrected visible-mass workspace |
| Primary observed 95% CLs limit | mu < {primary_lim['observed_limit']:.4f} | conservative observed result |
| Primary mu central value | {mu_summary['mu_hat']:.4f} +{mu_summary['err_plus']:.4f} -{mu_summary['err_minus']:.4f} | profile likelihood q(mu)=1 interval |
| Primary q0 Z | {primary['discovery_diagnostic']['z_value']:.4f} | diagnostic only |
| Primary combined data/background | {obs_val['combined']['data_over_background']:.4f} | validation after QCD/fake correction |
| Primary chi2/ndf | {obs_val['combined']['chi2_per_ndf']:.4f} | validation after QCD/fake correction |

The primary result does not show a Higgs-like excess: `mu` is
`{mu_summary['mu_hat']:.4f} +{mu_summary['err_plus']:.4f} -{mu_summary['err_minus']:.4f}`
and the observed 95% CLs limit is `mu < {primary_lim['observed_limit']:.4f}`.
The broad interval is compatible with the weak sensitivity expected from this
reduced single-final-state setup.

![Primary visible-mass validation in VBF. The plot compares full data to the
QCD-corrected visible-mass prediction in the VBF category. The remaining VBF
deficit is a limitation, but it no longer drives a fake signal-strength
increase.](figures/observed_mvis_vbf.pdf){{#fig:an-primary-vbf}}

![Primary visible-mass validation in boosted. The plot compares full data to
the QCD-corrected visible-mass prediction in the boosted category. This channel
is part of the conservative primary fit.](figures/observed_mvis_boosted.pdf){{#fig:an-primary-boosted}}

![Primary visible-mass validation in zero-jet. The zero-jet normalization is
stabilized by the same-sign QCD/fake estimate, which removes the dominant
normalization pathology seen before the QCD/fake correction.](figures/observed_mvis_zero_jet.pdf){{#fig:an-primary-zero}}

![Category signal-strength comparison. The figure shows the Standard Model
expectation `mu = 1` and the observed single-category profile-fit value for
VBF, boosted, and zero-jet categories using the primary visible-mass model.
These category fits are diagnostics; the quoted result remains the simultaneous
three-category fit.](figures/phase5_category_mu_comparison.pdf){{#fig:an-category-mu}}

# Comparison With Published Results

CMS Run 1 reported evidence for H to tau tau using 7 and 8 TeV data with
multiple final states, embedded backgrounds, and a full calibration program;
the quoted best-fit signal strength was 0.78 ± 0.27 with observed and expected
significances of 3.2 and 3.7 standard deviations [@cms_htt_2014]. CMS 2018
reported observed and expected significances of 4.9 and 4.7 in the 2016 data,
and 5.9 when combined with earlier CMS data, with a signal strength near
1.09 [@cms_htt_2018]. The ATLAS+CMS Run 1 combination gives broader global
Higgs-rate context, while the PDG/Higgs-summary SM H to tau tau branching
fraction provides the denominator convention for `mu = 1` rather than a
single-channel open-data comparison target [@atlas_cms_higgs_combination_2016;
@pdg_2024; @pdg_higgs_status_2024; @lhc_hxswg_yellow_report_4].

| Result | Scope | Significance | Signal-strength information |
|---|---|---:|---|
| This analysis | 8 TeV mu tau_h reduced mirror, visible mass | {primary['discovery_diagnostic']['z_value']:.3f} | mu = {mu_summary['mu_hat']:.3f} +{mu_summary['err_plus']:.3f} -{mu_summary['err_minus']:.3f}; 95% CLs mu < {primary_lim['observed_limit']:.3f}; expected mu < {primary_band[2]:.3f} |
| CMS Run 1 JHEP 2014 | 7+8 TeV multi-channel | observed 3.2, expected 3.7 | mu = 0.78 ± 0.27 |
| CMS PLB 2018 2016 data | 13 TeV multi-channel | observed 4.9, expected 4.7 | mu = 1.09 ± about 0.27 |
| CMS PLB 2018 combined | CMS 7+8+13 TeV combination | observed 5.9, expected 5.9 | same signal-strength model as CMS 2018 publication |
| ATLAS+CMS Run 1 combination | 7+8 TeV global Higgs couplings/rates | H to tau tau evidence context | global mu = 1.09 ± 0.11 |
| PDG / HXSWG SM context | H to tau tau branching fraction at mH near 125 GeV | not a search significance | BR(H to tau tau) about 6.3%, used only as SM normalization context |

![Signal-strength and limit comparison. The figure uses a CMS-style
expected-band and observed-marker presentation for the primary open-data limit,
published CMS/ATLAS+CMS signal-strength measurements, and a narrow PDG SM H to
tau tau branching-ratio normalization band at `mu = 1`. The open-data
diagnostic is not directly equivalent to CMS publication measurements.](figures/phase5_mu_limit_comparison.pdf){{#fig:an-mu-comparison}}

![Significance comparison. The figure compares the primary open-data diagnostic
with CMS and ATLAS+CMS publication values. Only the primary open-data result is
shown from this analysis in the final result figure.](figures/phase5_significance_comparison.pdf){{#fig:an-significance-comparison}}

# Conclusion

The final audit-corrected result is a conservative visible-mass plus QCD/fake
template fit. It gives `mu = {mu_summary['mu_hat']:.4f} +{mu_summary['err_plus']:.4f} -{mu_summary['err_minus']:.4f}`
and an observed 95% CLs limit `mu < {primary_lim['observed_limit']:.4f}`.
This is the correct interpretation of the reduced CMS Open Data workflow:
reproducible and useful for methodology, but not CMS-quality evidence for
H to tau tau.

# References {{-}}
"""


def build_paper_markdown(observed: dict) -> str:
    primary = observed["observed_fit"]
    primary_lim = primary["observed_upper_limit"]
    primary_band = primary_lim["expected_band_minus2_minus1_median_plus1_plus2"]
    mu_summary = profile_mu_summary()
    return f"""# A CMS Open Data Diagnostic Search for H to Tau Tau in the Mu Tau_h Final State

This PRL-formatted draft reports the audit-corrected result. The primary
visible-mass plus QCD/fake fit gives `mu = {mu_summary['mu_hat']:.3f} +{mu_summary['err_plus']:.3f} -{mu_summary['err_minus']:.3f}`,
`mu < {primary_lim['observed_limit']:.3f}` at 95% CLs, with median expected
limit `{primary_band[2]:.3f}`.
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


def build_prl_tex(observed: dict, yields: dict) -> str:
    primary = observed["observed_fit"]
    primary_lim = primary["observed_upper_limit"]
    primary_band = primary_lim["expected_band_minus2_minus1_median_plus1_plus2"]
    mu_summary = profile_mu_summary()
    qcd_primary = observed["qcd_sideband_estimates"]["visible_mass_qcd_primary"]
    vbf_scale = observed["vbf_background_scale"]
    rows = []
    for cat in ["vbf", "boosted", "zero_jet"]:
        total = yields["totals"][cat]
        rows.append(
            rf"{tex_escape(cat)} & {total['data_total']} & {total['background_total']:.1f} & "
            rf"{total['qcd_total']:.1f} & {total['signal_total']:.2f} \\"
        )
    category_rows = "\n".join(rows)
    return rf"""\documentclass[aps,prl,reprint,superscriptaddress,nofootinbib]{{revtex4-2}}
\usepackage{{graphicx}}
\usepackage{{amsmath}}
\usepackage{{booktabs}}
\usepackage{{xcolor}}
\begin{{document}}

\title{{A CMS Open Data Diagnostic Search for $H\to\tau\tau$ in the $\mu\tau_h$ Final State}}
\author{{Analysis my\_analysis}}
\affiliation{{CMS Open Data reduced-sample analysis}}
\date{{June 2, 2026}}

\begin{{abstract}}
A diagnostic search for Higgs boson decays to tau pairs is performed with
CMS 2012 Open Data reduced samples in the $\mu\tau_h$ final state.  The result
uses a conservative visible-mass fit in VBF, boosted, and zero-jet categories
with a same-sign data-driven QCD/fake template.  The fit gives
$\mu={mu_summary['mu_hat']:.3f}^{{+{mu_summary['err_plus']:.3f}}}_{{-{mu_summary['err_minus']:.3f}}}$
from the profile likelihood and an observed 95\% CLs upper limit
$\mu<{primary_lim['observed_limit']:.3f}$.
\end{{abstract}}

\maketitle

\paragraph{{Data and method.}}
The analysis uses the public Run2012B/C TauPlusX HiggsTauTauReduced mirror and
the CMS Open Data luminosity reference of 11.467 fb$^{{-1}}$.  Signal and
background simulations are normalized with official Open Data record event
denominators rather than local reduced-file entries.  Events are selected with
the $\mu+\tau_h$ trigger, tight muon and hadronic-tau requirements including a
tight anti-muon veto, opposite-sign charge, and low transverse mass.

\paragraph{{Background correction.}}
The W+jets normalization is measured in a high-$m_T$ control region.  The
VBF-background rate is calibrated in a VBF-like top-btag control region outside
the low-$m_T$ signal region, giving a scale
${vbf_scale['applied_scale_factor']:.3f}\pm{vbf_scale['absolute_uncertainty']:.3f}$.
The reducible QCD/fake contribution is estimated from same-sign low-$m_T$ data
after subtracting non-QCD simulation.  For the primary visible-mass fit, the
OS/SS transfer factor measured in the lowest visible-mass bin is
${qcd_primary['transfer_sideband']['scale_factor']:.3f}\pm{qcd_primary['transfer_sideband']['absolute_uncertainty']:.3f}$.

\begin{{table}}[b]
\caption{{Selected yields in the primary visible-mass fit after the QCD/fake
audit correction.  Background includes DY, ttbar, W+jets, and the same-sign
QCD/fake estimate.}}
\begin{{ruledtabular}}
\begin{{tabular}}{{lrrrr}}
Category & Data & Bkg. & QCD/fake & Signal \\
{category_rows}
\end{{tabular}}
\end{{ruledtabular}}
\end{{table}}

\begin{{table*}}[t]
\caption{{Comparison of the reduced open-data results with published and world
reference context.  The open-data rows use only the localized 2012
$\mu\tau_h$ reduced samples and are not direct reproductions of the
multi-channel CMS or ATLAS+CMS analyses.}}
\begin{{ruledtabular}}
\begin{{tabular}}{{llll}}
Result & Scope & Significance & Signal-strength information \\
This analysis & 8 TeV $\mu\tau_h$ reduced, visible mass & {primary['discovery_diagnostic']['z_value']:.3f} & $\mu={mu_summary['mu_hat']:.3f}^{{+{mu_summary['err_plus']:.3f}}}_{{-{mu_summary['err_minus']:.3f}}}$, 95\% CLs $\mu<{primary_lim['observed_limit']:.3f}$ \\
CMS Run 1 & 7+8 TeV multi-channel & obs. 3.2, exp. 3.7 & $\mu=0.78\pm0.27$ \\
CMS 2018 & 13 TeV multi-channel & obs. 4.9, exp. 4.7 & $\mu\simeq1.09$ \\
CMS 2018 combined & CMS 7+8+13 TeV & obs. 5.9, exp. 5.9 & CMS combination context \\
ATLAS+CMS Run 1 & 7+8 TeV global Higgs rates & global context & $\mu=1.09\pm0.11$ \\
PDG/HXSWG SM & $H\to\tau\tau$ branching fraction & not a search & BR about 6.3\%, $\mu=1$ convention \\
\end{{tabular}}
\end{{ruledtabular}}
\end{{table*}}

\paragraph{{Results.}}
The primary corrected workspace has median expected 95\% CLs limit
$\mu<{primary_band[2]:.3f}$ and observed limit
$\mu<{primary_lim['observed_limit']:.3f}$.  The best fit is
$\mu={mu_summary['mu_hat']:.3f}^{{+{mu_summary['err_plus']:.3f}}}_{{-{mu_summary['err_minus']:.3f}}}$
from the profile likelihood.  This is the conservative final observed result.

\begin{{figure}}[t]
\includegraphics[width=\linewidth]{{figures/phase5_mu_limit_comparison.pdf}}
\caption{{Signal-strength and limit comparison.  The primary open-data result
is shown with expected bands and an observed marker following CMS-style limit
plot conventions.  The CMS/ATLAS+CMS publication rows are context, and the
narrow band at $\mu=1$ shows the PDG/Higgs-summary SM $H\to\tau\tau$
normalization uncertainty.}}
\end{{figure}}

\begin{{figure}}[t]
\includegraphics[width=\linewidth]{{figures/phase5_category_mu_comparison.pdf}}
\caption{{Category signal-strength comparison for the primary visible-mass
model.  The expected marker is the Standard Model value $\mu=1$ and the
observed marker is the single-category profile-fit value; the quoted result
remains the simultaneous three-category fit.}}
\end{{figure}}

\begin{{figure}}[t]
\includegraphics[width=\linewidth]{{figures/observed_mvis_zero_jet.pdf}}
\caption{{Primary visible-mass validation in the zero-jet category.  The
same-sign QCD/fake estimate stabilizes the dominant zero-jet normalization,
which was the main pathology before the QCD/fake correction.}}
\end{{figure}}

\paragraph{{Comparison and interpretation.}}
CMS Run 1 reported evidence for $H\to\tau\tau$ with a best-fit signal strength
of $0.78\pm0.27$ and observed and expected significances of 3.2 and 3.7.  CMS
later observed the decay at 13 TeV with observed and expected significances of
4.9 and 4.7, and reported 5.9 standard deviations in the CMS combination.  The
ATLAS+CMS Run 1 combination and PDG/Higgs-summary branching fraction provide
global context but are not direct validation targets for this reduced
single-channel analysis.  The present result is methodological reproducibility,
not an independent CMS-quality evidence claim.

\begin{{thebibliography}}{{9}}
\bibitem{{cms2014}} CMS Collaboration, Evidence for the 125 GeV Higgs boson decaying to a pair of tau leptons, JHEP 05 (2014) 104.
\bibitem{{cms2018}} CMS Collaboration, Observation of the SM scalar boson decaying to a pair of tau leptons, Phys. Lett. B 779 (2018) 283.
\bibitem{{atlascms2016}} ATLAS and CMS Collaborations, Measurements of the Higgs boson production and decay rates and constraints on its couplings from a combined ATLAS and CMS analysis, JHEP 08 (2016) 045.
\bibitem{{pdg2024}} Particle Data Group, Review of Particle Physics, Phys. Rev. D 110 (2024) 030001.
\bibitem{{opendata}} CERN Open Data Portal, CMS Higgs to tau tau reduced samples for education and outreach.
\bibitem{{pyhf}} L. Heinrich et al., pyhf: pure-Python implementation of HistFactory statistical models.
\bibitem{{cls}} A. L. Read, Presentation of search results: the CLs technique.
\bibitem{{cowan}} G. Cowan et al., Asymptotic formulae for likelihood-based tests of new physics.
\end{{thebibliography}}

\end{{document}}
"""


def compile_prl(observed: dict, yields: dict) -> None:
    tex = build_prl_tex(observed, yields)
    (OUT / "PAPER_PRL_v1.tex").write_text(tex)
    subprocess.run(["tectonic", "PAPER_PRL_v1.tex"], cwd=OUT, check=True)
    append_log("Compiled PAPER_PRL_v1.tex with REVTeX PRL class.")


def write_docs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    observed = load_json("phase4_inference/4c_observed/outputs/observed_results.json")
    partial = load_json("phase4_inference/4b_partial/outputs/partial_results.json")
    expected = load_json("phase4_inference/4a_expected/outputs/expected_results.json")
    comparison = load_json("phase4_inference/4c_observed/outputs/comparison_to_4a_4b.json")
    yields = load_json("phase4_inference/4c_observed/outputs/observed_yields.json")

    copy_figures()
    merge_references()
    make_comparison_figures(observed)
    make_category_mu_figure()

    an = build_analysis_note(observed, partial, expected, comparison, yields)
    paper_md = build_paper_markdown(observed)
    (OUT / "ANALYSIS_NOTE_5_v1.md").write_text(an)
    (OUT / "PAPER_PRL_v1.md").write_text(paper_md)
    append_log("Wrote Phase 5 final analysis note and PRL summary markdown.")

    missing = figure_ref_check(OUT / "ANALYSIS_NOTE_5_v1.md")
    if missing:
        raise RuntimeError(f"Missing figure references in ANALYSIS_NOTE_5_v1.md: {missing}")

    compile_doc("ANALYSIS_NOTE_5_v1")
    compile_prl(observed, yields)

    with EXP_LOG.open("a") as handle:
        handle.write(
            "\n## Phase 5 documentation executor 2026-06-02T16:29:32Z\n\n"
            "- Rewrote final AN around the audit-corrected visible-mass/QCD primary result.\n"
            "- Reported the primary signal strength as a profile-likelihood central value with asymmetric uncertainty and as a 95% CLs upper limit.\n"
            "- Added a per-category expected/observed mu comparison for the primary visible-mass model.\n"
            "- Expanded comparison figures and tables with CMS 2014, CMS 2018, ATLAS+CMS, and PDG/HXSWG context.\n"
            "- Generated PAPER_PRL_v1.tex/pdf with REVTeX PRL formatting, not pandoc article formatting.\n"
        )
    append_log("Appended Phase 5 audit-corrected summary to experiment_log.md.")


if __name__ == "__main__":
    write_docs()
