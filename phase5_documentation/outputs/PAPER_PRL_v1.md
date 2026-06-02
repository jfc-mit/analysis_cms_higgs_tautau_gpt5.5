---
title: "A CMS Open Data Diagnostic Search for H to Tau Tau in the Mu Tau_h Final State"
author: "Analysis my_analysis"
date: "2026-06-02"
bibliography: references.bib
---

# Abstract {-}

A diagnostic search for H to tau tau is performed with CMS 2012 Open Data in
the mu tau_h final state using reduced Run2012B/C TauPlusX samples. A binned
profile-likelihood fit to classifier-score templates in VBF, boosted, and
zero-jet categories gives `mu_hat = 7.664`, an observed 95% CLs upper
limit `mu < 13.323`, and an observed q0 diagnostic `Z = 2.978`.
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
| VBF | 79 | 146.67 | 1.590 | 0.539 |
| Boosted | 2213 | 2062.80 | 9.175 | 1.073 |
| Zero-jet | 8466 | 6894.80 | 14.341 | 1.228 |

![Selected category yields. The figure shows the event yields in the three
exclusive fit categories for data, signal MC, and background MC. It documents
the channel composition of the simultaneous likelihood fit and shows that the
zero-jet channel dominates the selected event count.](figures/category_yields.pdf){#fig:paper-category-yields}

# Statistical Analysis

The fitted observable is a histogram-gradient-boosting classifier score in
the three event categories. The likelihood is a binned profile likelihood
implemented with pyhf [@pyhf_joss],

$$
L(\mu,\theta)=\prod_{c,b} \mathrm{Pois}\left(n_{cb}\mid
\mu s_{cb}(\theta)+b_{cb}(\theta)\right)
\prod_k \pi_k(\theta_k).
$$ {#eq:paper-likelihood}

Upper limits use the CLs construction [@read_cls], and the discovery
diagnostic uses the one-sided q0 asymptotic approximation [@cowan_asymptotic].
The W+jets rate is constrained by a high-mT control-region scale
`0.8528 ± 0.0370`.
The retained nuisances include luminosity, DY normalization, tau open-data
acceptance, W high-mT normalization, and MC statistical uncertainties.

# Results

The expected median 95% CLs upper limit is `mu < 4.199`,
and the expected discovery diagnostic is `Z = 0.526`. The full-data fit
gives the diagnostic results summarized in @tbl:paper-results.

| Quantity | Value | Status |
|---|---:|---|
| Expected median 95% CLs limit | mu < 4.199 | background Asimov |
| Expected discovery diagnostic | 0.526 | background Asimov |
| Observed mu_hat | 7.664 | flagged diagnostic |
| Observed 95% CLs limit | mu < 13.323 | flagged diagnostic |
| Observed q0 Z | 2.978 | flagged diagnostic |

: Main open-data fit results. The observed entries are not CMS-quality evidence because score-template validation is flagged. {#tbl:paper-results}

![Observed result summary. The figure summarizes the fitted signal strength,
observed upper limit, expected median limit, and observed q0 diagnostic. The
values are diagnostics of the reduced open-data model and must be read
together with the validation caveat.](figures/observed_limit_significance_summary.pdf){#fig:paper-result-summary}

# Validation Caveat

The score-template model is not validated at CMS-publication quality. In the
10% validation sample, the combined data/background ratio is
`1.232` with chi2/ndf
`1.732` and status `flagged`. In the full
data, the combined data/background ratio is
`1.182` with chi2/ndf
`3.218` and status `flagged`. Therefore
the observed `Z = 2.978` and `mu_hat = 7.664` are simplified
open-data diagnostics, not evidence comparable to CMS publications.

![Full-data score validation summary. The figure summarizes data/background
ratios and maximum pulls in the observed score templates. It is the main
diagnostic showing why the observed fit result is not promoted to a
CMS-quality evidence statement.](figures/observed_pull_ratio_summary.pdf){#fig:paper-validation}

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
| This open-data expected | 8 TeV mu tau_h reduced samples | 0.526 | expected mu < 4.199 |
| This open-data observed | 8 TeV mu tau_h reduced samples | 2.978 flagged | mu_hat = 7.664; mu < 13.323 |
| CMS Run 1 | 7+8 TeV multi-channel | >3 | mu = 0.78 ± 0.27 |
| CMS 2018 | 13 TeV multi-channel | observed 4.9, expected 4.7 | mu = 1.09 ± about 0.27 |

: Comparison of the open-data diagnostic with published CMS H to tau tau results. The entries differ in energy, channel coverage, calibration completeness, and validation quality. {#tbl:paper-comparison}

![Significance comparison. The figure compares the open-data expected and
observed diagnostic significances with CMS publication values. The open-data
observed point is explicitly labelled as flagged and should not be interpreted
as CMS-quality evidence.](figures/phase5_significance_comparison.pdf){#fig:paper-significance}

![Signal-strength and limit comparison. The figure compares open-data
signal-strength-scale diagnostics with CMS Run 1 and CMS 2018 signal-strength
measurements. The open-data limit and mu_hat are not directly equivalent to
the published measurements because the reduced public model has flagged
score-template validation.](figures/phase5_mu_limit_comparison.pdf){#fig:paper-mu}

# Conclusion

A reproducible reduced CMS 2012 Open Data H to tau tau diagnostic search has
been documented in the mu tau_h final state. The full-data fit gives
`mu_hat = 7.664`, `mu < 13.323` at 95% CLs, and
`Z = 2.978`. Because the 10% and full-data score-template validations
are flagged, these are simplified open-data diagnostics and not CMS-quality
evidence. The analysis is useful as a public workflow and as a scoped
comparison to CMS H to tau tau publications, not as an independent publication
measurement.

# Reproducibility Note {-}

The markdown, TeX, PDF, and comparison figures are generated from the committed
Phase 4 JSON outputs by `phase5_documentation/src/build_phase5_docs.py`.

# References {-}
