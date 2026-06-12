# Phase 5 Plot Validation

Session: `20260612T175456Z`

Scope reviewed:
- Plotting scripts in `phase5_documentation/src/` and upstream plotting scripts whose figures are copied into the Phase 5 figure directory.
- Rendered PNGs in `phase5_documentation/outputs/figures/`: 78 files, all visually inspected.
- Final note figure references in `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md`.
- Plotting standards in `methodology/appendix-plotting.md` and deterministic checks in `conventions/lint_plots.py`.

## Verdict

FAIL. The deterministic linter passes, but the visual inspection finds multiple Category A plotting failures in figures present in the final Phase 5 figure directory, including figures referenced by the final analysis note.

Blocking themes:
- RED FLAG: spurious `x` text artifact at the main/ratio boundary in many ratio plots.
- VIOLATION (A): experiment-label text collisions in several Phase 5 summary plots.
- VIOLATION (A): non-standard open-data/open-simulation labels, including shortened `Open Sim.` and custom `Open Data diagnostic` labels.
- VIOLATION (A): raw/internal variable names visible in rendered plots.
- VIOLATION (A): public plot text includes process/environment status sentences rather than physics labels or captions.
- VIOLATION (A): some comparison figures are not readable at analysis-note rendering size because long labels and legends dominate the canvas.

## Deterministic Checks

Commands run:

```bash
pixi run lint-plots
pixi run py conventions/lint_plots.py
```

Result: both commands reported `No plotting violations found in 18 file(s).`

Additional deterministic checks:
- Final note references 10 figure assets; all referenced assets exist.
- Final figure directory contains 78 PNG files.
- Duplicate rendered PNG content found:
  - `observed_primary_score_boosted.png` and `observed_score_boosted.png`
  - `observed_primary_score_vbf.png` and `observed_score_vbf.png`
  - `observed_primary_score_zero_jet.png` and `observed_score_zero_jet.png`
  These are exact duplicate images under different filenames. This is not a blocking plotting-standard failure by itself, but it should be intentional and documented if both names remain.

## Code-Level Findings

1. `phase2_exploration/src/plot_exploration.py:28` uses `Open Data + Open Sim.`.
   - Check failed: open data labeling must use publication-quality wording, not shortened labels.
   - Category: VIOLATION (A).
   - Suggested fix: use the full visible wording, for example `Open Data + Open Simulation`, and regenerate copied Phase 2 figures.

2. `phase4_inference/4c_observed/src/plot_observed_results.py:69` appends unexplained `ref.` to the experiment-label right text.
   - Check failed: visible plot labels must be self-contained and publication quality.
   - Category: VIOLATION (A).
   - Suggested fix: remove the unexplained qualifier from the rendered plot label; if a qualification is needed, explain it in the caption or note body.

3. `phase5_documentation/src/build_phase5_docs.py:107` and `phase5_documentation/src/build_phase5_docs.py:118` use custom `Open Data diagnostic` labels.
   - Check failed: open data labeling must render as `Open Data` or `Open Simulation`; analysis-status qualifiers do not belong in the experiment label.
   - Category: VIOLATION (A).
   - Suggested fix: use standard open-data labels and put diagnostic/context wording in captions.

4. `phase5_documentation/src/build_phase5_docs.py:112` appends unexplained `ref.` to the experiment-label right text.
   - Check failed: visible plot labels must be self-contained and publication quality.
   - Category: VIOLATION (A).
   - Suggested fix: remove the qualifier from the plot label and move any needed explanation to the caption.

## Visual Validation By Figure

### `addmet_mass_boosted.png`
PASS.

### `addmet_mass_slice.png`
VIOLATION (A): experiment label uses shortened `Open Sim.` rather than the required full open-simulation wording. Regenerate with full publication-quality label text.

### `addmet_mass_vbf.png`
PASS.

### `addmet_mass_zero_jet.png`
PASS.

### `approach_comparison.png`
PASS.

### `branch_feature_availability.png`
VIOLATION (A): experiment label uses shortened `Open Sim.`. Regenerate with full open-simulation wording.

### `category_yields.png`
PASS.

### `clean_jet_multiplicity.png`
PASS.

### `comparison_to_4a_4b.png`
VIOLATION (A): right-side experiment-label text contains an unexplained `ref.` qualifier. Remove from the plot label or explain in the caption.

### `cutflow_summary.png`
PASS.

### `dijet_deltaeta_slice.png`
VIOLATION (A): experiment label uses shortened `Open Sim.`. Regenerate with full open-simulation wording.

### `dijet_mass_slice.png`
VIOLATION (A): experiment label uses shortened `Open Sim.`. Regenerate with full open-simulation wording.

