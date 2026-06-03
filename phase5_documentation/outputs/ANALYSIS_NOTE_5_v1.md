---
title: "CMS Open Data H to tau tau Search: Final Analysis Note"
author: "Analysis my_analysis"
date: "2026-06-02"
bibliography: references.bib
---

# Abstract {-}

This note documents a reduced CMS 2012 Open Data search for Higgs boson decays
to tau pairs in the mu tau_h final state. An optimized calibrated-score model
is trained after multivariate input reweighting derived before training. On the
full data it gives `mu = 38.3802 +7.0346 -6.1157`
with the upper interval finite, and an observed 95% CLs limit
`mu < 50.0000`. This optimized-score result fails
the observed validation gate (`fail`), so the previous visible-mass
result is retained as the validated baseline: mu = 0.4382 +4.9443 -0.4382; 95% CLs mu < 10.7645; median expected 95% CLs mu < 10.7375.

# Change Log {-}

Phase 5 v3 updates the final result to the best available trained classifier
after applying data/MC input reweighting before training. It retains the
previous visible-mass result as a frozen baseline for `mu` comparison and
documents the absence of embedded and EWK Z reduced samples.

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
denominators and the cited luminosity reference.](figures/sample_event_count_file_size.pdf){#fig:an-samples}

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
| vbf | 79 | 60.17 | 0.36 | 1.590 | 1.313 |
| boosted | 2213 | 2115.53 | 5.64 | 9.175 | 1.046 |
| zero_jet | 8466 | 14047.12 | 22.93 | 14.341 | 0.603 |

![Cutflow summary. This plot shows raw event counts after each selection step
for data, signal MC, and background MC. It verifies that the selection chain is
monotonic and that the reduced samples remain populated after trigger, object,
charge, and transverse-mass requirements.](figures/cutflow_summary.pdf){#fig:an-cutflow}

# QCD And W Control Corrections

The W+jets normalization is measured in the high-mT control region as
`0.8528 ± 0.0370`.
The 10% validation value was `0.8433 ± 0.0868`.
The values agree within the larger 10% uncertainty and support the W-control
arithmetic.

The VBF category originally had a large MC overprediction. Tightening the VBF
cuts and applying a simple b-tag veto did not solve it, so a disjoint VBF-like
top-btag control region outside the low-mT signal region was used to calibrate
the MC-background rate in the VBF category. The resulting VBF background scale
is `0.5571 ± 0.0515`;
it is applied only to MC backgrounds in VBF and not to the signal or QCD/fake
template.

The same-sign QCD/fake estimate subtracts non-QCD MC from same-sign low-mT data
and transfers the resulting template to opposite-sign signal candidates. For
the primary calibrated-score model, the OS/SS transfer factor measured in the
lowest score bin is `0.0204 ± 0.2533`.

Large control-region data/MC differences in several classifier inputs are
handled before training by a multivariate density-ratio reweighting of
background MC. The reweighting classifier is trained only in non-signal
validation/control regions and is then applied to background MC in the
signal-region classifier training and final score templates. The reduced file
set contains no embedded Z to tau tau or EWK Z reduced sample, so DY/Z is not
silently substituted; instead its normalization is loosened to 30% in
boosted/zero-jet and 50% in VBF.

![Full high-mT W control comparison. The figure shows the derivation inputs for
the full-data W+jets control scale. The control region is outside the low-mT
signal region and the scale is propagated to the observed workspace without
signal-region tuning.](figures/w_highmt_scale_full.pdf){#fig:an-wscale}

# Optimized Score Result And Baseline

The primary statistical model is a binned pyhf profile likelihood in the
calibrated classifier score, with one signal-strength parameter `mu`, the W
high-mT scale, the same-sign QCD/fake transfer uncertainty, luminosity, widened
DY/Z and tau/open-data normalization terms, and MC statistical terms
[@pyhf_joss; @read_cls; @cowan_asymptotic].

| Quantity | Value | Interpretation |
|---|---:|---|
| Primary median expected 95% CLs limit | mu < 1.9735 | calibrated-score workspace |
| Primary observed 95% CLs limit | mu < 50.0000 | conservative observed result |
| Primary mu central value | 38.3802 +7.0346 -6.1157 | profile likelihood q(mu)=1 interval |
| Primary q0 Z | 12.4698 | diagnostic only |
| Primary combined data/background | 0.6631 | validation after QCD/fake correction |
| Primary chi2/ndf | 2.4808 | validation after QCD/fake correction |
| Optimized-score observed gate | fail | Observed optimized-score model must avoid boundary limits, >5 sigma diagnostic excesses, and gross combined normalization mismatch. |
| Frozen baseline visible-mass result | mu = 0.4382 +4.9443 -0.4382; 95% CLs mu < 10.7645; median expected 95% CLs mu < 10.7375 | previous primary result before this update |

The optimized score improves expected sensitivity but fails the observed-data
gate because the fitted signal strength is boundary-like and the diagnostic
significance is too large for this reduced single-channel setup. The previous
visible-mass result is therefore kept as the validated baseline, while the new
score result is reported as an attempted optimized model for comparison.

![Primary calibrated-score validation in VBF. The plot compares full data to
the calibrated score prediction in the VBF category after multivariate input
reweighting, widened DY/Z normalization, W and VBF control factors, and the
same-sign QCD/fake estimate.](figures/observed_primary_score_vbf.pdf){#fig:an-primary-vbf}

![Primary calibrated-score validation in boosted. The plot compares full data
to the calibrated score prediction in the boosted category. This channel is
part of the final simultaneous fit.](figures/observed_primary_score_boosted.pdf){#fig:an-primary-boosted}

![Primary calibrated-score validation in zero-jet. The zero-jet normalization
is stabilized by the same-sign QCD/fake estimate and the control-region-derived
background input reweighting.](figures/observed_primary_score_zero_jet.pdf){#fig:an-primary-zero}

![Category signal-strength comparison. The figure shows the Standard Model
expectation `mu = 1` and the observed single-category profile-fit value for
VBF, boosted, and zero-jet categories using the primary calibrated-score model.
These category fits are diagnostics; the quoted result remains the simultaneous
three-category fit.](figures/phase5_category_mu_comparison.pdf){#fig:an-category-mu}

![Primary and baseline signal-strength comparison. The figure compares the new
calibrated-score primary result with the frozen previous visible-mass baseline
using the same signal-strength convention. Error bars are profile-likelihood
`q(mu)=1` intervals with the physical lower bound at `mu >= 0`.](figures/phase5_primary_vs_baseline_mu.pdf){#fig:an-primary-baseline-mu}

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
| Optimized score attempt | 8 TeV mu tau_h reduced mirror, calibrated score | 12.470 | mu = 38.380 +7.035 -6.116; 95% CLs mu < 50.000; expected mu < 1.974; gate fail |
| This analysis baseline | 8 TeV mu tau_h reduced mirror, visible mass | 0.095 | mu = 0.4382 +4.9443 -0.4382; 95% CLs mu < 10.7645; median expected 95% CLs mu < 10.7375 |
| CMS Run 1 JHEP 2014 | 7+8 TeV multi-channel | observed 3.2, expected 3.7 | mu = 0.78 ± 0.27 |
| CMS PLB 2018 2016 data | 13 TeV multi-channel | observed 4.9, expected 4.7 | mu = 1.09 ± about 0.27 |
| CMS PLB 2018 combined | CMS 7+8+13 TeV combination | observed 5.9, expected 5.9 | same signal-strength model as CMS 2018 publication |
| ATLAS+CMS Run 1 combination | 7+8 TeV global Higgs couplings/rates | H to tau tau evidence context | global mu = 1.09 ± 0.11 |
| PDG / HXSWG SM context | H to tau tau branching fraction at mH near 125 GeV | not a search significance | BR(H to tau tau) about 6.3%, used only as SM normalization context |

![Signal-strength and limit comparison. The figure uses a CMS-style
expected-band and observed-marker presentation for the primary open-data limit,
published CMS/ATLAS+CMS signal-strength measurements, and a narrow PDG SM H to
tau tau branching-ratio normalization band at `mu = 1`. The open-data
diagnostic is not directly equivalent to CMS publication measurements.](figures/phase5_mu_limit_comparison.pdf){#fig:an-mu-comparison}

![Significance comparison. The figure compares the primary open-data diagnostic
with CMS and ATLAS+CMS publication values. Only the primary open-data result is
shown from this analysis in the final result figure.](figures/phase5_significance_comparison.pdf){#fig:an-significance-comparison}

# Conclusion

The optimized calibrated-score fit was attempted after pre-training
multivariate input reweighting, but it fails the observed validation gate. It
is therefore compared against, not substituted for, the frozen visible-mass
baseline. The baseline gives mu = 0.4382 +4.9443 -0.4382; 95% CLs mu < 10.7645; median expected 95% CLs mu < 10.7375. This remains a reduced Open Data
diagnostic, not CMS-quality evidence for H to tau tau.

# References {-}
