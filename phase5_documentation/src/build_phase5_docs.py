from __future__ import annotations

import json
import logging
import re
import shutil
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import mplhep as mh
import numpy as np
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
            dst = FIG / src.name
            shutil.copy2(src, dst)
            copied += 1
    log.info("Copied %d upstream figure files", copied)
    append_log(f"Copied {copied} upstream figure files into the Phase 5 figure directory.")


def merge_references() -> None:
    refs = (ROOT / "phase4_inference" / "4c_observed" / "outputs" / "references.bib").read_text()
    (OUT / "references.bib").write_text(refs)
    append_log("Merged Phase 4c references into the Phase 5 bibliography.")


def setup_style() -> None:
    mh.style.use("CMS")


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)


def make_comparison_figures(observed: dict, comparison: dict) -> None:
    setup_style()
    expected_z = comparison["phase4a_expected"]["expected_discovery_z"]
    observed_z = observed["observed_fit"]["discovery_diagnostic"]["z_value"]

    labels = [
        "This open data expected",
        "This open data observed",
        "CMS Run 1",
        "CMS 2018",
    ]
    z_values = [expected_z, observed_z, 3.0, 4.9]
    xerr = [0.0, 0.0, 0.0, 0.0]
    y = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(10, 10))
    colors = ["#7a7a7a", "#d55e00", "#0072b2", "#009e73"]
    ax.barh(y, z_values, color=colors, alpha=0.88, height=0.55)
    ax.errorbar(z_values, y, xerr=xerr, fmt="none", ecolor="black", capsize=0)
    ax.axvline(3.0, color="black", linestyle="--", linewidth=1.2)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Local significance diagnostic [standard deviations]")
    ax.set_xlim(0, 5.5)
    ax.invert_yaxis()
    mh.label.exp_label(
        exp="CMS",
        data=True,
        llabel="Open Data diagnostic",
        rlabel=r"$\sqrt{s}=8$ TeV",
        loc=0,
        ax=ax,
    )
    mh.label.add_text(
        "Open-data points have flagged score-template validation; CMS rows are publication results.",
        ax=ax,
        loc="lower right",
    )
    save(fig, "phase5_significance_comparison")

    labels = [
        "This open data mu_hat",
        "This open data 95% CLs limit",
        "CMS Run 1 mu",
        "CMS 2018 mu",
    ]
    values = [observed["observed_fit"]["mu_hat"], observed["observed_fit"]["observed_upper_limit"]["observed_limit"], 0.78, 1.09]
    errors = [0.0, 0.0, 0.27, 0.27]
    y = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.errorbar(values, y, xerr=errors, fmt="o", color="#202020", ecolor="#202020", capsize=5)
    ax.axvline(1.0, color="black", linestyle="--", linewidth=1.2)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Signal-strength scale mu")
    ax.set_xlim(0, 15)
    ax.invert_yaxis()
    mh.label.exp_label(
        exp="CMS",
        data=True,
        llabel="Open Data diagnostic",
        rlabel=r"$\sqrt{s}=8$ TeV",
        loc=0,
        ax=ax,
    )
    mh.label.add_text(
        "Open-data fit and limit are not directly equivalent to full CMS publication measurements.",
        ax=ax,
        loc="lower right",
    )
    save(fig, "phase5_mu_limit_comparison")
    append_log("Generated Phase 5 CMS-style significance and signal-strength comparison figures.")


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
    subprocess.run(["python", "../../conventions/postprocess_tex.py", f"{stem}.tex"], cwd=OUT, check=True)
    subprocess.run(["tectonic", f"{stem}.tex"], cwd=OUT, check=True)
    append_log(f"Compiled {stem}.md to TeX and PDF.")


def fmt(value: float, ndigits: int = 3) -> str:
    return f"{value:.{ndigits}f}"


