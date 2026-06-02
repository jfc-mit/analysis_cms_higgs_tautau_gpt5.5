# Phase 3 Plot and Provenance Rereview

Timestamp: 20260602T121228Z

Validator: fresh Phase 3 plot/provenance validator

Headline verdict: PASS. No unresolved Category A or Category B findings.

## Scope

This rereview checked the previously failed Phase 3 plot validation items from
`phase3_selection/review/validation/phase3_plot_validation_20260602T112429Z.md`
after fixes in commits `e0dd136`, `355120c`, and `4d2d03e`.

Checked inputs:

- `phase3_selection/outputs/SELECTION.md`
- `phase3_selection/outputs/normalization_inputs.json`
- `phase3_selection/src/plot_selection.py`
- `phase3_selection/src/build_selection.py`
- `phase2_exploration/outputs/local_sample_manifest.json`
- all figures in `phase3_selection/outputs/figures/`

## Commands

| Command | Outcome |
|---|---|
| `pixi run lint-plots` | Passed: no plotting violations found. |
| `pixi run py - <<'PY' ... figure dimension check ... PY` | Passed: all 21 PNGs are present and readable. |
| `pixi run py - <<'PY' ... markdown figure-reference check ... PY` | Passed: 21 unique figure references, no missing PDF/PNG targets, no unreferenced PDFs, no duplicate references. |
| `grep -RIn "Open Sim\|Open Simulation\|set_title\|tight_layout\|constrained_layout\|source_url\|2012/skim\|entries\|back-calculation\|back-calcul" ...` | Used as a targeted provenance/plotting string audit. No blocking issues found. |

## Plot Findings

No Category A or Category B findings.

Resolved checks:

- Mixed data/MC figures use the explicit CMS label wording `Open Data + Open Simulation`.
- The MC-only approach-comparison figure uses `Open Simulation`.
- All 21 generated figures have PDF and PNG pairs.
- No `ax.set_title()` use was found in the Phase 3 plotting source.
- The source uses CMS mplhep style, 10-by-10 inch figures, `bbox_inches="tight"`, `dpi=200`, transparent output, and closes figures after saving.
- The category-yields legend no longer visibly clips or obscures the plotted category points in full-resolution inspection.
- The approach-comparison categorical points have x-axis padding and are not pinned to the plot-frame edges.
- The MVA input modelling labels are no longer mechanically converted branch names for the previously flagged variables; labels such as `Visible+MET p_T proxy`, `Leading jet p_T`, and `Maximum b-tag score` are explicit.
- No ratio-panel spacing issue is applicable: these Phase 3 plots are single-panel figures.

Category C suggestions: none.

## Artifact References

`SELECTION.md` contains 21 unique figure references. Every referenced PDF exists
under `phase3_selection/outputs/figures/`, and every referenced PDF has a
matching PNG. No unreferenced Phase 3 PDFs were found. Captions remain
consistent with the current outputs and are multi-sentence captions.

## Provenance Findings

No Category A or Category B findings.

Resolved checks:

- `SELECTION.md` explicitly states that local ROOT `Events` entries are only
  processing, shape, and cutflow entries; they are not luminosity inputs or MC
  generation denominators.
- `SELECTION.md` explicitly states that no luminosity was computed from local
  entries, selected counts, generated MC counts, or data/MC back-calculation.
- The data luminosity is attributed to the CMS Open Data H to tau tau tutorial
  `skim.cxx` context and CERN Open Data luminosity provenance rather than event
  counts.
- `normalization_inputs.json` records CERN Open Data record 1054, record 12350,
  data records 12358 and 12359, MC records 12351-12357, and CMS PAS
  LUM-13-001.
- MC normalization denominators are recorded as CERN Open Data
  `distribution.number_events`, with local ROOT entries explicitly marked as
  non-denominators.
- The tutorial source URL uses the `2012` branch:
  `https://github.com/cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis/blob/2012/skim.cxx`.

## Verdict

PASS. The prior plot/provenance Category A items are resolved, and no new
unresolved Category A or Category B issue was found in the rereview scope.
