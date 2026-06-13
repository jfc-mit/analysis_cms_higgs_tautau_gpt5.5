# Phase 4c Observed Inference: Full Data

## Summary

The full-data result is rebuilt from the current local data and MC inputs using
two retained workspaces: the cut-based visible-mass baseline and the
three-category $D_NN$ classifier-score workspace. Historical optimized-score,
add-MET, and duplicate DNN aliases are not part of this output set.

## W and QCD Control Inputs

The full-data W+jets scale from the high-mT control region is
`0.9190 ± 0.0139`.
The VBF background control scale from the VBF-like top-btag non-signal region is
`0.3448 ± 0.0612`;
it is applied only to MC backgrounds in the VBF fit category. This addresses
the large VBF data/MC overprediction seen in the original observed templates
without changing the signal normalization or the boosted/zero-jet categories.
The same-sign QCD/fake estimate uses data minus non-QCD MC in the same-sign
low-mT region and a transfer factor measured in the lowest fitted-observable
bin. For the visible-mass baseline this factor is
`0.6163 ± 0.1944`.

![Full high-mT W control comparison. The figure shows non-W MC, nominal W MC,
the scaled control-region prediction, and full data in the control region.
The scale is derived outside the signal region and then propagated into the
observed workspaces.](figures/w_highmt_scale_full.pdf){#fig:p4c-wcr}

## Visible-Mass Baseline

| Category | Data | Background | QCD/fake | Data/background | Chi2/ndf | Max abs pull |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| vbf | 70 | 53.37 | 14.70 | 1.312 | 1.999 | 2.01 |
| boosted | 1138 | 1249.00 | 28.15 | 0.911 | 0.492 | 1.07 |
| zero_jet | 25920 | 26732.68 | 1742.04 | 0.970 | 0.126 | 0.55 |

The visible-mass baseline fit gives `mu_hat = 2.4740`,
an observed 95% CLs limit `mu < 5.9262`,
and a diagnostic `q0` value `Z = 1.3259`.
The median expected limit from the same workspace is `3.6919`.

![Visible-mass baseline validation in the VBF category. The plot compares
localized Run2012B/C TauPlusX data to the visible-mass baseline model after
the same-sign QCD/fake correction. This category remains statistically limited
but is included in the simultaneous baseline fit.](figures/observed_visible_vbf.pdf){#fig:p4c-visible-vbf}

![Visible-mass baseline validation in the boosted category. The plot compares
full data to the visible-mass baseline model with the W high-mT scale and
same-sign QCD/fake template. This category is used in the simultaneous baseline
fit.](figures/observed_visible_boosted.pdf){#fig:p4c-visible-boosted}

![Visible-mass baseline validation in the zero-jet category. The zero-jet
category contributes the largest data statistics to the visible-mass baseline
fit and anchors the cut-based result.](figures/observed_visible_zero_jet.pdf){#fig:p4c-visible-zero}

## D_NN Result

The retained NN result uses the XGBoost classifier score `mva_score_xgboost`
in the same VBF, boosted, and zero-jet categories with 20 uniform score bins.
It gives `mu_hat = 1.6160`, observed 95% CLs
`mu < 3.5769`, and median expected
limit `1.8069`.

![D_NN validation in the VBF category. The plot compares observed data to the
full MC expectation for the retained classifier-score workspace. The same
score definition and binning are used in all three categories.](figures/observed_nn_score_vbf.pdf){#fig:p4c-nn-vbf}

![D_NN validation in the boosted category. The plot compares observed data to
the retained classifier-score workspace in the boosted category. The lower
panel reports the data-to-prediction ratio.](figures/observed_nn_score_boosted.pdf){#fig:p4c-nn-boosted}

![D_NN validation in the zero-jet category. The plot compares observed data to
the retained classifier-score workspace in the statistically dominant zero-jet
category.](figures/observed_nn_score_zero_jet.pdf){#fig:p4c-nn-zero}

![Observed limit and significance summary. The figure shows the primary
visible-mass baseline and retained D_NN result on the same signal-strength
scale.](figures/observed_limit_significance_summary.pdf){#fig:p4c-result-summary}