### `expected_mva_score_boosted.png`
VIOLATION (A): x-axis label `mva score hist gradient boosting` is an internal variable/model name, not publication-quality text. Replace with a readable label such as `Gradient-boosted classifier score`.

### `expected_mva_score_vbf.png`
VIOLATION (A): x-axis label `mva score hist gradient boosting` is not publication-quality text. Replace with a readable label.

### `expected_mva_score_zero_jet.png`
VIOLATION (A): x-axis label `mva score hist gradient boosting` is not publication-quality text. Replace with a readable label.

### `expected_nuisance_summary.png`
VIOLATION (A): x-axis tick labels include raw handles such as `lumi_2012`, `dy ztautau open data`, `wjets high mt control`, and `global MC stat proxy`. Replace with publication-quality systematic-source names.

### `expected_s_over_b.png`
PASS.

### `gof_toys.png`
PASS.

### `input_reweighting_chi2.png`
VIOLATION (A): y-axis tick labels show raw variable identifiers such as `m_vis`, `mu_pt`, `tau_pt`, `met_pt`, `mt_mu_met`, and `pt_tautau_proxy`. Replace with publication-quality variable names.

### `jet_multiplicity_slice.png`
VIOLATION (A): experiment label uses shortened `Open Sim.`. Regenerate with full open-simulation wording.

### `met_pt.png`
PASS.

### `met_pt_slice.png`
VIOLATION (A): experiment label uses shortened `Open Sim.`. Regenerate with full open-simulation wording.

### `mt_mu_met.png`
PASS.

### `mt_mu_met_slice.png`
VIOLATION (A): experiment label uses shortened `Open Sim.`. Regenerate with full open-simulation wording.

### `mu_pt.png`
PASS.

### `muon_pt_slice.png`
VIOLATION (A): experiment label uses shortened `Open Sim.`. Regenerate with full open-simulation wording.

### `mva_input_modeling_chi2.png`
PASS.

### `mva_score_templates.png`
PASS.

### `observed_addmet_boosted.png`
RED FLAG: spurious `x` text is rendered at the lower-right edge of the main panel above the ratio panel. Remove the main-panel x-axis label/text and leave the x label only on the ratio axis.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `observed_addmet_vbf.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary. Remove the main-panel x-axis label/text.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `observed_addmet_zero_jet.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary. Remove the main-panel x-axis label/text.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `observed_limit_significance_summary.png`
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`. Remove or explain in caption.

### `observed_mvis_boosted.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `observed_mvis_vbf.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `observed_mvis_zero_jet.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `observed_primary_score_boosted.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `observed_primary_score_vbf.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary.
VIOLATION (A): the legend overlaps plotted content in the high-score region, including the signal overlay and full-data error bars. Move the legend or rescale the y-axis with `mpl_magic(ax)`.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `observed_primary_score_zero_jet.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `observed_pull_ratio_summary.png`
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `observed_score_boosted.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `observed_score_vbf.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary.
VIOLATION (A): the legend overlaps plotted content in the high-score region, including the signal overlay and full-data error bars. Move the legend or rescale the y-axis with `mpl_magic(ax)`.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `observed_score_zero_jet.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `observed_visible_boosted.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `observed_visible_vbf.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `observed_visible_zero_jet.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `partial_mvis_summary.png`
VIOLATION (A): legend label `mvis 10% data/MC` uses an internal variable shorthand. Replace with publication-quality text such as `Visible-mass data/MC ratio`.

### `partial_pull_summary.png`
VIOLATION (A): x-axis tick labels include internal bin identifiers such as `zero_jet b0`. Replace with publication-quality category/bin labels.

### `partial_score_boosted.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary. Remove the main-panel x-axis label/text.

### `partial_score_vbf.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary. Remove the main-panel x-axis label/text.

### `partial_score_zero_jet.png`
RED FLAG: spurious `x` text is rendered at the main/ratio boundary. Remove the main-panel x-axis label/text.

### `phase5_category_mu_comparison.png`
VIOLATION (A): experiment-label components overlap badly; `Open Data diagnostic` collides with the right-side energy/luminosity label.
VIOLATION (A): open-data label uses a non-standard diagnostic qualifier.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.
VIOLATION (A): the x-axis label uses plain `mu`; use a publication-quality signal-strength label.

