# Phase 5 Critical Review

Reviewer: critical reviewer  
Phase: 5 final documentation  
Verdict: **FAIL**

## Scope Reviewed

Final artifacts reviewed:

- `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md`
- `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.tex`
- `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.pdf`
- `phase5_documentation/outputs/PAPER_PRL_v1.md`
- `phase5_documentation/outputs/PAPER_PRL_v1.tex`
- `phase5_documentation/outputs/PAPER_PRL_v1.pdf`
- `phase5_documentation/outputs/references.bib`

Upstream artifacts and result JSONs reviewed:

- `phase1_strategy/outputs/STRATEGY.md`
- `phase2_exploration/outputs/EXPLORATION.md`
- `phase3_selection/outputs/SELECTION.md`
- `phase4_inference/4a_expected/outputs/INFERENCE_EXPECTED.md`
- `phase4_inference/4b_partial/outputs/INFERENCE_PARTIAL.md`
- `phase4_inference/4c_observed/outputs/INFERENCE_OBSERVED.md`
- `phase4_inference/4c_observed/outputs/observed_results.json`
- `phase4_inference/4c_observed/outputs/comparison_to_4a_4b.json`
- `phase4_inference/4c_observed/outputs/score_observed_yields.json`
- `phase4_inference/4c_observed/outputs/baseline_previous_result.json`
- `phase5_documentation/outputs/category_mu_comparison.json`
- `experiment_log.md`

## Applicable Convention

`conventions/search.md` applies. The Phase 1 strategy explicitly states that the primary technique is a search/template-fit analysis and that `conventions/search.md` is binding (`phase1_strategy/outputs/STRATEGY.md:16-17`, `phase1_strategy/outputs/STRATEGY.md:59-68`). `conventions/extraction.md` does not apply because the analysis is not a closed-form double-tag or counting extraction (`phase1_strategy/outputs/STRATEGY.md:68`).

## Category A Findings

### A1. The final AN is far below the Phase 5 standalone-documentation standard

The final note is not a reproducible final analysis note. It has 197 markdown lines, 10 figure references, and zero displayed equations. The Phase 5 note specification requires a complete standalone AN with event selection, corrections/statistical method, systematic uncertainty subsections, validation documentation, results, quantitative comparisons, known limitations, appendices, and a reproduction contract.

Evidence:

- `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md` has only nine top-level headings: Abstract, Change Log, Data and Simulation, Event Selection, QCD/W corrections, Optimized Score Result, Comparison, Conclusion, References (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:8`, `:19`, `:26`, `:46`, `:71`, `:106`, `:155`, `:189`, `:197`).
- The note contains zero displayed equations by markdown scan, while the Phase 5 requirements call for at least observable, likelihood/statistical model, systematic propagation, and correction/control equations.
- The note has no dedicated systematic-uncertainties section. The only systematic-like prose is a short model sentence listing nuisance classes (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:108-112`), not per-source physical origin, evaluation method, numerical impact, and interpretation.
- There is no validation summary table covering closure, signal injection, nuisance pulls/constraints, impact ranking, goodness of fit, and look-elsewhere applicability. The result table reports only a few global quantities (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:116-123`).
- There is no reproduction contract or execution DAG in the final AN.

This blocks Phase 5 acceptance.

### A2. The optimized-score model fails its own validation but is still presented as the primary/final model

The final AN and PRL present the optimized calibrated-score result prominently, including `mu = 38.3802 +7.0346 -6.1157`, `Z = 12.4698`, and `mu < 50.0000`, while simultaneously stating that the observed validation gate fails.

Evidence:

- The abstract states the optimized score gives `mu = 38.3802 +7.0346 -6.1157` and `mu < 50.0000`, then says it fails the observed validation gate (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:13-17`).
- The final result section labels the binned pyhf model as "primary" and reports the failed model's result (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:106-123`).
- Machine-readable output identifies the final primary model as `calibrated_score_qcd_primary` (`phase4_inference/4c_observed/outputs/observed_results.json:1927`).
- The same JSON gives `mu_hat = 38.380184326872644`, `z_value = 12.469838725635482`, and `observed_limit = 50.0` (`phase4_inference/4c_observed/outputs/observed_results.json:1196-1211`, `:1760-1775`).
- The validation summary for the primary model is `score_modeling_status: flagged`, with `combined_ratio_failure: true` and `high_score_shape_failure: true` (`phase4_inference/4c_observed/outputs/observed_results.json:2532-2550`, `:2658-2676`).
- The observed limit is 25.34 times the median expected limit (`phase4_inference/4c_observed/outputs/comparison_to_4a_4b.json:29-32`).

