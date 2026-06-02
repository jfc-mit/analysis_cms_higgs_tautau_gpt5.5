# Phase 3 Sensitivity Regression Fixer Plan

Session: `fixer_sensitivity_20260602T134700Z`

## Finding Restatement

The Phase 4a expected result, `Z = 0.191` and median expected CLs limit
`mu = 11.374`, is too weak for a credible reduced H to tau tau demonstration.
The regression ticket traces the dominant issue to Phase 3 category,
selection, and discriminant power rather than only pyhf nuisance choices.
The fix is not to tune nuisances downward or inspect observed full-data
signal-region shapes. The fix is to run serious MC/Asimov-only alternatives,
record the successful and failed attempts, and provide Phase 4a with a
machine-readable recommendation if an alternative improves expected
sensitivity and passes basic model-health gates.

## Inputs

- `phase3_selection/outputs/selected_events.npz`
- `phase3_selection/outputs/normalization_inputs.json`
- `phase3_selection/outputs/selection_config.json`
- `phase3_selection/outputs/variable_modeling.json`
- `phase4_inference/4a_expected/outputs/expected_results.json`
- `phase4_inference/4a_expected/outputs/nominal_yields.json`
- `phase2_exploration/outputs/local_sample_manifest.json`
- `phase1_strategy/outputs/STRATEGY.md`
- `conventions/search.md`

No observed full-data signal-region discriminant distribution will be used
for threshold optimization, classifier training, bin optimization, or model
choice. Data may appear only in copied validation caveats from existing Phase
3 control/validation outputs.

## Candidate Models

1. Baseline reproduction:
   - Observable: `m_vis`.
   - Categories: `vbf`, `boosted`, `zero_jet`.
   - Binning: Phase 4a `[0, 40, 60, 80, 100, 120, 160, 250]`.
   - Nuisance choices: nominal Phase 4a normsys and MC-stat implementation.

2. JHEP-inspired category variants:
   - VBF loose/tight splits using `mjj` and `delta_eta_jj`.
   - Boosted splits using `pt_tautau_proxy`, `tau_pt`, and `mu_pt`.
   - Zero-jet split using tau or muon pT where it improves expected metrics.
   - Top suppression variants with `btag_max <= 0`, `btag_max < 0.5`, and
     top-enriched/removal diagnostics. Because the reduced file lacks a
     calibrated working point, these are exploratory only unless clearly
     documented as uncalibrated.
   - Optimized bin merging for minimum expected background per bin.

3. Expected-only classifier variants:
   - HistGradientBoostingClassifier with fixed random seed.
   - MLPClassifier with StandardScaler and fixed random seed.
   - Candidate inputs from available reconstructed fields:
     `m_vis`, `m_addmet`, `mu_pt`, `mu_eta`, `mu_reliso`, `tau_pt`,
     `tau_eta`, `tau_reliso`, `met_pt`, `mt_mu_met`, `pt_tautau_proxy`,
     `n_clean_jets`, `mjj`, `delta_eta_jj`, `jet1_pt`, `btag_max`.
   - Train/test split on signal/background MC only, stratified by label.
   - Produce full selected-event MVA score arrays for MC and data, but use
     only MC scores for expected sensitivity optimization.
   - Output score templates and AUC/overtraining diagnostics.

4. Observable/binning audit:
   - Compare `m_vis`, `m_addmet`, `pt_tautau_proxy`, and classifier scores.
   - Compare Phase 4a binning with quantile/adaptive binnings that satisfy a
     minimum expected-background threshold.
   - Evaluate nominal nuisance, no-staterror, no-normsys, and low-nuisance
     diagnostics. Low/no nuisance models are diagnostics only, not final
     recommendations without source justification.

5. Missing-component feasibility:
   - Read the localized sample manifest and data/mc directory contents.
   - Explicitly record feasibility for QCD, diboson, single top, W4 or
     inclusive W, associated H, H to WW, extra DY categories, and embedded
     Z to tau tau. Do not fabricate unavailable components or import paper
     yields as pseudo-events.

