# Phase 3 Critical Sensitivity Re-review

Session: `critical_sensitivity_rereview_20260602T142634Z`
Reviewer: fresh Phase 3 critical reviewer after sensitivity regression
Scope: review-only pass over commit `ddc9dd5 fix(phase3): improve expected sensitivity strategy`

## Verdict

**PASS.** I find no unresolved Category A or Category B issues blocking a Phase 4a expected-only rerun.

The regression work genuinely addresses the requested sensitivity-remediation scope, remains blinded with respect to observed full-data signal-region optimization, and is honest that the MVA is expected-only until Phase 4b validates score modelling. The user-stated residual caveats remain binding Phase 4a/4b gates, not Phase 3 blockers.

## Category A/B Findings

None.

## Category C Notes

1. The compact `mva_sensitivity.json` entries for the two baseline-category MVA score models report `z_value: null` without carrying the failure reason. The full `sensitivity_scan.json` result contains the pyhf discovery failure reason (`Inequality constraints incompatible`), and the recommended best model is unaffected. This is not blocking, but future compact summaries should retain failure status/reason for audit readability.

2. The Phase 4a rerun instruction is actionable, but the Phase 4a executor should explicitly state that it is preserving the TauPlusX trigger-defined selected-event phase space, not rebuilding selection with alternate trigger ORs. This is already documented in `SELECTION.md`; making it explicit in the Phase 4a artifact will reduce reviewer ambiguity.

## Evidence

### Requested Methods Were Attempted

- JHEP-style categories were implemented in code via `assign_jhep_refined`, with tight/loose VBF and boosted/tau-pT/zero-jet splits (`phase3_selection/src/sensitivity_regression.py:141-164`) and a grid scan over `mjj`, `delta_eta_jj`, and `pt_tautau_proxy` thresholds (`phase3_selection/src/sensitivity_regression.py:620-639`).
- Top/b-veto handling was attempted through `btag_veto_le0.00`, `0.25`, and `0.50` split variants, explicitly caveated as uncalibrated (`phase3_selection/src/sensitivity_regression.py:640-653`).
- Alternative observable/binning audit includes `m_vis`, `m_addmet`, and `pt_tautau_proxy` baseline-category specs (`phase3_selection/src/sensitivity_regression.py:547-577`).
- Expected-only MVA/NN alternatives were attempted with two models: `HistGradientBoostingClassifier` and an MLP pipeline (`phase3_selection/src/sensitivity_regression.py:492-510`).
- The scan output contains 78 total models: 64 JHEP category-grid variants, 4 expected-only MVA variants, 3 b-tag/top variants, 3 boosted/tau split variants, 2 observable audits, 1 refined JHEP category model, and 1 baseline reproduction. My JSON check reported family best-Z values: expected-only MVA `0.5955`, b-tag/top `0.2637`, JHEP refined `0.2274`, boosted/tau split `0.2148`, JHEP grid `0.1992`, observable audit `0.1636`, baseline `0.1906`.
- Missing-component feasibility was checked against local ROOT files. Only `DYJetsToLL`, `GluGluToHToTauTau`, `TTbar`, `VBF_HToTauTau`, and `W1/W2/W3JetsToLNu` are locally available; QCD, diboson, single top, W4/inclusive W, associated H, H to WW, extra DY categories, and embedded Z to tau tau are marked unavailable/do-not-approximate (`phase3_selection/outputs/missing_component_feasibility.json:2-90`).

### Blinding / No Observed SR Optimization

- Training selects only rows with `role` in `["signal", "background"]` and `sample` in the MC `SAMPLES` list (`phase3_selection/src/sensitivity_regression.py:478-490`).
- Template building loops over `SAMPLES`, not data, and observations are background Asimov expectations (`phase3_selection/src/sensitivity_regression.py:217-221`, `phase3_selection/src/sensitivity_regression.py:329-342`).
- The recommendation JSON states `expected_only: true` and `observed_full_data_signal_region_used_for_optimization: false` (`phase3_selection/outputs/sensitivity_recommendation.json:392-395`).
- `SELECTION.md` states the remediation uses only MC and Asimov expectations and does not tune on observed full-data signal-region discriminant distributions (`phase3_selection/outputs/SELECTION.md:381-388`).

