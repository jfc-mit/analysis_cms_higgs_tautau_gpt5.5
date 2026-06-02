# Phase 4c Observed Inference: Audit-Corrected Full Data

## Summary

Phase 4c has been updated after the Phase 5 audit of the large expected versus
observed discrepancy. The audit found no evidence that Phase 4a and Phase 4c
used different categories, score bins, or pyhf definitions. The problem was
physics modelling: the score-template fit omitted a reducible QCD/fake-tau
component and the high-score shape validation remained flagged.

The primary observed result is therefore changed to a conservative visible-mass
fit in the same VBF, boosted, and zero-jet categories, with a same-sign
data-driven QCD/fake template. The requested categorized HGB-score fit is still
computed, but it is retained as a diagnostic rather than CMS-quality evidence.

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
bin. For the primary visible-mass model this factor is
`0.9958 ± 0.1201`.
For the score diagnostic it is
`0.8173 ± 0.0853`.
For the add-MET mass cross-check it is
`1.1612 ± 0.2466`.

![Full high-mT W control comparison. The figure shows non-W MC, nominal W MC,
the scaled control-region prediction, and full data in the control region.
The scale is derived outside the signal region and then propagated into the
observed workspaces.](figures/w_highmt_scale_full.pdf){#fig:p4c-wcr}

## Primary Visible-Mass Result

| Category | Data | Background | QCD/fake | Data/background | Chi2/ndf | Max abs pull |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| vbf | 78 | 96.28 | 17.75 | 0.810 | 1.449 | 2.66 |
| boosted | 2183 | 2364.39 | 325.58 | 0.923 | 0.605 | 1.25 |
| zero_jet | 8451 | 8456.81 | 1569.65 | 0.999 | 0.113 | 0.57 |

The primary visible-mass fit gives `mu_hat = 0.4382`,
an observed 95% CLs limit `mu < 10.7645`,
and a diagnostic `q0` value `Z = 0.0949`.
The median expected limit from the same corrected workspace is
`10.7375`.

![Primary visible-mass validation in the VBF category. The plot compares all
available localized Run2012B/C TauPlusX data to the QCD-corrected visible-mass
model. The VBF data deficit remains a limitation, but the zero-jet normalization
pathology from the score-only model is removed.](figures/observed_mvis_vbf.pdf){#fig:p4c-mvis-vbf}

![Primary visible-mass validation in the boosted category. The plot compares
full data to the visible-mass model with the W high-mT scale and same-sign QCD
template. This category is used in the final conservative observed fit.](figures/observed_mvis_boosted.pdf){#fig:p4c-mvis-boosted}

![Primary visible-mass validation in the zero-jet category. The zero-jet
normalization is stabilized by the same-sign QCD/fake estimate, making this
model more defensible than the unvalidated score template for final observed
reporting.](figures/observed_mvis_zero_jet.pdf){#fig:p4c-mvis-zero}

## Add-MET Mass Cross-Check

| Category | Data | Background | QCD/fake | Data/background | Chi2/ndf | Max abs pull |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| vbf | 77 | 99.03 | 21.47 | 0.778 | 0.632 | 1.34 |
| boosted | 2177 | 2403.36 | 379.33 | 0.906 | 0.584 | 1.02 |
| zero_jet | 8448 | 8722.42 | 1835.70 | 0.969 | 0.120 | 0.44 |

The simultaneous add-MET mass fit gives `mu_hat = 0.0000`,
an observed 95% CLs limit `mu < 13.2940`,
and `Z = 0.0006`.
This fit uses the same categories and nuisance model as the visible-mass
primary fit, but it is kept as a separate cross-check rather than replacing
the pre-existing primary result.

![Add-MET mass validation in the VBF category. The plot compares full data to
the QCD-corrected add-MET mass model in the VBF category. It uses the same W
control scale, VBF background control scale, and same-sign QCD/fake transfer
machinery as the visible-mass primary model.](figures/observed_addmet_vbf.pdf){#fig:p4c-addmet-vbf}

![Add-MET mass validation in the boosted category. The plot compares full data
to the add-MET mass model in the boosted category. The add-MET result is stored
as an explicit Phase 4c cross-check output for downstream documentation.](figures/observed_addmet_boosted.pdf){#fig:p4c-addmet-boosted}

![Add-MET mass validation in the zero-jet category. The plot compares full data
to the add-MET mass model in the zero-jet category. This validates the
alternative reconstructed-MET observable without modifying the primary
visible-mass fit.](figures/observed_addmet_zero_jet.pdf){#fig:p4c-addmet-zero}

## Score-Template Diagnostic

| Category | Data | Background | QCD/fake | Data/background | Chi2/ndf | Max abs pull |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| vbf | 79 | 94.14 | 12.43 | 0.839 | 1.334 | 1.66 |
| boosted | 2213 | 2331.71 | 268.90 | 0.949 | 0.676 | 1.30 |
| zero_jet | 8466 | 8187.20 | 1292.40 | 1.034 | 1.515 | 1.78 |

The categorized HGB-score fit gives `mu_hat = 9.3518`,
an observed 95% CLs limit `mu < 14.8373`,
and `Z = 3.9416`.
The score fit is diagnostic only; it is not promoted to evidence because the high-score bins remain shape-flagged
after the QCD normalization correction.

![Score-template diagnostic in the VBF category. This figure retains the
requested categorized score observable but labels it as a diagnostic because
the validation status remains flagged.](figures/observed_score_vbf.pdf){#fig:p4c-score-vbf}

![Observed pull and ratio summary. The figure compares primary visible-mass and
score-template validation behavior after the QCD/fake audit correction. It is
the central diagnostic for why the visible-mass result is primary and the score
fit is diagnostic only.](figures/observed_pull_ratio_summary.pdf){#fig:p4c-pulls}

![Observed limit and significance summary. The figure shows the primary
visible-mass fit and the score-template diagnostic on the same signal-strength
scale. The score result is flagged and not CMS-quality evidence.](figures/observed_limit_significance_summary.pdf){#fig:p4c-result-summary}

## Phase 5 Obligation

Phase 5 must report the visible-mass plus QCD model as the conservative final
observed result, and must show the categorized BDT-score fit only as a flagged
diagnostic. It must also state that the localized reduced mirror has about 10%
of the Open Data record entries, while the 11.467/fb value remains the cited
normalization reference for these reduced tutorial samples.
