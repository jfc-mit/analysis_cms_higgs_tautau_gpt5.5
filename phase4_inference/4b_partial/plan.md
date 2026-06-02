# Phase 4b Executor Plan

## Scope

Produce the 10% data-validation artifacts for the Phase 4a expected-primary
simultaneous score-template fit in `vbf`, `boosted`, and `zero_jet`.
Do not optimize, retune, or replace the model using data. Use only a
deterministic 10% subsample of rows with `role == "data"` and scale MC to
10% of the official luminosity.

## Inputs

- `phase3_selection/outputs/sensitivity_selected_events.npz`
- `phase3_selection/outputs/selected_events.npz`
- `phase3_selection/outputs/sensitivity_recommendation.json`
- `phase3_selection/outputs/normalization_inputs.json`
- `phase4_inference/4a_expected/outputs/expected_results.json`
- `phase4_inference/4a_expected/outputs/nominal_yields.json`
- `phase4_inference/4a_expected/outputs/pyhf_workspace.json`
- `phase4_inference/4a_expected/outputs/systematics.json`
- `phase4_inference/4a_expected/outputs/templates.npz`
- `phase4_inference/4a_expected/outputs/ANALYSIS_NOTE_4a_v1.md`

## Scripts

1. `src/build_partial_results.py`
   - Load Phase 4a model metadata and selected-event arrays.
   - Apply the deterministic data-only 10% rule:
     `(run * 1000003 + luminosityBlock * 9176 + event) % 10 == 0`.
   - For MC, keep all MC rows and scale official weights by
     `L_10pct / L_full = 0.1`; for data, count only masked rows.
   - Build score-template histograms for the fixed Phase 4a categories and
     bin edges.
   - Derive the W+jets high-`mT` scale factor from the masked 10% data:
     `(N_data_CR - nonW_MC_CR) / W_MC_CR`, with Poisson data and MC-stat
     uncertainty.
   - Build a partial pyhf workspace with masked 10% data observations for
     diagnostic fitting only.
   - Write `partial_results.json`, `partial_yields.json`,
     `wjets_highmt_scale.json`, `data_validation.json`,
     `pyhf_workspace_partial.json`, `partial_templates.npz`,
     `INFERENCE_PARTIAL.md`, and a minimal
     `ANALYSIS_NOTE_4b_v1.md`.

2. `src/plot_partial_results.py`
   - Plot 10% score-template data/MC validation for `vbf`, `boosted`, and
     `zero_jet` with ratio panels.
   - Plot high-`mT` W control-region comparison and derived scale.
   - Plot visible-mass validation by category if the required arrays are
     present.
   - Plot summary ratio and pull diagnostics.
   - Save every figure as PDF and PNG under `outputs/figures/`.

3. `src/validate_partial_outputs.py`
   - Check all required machine-readable outputs exist and parse.
   - Construct the partial pyhf workspace.
   - Verify the output blinding metadata says Phase 4b used only the
     deterministic 10% data subset and did not inspect the remaining 90%.
   - Verify required figures exist in both PDF and PNG.
   - Verify the W scale is finite or explicitly capped/downscoped.

## Artifact Structure

- `outputs/INFERENCE_PARTIAL.md`
- `outputs/ANALYSIS_NOTE_4b_v1.md`
- `outputs/ANALYSIS_NOTE_4b_v1.tex`
- `outputs/ANALYSIS_NOTE_4b_v1.pdf`
- `outputs/partial_results.json`
- `outputs/partial_yields.json`
- `outputs/wjets_highmt_scale.json`
- `outputs/data_validation.json`
- `outputs/pyhf_workspace_partial.json`
- `outputs/partial_templates.npz`
- `outputs/figures/*.pdf`
- `outputs/figures/*.png`

## Validation Criteria

- The selected final method remains the Phase 4a simultaneous
  `vbf`/`boosted`/`zero_jet` score-template fit.
- Full-data luminosity remains `11.467/fb`; Phase 4b MC comparisons use
  `1.1467/fb`.
- Official Open Data `N_gen` weights from Phase 3 normalization metadata
  remain the normalization source.
- The partial fit is labelled as a 10%-only diagnostic and not a final
  result.
- Score modelling is flagged if combined score-template validation has
  chi2/ndf > 3, any category has chi2/ndf > 5, or the combined data/MC
  ratio differs from unity by more than three total uncertainties.

## Verification Commands

- `pixi run phase4b-all`
- `pixi run lint-plots`
- `git diff --check`
- Inspect generated JSON metadata for the exact 10% mask rule and absence
  of full-data signal-region observations.
