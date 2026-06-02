# Phase 2 Plot Re-Validation After Fixes

Timestamp: 20260602T105441Z

Headline verdict: **PASS.** The previous Category A plot findings are resolved, and the regenerated Phase 2 figures pass the plot-validator code and visual checks.

## Scope

- Read `agents/plot_validator.md` in full and followed its prompt template.
- Read `methodology/appendix-plotting.md` in full.
- Read the previous failed validation:
  `phase2_exploration/review/validation/phase2_plot_validation_20260602T103830Z.md`.
- Read the fixer log:
  `phase2_exploration/logs/fixer_phase2_plots_20260602T105002Z.md`.
- Read Phase 2 scripts in `phase2_exploration/src/`.
- Read the updated Phase 2 artifact:
  `phase2_exploration/outputs/EXPLORATION.md`.
- Visually inspected every PNG in `phase2_exploration/outputs/figures/`.
- Ran `pixi run lint-plots`.
- Did not modify analysis outputs or plotting code.

## Previous Category A Findings

All previous blocking findings are resolved:

| Previous finding | Status | Evidence |
|---|---|---|
| Raw sample and variable identifiers visible in rendered labels | Resolved | `plot_exploration.py` now defines sample, feature, and variable display-label maps; inspected figures show publication labels without raw underscores. |
| `preselection_yield_summary.png` legend overlap | Resolved | Legend is outside the data axes and no longer overlaps markers. |
| `visible_mass_slice.png` readability failure from first-bin spike | Resolved | Plot now uses log-y rendering; non-spike bins are visible across the mass range. |
| `ax.plot` used for raw count/yield diagnostics | Resolved | Event counts and preselection yields are rendered with `mh.histplot(..., histtype="errorbar")`; the remaining separation ranking uses point plotting for a non-histogram diagnostic. |
| Mixed open-data/open-simulation label collision | Resolved | Rendered mixed figures use `CMS Open Data + Open Sim.` without collision with the `8 TeV` right label. |

## Code Linter Findings

Positive checks:

- `mh.style.use("CMS")` is applied in `phase2_exploration/src/plot_exploration.py:26`.
- All figures use `figsize=(10, 10)`.
- No `ax.set_title()` calls found.
- No numeric `fontsize=` values found; legends use `fontsize="x-small"`.
- Saves use both PDF and PNG with `bbox_inches="tight"`, `dpi=200`, and `transparent=True` in `phase2_exploration/src/plot_exploration.py:85-86`.
- `plt.close(fig)` is called in `phase2_exploration/src/plot_exploration.py:87`.
- `mh.label.exp_label(...)` is called on every produced figure.
- Open-data/open-simulation labels are explicit: mixed figures use `Open Data + Open Sim.`, and the MC-only separation plot uses `Open Simulation`.
- The 2D availability figure uses `mh.utils.make_square_add_cbar(ax)` and `fig.colorbar(im, cax=cax)`, not a forbidden colorbar pattern.
- No ratio plots are produced, so ratio-specific checks are not applicable.
- The derived-quantity trap is avoided: `h.view()[:] = counts_array` is paired with explicit `yerr=yerr` in `mh.histplot(...)`.
- `pixi run lint-plots` passed with `No plotting violations found in 3 file(s).`

No Category A or B code-linter findings remain.

## Artifact Figure Reference Checks

PASS:

- Every figure referenced in `EXPLORATION.md` exists as a PDF in `phase2_exploration/outputs/figures/`.
- Each referenced PDF has a corresponding PNG inspected here.
- No duplicate PNG content was found by checksum.

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

PASS. Text is legible, the experiment label is present, labels are publication-quality, error bars are plausible for the normalized slice diagnostic, and the legend does not overlap plotted data. Non-blocking note: the legend/headroom leaves a large empty upper-right region, but readability is not impaired.

### `branch_feature_availability.png`

PASS. Raw sample identifiers and raw feature names have been replaced with readable labels. The colorbar is properly placed, the experiment label does not collide with the right-side energy label, and all tick labels are legible.

### `dijet_deltaeta_slice.png`

PASS. Text and tick labels are legible, the experiment label is present, and the legend is clear of the plotted points. Non-blocking note: the y-axis headroom is generous.

### `dijet_mass_slice.png`

PASS. The figure is legible, units are present, and there is no legend-data overlap. Non-blocking note: the upper-right headroom remains large, but the plotted distribution and tail are readable.

### `jet_multiplicity_slice.png`

PASS. The raw-count diagnostic is rendered with visible uncertainties, readable labels, and no legend-data overlap.

### `met_pt_slice.png`

PASS. Text is legible, units are present, the experiment label is clean, and the legend does not overlap the distribution. Non-blocking note: substantial empty space remains above the data.

### `mt_mu_met_slice.png`

PASS. Text is legible, the label quality is acceptable, and no overlap is visible. Non-blocking note: y-axis headroom is large but not blocking.

### `muon_pt_slice.png`

PASS. Text is legible, units are present, and the legend is isolated from plotted points. Non-blocking note: y-axis headroom is large.

### `preselection_yield_summary.png`

PASS. The previous legend overlap is resolved by placing the legend outside the data axes. Sample labels are readable and publication-quality; the log-y range is appropriate for the multi-region raw-yield diagnostic.

### `sample_event_count_file_size.png`

PASS. The previous raw sample identifiers are replaced with readable sample labels, and the event-count portion is now rendered with `mh.histplot` error bars. The dual-axis display is dense but readable; no blocking overlap or label collision is present.

### `tau_pt_slice.png`

PASS. Text is legible, units are present, and no overlap is visible. Non-blocking note: y-axis headroom is large.

### `variable_separation_ranking.png`

PASS. Variable labels are publication-quality and the x-axis now uses a typeset `|AUC - 0.5|` label. The point diagnostic is readable and does not expose raw variable identifiers.

### `visible_mass_slice.png`

PASS. The previous linear-scale compression is resolved by the log-y rendering. The first-bin spike is visible without hiding the rest of the mass distribution, error bars are plausible, and the legend does not overlap data.

## Remaining Issues

No Category A or B issues remain.

Non-blocking Category C notes:

- Several normalized overlay plots retain large y-axis headroom to keep legends clear. This is visually conservative and readable, but future note-facing plots could tighten legend placement or y-limits once Phase 3 final selections stabilize.
- `sample_event_count_file_size.png` uses a dense dual-axis diagnostic. It is acceptable for Phase 2 exploration, but the final AN may prefer separated event-count and file-size diagnostics if either plot becomes note-facing.

## Final Verdict

**PASS.** Phase 2 plotting fixes resolve the previous blocking findings, and the regenerated figures pass both code-linter and visual validation checks.