### `phase5_hgb_permutation_importance.png`
VIOLATION (A): experiment-label components overlap near the top of the plot.
VIOLATION (A): y-axis tick labels are raw feature identifiers (`m_vis`, `btag_max`, `jet1_pt`, `met_pt`, `delta_eta_jj`, `n_clean_jets`, `pt_tautau_proxy`, `m_addmet`, `tau_reliso`). Replace with publication-quality feature names.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `phase5_mu_limit_comparison.png`
VIOLATION (A): the long y-axis labels and large legend dominate the canvas; this will not be legible at analysis-note rendering size.
VIOLATION (A): open-data label uses a non-standard diagnostic qualifier.
VIOLATION (A): the x-axis label uses plain `mu`; use a publication-quality signal-strength label.
WARNING (B): the figure mixes current-analysis quantities with external comparison rows. If kept in a standalone analysis note, the caption and labels need to make the comparison scope self-contained and clearly separated from the current result.

### `phase5_mva_auc_summary.png`
VIOLATION (A): experiment-label components overlap near the top of the plot.
VIOLATION (A): rendered plot contains a process/environment sentence: `Transformer not trained: no fast attention stack in the pixi environment.` This belongs in prose, not inside a physics figure.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `phase5_mva_roc.png`
VIOLATION (A): experiment-label components overlap near the top of the plot.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `phase5_primary_vs_baseline_mu.png`
VIOLATION (A): open-data label uses a non-standard diagnostic qualifier.
VIOLATION (A): the x-axis label uses plain `mu`; use a publication-quality signal-strength label.

### `phase5_significance_comparison.png`
VIOLATION (A): experiment-label components overlap badly; `Open Data diagnostic` collides with the right-side energy/luminosity label.
VIOLATION (A): long y-axis labels and wide bars make the figure difficult to read at analysis-note rendering size.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.
WARNING (B): the figure mixes current-analysis quantities with external comparison rows. If kept, make the comparison scope self-contained and clearly separated from the current result.

### `phase5_transformer_feasibility.png`
VIOLATION (A): experiment-label components overlap near the top of the plot.
VIOLATION (A): rendered plot contains a process/environment sentence about downscoping and availability. This belongs in prose, not inside a physics figure.
VIOLATION (A): the long annotation collides with the lower axis region and is not readable at analysis-note rendering size.
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`.

### `preselection_yield_summary.png`
VIOLATION (A): experiment label uses shortened `Open Sim.`. Regenerate with full open-simulation wording.

### `pt_tautau_proxy.png`
PASS.

### `qcd_same_sign_mvis.png`
PASS.

### `sample_event_count_file_size.png`
VIOLATION (A): experiment label uses shortened `Open Sim.`. Regenerate with full open-simulation wording.

### `sensitivity_nuisance_audit.png`
PASS.

### `sensitivity_variant_summary.png`
VIOLATION (A): plot content is compressed into a small area because long y-axis labels force an extremely wide rendered canvas. The figure will be illegible at analysis-note rendering size. Shorten labels or split into a table plus simpler plot.

### `signal_injection_recovery.png`
PASS.

### `tau_pt.png`
PASS.

### `tau_pt_slice.png`
VIOLATION (A): experiment label uses shortened `Open Sim.`. Regenerate with full open-simulation wording.

### `variable_separation_ranking.png`
PASS.

### `vbf_delta_eta_jj.png`
PASS.

### `vbf_dijet_mass.png`
PASS.

### `visible_mass_boosted.png`
PASS.

### `visible_mass_slice.png`
VIOLATION (A): experiment label uses shortened `Open Sim.`. Regenerate with full open-simulation wording.

### `visible_mass_vbf.png`
PASS.

### `visible_mass_zero_jet.png`
PASS.

### `w_high_mt_control_mt.png`
PASS.

### `w_highmt_scale.png`
PASS.

### `w_highmt_scale_full.png`
VIOLATION (A): right-side experiment-label text contains unexplained `ref.`. Remove from the plot label or explain in the caption.

### `z_rich_validation_mvis.png`
PASS.

## Data/MC Comparison Checks

Data/MC comparison figures generally use visible data points and ratio panels without obvious missing error bars. However:
- The ratio-panel figures listed above have a spurious `x` artifact at the main/ratio boundary, which is an automatic Category A rendering red flag.
- `observed_primary_score_vbf.png` and its duplicate `observed_score_vbf.png` have legend overlap with plotted content.
- Several data/MC plots have large visible data/prediction deviations, but I do not classify those as plotting failures by themselves; they need physics/statistics review rather than plot validation unless caused by a plotting normalization bug.

## Required Fixes Before PASS

1. Regenerate all ratio plots with the spurious `x` artifact removed.
2. Remove unexplained `ref.` text from experiment labels or move the explanation to captions.
3. Replace shortened and non-standard open-data/open-simulation labels with standard publication-quality labels.
4. Replace raw variable handles and internal labels with publication-quality text.
5. Redesign the Phase 5 summary plots with header collisions, unreadable long labels, and process/environment sentences.
6. Re-run `pixi run lint-plots` after regeneration and repeat visual inspection of all affected PNGs.
