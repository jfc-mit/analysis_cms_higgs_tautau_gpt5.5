---
title: "CMS Open Data H to tau tau Search: Final Analysis Note"
author: "Analysis my_analysis"
date: "2026-06-02"
bibliography: references.bib
---

# Abstract {-}

This note documents a reduced CMS 2012 Open Data search for Higgs boson decays
to tau pairs in the mu tau_h final state. A Phase 5 audit found that the
original observed BDT-score fit was not a valid evidence result: it omitted a
reducible QCD/fake-tau background estimate and failed high-score shape
validation. The final conservative result therefore uses visible mass in VBF,
boosted, and zero-jet categories with a same-sign data-driven QCD/fake template.
It gives `mu_hat = 0.4382`, an observed 95% CLs limit
`mu < 10.7645`, and `Z = 0.0949`.
The categorized BDT-score model is retained as a flagged diagnostic with
`mu_hat = 9.3518` and `Z = 3.9416`.

# Change Log {-}

Phase 5 v2 responds to the observed-versus-expected audit. It adds a same-sign
QCD/fake estimate, changes the primary full-data result to the visible-mass
fallback, keeps the BDT score as a diagnostic, adds NN/MVA performance figures,
and compiles the paper with REVTeX PRL formatting.

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
| vbf | 78 | 96.28 | 17.75 | 1.590 | 0.810 |
| boosted | 2183 | 2364.39 | 325.58 | 9.170 | 0.923 |
| zero_jet | 8451 | 8456.81 | 1569.65 | 14.341 | 0.999 |

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
the primary visible-mass model, the OS/SS transfer factor measured in the lowest
visible-mass bin is `0.9958 ± 0.1201`.
For the BDT score diagnostic, the corresponding low-score factor is
`0.8173 ± 0.0853`.

