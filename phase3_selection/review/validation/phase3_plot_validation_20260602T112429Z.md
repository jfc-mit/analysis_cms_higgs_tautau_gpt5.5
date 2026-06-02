# Phase 3 Plot Validation

Timestamp: 20260602T112429Z

Validator: Phase 3 plot validator

Headline verdict: FAIL. Category A plotting violations are present.

## Inputs Checked

- Role definition: `agents/plot_validator.md`
- Plotting standards: `methodology/appendix-plotting.md`
- Source files: `phase3_selection/src/build_selection.py`, `phase3_selection/src/model_inputs_and_mva.py`, `phase3_selection/src/compare_approaches.py`, `phase3_selection/src/plot_selection.py`
- Artifact: `phase3_selection/outputs/SELECTION.md`
- Rendered PNGs: all 21 PNG files in `phase3_selection/outputs/figures/`

## Code Linter Findings

1. `phase3_selection/src/plot_selection.py:109`
   - Check failed: open data labeling.
   - Category: VIOLATION (A).
   - Details: mixed data/MC figures use `llabel="Open Data + Open Sim."`. The plotting standard requires explicit open-data/open-simulation labeling. The abbreviated `Open Sim.` does not match the required `Open Simulation` wording.
   - Suggested fix: use a publication-quality label such as `llabel="Open Data + Open Simulation"` for mixed data/MC comparison plots, and keep `llabel="Open Simulation"` for MC-only plots.

2. `phase3_selection/src/plot_selection.py:128`, `:152`, `:173`, `:197`, `:213`
   - Check failed: legends use fixed `loc="upper right"` without `mpl_magic(ax)`.
   - Category: VIOLATION (A for affected visual overlaps, B otherwise).
   - Details: the standards prefer `mpl_magic(ax)` for y-axis scaling unless the legend is demonstrably in an empty region. At least `category_yields.png` visually places the legend in the same upper-right region as plotted zero-jet points.
   - Suggested fix: import and call `mpl_magic(ax)` after drawing each legend, or move legends to a proven empty region on a per-figure basis.

Positive source checks:

- `mh.style.use("CMS")` is applied.
- All plotted figures use `figsize=(10, 10)`.
- No `ax.set_title()` calls found.
- No forbidden `plt.colorbar`, `fig.colorbar(..., ax=...)`, `tight_layout`, `constrained_layout`, `ax.text`, `ax.annotate`, `ax.step`, or `ax.bar` patterns found.
- Figures are saved as both PDF and PNG with `bbox_inches="tight"`, `dpi=200`, and `transparent=True`.
- `plt.close(fig)` is called after saving.
- Derived normalized histograms assigned with `h.view()[:] = norm` are plotted with explicit `yerr=`, so the mplhep sqrt(bin-content trap is not present for those plots.

## Artifact Figure Reference Check

All 21 figure references in `SELECTION.md` exist as matching PDF and PNG outputs. Every referenced caption is at least two sentences.

No duplicate figure filenames were found.

## Visual Inspection By Figure

- `addmet_mass_boosted.png`: FAIL. Open-data label uses `Open Data + Open Sim.` rather than the required open-simulation wording. Otherwise text is readable, legend is clear, and no data overlap is visible.
- `addmet_mass_vbf.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable; sparse VBF statistics produce large but plausible statistical error bars.
- `addmet_mass_zero_jet.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable, with no legend overlap.
- `approach_comparison.png`: FAIL. The MC-only open label is correct, but the x-axis layout places the two points at the plot-frame edges with excessive empty space and the first point close to the upper-left frame; this is a layout violation affecting readability. Suggested fix: use a bar-style categorical comparison or set explicit x-limits with padding.
- `category_yields.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. The upper-right legend occupies the same region as the high zero-jet category points, consistent with the source-level legend-without-`mpl_magic` problem.
- `clean_jet_multiplicity.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable, with clear axes and no visible clipping.
- `cutflow_summary.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Axis labels and rotated tick labels are readable; no clipping was observed.
- `met_pt.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable and physically populated.
- `mt_mu_met.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable; no legend overlap.
- `mu_pt.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable; no legend overlap.
- `mva_input_modeling_chi2.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Some x tick labels are mechanically converted variable names (`pt tautau proxy`, `btag max`) rather than fully publication-quality names; improve these labels.
- `pt_tautau_proxy.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable; no legend overlap.
- `qcd_same_sign_mvis.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable; large signal-MC statistical error bars are plausible for sparse sideband signal MC.
- `tau_pt.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable.
- `vbf_delta_eta_jj.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable; large errors are plausible for the two-jet subset.
- `vbf_dijet_mass.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable; no legend overlap.
- `visible_mass_boosted.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable; no legend overlap.
- `visible_mass_vbf.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable; sparse VBF statistics produce large but plausible statistical error bars.
- `visible_mass_zero_jet.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable; no legend overlap.
- `w_high_mt_control_mt.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable; no legend overlap.
- `z_rich_validation_mvis.png`: FAIL. Open-data label uses `Open Data + Open Sim.`. Otherwise readable; no legend overlap.

## Required Fixes Before PASS

1. Replace `Open Data + Open Sim.` with standards-compliant `Open Data + Open Simulation` or another explicitly approved open-data/open-simulation wording.
2. Add `mpl_magic(ax)` legend scaling or validated per-figure legend placement, with particular attention to `category_yields.png`.
3. Redesign `approach_comparison.png` so the categorical points are not pinned to the plot-frame edges.
4. Improve publication labels in `mva_input_modeling_chi2.png`, especially mechanically converted variable names.
