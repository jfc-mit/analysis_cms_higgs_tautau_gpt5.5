# Phase 4a Sensitivity Rerun Fixer Plan

## Finding

Phase 4a executor outputs are stale after the Phase 3 sensitivity regression.
They still use the visible-mass, three-category baseline with expected
`Z = 0.191` and median expected limit `mu = 11.374`. The accepted Phase 3
recommendation is the expected-only histogram-gradient-boosting MVA score in
the inclusive signal region, with `Z = 0.596` and median expected limit
`mu = 3.977` before low-background-bin handling.

## Plan

1. Update `build_expected_model.py` to load
   `phase3_selection/outputs/sensitivity_recommendation.json` and
   `phase3_selection/outputs/sensitivity_selected_events.npz`.
2. Build the Phase 4a expected-primary candidate from
   `mva_score_hist_gradient_boosting` in `inclusive_sr`, preserving the
   existing official normalization weights, TauPlusX trigger-selected Phase 3
   inputs, luminosity, DY, tau/open-data acceptance, and MC-stat constraints.
3. Merge the adjacent high-score tail bins from `[0.86, 0.94]` and
   `[0.94, 1.0]` to remove the single expected-background bin below five
   events, then document the sensitivity change relative to the unmerged Phase
   3 recommendation.
4. Update Phase 4a figures and validation to use MVA score outputs and remove
   stale expected `m_vis` figure requirements.
5. Regenerate machine-readable outputs and `INFERENCE_EXPECTED.md` only. Do
   not edit the Phase 4a AN, TeX, or PDF; the note writer/typesetter will
   update those after this executor fix.
6. Run the requested verification commands, scan for real observed SR use, and
   commit with `fix(phase4a): rerun expected model with mva strategy`.

## 2026-06-02T14:54:52Z

Built Phase 4a MVA-score weighted templates, pyhf workspace, expected CLs result, injection tests, GoF toys, systematics, limitations, and inference artifact. The score model is an expected-primary candidate pending Phase 4b score-modelling validation.

## 2026-06-02T14:55:40Z

Built Phase 4a MVA-score weighted templates, pyhf workspace, expected CLs result, injection tests, GoF toys, systematics, limitations, and inference artifact. The score model is an expected-primary candidate pending Phase 4b score-modelling validation.

## 2026-06-02T14:57:41Z

Built Phase 4a MVA-score weighted templates, pyhf workspace, expected CLs result, injection tests, GoF toys, systematics, limitations, and inference artifact. The score model is an expected-primary candidate pending Phase 4b score-modelling validation.

## Completion Check

- RESOLVED: `build_expected_model.py` now reads the Phase 3 sensitivity
  recommendation and selected-event MVA score file, builds the inclusive
  score-template workspace, and keeps the existing luminosity, DY,
  tau/open-data acceptance, and MC-stat constraints.
- RESOLVED: The low-background score tail is handled by merging `[0.86, 0.94]`
  and `[0.94, 1.0]` into `[0.86, 1.0]`. The minimum nominal expected
  background bin is now `9.314`.
- RESULT: Merged expected `Z = 0.590` and median expected limit `mu = 3.988`.
  The unmerged Phase 3 recommendation was `Z = 0.596` and `mu = 3.977`, so
  merging costs about `0.006` in Z and `0.011` in median limit while removing
  the sparse-bin issue.
- NEIGHBORHOOD CHECK: Verified the plot and validation scripts now require the
  MVA score figure and enforce the Phase 4b MVA-validation caveat and
  no-low-background-bin condition.
- VERIFICATION: `pixi run phase4a-all`, `pixi run phase4a-validate`,
  `pixi run lint-plots`, JSON/NPZ/workspace validation, `git diff --check`,
  and the explicit background-only Asimov blinding scan passed.

## 2026-06-02T15:37:43Z

Built Phase 4a MVA-score weighted templates, pyhf workspace, expected CLs result, injection tests, GoF toys, systematics, limitations, and inference artifact. The score model is an expected-primary candidate pending Phase 4b score-modelling validation.

## 2026-06-02T15:39:41Z

Built Phase 4a MVA-score weighted templates, pyhf workspace, expected CLs result, injection tests, GoF toys, systematics, limitations, and inference artifact. The score model is an expected-primary candidate pending Phase 4b score-modelling validation.