![Full high-mT W control comparison. The figure shows the derivation inputs for
the full-data W+jets control scale. The control region is outside the low-mT
signal region and the scale is propagated to the observed workspace without
signal-region tuning.](figures/w_highmt_scale_full.pdf){#fig:an-wscale}

# MVA And Transformer Diagnostics

The requested NN/MVA program was evaluated using the available reduced event
features. Histogram gradient boosting, an MLP neural network, and XGBoost were
trained on selected MC only. A transformer was not trained because the current
pixi environment lacks a fast attention stack and the reduced files do not
contain the GenMET target needed for the requested missing-momentum regression.

![MVA ROC curves. This figure shows ROC curves for the HGB, MLP neural-network,
and XGBoost score columns on selected signal/background MC. It is an
open-simulation performance diagnostic and does not validate data/MC score
shapes.](figures/phase5_mva_roc.pdf){#fig:an-mva-roc}

![MVA AUC summary. This figure compares the full selected-MC ROC AUC values for
the trained classifiers and records that the transformer branch was not trained
in this fast reduced-sample pass. The BDT score has strong MC separation, but
that is not sufficient for an observed evidence claim.](figures/phase5_mva_auc_summary.pdf){#fig:an-mva-auc}

![HGB permutation importance. This figure shows the leading permutation
importance values for a retrained HGB classifier on a held-out selected-MC
split. It documents which reduced features drive the classifier response used
in the diagnostic score fit.](figures/phase5_hgb_permutation_importance.pdf){#fig:an-mva-importance}

![Transformer feasibility. This figure records which modern-model branches were
available in the current environment. The transformer and GenMET-regression
branches are explicitly downscoped rather than reported as unperformed
successes.](figures/phase5_transformer_feasibility.pdf){#fig:an-transformer}

# Primary Visible-Mass Result

The primary statistical model is a binned pyhf profile likelihood in visible
mass, with one signal-strength parameter `mu`, the W high-mT scale, the
same-sign QCD/fake transfer uncertainty, luminosity, DY and tau/open-data
normalization terms, and MC statistical terms [@pyhf_joss; @read_cls;
@cowan_asymptotic].

| Quantity | Value | Interpretation |
|---|---:|---|
| Primary median expected 95% CLs limit | mu < 10.7375 | corrected visible-mass workspace |
| Primary observed 95% CLs limit | mu < 10.7645 | conservative observed result |
| Primary mu_hat | 0.4382 | best fit, bounded at zero if no excess |
| Primary q0 Z | 0.0949 | diagnostic only |
| Primary combined data/background | 0.9812 | validation after QCD/fake correction |
| Primary chi2/ndf | 0.7224 | validation after QCD/fake correction |

The primary result is much more stable than the original score-only observed
fit. It does not show a Higgs-like excess: `mu_hat` is `0.4382`
and `Z = 0.0949`. The observed limit
is compatible with the weak sensitivity expected from this reduced single-final
state setup.

![Primary visible-mass validation in VBF. The plot compares full data to the
QCD-corrected visible-mass prediction in the VBF category. The remaining VBF
deficit is a limitation, but it no longer drives a fake signal-strength
increase.](figures/observed_mvis_vbf.pdf){#fig:an-primary-vbf}

![Primary visible-mass validation in boosted. The plot compares full data to
the QCD-corrected visible-mass prediction in the boosted category. This channel
is part of the conservative primary fit.](figures/observed_mvis_boosted.pdf){#fig:an-primary-boosted}

![Primary visible-mass validation in zero-jet. The zero-jet normalization is
stabilized by the same-sign QCD/fake estimate, which removes the dominant
normalization pathology seen in the original score-only result.](figures/observed_mvis_zero_jet.pdf){#fig:an-primary-zero}

# BDT Score Diagnostic

The BDT-score model is kept because it was explicitly requested and has better
expected MC separation. It is not used as the primary observed evidence result,
because its high-score bins remain shape-flagged after adding the QCD/fake
template.

| Category | Data | Background | QCD/fake | Signal | Data/background |
|---|---:|---:|---:|---:|---:|
| vbf | 79 | 94.14 | 12.43 | 1.590 | 0.839 |
| boosted | 2213 | 2331.71 | 268.90 | 9.175 | 0.949 |
| zero_jet | 8466 | 8187.20 | 1292.40 | 14.341 | 1.034 |

| Quantity | Value | Interpretation |
|---|---:|---|
| Score median expected 95% CLs limit | mu < 4.1802 | diagnostic expected score workspace |
| Score observed 95% CLs limit | mu < 14.8373 | flagged diagnostic |
| Score mu_hat | 9.3518 | flagged high-score shape diagnostic |
| Score q0 Z | 3.9416 | not CMS-quality evidence |
| Score combined data/background | 1.0137 | score validation after QCD/fake correction |
| Score chi2/ndf | 1.1750 | score validation after QCD/fake correction |

![Score-template diagnostic in VBF. This figure keeps the categorized BDT score
view requested for sensitivity studies. It is diagnostic because the score
shape is not validated well enough for an observed evidence claim.](figures/observed_score_vbf.pdf){#fig:an-score-vbf}

![Score-template diagnostic in boosted. This figure shows the boosted score
template after QCD/fake correction. High-score residuals motivate the
diagnostic-only status.](figures/observed_score_boosted.pdf){#fig:an-score-boosted}

![Score-template diagnostic in zero-jet. This figure shows that the zero-jet
normalization is improved by QCD/fake correction while high-score shape
residuals remain visible.](figures/observed_score_zero_jet.pdf){#fig:an-score-zero}

![Observed pull and ratio summary. The figure compares primary visible-mass and
BDT-score validation behavior after the QCD/fake audit correction. It shows why
the visible-mass model is primary and the score fit is diagnostic.](figures/observed_pull_ratio_summary.pdf){#fig:an-pull-summary}

# Comparison With Published Results

CMS Run 1 reported evidence for H to tau tau using 7 and 8 TeV data with
multiple final states, embedded backgrounds, and a full calibration program;
the quoted best-fit signal strength was 0.78 ± 0.27 [@cms_htt_2014]. CMS 2018
reported observed and expected significances of 4.9 and 4.7 and a signal
strength near 1.09 [@cms_htt_2018]. These are not direct pass/fail targets for
this reduced open-data workflow.

| Result | Scope | Significance | Signal-strength information |
|---|---|---:|---|
| This open-data primary | 8 TeV mu tau_h reduced mirror, visible mass | 0.095 | mu_hat = 0.438; mu < 10.764; expected mu < 10.738 |
| This BDT diagnostic | 8 TeV mu tau_h reduced mirror, HGB score | 3.942 flagged | mu_hat = 9.352; mu < 14.837; expected mu < 4.180 |
| CMS Run 1 | 7+8 TeV multi-channel | >3 | mu = 0.78 ± 0.27 |
| CMS 2018 | 13 TeV multi-channel | observed 4.9, expected 4.7 | mu = 1.09 ± about 0.27 |

![Signal-strength and limit comparison. The figure uses a CMS-style
expected-band and observed-marker presentation for the primary open-data limit,
with the flagged BDT diagnostic and published CMS signal-strength measurements
shown as context. The open-data diagnostic is not directly equivalent to CMS
publication measurements.](figures/phase5_mu_limit_comparison.pdf){#fig:an-mu-comparison}

![Significance comparison. The figure compares the primary open-data diagnostic
and the flagged BDT-score diagnostic with CMS publication values. The BDT row is
explicitly not interpreted as evidence.](figures/phase5_significance_comparison.pdf){#fig:an-significance-comparison}

# Conclusion

The final audit-corrected result is a conservative visible-mass plus QCD/fake
template fit. It gives `mu_hat = 0.4382`, an observed 95% CLs
limit `mu < 10.7645`, and `Z = 0.0949`.
The originally surprising BDT-score observed result is retained only as a
flagged diagnostic because the score shape is not validated in data. This is
the correct interpretation of the reduced CMS Open Data workflow: reproducible
and useful for methodology, but not CMS-quality evidence for H to tau tau.

# References {-}