## Metrics

Primary:

- Expected discovery `q0` Asimov `Z` from pyhf, directly comparable to Phase
  4a baseline.
- Median expected 95% CLs upper limit on `mu` from pyhf asymptotic CLs.

Secondary:

- Integrated and per-category `S/sqrt(B)`.
- Integrated and per-category `S/B`.
- Best-bin `S/B` concentration.
- Minimum expected background per final bin.
- Number of final bins below five expected background events.
- MVA train and test AUC, plus `train_auc - test_auc` overtraining gap.
- Signal injection recovery at 0x, 1x, 2x, and 5x nominal signal.
- Sensitivity with nominal, no-staterror, no-normsys, and no-nuisance
  diagnostic models.

## Validation Gates

Promotion gate:

- Improve expected `Z` or expected median CLs limit by at least 30% relative
  to Phase 4a baseline (`Z = 0.191`, median limit `mu = 11.374`).
- Pass Asimov signal injection with <20% relative bias for nonzero injected
  signals.
- Avoid final bins with expected background below five events, or explicitly
  flag the variant as requiring toy validation or bin merging before Phase 4a.
- Preserve the trigger and normalization rules: TauPlusX
  `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`, official `L_int`, official `N_gen`,
  and no entry-count normalization.

MVA caveat gate:

- A classifier may be recommended only as expected-only or Phase 4a candidate
  if the artifact records failed input-modelling caveats and Phase 4b gate
  requirements. Severe input modelling does not block recording expected-only
  gain, but it blocks unqualified promotion.

Failure criteria:

- Less than 30% expected improvement after serious category, observable, and
  classifier attempts.
- Expected improvement comes only from removing justified nuisances.
- Signal injection bias exceeds 20%.
- More than half of final bins have expected background below five events and
  no merging/toy path is supplied.
- Any change requires unavailable samples or observed signal-region tuning.

## Scripts and Artifacts

Add:

- `phase3_selection/src/sensitivity_regression.py`
  - Builds pyhf-compatible expected models from `selected_events.npz`.
  - Runs category, observable/binning, nuisance, and classifier scans.
  - Writes machine-readable outputs and figures.

Outputs:

- `phase3_selection/outputs/sensitivity_scan.json`
- `phase3_selection/outputs/mva_sensitivity.json`
- `phase3_selection/outputs/sensitivity_recommendation.json`
- `phase3_selection/outputs/sensitivity_selected_events.npz`
- `phase3_selection/outputs/missing_component_feasibility.json`
- `phase3_selection/outputs/figures/sensitivity_variant_summary.{pdf,png}`
- `phase3_selection/outputs/figures/mva_score_templates.{pdf,png}`
- `phase3_selection/outputs/figures/sensitivity_nuisance_audit.{pdf,png}`

Update:

- `pixi.toml`: add `phase3-sensitivity`, include it in `phase3-all`.
- `phase3_selection/outputs/SELECTION.md`: add a regression section with
  attempts, best metric, limitations, and Phase 4a rerun instructions.
- `experiment_log.md`: append the plan, attempts, results, and residual
  blockers.

Possible but not first-pass:

- `phase4_inference/4a_expected/src/build_expected_model.py` only if the best
  Phase 3 output requires a small compatibility option. Otherwise leave the
  Phase 4a rerun to the next executor with explicit instructions.

## Execution Order

1. Inspect selected-event fields and current weighted yields.
2. Implement `sensitivity_regression.py` with baseline reproduction first.
3. Add pixi task and run baseline reproduction.
4. Add category and binning scans; run and store results.
5. Add MVA training and score-template scan; run and store results.
6. Add missing-component feasibility output.
7. Render required figures as PDF and PNG.
8. Update `SELECTION.md`, experiment log, and session log.
9. Run `pixi run phase3-sensitivity`, affected `phase3-all`, `pixi run
   lint-plots`, and `git diff --check`.
10. Commit with `fix(phase3): improve expected sensitivity strategy`.