def build_analysis_note(observed: dict, partial: dict, expected: dict, comparison: dict, yields: dict) -> str:
    obs_fit = observed["observed_fit"]
    obs_val = observed["validation_summary"]
    pval = partial["validation_summary"]
    w_full = observed["wjets_high_mt_scale"]
    w_10 = partial["wjets_high_mt_scale"]
    exp_lim = expected["expected_upper_limit"]
    exp_z = expected["discovery_sensitivity"]["z_value"]
    obs_lim = obs_fit["observed_upper_limit"]["observed_limit"]
    mu_hat = obs_fit["mu_hat"]
    obs_z = obs_fit["discovery_diagnostic"]["z_value"]
    obs_exp_ratio = comparison["fit_comparison"]["observed_limit_over_phase4a_median_expected"]

    category_rows = []
    for cat in ["vbf", "boosted", "zero_jet"]:
        total = yields["totals"][cat]
        category_rows.append(
            f"| {cat} | {total['data_total']} | {total['background_total']:.2f} | "
            f"{total['signal_total']:.3f} | {total['data_over_background']:.3f} |"
        )
    category_table = "\n".join(category_rows)

    score_rows = []
    for label, vals in obs_val["score_template_validation"].items():
        score_rows.append(
            f"| {label} | {vals['data_total']:.0f} | {vals['background_total']:.2f} | "
            f"{vals['data_over_background']:.3f} | {vals['chi2_per_ndf']:.3f} | "
            f"{vals['max_abs_pull']:.2f} | flagged |"
        )
    score_table = "\n".join(score_rows)

    return f"""---
title: "CMS Open Data H to tau tau Search: Final Analysis Note"
author: "Analysis my_analysis"
date: "2026-06-02"
bibliography: references.bib
---

# Abstract {{-}}

This note documents a reduced CMS 2012 Open Data search for Higgs boson decays
to tau pairs in the mu tau_h final state. The final diagnostic fit uses
Run2012B/C TauPlusX reduced NanoAOD-like inputs with an integrated luminosity
of 11.467/fb and a binned pyhf profile likelihood in VBF, boosted, and zero-jet
categories [@cms_open_data_htt_2012; @cms_open_data_lumi_2012; @pyhf_joss].
The observed full-data fit gives `mu_hat = {mu_hat:.4f}`, an observed 95% CLs
upper limit `mu < {obs_lim:.4f}`, and a simplified discovery diagnostic
`Z = {obs_z:.4f}`. The score-template validation is flagged in both the 10%
data validation and full-data validation, so these numbers are open-data
diagnostics rather than CMS-quality evidence for H to tau tau.

# Change Log {{-}}

Phase 5 v1 consolidates the Phase 4c observed result into a final analysis note
and adds a PRL-style paper draft. It also adds publication-style comparison
figures for the open-data diagnostic result against CMS Run 1 and Run 2 H to
tau tau publications [@cms_htt_2014; @cms_htt_2018].

# Introduction

The H to tau tau decay tests the Higgs coupling to charged leptons. CMS
reported Run 1 evidence for this decay mode in JHEP 05 (2014) 104 and later
observed the decay with 13 TeV data in Phys. Lett. B 779 (2018) 283
[@cms_htt_2014; @cms_htt_2018]. This open-data analysis is intentionally much
smaller: it uses only the reduced 2012 mu tau_h outreach samples available from
the CERN Open Data Portal and does not use the full CMS calibration,
embedding, or multi-channel machinery [@cms_open_data_htt_2012].

The goal is a reproducible template-fit demonstration using public samples,
not a substitute for the CMS publications. The result is interpreted against
CMS Run 1, CMS Run 2, and ATLAS+CMS Higgs-combination context
[@atlas_cms_higgs_combination_2016], while every comparison is labelled for
scope and observable differences.

# Data And Simulation

The data are Run2012B and Run2012C TauPlusX reduced NanoAOD-like samples from
the CMS Open Data H to tau tau record [@cms_open_data_run2012b_tauplusx;
@cms_open_data_run2012c_tauplusx]. The signal samples are ggH and VBF
H to tau tau reduced samples [@cms_open_data_ggh_htt; @cms_open_data_vbf_htt].
The available background simulation includes DYJetsToLL, TTbar, and
W1/W2/W3JetsToLNu [@cms_open_data_dyjets; @cms_open_data_ttbar;
@cms_open_data_w1jets; @cms_open_data_w2jets; @cms_open_data_w3jets].

The luminosity is 11.467/fb for the Run2012B/C TauPlusX selection following
the CMS Open Data tutorial and 2012 luminosity provenance
[@cms_open_data_skim; @cms_open_data_lumi_2012]. The luminosity nuisance uses
2.6% from CMS PAS LUM-13-001 [@cms_lum_13_001]. The MC event denominators come
from official Open Data record `distribution.number_events` values, not from
local reduced-tree entries. This avoids circular normalization by keeping data
event counts out of the luminosity and MC-weight definitions.

| Sample | Role | Normalization input |
|---|---|---|
| Run2012B/C TauPlusX | data | 11.467/fb Run2012B/C luminosity |
| GluGluToHToTauTau | signal | sigma_prod times BR(H to tau tau) and record denominator |
| VBF_HToTauTau | signal | sigma_prod times BR(H to tau tau) and record denominator |
| DYJetsToLL | background | cross section times luminosity divided by record denominator |
| TTbar | background | cross section times luminosity divided by record denominator |
| W1/W2/W3JetsToLNu | background | cross section times luminosity divided by record denominator plus W high-mT scale |

The available reduced sample list is not the full CMS analysis sample set.
QCD multijet, diboson, single-top, embedded Z to tau tau, associated Higgs
production, H to WW, W4/inclusive W+jets, and additional DY categories are not
available as reduced samples and are documented limitations rather than
silently substituted.

![Sample inventory. The figure summarizes local reduced ROOT entries and file
sizes for the public H to tau tau files used in the analysis. The entries are
processing entries, while normalization uses official Open Data record
denominators and the cited luminosity.](figures/sample_event_count_file_size.pdf){{#fig:an-samples}}

![Branch feature availability. The figure records the reduced branch classes
available in data and simulation. It shows that the core muon, tau, jet, MET,
trigger, and generator-particle handles are available, while event weights,
pileup weights, and direct GenMET are absent.](figures/branch_feature_availability.pdf){{#fig:an-branches}}

# Event Selection And Categories

Events are selected with `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`, matching the
TauPlusX mu tau_h trigger path in the reduced samples. Muons require pt > 20
GeV, |eta| < 2.1, tight identification, and finite relative isolation below
0.20. Tau_h candidates require pt > 20 GeV, |eta| < 2.3, a decay-mode ID, tight
isolation ID, tight anti-muon ID, finite isolation, and separation
Delta R(mu,tau) > 0.5.

The signal-region candidate set requires opposite-sign mu tau_h pairs and
muon-MET transverse mass below 40 GeV. The high-mT W control region uses
opposite-sign pairs with transverse mass above 80 GeV. A same-sign low-mT
region is retained as the available fake/QCD handle, and a Z-rich validation
window is retained for DY modelling checks.

The mutually exclusive fit categories are assigned in this order: VBF first,
boosted/1-jet second, and zero-jet last. VBF requires at least two clean jets,
leading-dijet mass above 300 GeV, and leading-dijet |Delta eta| above 2.5.
Boosted events have at least one clean jet after failing the VBF selection.
Zero-jet events have no selected clean jets.

![Cutflow summary. This plot shows raw event counts after each selection step
for data, signal MC, and background MC. It verifies that the selection chain is
monotonic and that the reduced samples remain populated after the trigger,
object, charge, and transverse-mass requirements.](figures/cutflow_summary.pdf){{#fig:an-cutflow}}

![Exclusive category yields. The figure summarizes raw data, signal MC, and
background MC counts in the VBF, boosted, and zero-jet categories. These three
categories are the channels of the simultaneous fit and no event is counted in
more than one fit channel.](figures/category_yields.pdf){{#fig:an-category-yields}}

| Category | Data | Background | Signal | Data/background |
|---|---:|---:|---:|---:|
{category_table}

The category table is the final full-data selected-event summary after the W
control scale is applied to W+jets. The zero-jet category dominates the event
count and the combined data/background ratio, while the VBF category has the
largest signal-to-background leverage but also the strongest validation
deficit.

# Candidate Methods

The strategy evaluated visible mass, add-MET mass, an NN/MVA discriminator,
and an NN missing-momentum regression idea. Visible mass and add-MET mass were
implemented as transparent alternatives, but the best expected-only sensitivity
came from a histogram-gradient-boosting classifier score. The NN GenMET
regression was downscoped because direct GenMET and neutrino generator truth
targets were not present in the reduced files.

The classifier-score method was carried forward only because it improved the
expected diagnostic sensitivity in MC-only studies. That promotion was always
conditional on data score-template validation. The 10% and full-data
validation failed the combined ratio criterion, so the final score-template
result is deliberately labelled as a diagnostic.

![Approach comparison. The figure compares visible-mass and add-MET-mass
approaches using a common MC-only binned separation diagnostic. It supports the
existence of a transparent baseline and an add-MET cross-check, but it is not
the final likelihood result.](figures/approach_comparison.pdf){{#fig:an-approaches}}

![MVA input modelling gate. The figure shows data-versus-background-MC
validation chi2/ndf values for candidate classifier inputs. Most inputs fail
the predeclared modelling threshold, which is why the classifier result is
kept as an open-data diagnostic rather than a publication-quality model.](figures/mva_input_modeling_chi2.pdf){{#fig:an-mva-gate}}

![Expected classifier score templates. The figure shows expected signal and
background score distributions after the official Open Data normalization.
These templates define the fitted observable, but their full-data validation
status is flagged and limits the interpretation of the final result.](figures/mva_score_templates.pdf){{#fig:an-mva-score}}

# Statistical Model

The final model is a binned profile likelihood implemented with pyhf
[@pyhf_joss]. It has one parameter of interest, the signal-strength modifier
mu, multiplying the SM H to tau tau signal templates in all fit channels. The
likelihood is

$$
L(\\mu,\\theta)=\\prod_{{c,b}} \\mathrm{{Pois}}\\left(n_{{cb}}\\mid
\\mu s_{{cb}}(\\theta)+b_{{cb}}(\\theta)\\right)
\\prod_k \\pi_k(\\theta_k),
$$ {{#eq:likelihood}}

where c indexes category, b indexes score bin, and theta denotes nuisance
parameters. The normalization weight for a simulated background sample is

$$
w_i = \\frac{{\\sigma_i L_{{\\mathrm{{int}}}}}}{{N_{{\\mathrm{{gen}},i}}}},
$$ {{#eq:background-weight}}

while signal weights use the production cross section times BR(H to tau tau),
following the Phase 3 normalization record and the Higgs cross-section context
[@lhc_hxswg_yellow_report_4]. The W+jets control scale is computed as

$$
\\alpha_W = \\frac{{N_{{\\mathrm{{data}}}}^{{\\mathrm{{CR}}}} -
N_{{\\mathrm{{nonW}}}}^{{\\mathrm{{CR}}}}}}{{N_W^{{\\mathrm{{CR}}}}}} .
$$ {{#eq:w-scale}}

The expected and observed upper limits use the modified frequentist CLs
construction [@read_cls]. Discovery diagnostics use the one-sided q0
asymptotic approximation [@cowan_asymptotic]. These formulae are appropriate
for a compact diagnostic study, but the flagged data/MC score validation
prevents interpreting the observed q0 value as CMS-quality evidence.

# Systematic Uncertainties

The retained nuisance model is intentionally compact because the reduced
public samples lack many CMS calibration ingredients. The implemented
normalization nuisances are a 2.6% luminosity uncertainty, 15% DY open-data
normalization, 15% tau open-data acceptance, a W high-mT control-region
normalization uncertainty, and bin-by-bin MC statistical terms. The omitted
publication-level components are limitations, not hidden corrections.

| Nuisance | Size | Source or derivation | Role |
|---|---:|---|---|
| Luminosity | 2.6% | CMS PAS LUM-13-001 | MC-normalized components |
| DY normalization | 15% | Open-data missing scale-factor limitation | DY rate |
| Tau acceptance | 15% | Open-data missing tau trigger/ID scale-factor limitation | selected MC |
| W high-mT scale | {w_full['relative_uncertainty']:.3%} | high-mT control-region count | W+jets rate |
| MC statistics | per bin | finite selected MC yields | all templates |

The W scale improves in precision from the 10% validation to the full sample:
`{w_10['applied_scale_factor']:.4f} ± {w_10['absolute_uncertainty']:.4f}` at
10% and `{w_full['applied_scale_factor']:.4f} ± {w_full['absolute_uncertainty']:.4f}`
for the full data. The central values agree within the larger 10% uncertainty,
which supports the control-region arithmetic. It does not repair the
score-template validation failure.

![Expected nuisance summary. The figure shows the expected nuisance summary
from the Phase 4 expected model. Its compact nuisance list reflects the reduced
open-data scope and must not be read as a complete CMS systematic program.](figures/expected_nuisance_summary.pdf){{#fig:an-nuisance}}

![Full high-mT W control comparison. The figure shows the derivation inputs
for the full-data W+jets control scale. The control region is outside the
low-mT signal region and the scale is propagated to the observed workspace
without post-unblinding signal-region tuning.](figures/w_highmt_scale_full.pdf){{#fig:an-wscale}}

# Expected Results

The expected-only model uses background Asimov pseudo-data, so no real
signal-region data enter the expected limit or discovery diagnostic. The
median expected 95% CLs upper limit is `mu < {exp_lim['observed_on_background_asimov']:.4f}`,
with expected band `{exp_lim['expected_band_minus2_minus1_median_plus1_plus2']}`.
The expected discovery diagnostic is `Z = {exp_z:.4f}`.

![Expected score template in the VBF category. The figure shows expected
signal and background score distributions in the VBF channel. It illustrates
why the high-score region carries signal leverage, but also why sparse and
mismodelled VBF data are a critical validation risk.](figures/expected_mva_score_vbf.pdf){{#fig:an-exp-vbf}}

![Expected score template in the boosted category. The figure shows the
expected classifier-score template for the boosted/1-jet channel. The channel
has more data than VBF and contributes a moderate validation pull in the full
sample.](figures/expected_mva_score_boosted.pdf){{#fig:an-exp-boosted}}

![Expected score template in the zero-jet category. The figure shows the
expected classifier-score template for the zero-jet channel. The zero-jet
channel dominates event counts and drives much of the combined data/background
ratio.](figures/expected_mva_score_zero_jet.pdf){{#fig:an-exp-zero}}

![Signal injection recovery. The figure summarizes signal-injection recovery
checks performed on pseudo-data. These checks validate model plumbing and fit
response under controlled inputs, but they do not replace observed data/MC
score-template validation.](figures/signal_injection_recovery.pdf){{#fig:an-injection}}

# Ten Percent Data Validation

The deterministic 10% data validation used the mask `(run * 1000003 +
luminosityBlock * 9176 + event) % 10 == 0`, selecting 1120 signal-region data
events. The W high-mT scale from this subset was
`{w_10['applied_scale_factor']:.4f} ± {w_10['absolute_uncertainty']:.4f}`.
The combined score-template data/background ratio was
`{pval['combined']['data_over_background']:.4f}` with chi2/ndf
`{pval['combined']['chi2_per_ndf']:.4f}` and status `flagged`.

The 10% validation failed because the data/background ratio was outside the
predeclared statistical criterion. This warning was carried into unblinding
instead of being removed or tuned away. The full-data analysis therefore starts
from a known modelling limitation.

![Ten percent score-template validation in VBF. The figure compares the 10%
data subset to the frozen score-template model in the VBF category. It is one
component of the validation warning that constrains the final interpretation.](figures/partial_score_vbf.pdf){{#fig:an-partial-vbf}}

![Ten percent pull summary. The figure summarizes 10% validation ratios and
pulls. It shows that the warning is quantitative and pre-unblinding rather
than an after-the-fact explanation of the full-data result.](figures/partial_pull_summary.pdf){{#fig:an-partial-pulls}}

# Full Data Results

The full observed fit applies the frozen score-template model to all available
Run2012B/C TauPlusX selected data. No selection, classifier, category, score
bin, or statistical-model retuning was performed after full-data unblinding.

| Quantity | Value | Interpretation |
|---|---:|---|
| Full W high-mT scale | {w_full['applied_scale_factor']:.4f} ± {w_full['absolute_uncertainty']:.4f} | Control-region scale |
| mu_hat | {mu_hat:.4f} | Simplified open-data diagnostic |
| Observed 95% CLs limit | mu < {obs_lim:.4f} | Simplified open-data diagnostic |
| Observed q0 Z | {obs_z:.4f} | Not CMS-quality evidence |
| Phase 4a expected median limit | {exp_lim['observed_on_background_asimov']:.4f} | Background-only Asimov reference |
| Observed/expected limit ratio | {obs_exp_ratio:.4f} | Observed limit is much weaker than expected |

The observed limit is a factor `{obs_exp_ratio:.2f}` above the median expected
limit. The fitted signal strength and q0 diagnostic are numerically large, but
they occur in a model whose full-data score validation remains flagged. The
correct interpretation is that the reduced open-data templates do not provide
a CMS-quality evidence claim.

![Observed limit and significance summary. The figure summarizes mu_hat,
observed upper limit, expected median limit, and observed q0 diagnostic. The
caption and text deliberately label these values as simplified open-data
diagnostics because the score-template validation failed.](figures/observed_limit_significance_summary.pdf){{#fig:an-result-summary}}

![Comparison to expected and 10% validation. The figure compares the expected
limit, 10% diagnostic fit, full-data fit, and W scale evolution. It makes the
unblinding history visible and shows that the W control scale is stable while
the final score-template validation remains flagged.](figures/comparison_to_4a_4b.pdf){{#fig:an-unblind-history}}

# Validation Summary

| Test | Data scope | chi2/ndf | p-value | Verdict | What it validates |
|---|---|---:|---:|---|---|
| Expected Asimov toy plumbing | expected-only | 0.000 | 1.000 | pass as plumbing | pyhf workspace and toy generation |
| 10% score templates | 10% data | {pval['combined']['chi2_per_ndf']:.3f} | n/a | flagged | pre-unblinding score data/MC model |
| Full score templates | full data | {obs_val['combined']['chi2_per_ndf']:.3f} | n/a | flagged | observed score data/MC model |
| W high-mT scale stability | 10% to full | n/a | n/a | pass arithmetic | W control-region normalization |

| Category | Data | Background | Data/background | Chi2/ndf | Max pull | Verdict |
|---|---:|---:|---:|---:|---:|---|
{score_table}

The full combined data/background ratio is
`{obs_val['combined']['data_over_background']:.4f}` and the full combined
chi2/ndf is `{obs_val['combined']['chi2_per_ndf']:.4f}`. The VBF channel has
a data deficit, the zero-jet channel has a data excess, and the boosted
channel is closer to the model. This category pattern is not consistent with
an unqualified single signal interpretation.

![Full-data VBF score validation. The figure compares full data to the frozen
score-template model in the VBF category. The VBF category has the largest
category chi2/ndf and a deficit relative to the background template.](figures/observed_score_vbf.pdf){{#fig:an-full-vbf}}

![Full-data boosted score validation. The figure compares full data to the
frozen score-template model in the boosted category. This channel has the most
moderate full-data validation behavior among the three fitted categories.](figures/observed_score_boosted.pdf){{#fig:an-full-boosted}}

![Full-data zero-jet score validation. The figure compares full data to the
frozen score-template model in the zero-jet category. The zero-jet data excess
dominates the combined data/background ratio.](figures/observed_score_zero_jet.pdf){{#fig:an-full-zero}}

![Observed pull and ratio summary. The figure summarizes category-level
ratios, pulls, and the comparison with the 10% validation. It is the central
diagnostic showing why the observed signal-strength and Z values cannot be
promoted to CMS-quality evidence.](figures/observed_pull_ratio_summary.pdf){{#fig:an-pull-summary}}

# Published Comparisons

CMS Run 1 reported a best-fit H to tau tau signal strength of 0.78 ± 0.27 and
local significance above three standard deviations for Higgs-mass hypotheses
between 115 and 130 GeV [@cms_htt_2014]. CMS Run 2 reported observed and
expected significances of 4.9 and 4.7 and signal strength 1.09 with roughly
0.27 total uncertainty [@cms_htt_2018]. These are full CMS publication results
with many channels, categories, calibrations, and data-driven background
methods. The open-data diagnostic fit is not directly equivalent.

| Result | Scope | Significance | Signal strength or limit | Comparability |
|---|---|---:|---:|---|
| This open-data expected | 8 TeV mu tau_h reduced samples | {exp_z:.3f} | expected mu < {exp_lim['observed_on_background_asimov']:.3f} | internal expected reference |
| This open-data observed | 8 TeV mu tau_h reduced samples | {obs_z:.3f} flagged | mu_hat = {mu_hat:.3f}; mu < {obs_lim:.3f} | diagnostic only |
| CMS Run 1 | 7+8 TeV multi-channel | >3 | mu = 0.78 ± 0.27 | publication context |
| CMS 2018 | 13 TeV multi-channel | obs 4.9, exp 4.7 | mu = 1.09 ± about 0.27 | publication context |

<!-- FLAGSHIP -->
![Significance comparison. The figure compares the open-data expected and
observed diagnostics with CMS Run 1 and CMS 2018 H to tau tau publication
significances. The open-data observed value is labelled as flagged and should
not be read as evidence comparable to the CMS publication rows.](figures/phase5_significance_comparison.pdf){{#fig:an-significance-comparison}}

<!-- FLAGSHIP -->
![Signal-strength and limit comparison. The figure places the open-data
mu_hat and observed CLs limit on the same signal-strength scale as published
CMS Run 1 and Run 2 signal-strength measurements. The open-data points are not
directly equivalent to the CMS measurements because of reduced channel
coverage, missing calibrations, and flagged score-template validation.](figures/phase5_mu_limit_comparison.pdf){{#fig:an-mu-comparison}}

# Limitations And Resolving Power

The analysis can resolve only very large deviations from the SM expectation.
The median expected 95% CLs limit of `mu < {exp_lim['observed_on_background_asimov']:.2f}`
already shows that an SM-strength signal is below the expected sensitivity of
this reduced single-channel setup. The observed limit of `mu < {obs_lim:.2f}`
is still weaker because the observed score-template model is flagged.

The largest limitations are the reduced sample inventory, absent official
object and trigger scale-factor machinery in the reduced files, missing QCD
and electroweak background components, no pileup weights, no direct GenMET
truth target, and the full-data score-template validation failure. These
limitations explain why the diagnostic result sits far from published
CMS-quality signal-strength measurements without requiring any claim of a new
or independent physics effect.

# Reproducibility

The final documents are generated by `phase5_documentation/src/build_phase5_docs.py`.
The script reads Phase 4 JSON outputs, copies existing figures, creates Phase
5 comparison figures, merges the bibliography, writes markdown, and compiles
the TeX/PDF products. The statistical inputs are the Phase 4a expected JSON,
Phase 4b partial JSON, Phase 4c observed JSON, and full observed yields JSON.

# Conclusion

This Phase 5 pass produces a final analysis note and PRL-style draft for a
reproducible CMS 2012 Open Data H to tau tau diagnostic search. The full-data
fit reports `mu_hat = {mu_hat:.4f}`, `mu < {obs_lim:.4f}` at 95% CLs, and
`Z = {obs_z:.4f}`. Because the 10% and full-data score-template validations
are flagged, the result is explicitly not CMS-quality evidence. Its value is
as a transparent, citable open-data workflow and as a documented comparison to
published CMS H to tau tau analyses.

# References {{-}}
"""


