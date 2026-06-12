# Phase 5 Plot Re-Validation

Session: `phase5_full_panel_plot_rerevalidation_20260612T185507Z`

## Scope

- `phase5_documentation/src/build_phase5_docs.py`
- `phase5_documentation/outputs/figures/*.png`
- `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md`
- `methodology/appendix-plotting.md`
- `agents/plot_validator.md`

## Deterministic Lint

Command:

```bash
pixi run lint-plots
```

Result:

```text
Pixi task (lint-plots): python conventions/lint_plots.py .
No plotting violations found in 18 file(s).
```

Additional source checks on `phase5_documentation/src/build_phase5_docs.py` found:

- `mh.style.use("CMS")`: present.
- `figsize=(10, 10)`: used for generated figures; one ratio plot uses the required 10-by-10 canvas.
- `ax.set_title(...)`: none.
- Numeric `fontsize=`: none.
- `tight_layout()` / `constrained_layout=True`: none.
- `savefig(..., bbox_inches="tight", dpi=200, transparent=True)`: present for both PDF and PNG through the shared save helper.
- `plt.close(fig)`: present in the shared save helper.
- `mh.label.exp_label(...)`: present through the shared label helper.
- `data=False`: none.
- Ratio plot `sharex=True` and `fig.subplots_adjust(hspace=0)`: present.
- `.view()[:] =` / `.view()[:] +=`: none.
- `histtype="errorbar"`: none.
- Raw `ax.text(...)` / `ax.annotate(...)`: none.
- `plt.colorbar(...)` / `fig.colorbar(...)`: none.

## Artifact Consistency

`ANALYSIS_NOTE_5_v1.md` references 31 figure PDFs. The final figure directory contains 31 PNGs and 31 PDFs. Every referenced PDF has a matching PNG, every referenced PDF exists, and there are no unreferenced PNGs in `phase5_documentation/outputs/figures/`.

## Findings

### VIOLATION A: Non-standard open-data label abbreviation

1. Figure: `sample_event_count_file_size.png`
2. Failed check: Open data labeling / label quality. The rendered experiment label reads `CMS Open Data + Open Sim.`. The Phase 5 plotting spec requires explicit open-data/open-simulation status using `Open Data` and `Open Simulation`; the abbreviation `Open Sim.` is non-standard and should not appear in final AN figures.
3. Category: VIOLATION (A).
4. Suggested fix: Regenerate the figure with a non-abbreviated open-data label, e.g. `llabel="Open Data + Open Simulation"` for the mixed sample-inventory plot, or split the label by data/simulation content if this figure is regenerated from an upstream phase script. Re-run `pixi run lint-plots` and visually re-check the updated PNG.

No other rendered PNG showed spurious ratio-panel artifacts, raw/internal visible labels, label collisions, missing experiment labels, unreadable comparison content, or unreferenced final-figure clutter.

## Per-Figure Visual Inspection

| Figure | Visual result |
|---|---|
| `approach_comparison.png` | PASS |
| `category_yields.png` | PASS |
| `cutflow_summary.png` | PASS |
| `expected_s_over_b.png` | PASS |
| `gof_toys.png` | PASS |
| `met_pt.png` | PASS |
| `mt_mu_met.png` | PASS |
| `mu_pt.png` | PASS |
| `mva_input_modeling_chi2.png` | PASS |
| `phase5_baseline_limit_summary.png` | PASS |
| `phase5_baseline_validation_summary.png` | PASS |
| `phase5_baseline_visible_boosted.png` | PASS |
| `phase5_baseline_visible_vbf.png` | PASS |
| `phase5_baseline_visible_zero_jet.png` | PASS |
| `phase5_category_mu_comparison.png` | PASS |
| `phase5_nuisance_pulls_baseline.png` | PASS |
| `phase5_rejected_score_diagnostics.png` | PASS |
| `phase5_systematic_program_baseline.png` | PASS |
| `pt_tautau_proxy.png` | PASS |
| `qcd_same_sign_mvis.png` | PASS |
| `sample_event_count_file_size.png` | FAIL: non-standard `Open Sim.` abbreviation in experiment label |
| `sensitivity_nuisance_audit.png` | PASS |
| `signal_injection_recovery.png` | PASS |
| `tau_pt.png` | PASS |
| `vbf_delta_eta_jj.png` | PASS |
| `vbf_dijet_mass.png` | PASS |
| `visible_mass_boosted.png` | PASS |
| `visible_mass_vbf.png` | PASS |
| `visible_mass_zero_jet.png` | PASS |
| `w_high_mt_control_mt.png` | PASS |
| `z_rich_validation_mvis.png` | PASS |

## Ratio-Panel Checks

The three final Phase 5 visible-mass ratio plots were visually inspected:

- `phase5_baseline_visible_boosted.png`: PASS. No visible gap between main and ratio panels; no experiment label or stray shared-axis artifact appears in the ratio panel.
- `phase5_baseline_visible_vbf.png`: PASS. No visible gap between main and ratio panels; no experiment label or stray shared-axis artifact appears in the ratio panel.
- `phase5_baseline_visible_zero_jet.png`: PASS. No visible gap between main and ratio panels; no experiment label or stray shared-axis artifact appears in the ratio panel.

## Verdict

PLOT VALIDATION FAILS pending correction of `sample_event_count_file_size.png` because the rendered figure contains a non-standard open-simulation abbreviation in the experiment label. All other checked code, artifact-consistency, and visual criteria pass.
