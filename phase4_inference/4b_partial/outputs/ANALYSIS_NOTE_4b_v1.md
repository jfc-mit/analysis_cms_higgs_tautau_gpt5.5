---
title: "CMS Open Data H to tau tau Search: Phase 4b 10% Data Validation"
author: "Analysis my_analysis"
date: "2026-06-02"
bibliography: references.bib
---

# Change Log {-}

**Phase 4b v1**

- Added deterministic 10% data validation using `(run * 1000003 + luminosityBlock * 9176 + event) % 10 == 0` on data rows only.
- Added the W high-mT control scale `0.8433 ± 0.0868`.
- Added fixed-model score-template validation plots for `vbf`, `boosted`, and `zero_jet`.
- The remaining 90% and full-data signal-region distributions remain blinded until Phase 4c approval.

# Phase 4b Partial Inference: 10% Data Validation

## Summary

Phase 4b validates the Phase 4a expected-primary score-template model on a
deterministic 10% collision-data subsample. The fitted observable and category
structure are unchanged from Phase 4a: `mva_score_hist_gradient_boosting` in
`vbf`, `boosted`, and `zero_jet` channels with the Phase 4a score-bin edges.
No model retuning, binning optimization, or replacement method was performed
using the 10% data.

The 10% mask applies only to data rows and is exactly:
`(run * 1000003 + luminosityBlock * 9176 + event) % 10 == 0`. MC templates use all selected MC rows but their official Open
Data weights are scaled from `11.467/fb` to `1.1467/fb`. The remaining 90% and
full-data signal-region distributions are not inspected in this artifact.

## W High-mT Control Scale

The W+jets high-`mT` control scale is derived from the masked 10% data as
`(N_data_CR - nonW_MC_CR) / W_MC_CR`. The control region contains
`400` 10% data events, `W_MC = 241.478`,
and `nonW_MC = 196.357`. The
applied scale factor is `0.8433 ± 0.0868`
with status `valid`. This factor is derived outside the signal
region and is not tuned to improve the score-template agreement.

## Score-Template Validation

| Category | Data | Background | Data/background | Chi2/ndf | Max abs pull |
| --- | ---: | ---: | ---: | ---: | ---: |
| vbf | 9 | 14.64 | 0.615 | 2.690 | 3.24 |
| boosted | 228 | 205.92 | 1.107 | 0.387 | 0.96 |
| zero_jet | 883 | 688.35 | 1.283 | 2.121 | 2.01 |

Combined over all score-template bins, data/background is
`1.232` with chi2/ndf
`1.732`. The score-modelling status is
`flagged` under the predeclared Phase 4b gate.

![10% score-template validation in the VBF category. The plot compares the
masked 10% data score distribution to MC normalized to 10% luminosity with
the W high-mT control scale applied. The ratio panel uses the same bins as the
Phase 4a pyhf workspace and does not drive any retuning.](figures/partial_score_vbf.pdf){#fig:p4b-score-vbf}

![10% score-template validation in the boosted category. The plot compares the
masked 10% data score distribution to MC normalized to 10% luminosity with
the W high-mT control scale applied. The ratio panel is a validation diagnostic
for the fixed Phase 4a model.](figures/partial_score_boosted.pdf){#fig:p4b-score-boosted}

![10% score-template validation in the zero-jet category. The plot compares
the masked 10% data score distribution to MC normalized to 10% luminosity with
the W high-mT control scale applied. This category dominates the event count
and therefore the combined ratio.](figures/partial_score_zero_jet.pdf){#fig:p4b-score-zero}

![W high-mT control comparison. The figure shows the observed 10% data control
count against the expected W and non-W MC components at 10% luminosity. The
derived scale is propagated to W+jets in the partial workspace as a control
region constraint.](figures/w_highmt_scale.pdf){#fig:p4b-wcr}

![Visible-mass validation summary. The figure provides a mass-shape cross-check
using the same masked 10% data and fixed categories. It is auxiliary to the
score-template validation and is not used to choose a new observable.](figures/partial_mvis_summary.pdf){#fig:p4b-mvis}

![Score-validation pull summary. The figure summarizes per-bin pulls across
the three score-template channels using the diagonal validation covariance.
It highlights the largest observed 10% deviations without changing the model.](figures/partial_pull_summary.pdf){#fig:p4b-pulls}

## Partial Diagnostic Fit

The partial pyhf workspace in `pyhf_workspace_partial.json` uses the masked
10% signal-region observations. The diagnostic fit status is
`evaluated`. If evaluated, its fitted signal strength
is reported only as a 10%-data validation number and not as a final result.

## Reproduction

Run:

| Command | Purpose |
| --- | --- |
| `pixi run phase4b-results` | Build partial JSON, NPZ, workspace, and markdown outputs. |
| `pixi run phase4b-plots` | Render Phase 4b figures and compile the minimal 4b note. |
| `pixi run phase4b-validate` | Validate blinding metadata, workspace construction, and figures. |
| `pixi run phase4b-all` | Run the full Phase 4b executor chain. |


# Phase 4a Context

The Phase 4a expected model is the simultaneous pyhf score-template fit in
`vbf`, `boosted`, and `zero_jet` channels using
`mva_score_hist_gradient_boosting` with bin edges `[0.0, 0.2, 0.35, 0.5, 1.0]`.
Phase 4a reported a median expected 95% CLs upper limit of
`4.199` and an
expected discovery diagnostic of `Z = 0.526`.

# Unblinding Checklist

| Gate item | Phase 4b status |
| --- | --- |
| Background model validated on 10% data | `flagged` |
| Systematics retained | luminosity 2.6%, DY 15%, tau/open-data 15%, W high-mT control |
| Expected result physically sensible | inherited from Phase 4a expected artifacts |
| Signal injection/closure | inherited from Phase 4a expected artifacts |
| 10% partial unblinding pathologies | see score-template and W high-mT validation summaries |
| Remaining data blinded | yes |

# References {-}
