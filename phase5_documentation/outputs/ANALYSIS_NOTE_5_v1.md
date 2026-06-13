---
title: "CMS Open Data H to Tau Tau Search: Final Analysis Note"
author: "Analysis my_analysis"
date: "2026-06-13"
bibliography: references.bib
---

# Abstract {-}

This note reports a full rerun of the muon plus hadronic-tau Higgs-to-tau-tau
analysis with the current local CMS Open Data and simulation inputs. The
analysis follows the Run-1 H to tau tau strategy of a simultaneous binned fit
in VBF, boosted, and zero-jet categories [@cms_htt_2014] and keeps two
result streams: a cut-based visible-mass baseline and a single
three-category $D_{NN}$ classifier-score result. The visible-mass baseline
gives `mu_hat = 2.4740`, observed 95% CLs `mu < 5.9262`,
median expected limit `3.6919`, and interval proxy
`mu_hat = 2.4740 +3.4522 -2.4740`.
The $D_{NN}$ score result gives
`mu_hat = 1.6160`, observed 95% CLs `mu < 3.5769`,
median expected limit `1.8069`, and interval proxy
`mu_hat = 1.6160 +1.9610 -1.6160`.
The results are interpreted as a
single-channel public-data exercise, not as a replacement for the published CMS
combination [@cms_htt_2018].

# Introduction

The target process is Standard Model Higgs boson production followed by
$H \to \tau\tau$, reconstructed in the $\mu\tau_h$ final state. This channel
combines a clean isolated muon with a hadronic-tau candidate and is one of the
classic ingredients of the CMS H to tau tau program [@cms_htt_2014]. The
parameter of interest is the signal-strength modifier

