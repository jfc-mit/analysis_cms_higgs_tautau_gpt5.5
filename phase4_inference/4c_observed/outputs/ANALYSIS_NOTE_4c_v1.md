---
title: "CMS Open Data H to tau tau Search: Phase 4c Full Observed Results"
author: "Analysis my_analysis"
date: "2026-06-02"
bibliography: references.bib
---

# Change Log {-}

**Phase 4c v1**

- Applied the frozen Phase 4a/4b score-template method to full Run2012B/C TauPlusX data.
- Derived the full high-mT W+jets scale `0.8528 ± 0.0370`.
- Preserved the Phase 4b score-modeling warning in the observed result.
- Recorded that the 4b human gate was auto-passed by explicit user instruction.

# Phase 4c Observed Inference: Full Data

## Summary

Phase 4c applies the frozen Phase 4a/4b score-template model to all available
Run2012B/C TauPlusX data in `phase3_selection/outputs/sensitivity_selected_events.npz`.
No full-data retuning of the selection, classifier, categories, score bins, or
statistical model was performed. The Phase 4b human gate is recorded as
auto-passed by explicit user instruction.

The fitted observable remains `mva_score_hist_gradient_boosting` in the
`vbf`, `boosted`, and `zero_jet` channels with bin edges `[0.0, 0.2, 0.35,
0.5, 1.0]`. The Phase 4b score-template warning is not removed: the 10%
combined data/MC ratio was `1.232`,
chi2/ndf was `1.732`, and the status was
`flagged` with flags `{'category_chi2_failure': False, 'combined_chi2_failure': False, 'combined_ratio_failure': True}`.

## W High-mT Control Scale

The full-data W+jets scale is derived only from the high-`mT` control region
using `(N_data_CR - nonW_MC_CR) / W_MC_CR`. The full control region contains
`4023` data events, `W_MC = 2414.781`,
and `nonW_MC = 1963.570`. The
applied full-data scale is `0.8528 ± 0.0370`
with status `valid`. The 10% Phase 4b scale was
`0.8433 ± 0.0868`.

![Full high-mT W control comparison. The figure shows non-W MC, nominal W MC,
the scaled control-region prediction, and full data in the control region.
The scale is derived outside the signal region and then propagated into the
observed workspace.](figures/w_highmt_scale_full.pdf){#fig:p4c-wcr}

## Full-Data Score-Template Validation

| Category | Data | Background | Data/background | Chi2/ndf | Max abs pull |
| --- | ---: | ---: | ---: | ---: | ---: |
| vbf | 79 | 146.67 | 0.539 | 4.310 | 3.34 |
| boosted | 2213 | 2062.80 | 1.073 | 1.687 | 2.14 |
| zero_jet | 8466 | 6894.80 | 1.228 | 3.656 | 2.47 |

Combined over all score-template bins, data/background is
`1.182` with chi2/ndf
`3.218`. The full-data score-modelling status is
`flagged` under the same diagnostic criteria as
Phase 4b.

![Full-data score-template validation in the VBF category. The plot compares
all available Run2012B/C TauPlusX data to the frozen MC template model with
the full high-mT W scale applied. The ratio panel is a diagnostic and does not
drive any post-unblinding retuning.](figures/observed_score_vbf.pdf){#fig:p4c-score-vbf}

![Full-data score-template validation in the boosted category. The plot
compares full data to the frozen Phase 4a/4b score-template model. This is an
observed-result diagnostic with the Phase 4b score-modeling warning still
carried forward.](figures/observed_score_boosted.pdf){#fig:p4c-score-boosted}

![Full-data score-template validation in the zero-jet category. The zero-jet
channel dominates the full observed event count and therefore the combined
data/MC ratio. The model was not retuned after unblinding.](figures/observed_score_zero_jet.pdf){#fig:p4c-score-zero}

![Observed pull and ratio summary. The figure summarizes per-category
data/background ratios and maximum score-bin pulls for full data. It compares
the observed validation behavior to the Phase 4b 10% validation and Phase 4a
expected reference.](figures/observed_pull_ratio_summary.pdf){#fig:p4c-pulls}

## Observed Fit Result

The observed pyhf workspace is written to `pyhf_workspace_observed.json`.
Fit status is `evaluated`. The fitted signal strength is
`7.6642`. The observed 95% CLs upper limit
status is `evaluated` and the observed limit is
`13.3226` if evaluated. The observed
discovery diagnostic status is `evaluated`;
its `q0` significance is `Z = 2.9776` if
evaluated.

![Observed limit and significance summary. The figure shows the full-data
fitted signal strength, observed upper limit, Phase 4a expected median limit,
and observed discovery diagnostic where available. These numbers are a
simplified open-data result and must be interpreted with the documented
score-modeling caveat.](figures/observed_limit_significance_summary.pdf){#fig:p4c-result-summary}

![Comparison to Phase 4a expected and Phase 4b validation. The figure compares
the Phase 4a expected limit, Phase 4b diagnostic fit, full-data observed fit,
and the 10% versus full W high-mT scale factors. It is intended to make the
unblinding evolution explicit for Phase 5.](figures/comparison_to_4a_4b.pdf){#fig:p4c-comparison}

## Phase 5 Obligation

The Phase 5 paper must state that the score-modeling validation was flagged in
Phase 4b and remains a limitation of the simplified open-data result. The
result should not claim a clean CMS-quality score-template model, nor should
it describe the W+jets scale as signal-region tuned.


# References {-}
