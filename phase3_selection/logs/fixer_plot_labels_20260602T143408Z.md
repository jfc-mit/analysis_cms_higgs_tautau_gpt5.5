# Phase 3 Plot-Label Fixer

## 2026-06-02T14:34:08Z

Read `agents/fixer.md` and the failed plot-validation report
`phase3_selection/review/validation/phase3_plot_validation_sensitivity_20260602T142729Z.md`.

Findings to resolve:

- Category A: sensitivity figures expose internal model/config labels.
- Category A: `mva_score_templates` legend overlaps plotted background content.
- Category B: `SELECTION.md` does not reference the three new sensitivity figures.

Planned minimum fix:

- Add display-label helpers in `phase3_selection/src/sensitivity_regression.py`
  for plotted variant names, nuisance modes, model labels, and classifier-score
  axes without changing model keys or statistical results.
- Move the classifier-score legend outside the axes and add headroom.
- Regenerate the existing Phase 3 sensitivity outputs, then verify plots,
  markdown references, and whitespace.

## 2026-06-02T14:40:30Z

Resolved the Category A label findings by adding explicit display labels for
model variants, nuisance modes, and the classifier score axis. Resolved the
classifier-score legend overlap by placing the legend outside the plotting
area and increasing y-axis headroom. Resolved the Category B artifact finding
by adding all three sensitivity figures to `SELECTION.md` with interpretive
expected-only captions.

Regenerated `phase3-sensitivity`; the sensitivity JSON checksums matched the
pre-run values exactly. Neighborhood check: visually inspected
`mva_score_templates`, `sensitivity_variant_summary`, and
`sensitivity_nuisance_audit`; rerendered the variant summary from existing JSON
after compacting labels to avoid tick-label collision.
