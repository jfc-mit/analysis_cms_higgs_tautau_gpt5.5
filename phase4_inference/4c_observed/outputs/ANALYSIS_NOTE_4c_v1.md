---
title: "CMS Open Data H to tau tau Search: Phase 4c Audit-Corrected Observed Results"
author: "Analysis my_analysis"
date: "2026-06-02"
bibliography: references.bib
---

# Change Log {-}

**Phase 4c v2 audit correction**

- Added a same-sign data-driven QCD/fake background estimate.
- Added multivariate data/MC input reweighting derived in validation/control regions before classifier training.
- Promoted the calibrated categorized score model to the primary observed result.
- Widened DY/Z normalization to reflect the absence of embedding and EWK Z reduced samples.

# Phase 4c Observed Inference: Audit-Corrected Full Data

## Summary

Phase 4c has been updated after the audit of the large expected versus observed
discrepancy. The problem was physics modelling: the original score-template fit
omitted a reducible QCD/fake-tau component, used background MC before correcting
large data/MC input-shape differences, and carried too restrictive a DY/Z
normalization model for a reduced sample without embedding or EWK Z simulation.

The primary observed result is therefore the calibrated trained-discriminator
fit in the same VBF, boosted, and zero-jet categories. The classifier is trained
only on MC, but the background MC receives a multivariate data/MC input
reweighting derived before training in W high-mT, same-sign, Z-rich, and
top/b-tag validation/control regions. The primary score model also includes the
same-sign data-driven QCD/fake template and wider DY/Z normalization nuisance
terms. No alternative mass-fit result is quoted in this Phase 4c note; the
frozen previous visible-mass baseline is preserved only for the final
signal-strength comparison.

## W and QCD Control Inputs

The full-data W+jets scale from the high-mT control region is
`0.8528 ± 0.0370`.
The VBF background control scale from the VBF-like top-btag non-signal region is
`0.5571 ± 0.0515`;
it is applied only to MC backgrounds in the VBF fit category. This addresses
the large VBF data/MC overprediction seen in the original observed templates
without changing the signal normalization or the boosted/zero-jet categories.
The same-sign QCD/fake estimate uses data minus non-QCD MC in the same-sign
low-mT region and a transfer factor measured in the lowest fitted-observable
bin. For the primary calibrated-score model this factor is
`0.0204 ± 0.2533`.

![Full high-mT W control comparison. The figure shows non-W MC, nominal W MC,
the scaled control-region prediction, and full data in the control region.
The scale is derived outside the signal region and then propagated into the
observed workspaces.](figures/w_highmt_scale_full.pdf){#fig:p4c-wcr}

## Primary Calibrated-Score Result

| Category | Data | Background | QCD/fake | Data/background | Chi2/ndf | Max abs pull |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| vbf | 79 | 60.17 | 0.36 | 1.313 | 1.513 | 2.36 |
| boosted | 2213 | 2115.53 | 5.64 | 1.046 | 1.904 | 2.63 |
| zero_jet | 8466 | 14047.12 | 22.93 | 0.603 | 4.025 | 3.22 |

The primary calibrated-score fit gives `mu_hat = 38.3802`,
an observed 95% CLs limit `mu < 50.0000`,
and a diagnostic `q0` value `Z = 12.4698`.
The median expected limit from the same corrected workspace is
`1.9735`. This attempted optimized result is retained for
comparison, but the final Phase 5 interpretation keeps the frozen visible-mass
baseline because the optimized score fails the observed-data validation gate.

![Primary calibrated-score validation in the VBF category. The plot compares
localized Run2012B/C TauPlusX data to the calibrated score model after
pre-training multivariate input reweighting, wider DY/Z normalization, and
same-sign QCD/fake correction. This category remains statistically limited but
is included in the simultaneous primary fit.](figures/observed_primary_score_vbf.pdf){#fig:p4c-primary-vbf}

![Primary calibrated-score validation in the boosted category. The plot
compares full data to the calibrated score model with the W high-mT scale and
same-sign QCD/fake template. This category is used in the final observed
fit.](figures/observed_primary_score_boosted.pdf){#fig:p4c-primary-boosted}

![Primary calibrated-score validation in the zero-jet category. The zero-jet
normalization is stabilized by the same-sign QCD/fake estimate and the
background input reweighting. This category contributes the largest data
statistics to the primary simultaneous fit.](figures/observed_primary_score_zero_jet.pdf){#fig:p4c-primary-zero}

## Frozen Baseline For Final Comparison

The frozen previous visible-mass baseline gives `mu_hat = 0.4382`, observed 95% CLs `mu < 10.7645`, median expected `mu < 10.7375`. It is not
retrained or refit in this update; it is carried forward only so the final AN
and PRL can compare the optimized-score attempt with the previous result using
the same signal-strength convention.

![Observed pull and ratio summary. The figure compares the primary calibrated
score validation behavior after the QCD/fake, DY/Z, and input reweighting
corrections. It is the central diagnostic for the attempted optimized
model.](figures/observed_pull_ratio_summary.pdf){#fig:p4c-pulls}

![Observed limit and significance summary. The figure shows the primary
calibrated-score fit and the frozen visible-mass baseline on the same
signal-strength scale. The result remains an Open Data diagnostic rather than
CMS-quality evidence.](figures/observed_limit_significance_summary.pdf){#fig:p4c-result-summary}

## Phase 5 Obligation

Phase 5 must report the calibrated-score plus QCD model as an optimized
attempt, document the observed validation failure, and compare it with the
frozen visible-mass baseline. It must also document the pre-training input
reweighting, the widened DY/Z normalization, the absence of embedded/EWK Z
reduced samples, and the 11.467/fb luminosity reference for these reduced
tutorial samples.


# References {-}