$$
\mu =
\frac{\sigma(pp\to H)\,\mathcal{B}(H\to\tau\tau)}
{\left[\sigma(pp\to H)\,\mathcal{B}(H\to\tau\tau)\right]_{SM}} .
$$ {#eq:mu-def}

The reduced Open Data setting has less information than the published Run-1
analyses: embedded $Z\to\tau\tau$ samples, several rare backgrounds, and full
object-calibration machinery are not available. The note therefore emphasizes
the reproducible signal-extraction chain, the category-level validation, and the
relative behavior of the visible-mass and $D_{NN}$ observables.

# Data And Simulation

The data input is the localized CMS 2012 TauPlusX Run2012B and Run2012C sample.
The simulated inputs are ggH and VBF Higgs signal, DY+jets, top-pair, and
exclusive W+jets samples. The normalization uses the Open Data record event
counts and the luminosity reference stored in the local normalization artifact.

![Input and selected-event cutflow. The figure shows the data and simulation
counts through the main selection stages after the rerun on the current local
inputs. It is the first check that the event processing consumed the updated
ROOT files.](figures/cutflow_summary.pdf){#fig:cutflow}

![Final category yields. The figure summarizes the selected yields in the VBF,
boosted, and zero-jet categories before the final binned statistical fit. It
provides a compact check of the category split used by both retained
observables.](figures/category_yields.pdf){#fig:category-yields}

# Event Selection And Categories

Events are required to contain a selected muon, a selected hadronic-tau
candidate, low transverse mass, and an opposite-sign signal-region pair. The
categories are mutually exclusive. The VBF category requires two clean jets with
a large dijet mass and pseudorapidity separation, the boosted category captures
remaining events with a reconstructed recoil topology, and the zero-jet category
contains the statistically dominant inclusive remainder.

![Selected muon transverse momentum. The comparison shows the selected muon
$p_T$ spectrum in data and simulation after the signal-region selection. It is
used as an object-level validation input rather than a fitted observable.](figures/mu_pt.pdf){#fig:mu-pt}

![Selected hadronic-tau transverse momentum. The comparison shows the selected
$\tau_h$ $p_T$ spectrum in data and simulation. It checks the stability of the
tau-object phase space used by the baseline and $D_{NN}$ fits.](figures/tau_pt.pdf){#fig:tau-pt}

![Missing transverse momentum. The comparison shows the selected missing
transverse momentum distribution. This variable enters the classifier input set
and is also a key validation distribution for W+jets and tau-pair kinematics.](figures/met_pt.pdf){#fig:met-pt}

![Transverse mass control distribution. The comparison shows the
$m_T(\mu,p_T^{miss})$ distribution used to monitor the W+jets-rich high-mass
region. The final W+jets scale is derived from the corresponding high-$m_T$
control selection.](figures/mt_mu_met.pdf){#fig:mt-mu-met}

# Observables

The baseline observable is the visible di-tau mass $m_{vis}$, the invariant
mass of the reconstructed muon and hadronic-tau four-vectors. It is robust and
cut-based, but broad because neutrinos from both tau decays are not
reconstructed. The retained multivariate observable is $D_{NN}$, implemented
as an XGBoost classifier score `mva_score_xgboost` in 20 uniform bins from 0 to
1. Its input set is:

`m_vis`, `mu_pt`, `mu_eta`, `tau_pt`, `tau_eta`, `delta_r_mu_tau`, `delta_phi_mu_tau`, `met_pt`, `met_significance`, `mt_mu_met`, `mt_tau_met`, `mt_tot`, `pt_tautau_proxy`, `m_coll`, `tau_id_iso_raw`.

The classifier is trained on MC signal and background labels with the nominal MC
normalization weights and class balancing. In the current rerun the stored
training metric is test AUC `0.8247`
with train AUC `0.8524`.

![Visible-mass distribution in the VBF category. The pre-fit comparison shows
the fitted baseline observable in the most signal-enriched topology. The final
fit uses the corresponding Phase-4c template with the same category
definition.](figures/visible_mass_vbf.pdf){#fig:visible-vbf-prefit}

![Visible-mass distribution in the boosted category. The pre-fit comparison
shows the baseline observable in the recoil-enhanced category. This is a major
contributor to the simultaneous visible-mass baseline fit.](figures/visible_mass_boosted.pdf){#fig:visible-boosted-prefit}

![Visible-mass distribution in the zero-jet category. The pre-fit comparison
shows the broad baseline observable in the highest-statistics category. It
anchors the background-rich part of the simultaneous fit.](figures/visible_mass_zero_jet.pdf){#fig:visible-zero-prefit}

![MVA input modelling summary. The figure records the data/background modelling
quality of candidate classifier inputs. It documents the validation context for
using a single retained $D_{NN}$ tool.](figures/mva_input_modeling_chi2.pdf){#fig:mva-inputs}

![Expected classifier score templates. The figure shows the trained classifier
score response for signal and background before observed-data fitting. It
checks that the retained classifier has the intended signal/background
ordering.](figures/mva_score_templates.pdf){#fig:mva-score-templates}

# Background Model

The W+jets normalization is constrained from a high-$m_T$ control region. With
the current inputs the full-data scale factor is
`0.9190 ± 0.0139`.
The VBF background scale from the VBF-like non-signal control region is
`0.3448 ± 0.0612`.
The reducible QCD/fake component is estimated from same-sign data after
subtracting non-QCD simulation and transferring into the signal region.

![W high-$m_T$ control-region scale. The figure shows the non-W MC, nominal W
MC, scaled control-region prediction, and observed data in the high-$m_T$
control region. This scale is propagated to both retained workspaces.](figures/w_highmt_scale_full.pdf){#fig:w-scale}

# Systematic Uncertainties

The retained nuisance program covers luminosity, tau/open-data acceptance,
DY/Z normalization, W+jets control normalization, VBF background control
normalization, same-sign QCD/fake transfer, and MC statistical uncertainties.
The exact current values are read from the Phase-4c JSON artifact:

| Source | Current value |
| --- | --- |
| dy_ztautau_open_data | 30% in boosted/zero-jet and 50% in VBF |
| lumi_2012 | 2.6% |
| qcd_ss_transfer_nn | 1.07652 relative from same-sign/low-sideband data |
| qcd_ss_transfer_visible | 0.315486 relative from same-sign/low-sideband data |
| tau_open_data_acceptance | 15% |
| vbf_background_control | 0.177463 relative from VBF-like top-btag non-signal CR |
| wjets_high_mt_control | 0.015166 relative from full high-mT data CR |

![Sensitivity nuisance audit. The figure summarizes the expected sensitivity
response to the retained nuisance model. It is used to confirm that the
current results are not driven by a hidden no-systematics configuration.](figures/sensitivity_nuisance_audit.pdf){#fig:nuisance-audit}

# Statistical Model

Both retained results use binned HistFactory-style likelihoods implemented with
pyhf [@pyhf_joss]. For category $c$ and bin $b$, the expected count is

$$
\nu_{cb}(\mu,\theta) =
\mu s_{cb}(\theta) + \sum_k b_{kcb}(\theta),
$$ {#eq:expectation}

where $s_{cb}$ is the sum of ggH and VBF signal templates and $b_{kcb}$
are the background templates. The likelihood is the product of Poisson terms
for the binned data and Gaussian/log-normal constraints for nuisance
parameters. Upper limits use the modified frequentist CLs construction
[@read_cls] with asymptotic formulae [@cowan_asymptotic].

The expected median limit from the earlier expected-only reference point is
`2.90409966080617`. The current observed limits are computed from the full data
with the updated local selection and templates.

# Full-Data Results

| Category | Data | Background | Signal | Data/background | Chi2/ndf |
| --- | ---: | ---: | ---: | ---: | ---: |
| vbf | 70 | 53.37 | 4.13 | 1.312 | 1.999 |
| boosted | 1138 | 1249.00 | 11.28 | 0.911 | 0.492 |
| zero_jet | 25920 | 26732.68 | 106.26 | 0.970 | 0.126 |

The combined visible-mass validation gives data/background `0.968`
and chi2/ndf `0.873`. The combined $D_{NN}$ validation
gives data/background `1.003` and chi2/ndf
`0.685`.

The visible-mass baseline fit gives

$$
\hat{\mu}(m_{vis}) = 2.4740, \qquad
\mu < 5.9262 \; (95\%\; CLs),
$$ {#eq:baseline-result}

with median expected limit `3.6919`. The $D_{NN}$ result gives

$$
\hat{\mu}(D_{NN}) = 1.6160, \qquad
\mu < 3.5769 \; (95\%\; CLs),
$$ {#eq:nn-result}

with median expected limit `1.8069`.

![Visible-mass baseline in the VBF category. The plot compares data with the
baseline visible-mass prediction after the data-driven reducible-background
correction. The lower panel shows the data-to-prediction ratio.](figures/phase5_baseline_visible_vbf.pdf){#fig:p5-visible-vbf}

![Visible-mass baseline in the boosted category. The plot compares data with
the baseline visible-mass prediction in the boosted category. This category has
substantially more events than the VBF category and constrains the broad
visible-mass shape.](figures/phase5_baseline_visible_boosted.pdf){#fig:p5-visible-boosted}

![Visible-mass baseline in the zero-jet category. The plot compares data with
the baseline visible-mass prediction in the statistically dominant category.
This category controls the global normalization behavior of the baseline
workspace.](figures/phase5_baseline_visible_zero_jet.pdf){#fig:p5-visible-zero}

![$D_{NN}$ score in the VBF category. The plot compares data with the retained
classifier-score prediction in the VBF category. The same score definition and
binning are used in the other categories.](figures/phase5_nn_score_vbf.pdf){#fig:p5-nn-vbf}

![$D_{NN}$ score in the boosted category. The plot compares data with the
retained classifier-score prediction in the boosted category. The ratio panel
checks whether the classifier ordering is modelled in observed data.](figures/phase5_nn_score_boosted.pdf){#fig:p5-nn-boosted}

![$D_{NN}$ score in the zero-jet category. The plot compares data with the
retained classifier-score prediction in the zero-jet category. The category has
the largest statistical weight in the combined classifier fit.](figures/phase5_nn_score_zero_jet.pdf){#fig:p5-nn-zero}

![Observed result summary. The figure compares the visible-mass baseline,
retained $D_{NN}$ result, CMS 2014 result, and CMS 2018 result on the same
signal-strength scale. Each row uses the same convention: black observed point
with horizontal uncertainty, green and yellow expected one- and two-standard
deviation bands, a black dashed median-expected marker, and the common Standard
Model line at $\mu=1$.](figures/observed_limit_significance_summary.pdf){#fig:p5-summary}

# Comparison To Published Measurements

The CMS Run-1 H to tau tau analysis and later CMS combination use more final
states, more luminosity, embedded backgrounds, and a much richer calibration
program than this single-channel public-data analysis [@cms_htt_2014;
@cms_htt_2018]. The correct comparison is therefore qualitative: the present
analysis demonstrates a reproducible template-fit chain and produces limits
that are much weaker than the published measurements. The retained
$D_{NN}$ result is the more sensitive of the two current outputs by expected
median limit, while the visible-mass baseline remains the cut-based reference.

# Validation And Limitations

The current run validates that both pyhf workspaces construct, that both fits
evaluate, that the $D_{NN}$ template uses `mva_score_xgboost`, and that the
classifier score uses 20 uniform bins. Remaining limitations are inherited from
the reduced public-input setting: the absence of embedded $Z\to\tau\tau$,
incomplete rare backgrounds, simplified object systematics, and reliance on
control-derived nuisance parameters.

# Reproduction Contract

The current machine-readable result artifacts are:

| Artifact | Purpose |
| --- | --- |
| `phase4_inference/4c_observed/outputs/baseline_visible_result.json` | visible-mass baseline result |
| `phase4_inference/4c_observed/outputs/nn_score_result.json` | retained $D_{NN}$ result |
| `phase4_inference/4c_observed/outputs/pyhf_workspace_baseline_visible.json` | baseline pyhf workspace |
| `phase4_inference/4c_observed/outputs/pyhf_workspace_nn_score.json` | $D_{NN}$ pyhf workspace |
| `phase4_inference/4c_observed/outputs/visible_observed_templates.npz` | baseline templates |
| `phase4_inference/4c_observed/outputs/nn_score_observed_templates.npz` | $D_{NN}$ templates |

The focused rebuild commands are `pixi run phase3-select`, `pixi run phase3-mva`,
`pixi run phase3-sensitivity`, `pixi run phase3-plots`, `pixi run phase4c-all`,
and `pixi run phase5-docs`.
