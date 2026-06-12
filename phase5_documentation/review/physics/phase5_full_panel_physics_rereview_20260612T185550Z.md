# Phase 5 Physics Re-review: Full-Panel Iterate

Reviewer role: physics reviewer  
Artifact reviewed: `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.{pdf,md}`, `PAPER_PRL_v1.{pdf,md}`, final-result JSON artifacts, category diagnostic JSON, prior arbiter/fixer records, and the figure set referenced by the final documents.  
Decision: **PASS on the prior physics blockers.**

## Scope and Bottom Line

The full-panel iterate resolves the previous physics blockers. The validated visible-mass baseline is now the only final result in the AN abstract, PRL abstract, result tables, conclusion/interpretation text, final limit figure, and machine-readable final-result role metadata. The optimized classifier appears only as a rejected diagnostic study, with its failed validation gate, boundary-like limit, large fitted signal strength, and category breakdown explicitly stated.

I would approve the current physics framing as a reduced Open Data limit: `mu = 0.4382 +4.9443 -0.4382`, observed 95% CLs `mu < 10.7645`, median expected 95% CLs `mu < 10.7375`. The documents correctly state that this has no Standard Model resolving power and is not evidence or observation of `H to tau tau`.

## Prior Blocker Resolution

### Resolved: visible-mass baseline is the sole final result

The AN abstract and final-result section identify `visible_mass_qcd_primary` as the only final-result model. The PRL draft also leads with the visible-mass template fit and quotes only the baseline result. The final-result plot `phase5_baseline_limit_summary` contains no optimized-score result.

The JSON provenance is also corrected at the decisive role level:

- `observed_results.json` has `final_result_model = visible_mass_qcd_primary` and `primary_model = visible_mass_qcd_primary`.
- `observed_results.json` `final_result.role` is `final_result`.
- `baseline_previous_result.json` now labels the baseline as `Validated visible-mass final result`, with `role = final_result`.

### Resolved: optimized classifier is only a rejected diagnostic

The AN section `Rejected Classifier Diagnostic` states that the classifier is not a final result and reports the pathological values only to explain rejection: `mu = 38.3802 +7.0346 -6.1157`, observed limit `mu < 50.0000`, `Z = 12.4698`, combined data/background `0.6631`, and validation gate `fail`.

The category comparison JSON has `role = diagnostic_failed_validation` and its interpretation says the per-category fits demonstrate why the optimized classifier is not used as the final result. The category plot is visually labeled as a rejected classifier fit rather than a category-consistency result.

### Resolved: published comparisons use the validated baseline

The published-context comparison table now uses the baseline visible-mass result for "This analysis". The text explicitly says the comparison is interpretive, not a validation target, and that the small pulls against CMS/ATLAS+CMS values reflect low resolving power rather than precision agreement. The failed classifier `Z = 12.47` no longer appears as a published-context comparison value.

### Resolved: baseline validation and limitations are honestly framed

The baseline validation section quotes the combined pass metrics and the localized VBF tension:

- combined data/background `0.9812`
- combined chi2/ndf `0.7224`
- VBF max pull `2.66`
- VBF bin ratio reaching `0.285`
- zero-jet chi2/ndf `0.113`, explicitly noted as possible overcoverage from conservative diagonal validation uncertainties

This is the right framing. The VBF mismatch is visible and nontrivial, but it is disclosed and the final interpretation is a weak upper limit, not evidence.

## Figure Inspection

I inspected all 31 figures referenced by the AN/PRL via their generated PNG counterparts and the key final/rejected figures at higher resolution.

Final baseline data/MC figures:

- `phase5_baseline_visible_vbf`: visible localized VBF deficit in the 80-100 GeV bin; documented numerically in the AN.
- `phase5_baseline_visible_boosted`: no bulk factor-of-two disagreement; residual ratios are consistent with the quoted weak-limit framing.
- `phase5_baseline_visible_zero_jet`: ratio panel is centered near one and supports the global validation pass.
- `phase5_baseline_validation_summary`: correctly highlights VBF as the largest residual.
- `phase5_baseline_limit_summary`: baseline-only final-result plot.

Rejected-model figures:

- `phase5_rejected_score_diagnostics`: clearly diagnostic and visually separate from final result.
- `phase5_category_mu_comparison`: shows the rejected classifier category fits and labels them as rejected, not as physics evidence.

Appendix/control figures show expected reduced-sample modeling limitations in object, MET, VBF-topology, and MVA-input distributions. They are not used as final result claims and are consistent with the document's explanation for rejecting aggressive observables.

## Statistical and Method-Health Check

The final extraction method is appropriate for the limited analysis scope: a simultaneous binned pyhf/HistFactory visible-mass template fit with CLs limits. The result is weak but interpretable.

The validation chi2 values use a diagonal validation covariance rather than a full observed-data covariance. The note states this explicitly and does not overclaim precision. The zero-jet chi2/ndf is low, but not identically zero, and the note flags possible overcoverage. No suspiciously perfect global result is presented as proof of correctness.

No evidence was found for circular normalization to the final answer. The note states that MC normalization uses Open Data record event counts, not selected data yields. The published comparisons are no longer tautological or inflated by the failed classifier.

## Findings

No Category A or Category B physics blockers remain for the prior issues under re-review.

### Category C: clean up one legacy metadata field

`observed_results.json` still contains a top-level `model` block whose `selection_role` is `primary_candidate` and whose status says the classifier was an expected-primary candidate pending Phase 4b validation. The decisive fields now correctly set `final_result_model`, `primary_model`, `final_result`, and `model_roles`, so this is not a physics blocker. For machine-readability, a future cleanup should either rename that block to `phase3_expected_candidate` or move it under diagnostics/history so no downstream consumer mistakes it for the final model declaration.

## Approval Decision

**PASS.** The full-panel iterate resolves the prior physics blockers. The final artifacts now present a coherent baseline-only low-sensitivity Open Data limit, honestly retain the classifier only as a failed diagnostic, and avoid using failed-model quantities in published-result comparisons.