def build_paper(observed: dict, partial: dict, expected: dict, comparison: dict, yields: dict) -> str:
    obs_fit = observed["observed_fit"]
    obs_val = observed["validation_summary"]
    pval = partial["validation_summary"]
    w_full = observed["wjets_high_mt_scale"]
    exp_lim = expected["expected_upper_limit"]
    exp_z = expected["discovery_sensitivity"]["z_value"]
    obs_lim = obs_fit["observed_upper_limit"]["observed_limit"]
    mu_hat = obs_fit["mu_hat"]
    obs_z = obs_fit["discovery_diagnostic"]["z_value"]

    return f"""---
title: "A CMS Open Data Diagnostic Search for H to Tau Tau in the Mu Tau_h Final State"
author: "Analysis my_analysis"
date: "2026-06-02"
bibliography: references.bib
---

# Abstract {{-}}

A diagnostic search for H to tau tau is performed with CMS 2012 Open Data in
the mu tau_h final state using reduced Run2012B/C TauPlusX samples. A binned
profile-likelihood fit to classifier-score templates in VBF, boosted, and
zero-jet categories gives `mu_hat = {mu_hat:.3f}`, an observed 95% CLs upper
limit `mu < {obs_lim:.3f}`, and an observed q0 diagnostic `Z = {obs_z:.3f}`.
The score-template validation is flagged in both the 10% validation sample and
the full data, so these values are simplified open-data diagnostics and are
not CMS-quality evidence for H to tau tau.

# Introduction

The H to tau tau decay probes the Higgs coupling to charged leptons. CMS
reported Run 1 evidence for this decay and later observed it with 13 TeV data
[@cms_htt_2014; @cms_htt_2018]. This paper draft presents a compact
open-data diagnostic using the public reduced CMS 2012 H to tau tau samples
[@cms_open_data_htt_2012]. The analysis is limited to the mu tau_h final state
and is intended as a reproducible public-data workflow, not a replacement for
the full CMS publications.

# Data And Simulation

The data are Run2012B and Run2012C TauPlusX reduced NanoAOD-like samples from
the CERN Open Data Portal [@cms_open_data_run2012b_tauplusx;
@cms_open_data_run2012c_tauplusx]. The integrated luminosity is 11.467/fb,
following the CMS Open Data H to tau tau tutorial and 2012 luminosity
provenance [@cms_open_data_skim; @cms_open_data_lumi_2012]. The luminosity
uncertainty is 2.6% [@cms_lum_13_001].

| Sample group | Samples | Use |
|---|---|---|
| Data | Run2012B/C TauPlusX | observed signal and control regions |
| Signal | ggH and VBF H to tau tau | fitted signal templates |
| Background | DYJetsToLL, TTbar, W1/W2/W3JetsToLNu | fitted background templates |
| Unavailable in reduced set | QCD, diboson, single top, embedded Z to tau tau, W4/inclusive W | documented limitation |

The signal and background records are the public CMS Open Data reduced samples
[@cms_open_data_ggh_htt; @cms_open_data_vbf_htt; @cms_open_data_dyjets;
@cms_open_data_ttbar; @cms_open_data_w1jets; @cms_open_data_w2jets;
@cms_open_data_w3jets]. MC normalization uses official Open Data event
denominators and cited cross-section inputs; it is not derived by matching
data yields.

# Event Selection And Categories

Events are required to pass `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`. Muons have
pt > 20 GeV and |eta| < 2.1 with tight identification and isolation.
Hadronic-tau candidates have pt > 20 GeV, |eta| < 2.3, decay-mode ID, tight
isolation ID, and tight anti-muon ID. The signal-region selection requires an
opposite-sign mu tau_h pair and muon-MET transverse mass below 40 GeV.

The fit uses three mutually exclusive categories: VBF, boosted, and zero-jet.
VBF events have at least two clean jets with leading-dijet mass above 300 GeV
and leading-dijet |Delta eta| above 2.5. Boosted events have at least one
clean jet after failing the VBF selection, and zero-jet events have no clean
jets.

| Category | Data | Background | Signal | Data/background |
|---|---:|---:|---:|---:|
| VBF | {yields['totals']['vbf']['data_total']} | {yields['totals']['vbf']['background_total']:.2f} | {yields['totals']['vbf']['signal_total']:.3f} | {yields['totals']['vbf']['data_over_background']:.3f} |
| Boosted | {yields['totals']['boosted']['data_total']} | {yields['totals']['boosted']['background_total']:.2f} | {yields['totals']['boosted']['signal_total']:.3f} | {yields['totals']['boosted']['data_over_background']:.3f} |
| Zero-jet | {yields['totals']['zero_jet']['data_total']} | {yields['totals']['zero_jet']['background_total']:.2f} | {yields['totals']['zero_jet']['signal_total']:.3f} | {yields['totals']['zero_jet']['data_over_background']:.3f} |

![Selected category yields. The figure shows the event yields in the three
exclusive fit categories for data, signal MC, and background MC. It documents
the channel composition of the simultaneous likelihood fit and shows that the
zero-jet channel dominates the selected event count.](figures/category_yields.pdf){{#fig:paper-category-yields}}

# Statistical Analysis

The fitted observable is a histogram-gradient-boosting classifier score in
the three event categories. The likelihood is a binned profile likelihood
implemented with pyhf [@pyhf_joss],

$$
L(\\mu,\\theta)=\\prod_{{c,b}} \\mathrm{{Pois}}\\left(n_{{cb}}\\mid
\\mu s_{{cb}}(\\theta)+b_{{cb}}(\\theta)\\right)
\\prod_k \\pi_k(\\theta_k).
$$ {{#eq:paper-likelihood}}

Upper limits use the CLs construction [@read_cls], and the discovery
diagnostic uses the one-sided q0 asymptotic approximation [@cowan_asymptotic].
The W+jets rate is constrained by a high-mT control-region scale
`{w_full['applied_scale_factor']:.4f} ± {w_full['absolute_uncertainty']:.4f}`.
The retained nuisances include luminosity, DY normalization, tau open-data
acceptance, W high-mT normalization, and MC statistical uncertainties.

# Results

The expected median 95% CLs upper limit is `mu < {exp_lim['observed_on_background_asimov']:.3f}`,
and the expected discovery diagnostic is `Z = {exp_z:.3f}`. The full-data fit
gives the diagnostic results summarized in @tbl:paper-results.

| Quantity | Value | Status |
|---|---:|---|
| Expected median 95% CLs limit | mu < {exp_lim['observed_on_background_asimov']:.3f} | background Asimov |
| Expected discovery diagnostic | {exp_z:.3f} | background Asimov |
| Observed mu_hat | {mu_hat:.3f} | flagged diagnostic |
| Observed 95% CLs limit | mu < {obs_lim:.3f} | flagged diagnostic |
| Observed q0 Z | {obs_z:.3f} | flagged diagnostic |

: Main open-data fit results. The observed entries are not CMS-quality evidence because score-template validation is flagged. {{#tbl:paper-results}}

![Observed result summary. The figure summarizes the fitted signal strength,
observed upper limit, expected median limit, and observed q0 diagnostic. The
values are diagnostics of the reduced open-data model and must be read
together with the validation caveat.](figures/observed_limit_significance_summary.pdf){{#fig:paper-result-summary}}

# Validation Caveat

The score-template model is not validated at CMS-publication quality. In the
10% validation sample, the combined data/background ratio is
`{pval['combined']['data_over_background']:.3f}` with chi2/ndf
`{pval['combined']['chi2_per_ndf']:.3f}` and status `flagged`. In the full
data, the combined data/background ratio is
`{obs_val['combined']['data_over_background']:.3f}` with chi2/ndf
`{obs_val['combined']['chi2_per_ndf']:.3f}` and status `flagged`. Therefore
the observed `Z = {obs_z:.3f}` and `mu_hat = {mu_hat:.3f}` are simplified
open-data diagnostics, not evidence comparable to CMS publications.

![Full-data score validation summary. The figure summarizes data/background
ratios and maximum pulls in the observed score templates. It is the main
diagnostic showing why the observed fit result is not promoted to a
CMS-quality evidence statement.](figures/observed_pull_ratio_summary.pdf){{#fig:paper-validation}}

# Comparison With Published Results

The open-data result is compared with CMS H to tau tau publications only as
context. CMS Run 1 used 7 and 8 TeV data with multiple channels and reported
mu = 0.78 ± 0.27 with local significance above three standard deviations
[@cms_htt_2014]. CMS 2018 used 13 TeV data and reported observed and expected
significances of 4.9 and 4.7 with mu = 1.09 and roughly 0.27 uncertainty
[@cms_htt_2018]. These publication results are not direct pass/fail targets
for the reduced single-channel open-data model.

| Result | Scope | Significance | Signal-strength information |
|---|---|---:|---|
| This open-data expected | 8 TeV mu tau_h reduced samples | {exp_z:.3f} | expected mu < {exp_lim['observed_on_background_asimov']:.3f} |
| This open-data observed | 8 TeV mu tau_h reduced samples | {obs_z:.3f} flagged | mu_hat = {mu_hat:.3f}; mu < {obs_lim:.3f} |
| CMS Run 1 | 7+8 TeV multi-channel | >3 | mu = 0.78 ± 0.27 |
| CMS 2018 | 13 TeV multi-channel | observed 4.9, expected 4.7 | mu = 1.09 ± about 0.27 |

: Comparison of the open-data diagnostic with published CMS H to tau tau results. The entries differ in energy, channel coverage, calibration completeness, and validation quality. {{#tbl:paper-comparison}}

![Significance comparison. The figure compares the open-data expected and
observed diagnostic significances with CMS publication values. The open-data
observed point is explicitly labelled as flagged and should not be interpreted
as CMS-quality evidence.](figures/phase5_significance_comparison.pdf){{#fig:paper-significance}}

![Signal-strength and limit comparison. The figure compares open-data
signal-strength-scale diagnostics with CMS Run 1 and CMS 2018 signal-strength
measurements. The open-data limit and mu_hat are not directly equivalent to
the published measurements because the reduced public model has flagged
score-template validation.](figures/phase5_mu_limit_comparison.pdf){{#fig:paper-mu}}

# Conclusion

A reproducible reduced CMS 2012 Open Data H to tau tau diagnostic search has
been documented in the mu tau_h final state. The full-data fit gives
`mu_hat = {mu_hat:.3f}`, `mu < {obs_lim:.3f}` at 95% CLs, and
`Z = {obs_z:.3f}`. Because the 10% and full-data score-template validations
are flagged, these are simplified open-data diagnostics and not CMS-quality
evidence. The analysis is useful as a public workflow and as a scoped
comparison to CMS H to tau tau publications, not as an independent publication
measurement.

# Reproducibility Note {{-}}

The markdown, TeX, PDF, and comparison figures are generated from the committed
Phase 4 JSON outputs by `phase5_documentation/src/build_phase5_docs.py`.

# References {{-}}
"""


