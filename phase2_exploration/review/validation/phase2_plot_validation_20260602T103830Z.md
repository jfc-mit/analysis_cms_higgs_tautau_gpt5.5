# Phase 2 Plot Validation After Data Localization

Timestamp: 20260602T103830Z

Headline verdict: **FAIL: Category A plotting violations present.**

Scope:
- Read `agents/plot_validator.md` in full and followed its prompt template.
- Read `methodology/appendix-plotting.md` in full.
- Read Phase 2 scripts in `phase2_exploration/src/`.
- Read `phase2_exploration/outputs/EXPLORATION.md`.
- Read `phase2_exploration/outputs/local_sample_manifest.json`.
- Visually inspected every PNG in `phase2_exploration/outputs/figures/`.
- Did not modify exploration outputs.

## Code Linter Findings

Positive checks:
- `mh.style.use("CMS")` is applied in `phase2_exploration/src/plot_exploration.py:26`.
- All plotted figures use `figsize=(10, 10)`.
- No `ax.set_title()` calls found.
- No numeric `fontsize=` values found; legends use `fontsize="x-small"`.
- Saves use both PDF and PNG with `bbox_inches="tight"`, `dpi=200`, and `transparent=True` in `phase2_exploration/src/plot_exploration.py:44-45`.
- `plt.close(fig)` is called in `phase2_exploration/src/plot_exploration.py:46`.
- `mh.label.exp_label(...)` is called on every produced figure.
- No ratio plots are produced, so ratio-specific checks are not applicable.
- The derived-quantity trap is avoided in the overlay plots: `h.view()[:] = counts_array` at `phase2_exploration/src/plot_exploration.py:140` is paired with explicit `yerr=yerr` at `phase2_exploration/src/plot_exploration.py:141`.
- `pixi run lint-plots` completed with "No plotting violations found in 3 file(s)", but the repo linter does not catch all role-template checks below.

Category A findings:

1. `phase2_exploration/src/plot_exploration.py:64`
   - Check failed: raw-count histogram-like sample event counts are plotted with `ax.plot`, not `mh.histplot`.
   - Category: VIOLATION (A)
   - Affected figure: `sample_event_count_file_size.png`
   - Suggested fix: render event counts with a standards-compliant histogram/bar-style representation using `mh.histplot` where applicable, or document why this is a non-histogram diagnostic and use publication-quality point plotting with full uncertainty/label treatment.

2. `phase2_exploration/src/plot_exploration.py:164`
   - Check failed: raw selection yields are plotted with `ax.plot`, not `mh.histplot`.
   - Category: VIOLATION (A)
   - Affected figure: `preselection_yield_summary.png`
   - Suggested fix: use `mh.histplot` for raw counts or redesign as a publication-quality categorical yield chart with explicit justification and no legend overlap.

3. `phase2_exploration/src/plot_exploration.py:69`, `:99`, `:169`, `:184`
   - Check failed: labels are created directly from sample names and variable identifiers, exposing code-style names in rendered figures.
   - Category: VIOLATION (A)
   - Affected figures: `sample_event_count_file_size.png`, `branch_feature_availability.png`, `preselection_yield_summary.png`, `variable_separation_ranking.png`
   - Suggested fix: map sample and variable identifiers to publication-quality labels, e.g. `Run 2012B TauPlusX`, `VBF H to tau tau`, `Muon eta`, `Visible mass`, `mT(mu, MET)`.

4. `phase2_exploration/src/plot_exploration.py:75`, `:102`, `:146`, `:172`
   - Check failed: mixed data/MC plots use `llabel="Open Data / Open Simulation"` instead of the required unambiguous open-data/open-simulation labeling patterns.
   - Category: VIOLATION (A)
   - Affected figures: all mixed data/MC figures except `variable_separation_ranking.png`
   - Suggested fix: use a label convention that remains visibly unambiguous and does not imply an official result. If a plot combines data and MC, document and use a compact label such as `Open Data + Open Simulation`, or split data-only and MC-only diagnostics if needed.

## Artifact Figure Reference Checks

PASS:
- Every figure referenced in `EXPLORATION.md` exists as a PDF in `phase2_exploration/outputs/figures/`.
- Each referenced PDF has a corresponding PNG inspected here.
- All 13 figure captions in `EXPLORATION.md` are at least two sentences.
- No duplicate figure filenames were found in the figures directory.

Referenced figures checked:
- `figures/addmet_mass_slice.pdf`
- `figures/branch_feature_availability.pdf`
- `figures/dijet_deltaeta_slice.pdf`
- `figures/dijet_mass_slice.pdf`
- `figures/jet_multiplicity_slice.pdf`
- `figures/met_pt_slice.pdf`
- `figures/mt_mu_met_slice.pdf`
- `figures/muon_pt_slice.pdf`
- `figures/preselection_yield_summary.pdf`
- `figures/sample_event_count_file_size.pdf`
- `figures/tau_pt_slice.pdf`
- `figures/variable_separation_ranking.pdf`
- `figures/visible_mass_slice.pdf`

## Visual Validation By Figure

### `addmet_mass_slice.png`

PASS with warning.
- Text is legible, the experiment label is present, and no legend-data overlap is visible.
- Warning (C): the upper-right legend/headroom leaves substantial whitespace. Suggested fix: tighten the y-range or place the legend in a genuinely empty region without excessive range expansion.

