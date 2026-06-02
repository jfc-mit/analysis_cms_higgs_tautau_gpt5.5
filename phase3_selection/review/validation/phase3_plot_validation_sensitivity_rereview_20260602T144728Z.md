# Phase 3 Plot Validation Sensitivity Rereview

Review timestamp: `20260602T144728Z`

Reviewed commit: `196b55d fix(phase3): polish sensitivity figures`

Review scope: fresh plot revalidation after the sensitivity-figure polish commit. This is review-only; no implementation files were modified.

## Verdict

**PASS.** I find no unresolved Category A or Category B plot-validation issues in the requested rereview scope.

## Prior Blocker Resolution

### Raw/Internal Labels

**PASS.** The three sensitivity figures no longer expose the prior raw/internal labels.

Evidence:

- `phase3_selection/outputs/figures/mva_score_templates.png` labels the x axis as `Gradient-boosted classifier score`, not `HistGradientBoosting score`.
- `phase3_selection/outputs/figures/sensitivity_variant_summary.png` uses reader-facing variant labels such as `Gradient-boosted classifier score, inclusive signal region`, `Neural-network classifier score, inclusive signal region`, `Top-veto scan, max b tag <= 0.50`, and `Dijet/boost scan, 300 GeV, separation 3.0, boost pT 100 GeV`.
- `phase3_selection/outputs/figures/sensitivity_nuisance_audit.png` uses `Visible mass baseline`, `Gradient-boosted classifier score, inclusive signal region`, and readable nuisance-mode labels.
- Grep over `phase3_selection/outputs/SELECTION.md` and `phase3_selection/outputs/figures/` found no remaining `HistGradientBoosting score`, snake_case MVA observable labels, or raw grid configuration labels in visible outputs. The only `mva_score` match is the intended figure filename/reference in `SELECTION.md`.

I also inspected `phase3_selection/src/sensitivity_regression.py`; it still contains internal model/config identifiers where expected in code, but the plotting label map and axis labels convert them to human-readable labels for output figures.

### `mva_score_templates` Legend Overlap

**PASS.** Visual inspection of `phase3_selection/outputs/figures/mva_score_templates.png` shows the legend placed outside the plotting axes on the right. It no longer overlaps the blue background points, green signal points, error bars, or CMS label.

### `SELECTION.md` Figure References And Captions

**PASS.** `phase3_selection/outputs/SELECTION.md` references all three new figures:

- `figures/sensitivity_variant_summary.pdf` at lines 397-401.
- `figures/mva_score_templates.pdf` at lines 403-407.
- `figures/sensitivity_nuisance_audit.pdf` at lines 409-413.

Each caption is interpretive and contains three sentences, satisfying the required 2-5 sentence range. The captions describe what is plotted, how it should be interpreted, and the expected-only/diagnostic caveat.

## Expected-Only Caveats

**PASS.** The expected-only caveats remain visible in both prose and captions.

Evidence:

- `SELECTION.md` lines 383-388 state that the sensitivity remediation uses only MC and Asimov expectations and does not tune on observed full-data signal-region discriminant distributions.
- `SELECTION.md` lines 397-401 state that the variant summary is an optimization diagnostic and not an observed-data result.
- `SELECTION.md` lines 403-407 state that the classifier was trained only on MC and that Phase 4b must validate score modelling before promotion as a primary result.
- `SELECTION.md` lines 409-413 state that the nuisance curves are expected-model diagnostic stress tests and not final statistical results.
- `sensitivity_recommendation.json` and `mva_sensitivity.json` retain the caveat that the MVA gain is expected-only and requires Phase 4b modelling validation before unqualified promotion.

## File Pair Verification

**PASS.** All requested PDF+PNG pairs exist and are non-empty:

- `phase3_selection/outputs/figures/sensitivity_variant_summary.pdf` and `.png`
- `phase3_selection/outputs/figures/mva_score_templates.pdf` and `.png`
- `phase3_selection/outputs/figures/sensitivity_nuisance_audit.pdf` and `.png`

Observed file sizes:

| Figure | PDF bytes | PNG bytes |
|---|---:|---:|
| `sensitivity_variant_summary` | 24728 | 268673 |
| `mva_score_templates` | 24661 | 116336 |
| `sensitivity_nuisance_audit` | 22209 | 229616 |

## Required Checks

Commands run:

```bash
pixi run lint-plots
git diff --check
```

Results:

- `pixi run lint-plots`: PASS, `No plotting violations found in 11 file(s).`
- `git diff --check`: PASS, no whitespace errors reported.

Additional checks:

- `git show --name-status --oneline --stat 196b55d` confirms the fix commit modified `SELECTION.md`, the three PDF/PNG figure pairs, plotting source, and logs, but did not modify JSON output files.
- `pdftotext` did not expose extractable text for these PDFs, so label verification is based on PNG visual inspection plus greps over output markdown/figure files.

## Regression Checklist

- [x] Any validation test failures without 3 documented remediation attempts? **No.** Requested validation checks pass.
- [x] Any single systematic > 80% of total uncertainty? **Not applicable.** This plot rereview does not introduce or modify the Phase 4 systematic uncertainty decomposition.
- [x] Any GoF toy distribution inconsistent with observed chi2? **Not applicable.** No GoF toy distribution is reviewed in this plot-only pass.
- [x] Any flat-prior gate excluding > 50% of bins? **Not applicable.** No bin-exclusion gate is modified in this plot-only pass.
- [x] Any tautological comparison presented as independent validation? **No.** The figures are labelled as expected-only diagnostics, not independent observed-data validation.
- [x] Any visually identical distributions that should be independent? **No.** Visual inspection found distinct signal/background score templates and distinct diagnostic points.
- [x] Any result with > 30% relative deviation from a well-measured reference value? **Not applicable.** This pass validates figure presentation and caveats, not a final measured result.
- [x] All binding commitments from strategy fulfilled or formally downscoped? **Adequate for this rereview scope.** The expected-only caveats and Phase 4b validation gate remain explicit.
- [x] Is the fit chi2 identically zero or within numerical precision? **Not applicable.** No fit chi2 is introduced or reviewed here.

## Changed Files In This Review

- `phase3_selection/review/validation/phase3_plot_validation_sensitivity_rereview_20260602T144728Z.md`
- `phase3_selection/logs/plot_validator_phase3_sensitivity_rereview_20260602T144728Z.md`
