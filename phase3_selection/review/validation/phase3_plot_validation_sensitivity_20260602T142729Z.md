# Phase 3 Plot Validation Rereview: Sensitivity Regression

Timestamp: 20260602T142729Z

Reviewer: fresh plot validator

Commit reviewed: `ddc9dd5 fix(phase3): improve expected sensitivity strategy`

Verdict: FAIL

PASS is blocked by unresolved Category A/B findings in the new sensitivity
figures and the Phase 3 selection artifact.

## Scope

- Ran `pixi run lint-plots`.
- Inspected the three new sensitivity/MVA figures:
  `mva_score_templates`, `sensitivity_nuisance_audit`, and
  `sensitivity_variant_summary`.
- Inspected the regenerated/changed Phase 3 rendered figure set for plotting
  regressions.
- Checked PDF/PNG pairing for all Phase 3 figures.
- Checked `SELECTION.md` figure references, caption sentence counts, and
  expected-only MVA caveat language.

## Findings

### Category A: raw code/config labels visible in new sensitivity figures

Affected figures:

- `phase3_selection/outputs/figures/mva_score_templates.png`
- `phase3_selection/outputs/figures/sensitivity_nuisance_audit.png`
- `phase3_selection/outputs/figures/sensitivity_variant_summary.png`

Evidence:

- [phase3_selection/src/sensitivity_regression.py](/sandbox/work/jfc/analyses/higgs_tautau/phase3_selection/src/sensitivity_regression.py:797)
  builds tick labels by replacing underscores in internal variant names.
- [phase3_selection/src/sensitivity_regression.py](/sandbox/work/jfc/analyses/higgs_tautau/phase3_selection/src/sensitivity_regression.py:829)
  builds legend labels by replacing underscores in internal model names.
- [phase3_selection/src/sensitivity_regression.py](/sandbox/work/jfc/analyses/higgs_tautau/phase3_selection/src/sensitivity_regression.py:874)
  labels the MVA score axis as `HistGradientBoosting score`.

Visible examples include `mva hist gradient boosting score single category`,
`baseline phase4a mvis`, `mva hist gradient boosting score single category`,
`grid mjj300 delta3.0 pt50`, and `HistGradientBoosting score`. These are
internal analysis/config identifiers rather than publication-quality labels.

Rule failed: rendered figures must not show raw code variable names or
configuration identifiers.

Suggested fix: introduce explicit display labels for all sensitivity variants,
models, nuisance modes, and classifier score axes. For example, use
`Gradient-boosting score, one category`, `Phase 4a visible-mass baseline`,
`MVA score, one category`, and compact physics labels for the grid scans.

### Category A: legend overlaps plotted content in `mva_score_templates`

Affected figure:

- `phase3_selection/outputs/figures/mva_score_templates.png`

Evidence:

- [phase3_selection/src/sensitivity_regression.py](/sandbox/work/jfc/analyses/higgs_tautau/phase3_selection/src/sensitivity_regression.py:877)
  places the legend at `upper left`.
- The rendered PNG shows the legend in the same low-score region occupied by
  the high-yield background points.

Rule failed: legend must not overlap data points, error bars, or curves.

Suggested fix: move the legend to a genuinely empty region, likely upper right
after checking the experiment label/rlabel spacing, or scale/reposition using
the project's legend policy. Re-render and visually confirm no overlap.

### Category B: new sensitivity figures are not referenced in `SELECTION.md`

Affected artifact:

- [phase3_selection/outputs/SELECTION.md](/sandbox/work/jfc/analyses/higgs_tautau/phase3_selection/outputs/SELECTION.md:381)

Evidence:

- `SELECTION.md` contains no references to:
  - `figures/mva_score_templates.pdf`
  - `figures/sensitivity_nuisance_audit.pdf`
  - `figures/sensitivity_variant_summary.pdf`
- The sensitivity-regression section describes the new scan and MVA outcome,
  but includes no rendered figure links or captions for the key new figures.

Rule failed: the review request requires verifying that `SELECTION.md`
references the new figures correctly and that captions are interpretive,
two or more sentences. The figures are absent from the artifact, so their
captions cannot pass.

Suggested fix: add all three figure references to the sensitivity-regression
section with pandoc-crossref labels and 2-5 sentence captions that explain
what is plotted, what selection/model was used, and the expected-only caveat.

## Figure-by-Figure Visual Results

- `addmet_mass_boosted`: PASS. CMS Open Data + Open Simulation label present;
  no title, no clipping, readable labels, no legend overlap.