def write_docs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    observed = load_json("phase4_inference/4c_observed/outputs/observed_results.json")
    partial = load_json("phase4_inference/4b_partial/outputs/partial_results.json")
    expected = load_json("phase4_inference/4a_expected/outputs/expected_results.json")
    comparison = load_json("phase4_inference/4c_observed/outputs/comparison_to_4a_4b.json")
    yields = load_json("phase4_inference/4c_observed/outputs/observed_yields.json")

    copy_figures()
    merge_references()
    make_comparison_figures(observed, comparison)

    an = build_analysis_note(observed, partial, expected, comparison, yields)
    paper = build_paper(observed, partial, expected, comparison, yields)
    (OUT / "ANALYSIS_NOTE_5_v1.md").write_text(an)
    (OUT / "PAPER_PRL_v1.md").write_text(paper)
    append_log("Wrote Phase 5 final analysis note and PRL-style paper markdown.")

    for name in ("ANALYSIS_NOTE_5_v1.md", "PAPER_PRL_v1.md"):
        missing = figure_ref_check(OUT / name)
        if missing:
            raise RuntimeError(f"Missing figure references in {name}: {missing}")

    compile_doc("ANALYSIS_NOTE_5_v1")
    compile_doc("PAPER_PRL_v1")

    with EXP_LOG.open("a") as handle:
        handle.write(
            "\n## Phase 5 documentation executor 2026-06-02T16:29:32Z\n\n"
            "- Generated final Phase 5 AN and PRL-style paper from Phase 4 JSON outputs.\n"
            "- Copied upstream figures into Phase 5 outputs and added CMS-style comparison figures.\n"
            "- Explicitly labelled observed Z and mu_hat as simplified open-data diagnostics because score-template validation is flagged.\n"
        )
    append_log("Appended Phase 5 summary to experiment_log.md.")


if __name__ == "__main__":
    write_docs()
