# Phase 2 Plot Fixer Log

Timestamp: 20260602T105002Z

## Inputs Read

- `agents/fixer.md`
- `phase2_exploration/review/validation/phase2_plot_validation_20260602T103830Z.md`
- `phase2_exploration/src/plot_exploration.py`
- `phase2_exploration/outputs/EXPLORATION.md`
- `methodology/appendix-plotting.md`
- `experiment_log.md`

## Finding Resolution

- Raw identifiers in visible labels: RESOLVED. Added explicit sample, feature,
  and variable display-label maps and regenerated all Phase 2 figures.
- `preselection_yield_summary.png` legend overlap: RESOLVED. Moved the legend
  outside the plotting area and verified it no longer overlaps markers.
- `visible_mass_slice.png` readability failure: RESOLVED. Switched the visible
  mass diagnostic to log-y rendering so non-spike bins remain readable.
- `ax.plot` for raw count/yield diagnostics: RESOLVED. Replaced event-count and
  preselection-yield raw counts with `mh.histplot` errorbar rendering. Kept
  file size as a metadata scatter diagnostic with an inline justification.
- Mixed data/MC label collision: RESOLVED. Shortened the mixed open-data/open-
  simulation label to `Open Data + Open Sim.` and visually checked the affected
  diagnostics.

## Verification

- Ran `pixi run phase2-plots` successfully.
- Ran `pixi run lint-plots` successfully after regeneration; result:
  "No plotting violations found in 3 file(s)."
- Visually inspected the regenerated PNGs that failed validation:
  `sample_event_count_file_size.png`, `branch_feature_availability.png`,
  `preselection_yield_summary.png`, `visible_mass_slice.png`, and
  `variable_separation_ranking.png`. Also spot-checked `muon_pt_slice.png` for
  the shared mixed-label placement.

## Neighborhood Check

- Checked the plotting script for remaining `ax.bar`, `ax.step`, `set_title`,
  `tight_layout`, and old `Open Data / Open Simulation` label usage.
- Confirmed the remaining `ax.plot` call is the non-histogram single-variable
  separation diagnostic, not a raw event-count histogram.
- No numerical analysis values changed, so no downstream numeric propagation
  was required.