- `addmet_mass_vbf`: PASS. CMS Open Data + Open Simulation label present;
  no title, no clipping, readable labels, no legend overlap.
- `addmet_mass_zero_jet`: PASS. CMS Open Data + Open Simulation label present;
  no title, no clipping, readable labels, no legend overlap.
- `approach_comparison`: PASS. CMS Open Simulation label present; no title,
  no clipping, and legend is in an empty region.
- `category_yields`: PASS. CMS Open Data + Open Simulation label present;
  no title, readable category labels, no legend overlap.
- `clean_jet_multiplicity`: PASS. CMS Open Data + Open Simulation label
  present; no title, readable labels, no legend overlap.
- `cutflow_summary`: PASS. CMS Open Data + Open Simulation label present;
  no title, long cutflow labels remain readable, no legend overlap.
- `met_pt`: PASS. CMS Open Data + Open Simulation label present; no title,
  readable labels, no legend overlap.
- `mt_mu_met`: PASS. CMS Open Data + Open Simulation label present; no title,
  readable labels, no legend overlap.
- `mu_pt`: PASS. CMS Open Data + Open Simulation label present; no title,
  readable labels, no legend overlap.
- `mva_input_modeling_chi2`: PASS. CMS Open Data + Open Simulation label
  present; no title, no clipping, labels are readable.
- `mva_score_templates`: FAIL. CMS Open Simulation label present and PDF/PNG
  pair exists, but the legend overlaps the background template and the x-axis
  label uses the raw class-style name `HistGradientBoosting score`.
- `pt_tautau_proxy`: PASS. CMS Open Data + Open Simulation label present;
  no title, readable labels, no legend overlap.
- `qcd_same_sign_mvis`: PASS. CMS Open Data + Open Simulation label present;
  no title, readable labels, no legend overlap.
- `sensitivity_nuisance_audit`: FAIL. CMS Open Simulation label present and
  PDF/PNG pair exists, but legend entries expose internal model identifiers.
- `sensitivity_variant_summary`: FAIL. CMS Open Simulation label present and
  PDF/PNG pair exists, but x-tick labels expose internal variant identifiers;
  the long vertical labels also produce an unusually tall rendered image.
- `tau_pt`: PASS. CMS Open Data + Open Simulation label present; no title,
  readable labels, no legend overlap.
- `vbf_delta_eta_jj`: PASS. CMS Open Data + Open Simulation label present;
  no title, readable labels, no legend overlap.
- `vbf_dijet_mass`: PASS. CMS Open Data + Open Simulation label present;
  no title, readable labels, no legend overlap.
- `visible_mass_boosted`: PASS. CMS Open Data + Open Simulation label present;
  no title, readable labels, no legend overlap.
- `visible_mass_vbf`: PASS. CMS Open Data + Open Simulation label present;
  no title, readable labels, no legend overlap.
- `visible_mass_zero_jet`: PASS. CMS Open Data + Open Simulation label
  present; no title, readable labels, no legend overlap.
- `w_high_mt_control_mt`: PASS. CMS Open Data + Open Simulation label present;
  no title, readable labels, no legend overlap.
- `z_rich_validation_mvis`: PASS. CMS Open Data + Open Simulation label
  present; no title, readable labels, no legend overlap.

## Artifact and Caption Checks

- Existing figure references in `SELECTION.md`: PASS. The 21 referenced
  existing figures all point to files under `outputs/figures/`, and each
  parsed caption has three sentences.
- New sensitivity figure references in `SELECTION.md`: FAIL. The three new
  figures are not referenced, so no captions exist for them.
- Expected-only caveat prose: PASS. Lines 383-388 state that the remediation
  uses only MC and Asimov expectations and does not tune on observed full-data
  signal-region discriminant distributions. Lines 407-412 state that the MVA
  improvement remains gated and requires Phase 4b validation or calibration
  uncertainty before use as an unqualified primary result.

## Verification

- `pixi run lint-plots`: PASS, no plotting violations found in 11 files.
- `identify phase3_selection/outputs/figures/*.png`: all 24 PNGs render and
  have nonzero dimensions.
- PDF/PNG pair check with `pixi run py`: PASS, all 24 Phase 3 PDFs have
  matching PNGs.
- `SELECTION.md` figure-reference parse with `pixi run py`: 21 existing
  references found; each existing caption has three sentences; the three new
  sensitivity figures are absent.
- Visual inspection: completed for all 24 Phase 3 PNG figures.