The script does compute MVA scores for all rows for downstream validation (`phase3_selection/src/sensitivity_regression.py:512-533`, `phase3_selection/src/sensitivity_regression.py:1040-1044`), but ranking and templates use MC/Asimov only. I find no evidence that observed full-data SR distributions entered optimization/training/selection.

### MVA Technical Defensibility for Phase 4a Expected-only Use

- The MVA train/test split is stratified with `test_size = 0.35` and `random_state = 31415` (`phase3_selection/src/sensitivity_regression.py:491-523`).
- `mva_sensitivity.json` reports class counts of 8402 background and 1668 signal MC rows, train/test sizes 6545/3525, and AUCs:
  - HistGradientBoosting: train AUC `0.956596`, test AUC `0.877792`, gap `0.078805`.
  - MLP pipeline: train AUC `0.880548`, test AUC `0.864354`, gap `0.016194`.
  These are recorded in `phase3_selection/outputs/mva_sensitivity.json:108-130`.
- The feature list contains 16 reconstructed inputs and is recorded in both code and JSON (`phase3_selection/src/sensitivity_regression.py:52-69`, `phase3_selection/outputs/mva_sensitivity.json:89-106`).
- The expected-only caveat is explicit in each MVA result (`phase3_selection/outputs/mva_sensitivity.json:15`, `phase3_selection/outputs/mva_sensitivity.json:34-35`, `phase3_selection/outputs/mva_sensitivity.json:74-75`) and in the modelling caveat (`phase3_selection/outputs/mva_sensitivity.json:107`).
- My NPZ check found `sensitivity_selected_events.npz` contains finite `mva_score_hist_gradient_boosting` and `mva_score_mlp` arrays with shape `(61081,)`, plus `sensitivity_best_category`; signal-region best categories are `['inclusive_sr']`, matching the recommendation.

The gradient-boosting overtraining gap is non-negligible, but it is disclosed through train/test AUC and the MVA is not being promoted as validated on data. For Phase 4a expected-only sensitivity studies, this is defensible.

### Internal Consistency and Honesty

- The best recommendation is `mva_hist_gradient_boosting_score_single_category`, `Z = 0.5955085932694459`, median expected limit `3.977300465753028`, signal `25.105576868113534`, background `9338.22528295425`, one low-background bin, and improvement factors of `3.1242` in Z and `2.8598` in median limit (`phase3_selection/outputs/sensitivity_recommendation.json:2-20`).
- The best full result uses the same spec and one inclusive channel, with evaluated discovery sensitivity and expected limit (`phase3_selection/outputs/sensitivity_recommendation.json:21-50`, `phase3_selection/outputs/sensitivity_recommendation.json:85-103`).
- Signal injection passes for injected `mu = 0, 1, 2, 5`; the largest nonzero relative bias is about `4.32e-4`, well below the 20% gate (`phase3_selection/outputs/sensitivity_recommendation.json:52-84`).
- `sensitivity_scan.json` reproduces the Phase 4a baseline `Z = 0.1906097504953417` and baseline median expected limit `11.374122822819393` (`phase3_selection/outputs/sensitivity_scan.json:2-6`).
- The nuisance audit honestly separates diagnostics from final results, with baseline nominal/no-nuisance Z values `0.1906/0.3894` and best-MVA nominal/no-nuisance Z values `0.5955/0.8666` (`phase3_selection/outputs/sensitivity_scan.json:8-70`).
- Residual blockers are explicitly carried: Phase 4b MVA input/output validation before unqualified use, missing SVFIT/embedding/QCD/additional channels, and low-background bin merging or toy validation (`phase3_selection/outputs/sensitivity_recommendation.json:415-419`; `phase3_selection/outputs/SELECTION.md:407-418`).