### `branch_feature_availability.png`

FAIL.
- Check failed: visible y-axis tick labels include raw sample identifiers with underscores, e.g. `Run2012B_TauPlusX` and `VBF_HToTauTau`.
- Category: VIOLATION (A)
- Suggested fix: map samples to publication-quality labels.
- Check failed: experiment label components are cramped; visually, `Open Simulation` runs into the right-side `sqrt(s)` label.
- Category: VIOLATION (A)
- Suggested fix: use a shorter mixed-sample label or move the label location so left and right components do not collide.

### `dijet_deltaeta_slice.png`

PASS with warning.
- Text is legible, experiment label is present, and no overlap is visible.
- Warning (C): large empty upper-right area from legend/headroom. Suggested fix: tighten y-axis range or move legend.

### `dijet_mass_slice.png`

PASS with warning.
- Text is legible, experiment label is present, and no overlap is visible.
- Warning (C): large empty upper-right area from legend/headroom. Suggested fix: tighten y-axis range or use a log y-scale if the tail is the intended feature.

### `jet_multiplicity_slice.png`

PASS.
- Text is legible, experiment label is present, no raw variable labels are visible, and no overlap is visible.
- The figure is a raw-count diagnostic and inherits the code-level `mh.histplot` concern listed above only if treated as a histogram/count plot.

### `met_pt_slice.png`

PASS with warning.
- Text is legible, experiment label is present, and no overlap is visible.
- Warning (C): large empty upper-right area from legend/headroom. Suggested fix: tighten y-axis range or use a log y-scale if tail behavior is relevant.

### `mt_mu_met_slice.png`

PASS with warning.
- Text is legible, experiment label is present, and no overlap is visible.
- Warning (C): large empty upper-right area from legend/headroom. Suggested fix: tighten y-axis range or move legend.

### `muon_pt_slice.png`

PASS with warning.
- Text is legible, experiment label is present, and no overlap is visible.
- Warning (C): large empty upper-right area from legend/headroom. Suggested fix: tighten y-axis range or move legend.

### `preselection_yield_summary.png`

FAIL.
- Check failed: visible x-axis tick labels include raw sample identifiers with underscores, e.g. `Run2012B_TauPlusX` and `VBF_HToTauTau`.
- Category: VIOLATION (A)
- Suggested fix: map samples to publication-quality labels.
- Check failed: the legend overlaps plotted markers near the top-right of the axes.
- Category: VIOLATION (A)
- Suggested fix: move the legend outside the data region, use `mpl_magic` after confirming it creates a genuinely empty region, or redesign the categorical yield display.

### `sample_event_count_file_size.png`

FAIL.
- Check failed: visible x-axis tick labels include raw sample identifiers with underscores, e.g. `Run2012B_TauPlusX` and `VBF_HToTauTau`.
- Category: VIOLATION (A)
- Suggested fix: map samples to publication-quality labels.
- Warning (C): the dual-axis presentation is readable but visually dense. Suggested fix: consider two separate standards-compliant figures if the note needs both quantities.

### `tau_pt_slice.png`

PASS with warning.
- Text is legible, experiment label is present, and no overlap is visible.
- Warning (C): large empty upper-right area from legend/headroom. Suggested fix: tighten y-axis range or move legend.

### `variable_separation_ranking.png`

FAIL.
- Check failed: visible y-axis tick labels are code-derived variable names, e.g. `mt mu met`, `delta eta jj`, `m addmet`, `njet`.
- Category: VIOLATION (A)
- Suggested fix: map variables to publication-quality labels with physics notation or clear prose.
- Warning (C): the x-axis label `abs(AUC - 0.5)` is understandable but should be typeset more professionally, e.g. `|AUC - 0.5|`.

### `visible_mass_slice.png`

FAIL.
- Check failed: axis range/layout makes most bins visually compressed near zero because the first-bin spike dominates the y-scale.
- Category: VIOLATION (A)
- Suggested fix: use log y-scale, an inset/broken-axis treatment with explicit documentation, or a Phase 3-cleaned version before using the figure as a note-facing diagnostic. The artifact documents the physics caveat, but the rendered figure still fails readability for the bulk of the distribution.

## Data Localization And Paper-Level MC Limitation Check

PASS.
- The updated artifact explicitly documents that local reduced files are under `data/` and `mc/`.
- `phase2_exploration/src/explore_samples.py` now prefers local paths and falls back to the HTTPS mirror.
- `local_sample_manifest.json` records downloaded reduced samples, local paths, validation status, event counts, and paper-level components marked `missing-reduced` or `deferred-AOD-conversion`.
- `EXPLORATION.md` explicitly documents missing/deferred paper-level MC limitations and downstream final-analysis-note obligations.
- I saw no obvious contradiction between the manifest and the artifact's localization narrative.

## Required Fix Summary

Blocking Category A items:
- Replace raw code/sample/variable identifiers in rendered labels with publication-quality text.
- Resolve legend overlap in `preselection_yield_summary.png`.
- Resolve visual readability failure in `visible_mass_slice.png`.
- Address or formally justify the use of `ax.plot` for raw count/yield diagnostics under the plotting standards.
- Use a mixed data/MC open-data label convention that does not create cramped or ambiguous experiment labels.

Re-review required after fixes because Category A findings are present.
