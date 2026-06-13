# Phase 4c Observed Results Plan

## Scope

Use the frozen Phase 4a/4b analysis method to evaluate full Run2012B/C
TauPlusX observations. No selection, category, score-bin, classifier, or
signal/background model retuning is allowed after unblinding.

The 4b human gate is treated as passed by explicit user instruction. The
Phase 4b score-modeling warning remains binding context and will be carried
into the 4c outputs and analysis note.

## Inputs

- `phase3_selection/outputs/sensitivity_selected_events.npz`
- `phase3_selection/outputs/sensitivity_recommendation.json`
- `phase3_selection/outputs/normalization_inputs.json`
- `phase4_inference/4a_expected/outputs/expected_results.json`
- `phase4_inference/4a_expected/outputs/pyhf_workspace.json`
- `phase4_inference/4a_expected/outputs/templates.npz`
- `phase4_inference/4a_expected/outputs/nominal_yields.json`
- `phase4_inference/4b_partial/outputs/data_validation.json`
- `phase4_inference/4b_partial/outputs/partial_results.json`
- `phase4_inference/4b_partial/outputs/partial_yields.json`
- `phase4_inference/4b_partial/outputs/wjets_highmt_scale.json`

## Scripts

1. `src/build_observed_results.py`
   - Keep only two result paths in the generated final-result semantics:
     `visible_mass_qcd_primary` and `dnn_classifier_score_secondary`.
   - Build the visible-mass baseline/cut-based result from `m_vis` in the
     VBF, boosted, and zero-jet categories.
   - Build the `D_NN` result from `mva_score_xgboost` in the same three
     categories with fixed 20 uniform score bins.
   - Do not generate calibrated-score primary, score-diagnostic, add-MET, or
     HGB/input-reweighting variant result sections.
   - Write JSON/NPZ/workspace outputs and the `INFERENCE_OBSERVED.md` and
     `ANALYSIS_NOTE_4c_v1.md` drafts around those two result paths.

2. `src/plot_observed_results.py`
   - Produce PDF and PNG figures for visible-mass and `D_NN` data/MC
     comparisons, full high-mT W scale, validation summary, observed result
     summary, and comparison to Phase 4a/4b.
   - Draw validation plots with true SM Higgs normalization, red data points
     with error bars, and Data/MC(total signal + background) ratios.

3. `src/validate_observed_outputs.py`
   - Check JSON integrity, visible and `D_NN` workspace construction, required
     figure existence, full-data source documentation, preservation of Phase
     4b warnings, and absence of old calibrated-score/add-MET final semantics.

## Outputs

- `outputs/observed_results.json`
- `outputs/observed_yields.json`
- `outputs/wjets_highmt_scale_full.json`
- `outputs/comparison_to_4a_4b.json`
- `outputs/pyhf_workspace_observed.json`
- `outputs/observed_templates.npz`
- `outputs/INFERENCE_OBSERVED.md`
- `outputs/ANALYSIS_NOTE_4c_v1.md`
- Figures in `outputs/figures/` as PDF and PNG.

PDF compilation of the 4c AN is optional for this fast implementation; it
will be attempted only if the existing document tooling is immediately
available.

## Verification

- `pixi run phase4c-all`
- `pixi run lint-plots`
- `git diff --check`

The validation output must state that the full data were only used by Phase
4c observed outputs and that the Phase 4b score-modeling warning is retained.
