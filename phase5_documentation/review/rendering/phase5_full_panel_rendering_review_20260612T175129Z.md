# Phase 5 Rendering Review

Reviewer: rendering reviewer
Session: phase5 full panel, 20260612T175129Z
Scope:
- `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.{md,tex,pdf}`
- `phase5_documentation/outputs/PAPER_PRL_v1.{md,tex,pdf}`
- `phase5_documentation/outputs/figures/`
- `phase5_documentation/outputs/references.bib`

## Verdict

FAIL. The documents compile, citations and cross-references resolve, and all included figures are present. However, the final analysis note is far below the Phase 5 page-count target, several figure assets have referee-visible label or legend defects, and the PRL draft has table and float-placement problems.

## Compilation Checks

- `pixi run build-pdf` completed successfully for `ANALYSIS_NOTE_5_v1.md -> .tex -> .pdf`.
- `pixi run tectonic phase5_documentation/outputs/PAPER_PRL_v1.tex` completed successfully for the PRL PDF.
- Compilation regenerated `ANALYSIS_NOTE_5_v1.pdf` and `PAPER_PRL_v1.pdf` deterministically during verification.
- Poppler text extraction found no unresolved `??` references or `[?]` citations in either PDF.
- Bibliography sections render in both outputs.
- Page counts: AN = 9 pages; PRL = 3 pages.

## Findings

### A1. Final analysis note is only 9 pages

Symptom: `ANALYSIS_NOTE_5_v1.pdf` is 9 pages. This is below the Phase 5 target of 50-100 pages and below the explicit under-30-page Category A threshold.

Root cause: `ANALYSIS_NOTE_5_v1.md` is a compact summary document, not a complete final analysis note. The rendered note has a title/TOC, abstract, change log, six short sections, ten figures, three compact tables, and references. The TeX postprocess also permits major sections to continue on the current page when space is available, so it does not create the depth or spacing expected for a final AN.

Required fix: Expand the final AN source into a full reproducible analysis note with the required methodological detail, full cutflows, validation details, systematic tables, fit model specification, and figure/table discussion. Page count cannot be fixed by scaling alone; the source document needs substantive note content.

### A2. Several figure assets have overlapping experiment labels

Symptom: In `ANALYSIS_NOTE_5_v1.pdf`, the experiment label collides with the right-side energy/luminosity label in:
- Figure 7, `figures/phase5_category_mu_comparison.pdf`
- Figure 10, `figures/phase5_significance_comparison.pdf`

The same source-asset defect is also visible in `PAPER_PRL_v1.pdf` Figure 3.

Root cause: The figure assets already contain the overlap before LaTeX inclusion. The text placed after `CMS Open Data` is too long for the available top margin, so it runs into the right label. This is not caused by `\includegraphics` scaling; the PNG/PDF figure files themselves show the collision.

Required fix: Regenerate the affected figures with non-overlapping experiment labeling. Options include shortening the left label, moving the qualifier into the caption, increasing top margin, or using a two-line/custom label layout. Verify the standalone PDF/PNG assets before rebuilding the AN and PRL.

### A3. Calibrated-score validation figures contain source-level plot defects

Symptom: The calibrated-score validation figures show referee-visible defects:
- `figures/observed_primary_score_vbf.pdf`: the signal step/marker content intrudes into the upper-right legend region.
- `figures/observed_primary_score_vbf.pdf`, `figures/observed_primary_score_boosted.pdf`, and `figures/observed_primary_score_zero_jet.pdf`: a stray `x` appears near the right boundary between the main and ratio panels.

These defects are visible in AN Figures 4-6 and in PRL Figure 4 for the zero-jet plot.

Root cause: The defects are present in the source figure assets. The legend is placed inside the plotting area while plotted signal content extends through the same region. The stray `x` appears to come from an axis-label or shared-axis artifact in the ratio-plot generation, not from LaTeX placement.

Required fix: Regenerate the score-validation figures with the legend moved outside the data region or with plot limits adjusted. Remove the stray top-axis/shared-axis label artifact before saving both PDF and PNG outputs.

### A4. PRL Table II is cramped and hard to read

Symptom: `PAPER_PRL_v1.pdf` page 2 Table II has crowded columns and visually merged entries. Several row labels and scope entries wrap awkwardly, including the long open-data and ATLAS+CMS rows. The table is technically within the page, but the rendered result is not publication quality.

Root cause: `PAPER_PRL_v1.tex` uses a `table*` with fixed paragraph widths:
`p{0.16\textwidth}p{0.27\textwidth}cp{0.40\textwidth}`.
The content is too dense for these widths in the PRL two-column layout, especially with long result names and signal-strength strings.

Required fix: Reformat the comparison table for PRL. Use shorter row labels, split long signal-strength details into footnotes or caption text, reduce precision where appropriate for the paper draft, or move the table to an AN-only detailed table and keep a compact PRL summary.

### A5. PRL final page has poor two-column float placement

Symptom: `PAPER_PRL_v1.pdf` page 3 stacks Figures 3 and 4 in the left column while leaving the entire right column blank. This creates a large blank area and looks like a broken float layout.

Root cause: `PAPER_PRL_v1.tex` declares the late figures as one-column `[t]` floats after the main text and bibliography material. REVTeX places them in the left column, and there is no right-column text left to balance the page.

Required fix: Reorder floats before the bibliography, combine late figures, or use suitable `figure*` placement for wide floats. Recompile and inspect the final page to ensure both columns are balanced.

## Non-Blocking Observations

- The AN build emitted a nonfatal `glob: no matches found ... [` warning before postprocessing. The PDF still compiled correctly. This appears to come from the `build-pdf` pixi task's shell test for an optional preamble file, not from the rendered document.
- PRL compilation emitted underfull hbox warnings in short front-matter and paragraph lines. I did not see a standalone visible defect from those warnings after raster inspection.

## Checks Passed

- No missing image placeholders were observed.
- Figure captions appear below included figures.
- Table of contents is present in the AN and page numbers match the compiled PDF.
- No raw LaTeX control sequences were visible in the rendered text.
- No unresolved citations or references were found by PDF text extraction.
- The bibliography renders at the end of each document.