I verified exact consistency between `sensitivity_recommendation.json` and the top-ranked entry in `sensitivity_scan.json` for best model name, Z, median limit, improvement factors, signal/background totals, and low-background bin count; all deltas were zero.

### Phase 4a Rerun Instructions

- `pixi.toml` includes `phase3-sensitivity` and chains it through `phase3-all`, and `all` chains Phase 3 through `phase4a-all` (`pixi.toml:61-68`).
- The recommendation instructs Phase 4a to read the recommendation and sensitivity NPZ, use the best observable/categories/category labels, keep official `L_int` and `N_gen` weights from `normalization_inputs.json`, recompute workspace/results/systematics/plots/AN/PDF, and restart full 4-bot+bib review (`phase3_selection/outputs/sensitivity_recommendation.json:403-408`).
- `SELECTION.md` documents the TauPlusX trigger requirement and the intentional decision not to OR in single-muon triggers (`phase3_selection/outputs/SELECTION.md:18-22`), and documents official normalization provenance with no luminosity back-calculation (`phase3_selection/outputs/SELECTION.md:275-314`).

These instructions are actionable and preserve the trigger/normalization constraints, provided the Phase 4a executor consumes the selected-event summaries rather than redefining event selection.

## Regression Checklist

- [x] Validation test failures without 3 documented remediation attempts? **No.** The broad validation failure remains scoped, and three remediation attempts are documented in `SELECTION.md:217-239`.
- [x] Any single systematic > 80% of total uncertainty? **Not applicable at Phase 3 expected-sensitivity scan.** No final systematic uncertainty decomposition is produced here.
- [x] Any GoF toy distribution inconsistent with observed chi2? **Not applicable.** Phase 4a must produce GoF/toy validation if low counts remain.
- [x] Any flat-prior gate excluding > 50% of bins? **No evidence.** The selected best has one low-background bin out of six populated bins (`16.7%`), not wholesale exclusion (`phase3_selection/outputs/sensitivity_recommendation.json:118-125`).
- [x] Any tautological comparison presented as independent validation? **No.** Signal injection uses Asimov self-checks and is presented as a gate, not data validation; MVA data validation is deferred explicitly.
- [x] Any visually identical distributions that should be independent? **No evidence from this scope.** Plot linter passed; visual plot validation was outside this critical rereview's requested artifact set.
- [x] Any result with > 30% relative deviation from a well-measured reference value? **Not applicable.** No observed physics measurement/result is extracted at this Phase 3 rereview.
- [x] All binding commitments from strategy fulfilled or formally downscoped? **Adequate for the sensitivity regression scope.** [D9] was the trigger; the current scan evaluates the expected-sensitivity alternatives and documents remaining Phase 4a/4b gates.
- [x] Fit chi2 identically zero? **Not applicable.** No observed fit chi2 is reported in this Phase 3 remediation.

No regression trigger is newly fired by this rereview.

## Verification Commands

Commands run:

- `pixi run lint-plots` — passed, "No plotting violations found in 11 file(s)."
- `git diff --check` — passed with no whitespace errors.
- `pixi run py - <<'PY' ...` JSON consistency checks — passed:
  - `sensitivity_recommendation.json` best equals `sensitivity_scan.json` top-ranked entry for model name and all checked numeric fields.
  - `mva_sensitivity.json` contains both MVA models, split metadata, AUCs, feature list, and expected-only caveat.
  - `sensitivity_selected_events.npz` contains finite MVA scores and matching best-category labels.

I did not rerun `pixi run phase3-sensitivity` because the task appends to the fixer session log and rewrites output artifacts. The review-only checks above were sufficient to verify consistency without mutating implementation outputs.