A failed validation gate cannot be converted into a final primary result by labeling it diagnostic. The final public-facing result must either use a validated current model or state that no validated optimized result is available.

### A3. Figure physics check: the primary score plots show large data/MC mismodelling

The data/MC comparisons for the primary score model show normalization and shape failures large enough to block publication.

Evidence:

- `score_observed_yields.json` reports zero-jet data/background = 0.6027 (`phase4_inference/4c_observed/outputs/score_observed_yields.json:1138`), while the AN's table rounds the same zero-jet category to 0.603 (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:64`).
- The primary validation JSON reports zero-jet `chi2_per_ndf = 4.025381534219614` and data/background = 0.6026857914638979 (`phase4_inference/4c_observed/outputs/observed_results.json:2624-2626`).
- The combined primary validation reports data/background = 0.6631396081219646 with ratio statistical uncertainty = 0.006393507785069643, so the global normalization deficit is far beyond a statistical fluctuation (`phase4_inference/4c_observed/outputs/observed_results.json:2658-2662`).
- Visual inspection of `phase5_documentation/outputs/figures/observed_primary_score_zero_jet.png` shows the first score bin overpredicted by roughly a factor of two and high-score bins underpredicted. `observed_primary_score_boosted.png` and `observed_primary_score_vbf.png` show high-score data/prediction ratios near or above 2.

This is a regression trigger under the data/MC-disagreement rule and independently blocks the optimized-score result.

### A4. Binding strategy decision [D9] is violated

Phase 1 made the alternative-observable gate binding: an NN/classifier observable may replace visible mass only if it passes input modelling, closure/GoF, signal injection, and expected-sensitivity criteria.

Evidence:

- Phase 1 decision [D9] states that an NN or add-MET observable may become primary only if it passes modelling/injection gates and improves expected sensitivity by at least 10% (`phase1_strategy/outputs/STRATEGY.md:140-143`).
- The strategy explicitly says an NN approach that wins expected sensitivity but fails MVA input modelling may not be promoted to the observed-data primary result (`phase1_strategy/outputs/STRATEGY.md:295-299`).
- Phase 3 found that 13 of 16 candidate classifier inputs had data/background-MC `chi2/ndf > 5`; the classifier was formally downscoped rather than promoted (`phase3_selection/outputs/SELECTION.md:196-198`).
- Phase 4b score modelling was still `flagged` with combined data/background = 1.232 and `combined_ratio_failure: true` (`phase4_inference/4c_observed/outputs/comparison_to_4a_4b.json:17-24`).
- Phase 4c/5 nevertheless set `primary_model` to `calibrated_score_qcd_primary` (`phase4_inference/4c_observed/outputs/observed_results.json:1927`) and the AN describes the score model as primary (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:106-123`).

This is a decision-label traceability failure and a Category A process/physics issue.

### A5. The "validated baseline" is a historical/frozen result, not a current standalone model result

The final AN uses a "frozen previous visible-mass result" as the validated baseline, while the current observed-results JSON contains current visible-mass and add-MET cross-checks that are flagged or boundary-like. A standalone current-data/current-MC study cannot make a historical frozen result the final validated answer without regenerating and documenting it as a current model.

Evidence:

- The AN calls the baseline "Frozen" and "previous" (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:123`, `:151`, `:193-194`).
- The machine-readable baseline object says its source is frozen from a previous observed output (`phase4_inference/4c_observed/outputs/observed_results.json:743-744`).
- The current visible-mass observed fit in `observed_results.json` has `mu_hat = 50.0`, `observed_limit = 50.0`, and `score_modeling_status: flagged` (`phase4_inference/4c_observed/outputs/observed_results.json:2823-2834`, `:2994`).
- The frozen baseline has `mu_hat = 0.43822864200217504`, observed limit 10.764467444563975, and validation status `pass` (`phase4_inference/4c_observed/outputs/baseline_previous_result.json:11-22`, `:202`).

The final note must present a current validated model, with current inputs and outputs, or state that the current model set does not produce a validated result.

### A6. The reported optimized result grossly deviates from well-measured H to tau tau signal-strength references without a calibration investigation

The optimized score gives a signal strength near 38, while the published H to tau tau signal-strength references quoted in the AN are near 1. This exceeds the 30% gross-deviation trigger by orders of magnitude.

Evidence:

- This analysis's optimized score row reports `mu = 38.380 +7.035 -6.116` and `Z = 12.470` (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:171`).
- The same table quotes CMS Run 1 `mu = 0.78 ± 0.27`, CMS 2018 `mu = 1.09`, and ATLAS+CMS global `mu = 1.09 ± 0.11` (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:173-176`).
- The note says the score result fails validation, but it does not provide a quantitative calibration-first investigation explaining how a 38x SM signal-strength fit arises from the reduced current data/current MC model.

The optimized result must be removed from result status or backed by a documented calibration investigation. As written, it is not a credible physics result.

### A7. Systematic uncertainty documentation and propagation are incomplete

The search-convention systematic program is not documented at Phase 5 depth. The final note does not provide per-source subsections, source-by-source impacts, nuisance pulls/constraints, an impact ranking, or a systematic breakdown figure.

Evidence:

- Phase 1 committed to signal cross-section/acceptance/shape, luminosity, DY/Z, W, QCD, top, diboson/single-top, detector/object calibration, MC statistics, PDF/scale, and modelling uncertainties (`phase1_strategy/outputs/STRATEGY.md:377-399`).
- The final note only lists nuisance classes in one sentence (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:108-112`).
- The QCD same-sign transfer factor for the primary score model is `0.02036989339180365 ± 0.25325546570729784`, a relative uncertainty of 12.43, but the AN only quotes the central value and uncertainty in prose without a propagated impact table or figure (`phase4_inference/4c_observed/outputs/score_observed_yields.json:175`; `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:87-90`).
- The final note has no nuisance pull table, no impact ranking, and no explicit treatment of low-stat/asymptotic validity for the boundary limit at `mu < 50`.

This is Category A because the reader cannot reproduce or assess the uncertainty model from the AN.

### A8. The PRL-style paper draft is not a paper draft

`PAPER_PRL_v1.md` is 13 lines long, has no figures, no citations, no equations, no abstract, no method section, and no results table beyond prose snippets.

Evidence:

- `phase5_documentation/outputs/PAPER_PRL_v1.md:1-13` is the entire markdown draft.
- It contains zero figure references and zero citation keys by markdown scan.
- It reports the failed optimized score and the historical baseline, but does not document the statistical model, samples, systematics, validation, or comparisons in a paper-readable form (`phase5_documentation/outputs/PAPER_PRL_v1.md:3-13`).

This artifact cannot pass Phase 5 review.

## Category B Findings

### B1. Public-facing artifacts contain internal process language instead of standalone analysis language

The final AN and PRL repeatedly refer to "Phase 5 v3", "previous", "frozen", and "audit-corrected". These terms make the artifacts read like a process log rather than a standalone current analysis.

Evidence:

- `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:21-23` says "Phase 5 v3" and "previous visible-mass result as a frozen baseline".
- `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:123` labels the baseline as "Frozen" and "previous primary result before this update".
- `phase5_documentation/outputs/PAPER_PRL_v1.md:3` says "audit-corrected".
- `phase5_documentation/outputs/PAPER_PRL_v1.md:11-13` says "previous" and "frozen baseline".

The final documents should describe the current model choices and current results, not the artifact history.

### B2. Published comparisons are not quantitative enough

The final comparison table quotes published values, but the AN does not provide pulls, chi2 values, or a clear statement of resolving power for each reported result.

Evidence:

- The comparison section lists CMS/ATLAS+CMS/PDG context (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:155-177`), but no row gives a pull or chi2.
- The final comparison figures are described as not directly equivalent to CMS publication measurements (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:180-187`), but the text does not quantify the remaining comparison.
- The conclusion says the result is a diagnostic, but does not state what signal-strength deviations the validated result can resolve at 2 sigma (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:189-195`).

## Category C Suggestions

No Category C-only suggestions are material until the Category A/B issues above are resolved.

## Numerical Self-Consistency Checks

Spot checks against machine-readable outputs:

- Optimized score `mu_hat`: AN reports 38.3802 (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:118`); JSON reports 38.380184326872644 (`phase4_inference/4c_observed/outputs/observed_results.json:1764`) — consistent after rounding.
- Optimized score observed limit: AN reports 50.0000 (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:117`); JSON reports 50.0 (`phase4_inference/4c_observed/outputs/observed_results.json:1775`) — consistent, but boundary-like.
- Optimized score `Z`: AN reports 12.4698 (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:119`); JSON reports 12.469838725635482 (`phase4_inference/4c_observed/outputs/observed_results.json:1760-1761`) — consistent after rounding.
- Primary combined data/background: AN reports 0.6631 (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:120`); JSON reports 0.6631396081219646 (`phase4_inference/4c_observed/outputs/observed_results.json:2532-2536`) — consistent after rounding and physically problematic.
- Baseline `mu_hat`: AN reports 0.4382 (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:123`); baseline JSON reports 0.43822864200217504 (`phase4_inference/4c_observed/outputs/baseline_previous_result.json:11`) — consistent after rounding, but not a current standalone model result.
- Category single-fit values: JSON has boosted 7.837, VBF 8.428, zero-jet 50.0 (`phase5_documentation/outputs/category_mu_comparison.json:6`, `:11`, `:16`). The AN discusses the figure but does not tabulate or interpret these extreme category values (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:145-148`).

## Decision-Label Traceability

- [D1] Search/template fit: implemented in form. Search convention applies.
- [D2] Visible mass baseline, alternatives may replace only after evidence: not satisfied. The final primary model is a classifier score while the visible baseline is historical/frozen rather than a current primary model.
- [D3] VBF/boosted/zero-jet categories: implemented.
- [D4] W high-mT normalization: implemented numerically; full scale = 0.8528436634946431 ± 0.037049894579940935 (`phase4_inference/4c_observed/outputs/wjets_highmt_scale_full.json` fields `applied_scale_factor`, `absolute_uncertainty`).
- [D5] Tau anti-muon veto: selection prose says tight anti-muon ID is applied (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:49-51`).
- [D6] DY/Z normalization: final note says DY/Z is loosened to 30% in boosted/zero-jet and 50% in VBF (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:97-98`), but the final AN does not provide a full systematic evaluation or validation of those values.
- [D7] pyhf/HistFactory: implemented in form (`phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:108-112`).
- [D8] Blinding: not fully reviewed here; Phase 4 artifacts state the staged flow was followed.
- [D9] Alternative-observable gate: violated as Finding A4.

## Mandatory Regression Checklist

| Checklist item | Status | Evidence / action |
|---|---|---|
| Validation test failures without 3 documented remediation attempts? | **Checked: YES** | The final optimized score is `flagged` with `combined_ratio_failure: true` and `high_score_shape_failure: true` (`observed_results.json:2539-2550`). The final AN reports the failure but does not document three remediation attempts for the final optimized score model (`ANALYSIS_NOTE_5_v1.md:122-128`). |
| Any single systematic > 80% of total uncertainty? | Inconclusive, concerning | No total systematic budget is documented. The primary score QCD transfer has relative uncertainty 12.43 (`score_observed_yields.json:175`), but the AN does not show contribution to total uncertainty. |
| GoF toy distribution inconsistent with observed chi2? | Not evaluated | The final AN does not include observed-data GoF toys. Phase 4a toy GoF was Asimov-only and explicitly not an independent real-data validation (`INFERENCE_EXPECTED.md:139-147`). |
| Flat-prior gate excluding > 50% of bins? | Not found | No evidence of a >50% bin exclusion gate in reviewed artifacts. |
| Tautological comparison presented as independent validation? | **Checked: YES, weak form** | The "primary vs frozen baseline" comparison is a comparison to a historical analysis state, not an independent validation of the current model (`ANALYSIS_NOTE_5_v1.md:150-153`). |
| Visually identical independent distributions? | Not found | Sampled primary score plots are not visually identical; they show mismodelling instead. |
| Result >30% relative deviation from well-measured reference? | **Checked: YES** | Optimized `mu = 38.380` versus published values near 1 (`ANALYSIS_NOTE_5_v1.md:171-176`). |
| All binding [D] commitments fulfilled? | **Checked: NO** | [D9] alternative promotion gate is violated; see Finding A4. |
| Fit chi2 identically zero? | No for final observed model | Primary final validation has chi2/ndf = 2.4808 (`ANALYSIS_NOTE_5_v1.md:121`; `observed_results.json:2532`). |

## Required Rework Before Re-review

1. Choose and document a current validated final model. If no optimized model passes validation, do not present the optimized score as a final result.
2. Regenerate the final AN as a standalone current-data/current-MC analysis note with full equations, systematic subsections, validation tables, nuisance/impact diagnostics, comparisons, appendices, and reproduction contract.
3. Regenerate the PRL draft into a real paper draft or remove it from the deliverable set until it is publication-shaped.
4. Resolve the score-model data/MC disagreement through regression or remove the model from final-result status.
5. Re-run number-consistency checks after the final model choice is fixed, especially for the current visible-mass, add-MET, and score outputs.
