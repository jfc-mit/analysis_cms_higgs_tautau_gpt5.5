# Phase 5 Rendering Re-review

Reviewer: rendering reviewer
Session: phase5 full panel rendering re-review, 20260612T185843Z

Scope:
- `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.{md,tex,pdf}`
- `phase5_documentation/outputs/PAPER_PRL_v1.{md,tex,pdf}`
- `phase5_documentation/outputs/figures/`
- `phase5_documentation/outputs/references.bib`

## Verdict

FAIL. The final analysis note now compiles to exactly 30 pages and passes the
under-30-page Category A gate. References, citations, tables, and AN figures
render without visible blocking defects. The PRL draft still has a visible
float-layout defect on page 2.

## Compilation and Mechanical Checks

- `pixi run build-pdf` completed successfully for
  `ANALYSIS_NOTE_5_v1.md -> ANALYSIS_NOTE_5_v1.tex -> ANALYSIS_NOTE_5_v1.pdf`.
- `tectonic PAPER_PRL_v1.tex` completed successfully from
  `phase5_documentation/outputs` using the Pixi environment path.
- `tectonic --keep-logs` was run for both documents. This created
  `ANALYSIS_NOTE_5_v1.log`, `PAPER_PRL_v1.log`, and `PAPER_PRL_v1.blg`.
  Tectonic did not leave aux files in the outputs directory.
- Temporary Poppler tools via `pixi exec --spec poppler` reported:
  AN = 30 pages, letter paper, PDF 1.5; PRL = 2 pages, letter paper, PDF 1.5.
- PDF text extraction found no unresolved `??` references, `[?]` citations,
  raw `@fig:`, `@tbl:`, `@eq:`, or `@sec:` references in either PDF.
- Source-level checks found all markdown citation keys in `references.bib`
  and all AN markdown cross-references matched labels.
- TeX logs contain no overfull boxes, undefined references, undefined
  citations, or fatal errors. The PRL log contains one underfull hbox warning
  at lines 27-33, and the PRL `.blg` contains one non-rendering journal-list
  warning.

## Findings

### A1. PRL page 2 has a referee-visible float-layout defect

Symptom: `PAPER_PRL_v1.pdf` page 2 is mostly float material. The three-panel
visible-mass figure spans the top of the page, while the final limit figure is
placed as a one-column float in the lower left. The lower right column and much
of the lower page are blank. This is a large visible whitespace gap and looks
like an unfinished PRL layout rather than a balanced two-column paper page.

Root cause: `PAPER_PRL_v1.tex` places a `figure*` followed by a one-column
`figure[t]` after the main result text. REVTeX defers the wide float to the top
of page 2, then places the following one-column float in the left column with
no remaining text to balance the right column.

Required fix: Rework the PRL float structure. Suitable fixes include combining
the validation and limit material into one `figure*`, making the limit plot a
wide `figure*` below the validation panels, moving float declarations earlier
so text can flow around them, or adding enough PRL text after the figures to
balance the page. Recompile and inspect page 2 after the change.

## Checks Passed

- AN page count is 30, satisfying the explicit at-least-30 requirement.
- AN table of contents renders and matches the compiled page count.
- AN and PRL PDFs contain no missing-image placeholders in the rasterized page
  inspection.
- AN figures render at bounded sizes with captions below figures.
- The previously reported source-figure label collisions and score-template
  artifacts are not present in the current Phase 5 figure set.
- AN tables do not overflow the page; TeX logs show no overfull table boxes.
- PRL Table I fits within the left column and is readable.
- PRL Figure 1 is a wide three-panel figure with readable labels at rendered
  size.

## Non-blocking Observations

- The AN is exactly 30 pages, so it passes the threshold but has no page-count
  margin.
- `pixi run build-pdf` emits a nonfatal glob warning before postprocessing:
  `glob: no matches found ... [`; the PDF still compiles and renders.
- The PRL source PDF is built from the hand-written REVTeX file. The PRL
  markdown is present in scope, but the rendered PRL layout corresponds to
  `PAPER_PRL_v1.tex`.
