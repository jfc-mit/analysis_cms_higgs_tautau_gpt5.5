# Phase 4a Expected-Results Plan

Timestamp: 2026-06-02T12:44:06Z

Executor: Phase 4a expected-results statistical-analysis executor.

## Scope

This phase builds the expected-only statistical model for the reduced CMS 2012
Open Data H to tau tau search in the mu tau_h final state. Phase 1 resolved the
analysis as a search/template fit, so `conventions/search.md` is binding even
though `phase4_inference/CLAUDE.md` still says "measurement". Phase 4a will use
Asimov/pseudo-data from the nominal model only; it will not use real-data
signal-region distributions or observed full-data fit results.

## Inputs

Read and use the following upstream artifacts:

- `prompt.md`
- `phase1_strategy/outputs/STRATEGY.md`
- `phase2_exploration/outputs/EXPLORATION.md`
- `phase2_exploration/outputs/local_sample_manifest.json`
- `phase2_exploration/outputs/FINAL_AN_SAMPLE_LIMITATION_OBLIGATIONS.md`
- `phase3_selection/outputs/SELECTION.md`
- `phase3_selection/outputs/selected_events.npz`
- `phase3_selection/outputs/normalization_inputs.json`
- `phase3_selection/outputs/category_yields.json`
- `phase3_selection/outputs/region_yields.json`
- `phase3_selection/outputs/variable_modeling.json`
- latest Phase 3 PASS reviews under `phase3_selection/review/`

## Artifact Structure

Create and populate:

- `phase4_inference/4a_expected/src/build_expected_model.py`
- `phase4_inference/4a_expected/src/plot_expected_model.py`
- `phase4_inference/4a_expected/src/validate_expected_outputs.py`
- `phase4_inference/4a_expected/outputs/INFERENCE_EXPECTED.md`
- `phase4_inference/4a_expected/outputs/templates.npz`
- `phase4_inference/4a_expected/outputs/nominal_yields.json`
- `phase4_inference/4a_expected/outputs/pyhf_workspace.json`
- `phase4_inference/4a_expected/outputs/expected_results.json`
- `phase4_inference/4a_expected/outputs/systematics.json`
- `phase4_inference/4a_expected/outputs/signal_injection.json`
- `phase4_inference/4a_expected/outputs/gof_validation.json`
- `phase4_inference/4a_expected/outputs/limitations_downscope.json`
- `phase4_inference/4a_expected/outputs/figures/*.pdf`
- `phase4_inference/4a_expected/outputs/figures/*.png`
- `phase4_inference/4a_expected/logs/executor_phase4a_expected_20260602T124406Z.md`

If `COMMITMENTS.md` is absent, reconstruct it at the analysis root from Phase 1
decision, constraint, limitation, and systematic commitments, mark it as
reconstructed at Phase 4a start, and update Phase 4a statuses.

## Statistical Model

Build a binned pyhf/HistFactory-compatible model over mutually exclusive
signal-region categories:

- `vbf`
- `boosted`
- `zero_jet`

The primary observable is `m_vis`. Use `is_signal_region` and `category` from
`selected_events.npz`; do not use real data signal-region histograms. Real-data
control/validation information may be referenced only as a Phase 3 diagnostic
caveat. For expected 4a fits, observations are Asimov nominal background plus
the selected injected signal strength.

Template construction:

- Use the official normalization inputs in
  `phase3_selection/outputs/normalization_inputs.json`.
- Signal weights use `sigma_prod * BR(H->tautau) * L_int / N_gen`.
- Background weights use `sigma * L_int / N_gen`.
- Local ROOT entries are not generation denominators.
- Use coarse visible-mass binning with no final SR bin below about five
  expected events after summing nominal signal plus background. Merge bins if
  needed and record the final binning.

Samples:

- Signal: `GluGluToHToTauTau`, `VBF_HToTauTau`.
- Background: `DYJetsToLL`, `TTbar`, `W1JetsToLNu`, `W2JetsToLNu`,
  `W3JetsToLNu`.
- Missing components remain explicit downscopes: embedded Z to tau tau, QCD
  multijet, diboson WW/WZ/ZZ, single top, W4/inclusive W, associated Higgs
  production, H to WW, and additional DY categories.

## Systematics

Implement only sourced or strategy-bound nuisance parameters. Do not invent
new flat uncertainties.

Implemented in the Phase 4a workspace:

- Luminosity normalization: 2.6% on MC-normalized processes, from CMS PAS
  LUM-13-001 as recorded in `normalization_inputs.json`.
- DY/Z normalization: 15% constrained normalization on `DYJetsToLL`, following
  Phase 1 [D6] and the user-provided 10-15% requirement for missing trigger
  turn-on and tau scale factors.
- Tau efficiency/trigger/open-data acceptance: 15% on templates with selected
  tau_h candidates, following Phase 1 [D5] and its CMS Run 1 reference range.
- MC statistical uncertainty: pyhf `staterror` modifiers per sample and
  category from the weighted template variances.

Formally downscope, with impact/limitation text, all systematic sources that
require unavailable reduced-sample inputs or external variation samples:

- Tau energy scale, muon scale/efficiency, JES/JER, MET scale/resolution,
  b-tag/mistag, pileup reweighting, PDF/scale/UE/PS acceptance, W transfer
  factor, QCD data-driven sideband shape/rate, diboson/single-top rates, and
  missing-sample shape systematics.

The artifact will include a completeness table versus `conventions/search.md`,
CMS 2014, CMS 2018, and this Phase 4a implementation.

## Validations

Run required search validations on Asimov/pseudo-data:

- Expected CLs upper limit using pyhf asymptotic inference.
- Expected discovery sensitivity where feasible, otherwise document the pyhf
  API limitation and report the expected limit as the primary sensitivity
  result.
- Signal injections at 0x, 1x, 2x, and 5x nominal signal. Fit injected Asimov
  samples and require recovered signal strength bias below 20% where the model
  can identify the injection.
- Nuisance pull/constraint summary on Asimov fits.
- Chi2/ndf against Asimov pseudo-data by category and combined.
- Limited toy saturated-model GoF ensemble with fixed seed and recorded toy
  count/runtime. If exact pyhf saturated GoF API support is unavailable, use a
  Poisson toy Pearson/saturated-style statistic with a documented limitation.
- Asymptotic-bin check: record any bin with expected count below five and the
  remedial binning choice.

## Figures

`plot_expected_model.py` will read only Phase 4a machine-readable outputs and
produce PDF+PNG figures using CMS Open Simulation labels:

- Nominal stacked expected `m_vis` templates for `vbf`, `boosted`, and
  `zero_jet`, with signal overlay.
- Expected signal-to-background by category.
- Nuisance impact or expected uncertainty ranking from the available model
  outputs.
- Signal injection closure plot.
- Limited toy GoF distribution with the Asimov statistic marker.

Captions will be drafted in `INFERENCE_EXPECTED.md`.

## Pixi Tasks

Add tasks:

- `phase4a-model`
- `phase4a-plots`
- `phase4a-validate`
- `phase4a-all`

Update `all` to include `phase4a-all` after `phase3-all`.

## Verification

Before final handoff, run:

- `pixi run phase4a-all`
- `pixi run lint-plots`
- `pixi run phase4a-validate`
- JSON validity checks through the validation script
- pyhf workspace validation/model construction through the validation script
- `git diff --check`
- explicit source scan confirming Phase 4a model construction does not use
  real data signal-region observed results.

## Commit Plan

Commit after:

1. Plan and reconstructed commitments/log setup.
2. Model/script implementation and machine-readable outputs.
3. Plots, artifact, verification, and final Phase 4a executor outputs.
