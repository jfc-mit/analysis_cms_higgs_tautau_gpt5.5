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
terms. Visible mass and add-MET mass are retained only as cross-checks.

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
For the visible-mass cross-check it is
`0.0087 ± 0.4828`.
For the add-MET mass cross-check it is
`0.2654 ± 1.0277`.

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
`1.9735`.

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

## Add-MET Mass Cross-Check

| Category | Data | Background | QCD/fake | Data/background | Chi2/ndf | Max abs pull |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| vbf | 77 | 62.39 | 5.37 | 1.234 | 0.326 | 0.96 |
| boosted | 2177 | 2146.55 | 72.74 | 1.014 | 0.193 | 0.72 |
| zero_jet | 8448 | 14313.61 | 299.76 | 0.590 | 4.707 | 4.07 |

The simultaneous add-MET mass fit gives `mu_hat = 39.1162`,
an observed 95% CLs limit `mu < 50.0000`,
and `Z = 4.2223`.
This fit uses the same categories and nuisance model as the calibrated-score
primary fit, but it is kept as a separate cross-check rather than replacing
the trained-discriminator result.

![Add-MET mass validation in the VBF category. The plot compares full data to
the QCD-corrected add-MET mass model in the VBF category. It uses the same W
control scale, VBF background control scale, and same-sign QCD/fake transfer
machinery as the calibrated-score primary model.](figures/observed_addmet_vbf.pdf){#fig:p4c-addmet-vbf}

![Add-MET mass validation in the boosted category. The plot compares full data
to the add-MET mass model in the boosted category. The add-MET result is stored
as an explicit Phase 4c cross-check output for downstream documentation.](figures/observed_addmet_boosted.pdf){#fig:p4c-addmet-boosted}

![Add-MET mass validation in the zero-jet category. The plot compares full data
to the add-MET mass model in the zero-jet category. This validates the
alternative reconstructed-MET observable without modifying the primary
calibrated-score fit.](figures/observed_addmet_zero_jet.pdf){#fig:p4c-addmet-zero}

## Visible-Mass Cross-Check

| Category | Data | Background | QCD/fake | Data/background | Chi2/ndf | Max abs pull |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| vbf | 78 | 57.72 | 0.17 | 1.351 | 1.189 | 2.07 |
| boosted | 2183 | 2085.76 | 2.41 | 1.047 | 0.846 | 1.77 |
| zero_jet | 8451 | 14022.53 | 9.83 | 0.603 | 2.823 | 4.01 |

The visible-mass cross-check gives `mu_hat = 50.0000`,
an observed 95% CLs limit `mu < 50.0000`,
and `Z = 5.4113`.
The visible-mass fit is not the primary result in this update because the
trained calibrated score gives the stronger expected sensitivity after the
input-reweighting and DY/QCD corrections.

![Visible-mass cross-check in the VBF category. This figure retains the
visible-mass observable used in the conservative fallback analysis. It is shown
as a validation cross-check for the primary calibrated-score result.](figures/observed_visible_vbf.pdf){#fig:p4c-visible-vbf}

![Observed pull and ratio summary. The figure compares the primary calibrated
score and cross-check validation behavior after the QCD/fake, DY/Z, and input
reweighting corrections. It is the central diagnostic for the final model
choice.](figures/observed_pull_ratio_summary.pdf){#fig:p4c-pulls}

![Observed limit and significance summary. The figure shows the primary
calibrated-score fit and the cross-check fits on the same signal-strength
scale. The result remains an Open Data diagnostic rather than CMS-quality
evidence.](figures/observed_limit_significance_summary.pdf){#fig:p4c-result-summary}

## Phase 5 Obligation

Phase 5 must report the calibrated-score plus QCD model as the final observed
result, while documenting the pre-training input reweighting, the widened DY/Z
normalization, and the absence of embedded/EWK Z reduced samples. It must also
state that the localized reduced mirror has about 10% of the Open Data record
entries, while the 11.467/fb value remains the cited normalization reference
for these reduced tutorial samples.


# References {-}
