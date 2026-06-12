# Phase 5 Physics Review: Final Analysis Note

Reviewer role: physics reviewer  
Artifact reviewed: `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.pdf` and markdown source  
Decision: **Do not approve on physics merits in the current form.**

## Scope Reviewed

I reviewed the final note source, the compiled-output figure set referenced by the note, the final observed-result provenance JSON files, the physics prompt, the Phase 1 strategy, and the applicable search-analysis convention. The final approach is a binned profile-likelihood search/template fit for a signal-strength parameter `mu`; extraction-measurement conventions are not the binding convention for this result.

The final note is internally honest that the optimized calibrated-score model fails its observed validation gate and that the visible-mass result is retained as the validated baseline. That is important. However, the final public-facing artifact still gives the failed optimized-score model excessive prominence as the "primary" statistical model and presents failed-model diagnostics alongside published-result comparisons in a way that is not approvable as a final physics result.

## Category A Findings

### A1. Failed optimized-score model is still presented as a primary result

The final note reports the optimized calibrated-score result as `mu = 38.3802 +7.0346 -6.1157`, observed 95% CLs limit `mu < 50.0000`, diagnostic `q0 Z = 12.4698`, combined data/background `0.6631`, and observed gate `fail`. The provenance file confirms the same model has:

- `mu_hat = 38.380184326872644`
- observed limit pegged at the scan maximum, `50.0`
- expected median limit `1.9735117795854344`
- observed limit / expected median limit about `25.3`
- validation flags `combined_ratio_failure = true` and `high_score_shape_failure = true`

This is not a valid signal extraction. It is a failed model diagnostic. A model with a boundary-like observed limit, a fitted signal strength around 38 times the SM, and a 12.5 sigma diagnostic excess in a reduced single-channel H to tau tau study must not be framed as the current primary statistical model or placed in headline result tables except clearly inside a failed-method section.

Required resolution: make the validated visible-mass baseline the sole quoted analysis result, or fix and revalidate the optimized-score model before using it as primary.

### A2. Data/MC disagreement in the optimized-score figures is visibly too large for an approved result

The optimized-score data/MC comparison plots show large shape and normalization failures:

- In `observed_primary_score_zero_jet`, the dominant low-score bin has data/prediction near `0.51`, while high-score bins rise to about `1.6-1.8`. The combined zero-jet data/background is `0.603` with `chi2/ndf = 4.025` and max pull `3.22`.
- In `observed_primary_score_vbf`, high-score bins are about `2.1-2.3` times prediction and the category data/background is `1.313`.
- In `observed_primary_score_boosted`, the highest score bin is about `1.84` times prediction and max pull is `2.63`.

These are exactly the regions where the classifier fit derives its signal strength. The note says the model fails, but the failed plots are still the main optimized-result evidence. This is a physics blocker for approval of the optimized-score result.

Required resolution: either remove the failed optimized-score model from the final result narrative, or redo the background/modeling strategy until the score templates pass observed validation.

### A3. Category signal-strength diagnostics indicate model breakdown, not category-level consistency

The category `mu` comparison gives:

- VBF: `mu_hat = 8.43`
- boosted: `mu_hat = 7.84`
- zero-jet: `mu_hat = 50.0`

The zero-jet fit is pinned to the scan boundary and dominates the event count. This is not a physically meaningful category comparison to the SM expectation of `mu = 1`; it indicates the discriminant is absorbing a mismodeled background shape or normalization. The figure also has visible text overlap in the CMS label, but the physics issue is the boundary fit and category inconsistency.

Required resolution: treat the category comparison as a failed-model diagnostic and keep it out of the result summary, or provide a corrected model whose category fits are statistically compatible.

### A4. Final comparison with published H to tau tau context uses a failed diagnostic value

The comparison table and significance plot include the optimized-score diagnostic significance `12.470` as "This analysis" context, even though the note states the optimized-score gate fails. A 12.5 sigma diagnostic in this reduced open-data single-channel setup is manifestly inconsistent with the known CMS H to tau tau context and with the model validation. Including it in a comparison table next to published CMS significances risks making a failed diagnostic look like a physics measurement.

Required resolution: comparisons to published H to tau tau results should use only the validated baseline result, with the failed optimized model confined to a methods-validation or failed-cross-check subsection.

## Category B Findings

### B1. The validated baseline is too weak to support anything beyond a diagnostic open-data limit

The retained visible-mass baseline is much more defensible than the optimized-score attempt:

- `mu = 0.4382 +4.9443 -0.4382`
- observed limit `mu < 10.7645`
- median expected limit `mu < 10.7375`
- combined data/background `0.9812`
- combined `chi2/ndf = 0.722`

This is acceptable as a low-sensitivity standalone current-data/current-MC study if the note presents it as such. It is not strong evidence for H to tau tau and it cannot support claims of observation, evidence, or detailed compatibility with the published multi-channel CMS results. The final conclusion mostly says this, but the result ordering and comparison figures dilute that message.

Recommended resolution: make the baseline limit and weak-sensitivity interpretation the first and only abstract/conclusion result.

### B2. Baseline validation still has localized tension that should be discussed

The baseline validation summary is globally acceptable, but the VBF category has a max pull of `2.66` and a bin data/prediction ratio of `0.285`; boosted bins also sit around `0.82` in two bins. These do not automatically invalidate the weak baseline limit, but they should be explicitly discussed because VBF is one of the analysis-motivated categories and the VBF background uses a control-region scale factor.

Recommended resolution: add a short baseline-only validation paragraph summarizing category-level pulls and why the residual VBF tension does not bias the quoted weak limit.

### B3. Statistical health documentation in the final note is incomplete

The final note cites pyhf/CLs and gives headline fit numbers, but it does not present enough nuisance-pull, impact-ranking, signal-injection, and goodness-of-fit information for a senior reader to judge the likelihood model from the note alone. The provenance files contain some useful validation numbers, but the final artifact should carry the decisive health checks.

Recommended resolution: add baseline-only tables for nuisance pulls/constraints, impacts, injection recovery, and goodness-of-fit. For failed optimized-score diagnostics, present the failed validation metrics separately and do not mix them with the final result.

## Category C Findings

### C1. Figure labels need cleanup for readability

Several final figures have overlapping CMS labels or crowded legends:

- `phase5_category_mu_comparison`
- `phase5_significance_comparison`
- `observed_primary_score_vbf`

This does not drive the physics decision, but it weakens the reader-facing artifact.

### C2. The final note is short for a final analysis note

The note is concise and readable, but it does not yet contain enough procedural detail for independent reproduction of every number. This is secondary to the physics blockers above.

## Figure Inspection Summary

Referenced figures inspected:

- `sample_event_count_file_size`: no physics issue; inventory plot only.
- `cutflow_summary`: monotonic selection behavior is visible.
- `w_highmt_scale_full`: high-mT W control arithmetic appears plausible from the shown component totals.
- `observed_primary_score_vbf`: high-score data excess over prediction by about a factor of two; failed-model evidence.
- `observed_primary_score_boosted`: high-score excess reaching roughly 1.8 times prediction.
- `observed_primary_score_zero_jet`: dominant low-score deficit and high-score excess; failed-model evidence.
- `phase5_category_mu_comparison`: category fitted `mu` values far from SM and zero-jet boundary behavior.
- `phase5_primary_vs_baseline_mu`: clearly shows the optimized-score attempt far from the baseline.
- `phase5_mu_limit_comparison`: mixes failed optimized-score diagnostics with published comparison context; should be baseline-only for final results.
- `phase5_significance_comparison`: presents failed optimized-score diagnostic significance as the analysis comparison value; should be removed or reframed.

## Method-Health Checklist

- Tautological comparison: no direct evidence that the final validated baseline result is purely tautological, but the optimized-score validation fails independently.
- Circular calibration: no evidence that the quoted baseline `mu` is calibrated by fixing it to a known result.
- Suspiciously good agreement: the baseline zero-jet `chi2/ndf = 0.113` is very low, but the overall baseline result is low-sensitivity and the VBF/boosted categories are not trivially perfect. This is a warning, not a standalone blocker.
- Dominant systematic: no single systematic impact ranking is presented in the final note, so this cannot be fully assessed from the public artifact.
- Failed validation gates: yes, the optimized-score model explicitly fails. This is the main approval blocker because the final note still foregrounds it.
- Published-context pull: the optimized-score `mu` and diagnostic significance are grossly inconsistent with H to tau tau context and must not be treated as physics results. The baseline weak limit is consistent with low sensitivity.

## Approval Decision

I would approve the standalone analysis only after the final note is restructured so that the validated visible-mass baseline is the sole final result, with the optimized-score model documented only as a failed optimization study. In the current artifact, the failed optimized-score model is too prominent and its failed diagnostics are mixed with result comparisons. Therefore my Phase 5 physics-review decision is **FAIL / do not approve** until the Category A items are resolved.
