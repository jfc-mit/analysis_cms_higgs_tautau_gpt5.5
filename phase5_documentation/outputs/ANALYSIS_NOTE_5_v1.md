---
title: "CMS Open Data H to tau tau Search: Final Analysis Note"
author: "Analysis my_analysis"
date: "2026-06-02"
bibliography: references.bib
---

# Abstract {-}

This note documents a reduced CMS 2012 Open Data search for Higgs boson decays
to tau pairs in the mu tau_h final state. The final diagnostic fit uses
Run2012B/C TauPlusX reduced NanoAOD-like inputs with an integrated luminosity
of 11.467/fb and a binned pyhf profile likelihood in VBF, boosted, and zero-jet
categories [@cms_open_data_htt_2012; @cms_open_data_lumi_2012; @pyhf_joss].
The observed full-data fit gives `mu_hat = 7.6642`, an observed 95% CLs
upper limit `mu < 13.3226`, and a simplified discovery diagnostic
`Z = 2.9776`. The score-template validation is flagged in both the 10%
data validation and full-data validation, so these numbers are open-data
diagnostics rather than CMS-quality evidence for H to tau tau.

# Change Log {-}

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
denominators and the cited luminosity.](figures/sample_event_count_file_size.pdf){#fig:an-samples}

![Branch feature availability. The figure records the reduced branch classes
available in data and simulation. It shows that the core muon, tau, jet, MET,
trigger, and generator-particle handles are available, while event weights,
pileup weights, and direct GenMET are absent.](figures/branch_feature_availability.pdf){#fig:an-branches}

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
object, charge, and transverse-mass requirements.](figures/cutflow_summary.pdf){#fig:an-cutflow}

![Exclusive category yields. The figure summarizes raw data, signal MC, and
background MC counts in the VBF, boosted, and zero-jet categories. These three
categories are the channels of the simultaneous fit and no event is counted in
more than one fit channel.](figures/category_yields.pdf){#fig:an-category-yields}

| Category | Data | Background | Signal | Data/background |
|---|---:|---:|---:|---:|
| vbf | 79 | 146.67 | 1.590 | 0.539 |
| boosted | 2213 | 2062.80 | 9.175 | 1.073 |
| zero_jet | 8466 | 6894.80 | 14.341 | 1.228 |

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
the final likelihood result.](figures/approach_comparison.pdf){#fig:an-approaches}

![MVA input modelling gate. The figure shows data-versus-background-MC
validation chi2/ndf values for candidate classifier inputs. Most inputs fail
the predeclared modelling threshold, which is why the classifier result is
kept as an open-data diagnostic rather than a publication-quality model.](figures/mva_input_modeling_chi2.pdf){#fig:an-mva-gate}

![Expected classifier score templates. The figure shows expected signal and
background score distributions after the official Open Data normalization.
These templates define the fitted observable, but their full-data validation
status is flagged and limits the interpretation of the final result.](figures/mva_score_templates.pdf){#fig:an-mva-score}

# Statistical Model

The final model is a binned profile likelihood implemented with pyhf
[@pyhf_joss]. It has one parameter of interest, the signal-strength modifier
mu, multiplying the SM H to tau tau signal templates in all fit channels. The
likelihood is

$$
L(\mu,\theta)=\prod_{c,b} \mathrm{Pois}\left(n_{cb}\mid
\mu s_{cb}(\theta)+b_{cb}(\theta)\right)
\prod_k \pi_k(\theta_k),
$$ {#eq:likelihood}

where c indexes category, b indexes score bin, and theta denotes nuisance
parameters. The normalization weight for a simulated background sample is

$$
w_i = \frac{\sigma_i L_{\mathrm{int}}}{N_{\mathrm{gen},i}},
$$ {#eq:background-weight}

while signal weights use the production cross section times BR(H to tau tau),
following the Phase 3 normalization record and the Higgs cross-section context
[@lhc_hxswg_yellow_report_4]. The W+jets control scale is computed as

$$
\alpha_W = \frac{N_{\mathrm{data}}^{\mathrm{CR}} -
N_{\mathrm{nonW}}^{\mathrm{CR}}}{N_W^{\mathrm{CR}}} .
$$ {#eq:w-scale}

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
| W high-mT scale | 4.344% | high-mT control-region count | W+jets rate |
| MC statistics | per bin | finite selected MC yields | all templates |

The W scale improves in precision from the 10% validation to the full sample:
`0.8433 ± 0.0868` at
10% and `0.8528 ± 0.0370`
for the full data. The central values agree within the larger 10% uncertainty,
which supports the control-region arithmetic. It does not repair the
score-template validation failure.

![Expected nuisance summary. The figure shows the expected nuisance summary
from the Phase 4 expected model. Its compact nuisance list reflects the reduced
open-data scope and must not be read as a complete CMS systematic program.](figures/expected_nuisance_summary.pdf){#fig:an-nuisance}

![Full high-mT W control comparison. The figure shows the derivation inputs
for the full-data W+jets control scale. The control region is outside the
low-mT signal region and the scale is propagated to the observed workspace
without post-unblinding signal-region tuning.](figures/w_highmt_scale_full.pdf){#fig:an-wscale}

# Expected Results

The expected-only model uses background Asimov pseudo-data, so no real
signal-region data enter the expected limit or discovery diagnostic. The
median expected 95% CLs upper limit is `mu < 4.1994`,
with expected band `[2.143687842430168, 2.9202283397658175, 4.199448081748937, 6.145739528239424, 8.817265131700397]`.
The expected discovery diagnostic is `Z = 0.5264`.

![Expected score template in the VBF category. The figure shows expected
signal and background score distributions in the VBF channel. It illustrates
why the high-score region carries signal leverage, but also why sparse and
mismodelled VBF data are a critical validation risk.](figures/expected_mva_score_vbf.pdf){#fig:an-exp-vbf}

![Expected score template in the boosted category. The figure shows the
expected classifier-score template for the boosted/1-jet channel. The channel
has more data than VBF and contributes a moderate validation pull in the full
sample.](figures/expected_mva_score_boosted.pdf){#fig:an-exp-boosted}

![Expected score template in the zero-jet category. The figure shows the
expected classifier-score template for the zero-jet channel. The zero-jet
channel dominates event counts and drives much of the combined data/background
ratio.](figures/expected_mva_score_zero_jet.pdf){#fig:an-exp-zero}

![Signal injection recovery. The figure summarizes signal-injection recovery
checks performed on pseudo-data. These checks validate model plumbing and fit
response under controlled inputs, but they do not replace observed data/MC
score-template validation.](figures/signal_injection_recovery.pdf){#fig:an-injection}

# Ten Percent Data Validation

The deterministic 10% data validation used the mask `(run * 1000003 +
luminosityBlock * 9176 + event) % 10 == 0`, selecting 1120 signal-region data
events. The W high-mT scale from this subset was
`0.8433 ± 0.0868`.
The combined score-template data/background ratio was
`1.2322` with chi2/ndf
`1.7325` and status `flagged`.

The 10% validation failed because the data/background ratio was outside the
predeclared statistical criterion. This warning was carried into unblinding
instead of being removed or tuned away. The full-data analysis therefore starts
from a known modelling limitation.

![Ten percent score-template validation in VBF. The figure compares the 10%
data subset to the frozen score-template model in the VBF category. It is one
component of the validation warning that constrains the final interpretation.](figures/partial_score_vbf.pdf){#fig:an-partial-vbf}

![Ten percent pull summary. The figure summarizes 10% validation ratios and
pulls. It shows that the warning is quantitative and pre-unblinding rather
than an after-the-fact explanation of the full-data result.](figures/partial_pull_summary.pdf){#fig:an-partial-pulls}

# Full Data Results

The full observed fit applies the frozen score-template model to all available
Run2012B/C TauPlusX selected data. No selection, classifier, category, score
bin, or statistical-model retuning was performed after full-data unblinding.

| Quantity | Value | Interpretation |
|---|---:|---|
| Full W high-mT scale | 0.8528 ± 0.0370 | Control-region scale |
| mu_hat | 7.6642 | Simplified open-data diagnostic |
| Observed 95% CLs limit | mu < 13.3226 | Simplified open-data diagnostic |
| Observed q0 Z | 2.9776 | Not CMS-quality evidence |
| Phase 4a expected median limit | 4.1994 | Background-only Asimov reference |
| Observed/expected limit ratio | 3.1725 | Observed limit is much weaker than expected |

The observed limit is a factor `3.17` above the median expected
limit. The fitted signal strength and q0 diagnostic are numerically large, but
they occur in a model whose full-data score validation remains flagged. The
correct interpretation is that the reduced open-data templates do not provide
a CMS-quality evidence claim.

![Observed limit and significance summary. The figure summarizes mu_hat,
observed upper limit, expected median limit, and observed q0 diagnostic. The
caption and text deliberately label these values as simplified open-data
diagnostics because the score-template validation failed.](figures/observed_limit_significance_summary.pdf){#fig:an-result-summary}

![Comparison to expected and 10% validation. The figure compares the expected
limit, 10% diagnostic fit, full-data fit, and W scale evolution. It makes the
unblinding history visible and shows that the W control scale is stable while
the final score-template validation remains flagged.](figures/comparison_to_4a_4b.pdf){#fig:an-unblind-history}

# Validation Summary

| Test | Data scope | chi2/ndf | p-value | Verdict | What it validates |
|---|---|---:|---:|---|---|
| Expected Asimov toy plumbing | expected-only | 0.000 | 1.000 | pass as plumbing | pyhf workspace and toy generation |
| 10% score templates | 10% data | 1.732 | n/a | flagged | pre-unblinding score data/MC model |
| Full score templates | full data | 3.218 | n/a | flagged | observed score data/MC model |
| W high-mT scale stability | 10% to full | n/a | n/a | pass arithmetic | W control-region normalization |

| Category | Data | Background | Data/background | Chi2/ndf | Max pull | Verdict |
|---|---:|---:|---:|---:|---:|---|
| boosted | 2213 | 2062.80 | 1.073 | 1.687 | 2.14 | flagged |
| vbf | 79 | 146.67 | 0.539 | 4.310 | 3.34 | flagged |
| zero_jet | 8466 | 6894.80 | 1.228 | 3.656 | 2.47 | flagged |

The full combined data/background ratio is
`1.1816` and the full combined
chi2/ndf is `3.2176`. The VBF channel has
a data deficit, the zero-jet channel has a data excess, and the boosted
channel is closer to the model. This category pattern is not consistent with
an unqualified single signal interpretation.

![Full-data VBF score validation. The figure compares full data to the frozen
score-template model in the VBF category. The VBF category has the largest
category chi2/ndf and a deficit relative to the background template.](figures/observed_score_vbf.pdf){#fig:an-full-vbf}

![Full-data boosted score validation. The figure compares full data to the
frozen score-template model in the boosted category. This channel has the most
moderate full-data validation behavior among the three fitted categories.](figures/observed_score_boosted.pdf){#fig:an-full-boosted}

![Full-data zero-jet score validation. The figure compares full data to the
frozen score-template model in the zero-jet category. The zero-jet data excess
dominates the combined data/background ratio.](figures/observed_score_zero_jet.pdf){#fig:an-full-zero}

![Observed pull and ratio summary. The figure summarizes category-level
ratios, pulls, and the comparison with the 10% validation. It is the central
diagnostic showing why the observed signal-strength and Z values cannot be
promoted to CMS-quality evidence.](figures/observed_pull_ratio_summary.pdf){#fig:an-pull-summary}

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
| This open-data expected | 8 TeV mu tau_h reduced samples | 0.526 | expected mu < 4.199 | internal expected reference |
| This open-data observed | 8 TeV mu tau_h reduced samples | 2.978 flagged | mu_hat = 7.664; mu < 13.323 | diagnostic only |
| CMS Run 1 | 7+8 TeV multi-channel | >3 | mu = 0.78 ± 0.27 | publication context |
| CMS 2018 | 13 TeV multi-channel | obs 4.9, exp 4.7 | mu = 1.09 ± about 0.27 | publication context |

<!-- FLAGSHIP -->
![Significance comparison. The figure compares the open-data expected and
observed diagnostics with CMS Run 1 and CMS 2018 H to tau tau publication
significances. The open-data observed value is labelled as flagged and should
not be read as evidence comparable to the CMS publication rows.](figures/phase5_significance_comparison.pdf){#fig:an-significance-comparison}

<!-- FLAGSHIP -->
![Signal-strength and limit comparison. The figure places the open-data
mu_hat and observed CLs limit on the same signal-strength scale as published
CMS Run 1 and Run 2 signal-strength measurements. The open-data points are not
directly equivalent to the CMS measurements because of reduced channel
coverage, missing calibrations, and flagged score-template validation.](figures/phase5_mu_limit_comparison.pdf){#fig:an-mu-comparison}

# Limitations And Resolving Power

The analysis can resolve only very large deviations from the SM expectation.
The median expected 95% CLs limit of `mu < 4.20`
already shows that an SM-strength signal is below the expected sensitivity of
this reduced single-channel setup. The observed limit of `mu < 13.32`
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
fit reports `mu_hat = 7.6642`, `mu < 13.3226` at 95% CLs, and
`Z = 2.9776`. Because the 10% and full-data score-template validations
are flagged, the result is explicitly not CMS-quality evidence. Its value is
as a transparent, citable open-data workflow and as a documented comparison to
published CMS H to tau tau analyses.

# References {-}
