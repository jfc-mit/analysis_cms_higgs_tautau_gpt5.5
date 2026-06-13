# Phase 5 Full-Panel Fixer Log

Session: `20260612T180909Z`

## Plan

1. Reclassify machine-readable result roles so `visible_mass_qcd_primary` is the final result and `calibrated_score_qcd_primary` is a failed validation diagnostic, without changing fit numbers.
2. Patch `phase5_documentation/src/build_phase5_docs.py` so regenerated AN/PRL outputs are standalone, baseline-first documents and score-model numbers appear only in a rejected-method section.
3. Regenerate clean Phase 5 figures used by the public documents, avoiding retained figures with known plot-validation defects.
4. Fix bibliography generation by retaining only cited entries with corrected metadata.
5. Run `pixi run phase5-docs`, `pixi run lint-plots`, and `pixi run build-pdf`, then scan generated outputs for stale process wording and incorrect score-primary usage.

## Resolution

- RESOLVED: result metadata now marks `visible_mass_qcd_primary` as `final_result_model` and keeps the optimized classifier as `diagnostic_failed_validation`.
- RESOLVED: final AN and PRL now present the validated visible-mass result as the only final result; classifier numbers are confined to a rejected-diagnostic section.
- RESOLVED: generated clean Phase 5 figures for baseline visible-mass validation, the final CLs limit, validation summary, nuisance pulls, the systematic program, and rejected classifier diagnostics.
- RESOLVED: final AN expanded to 30 rendered pages, with 31 figure references and 20 display equations.
- RESOLVED: bibliography was reduced to cited entries and updated for the metadata issues found by validation.
- RESOLVED: verification passed with `pixi run phase5-docs`, `pixi run lint-plots`, and `pixi run build-pdf`.

## Verification Notes

- `tectonic --keep-logs --keep-intermediates ANALYSIS_NOTE_5_v1.tex` reported `30 pages`.
- Public AN/PRL outputs scan clean for stale score-primary wording and non-analysis provenance terms.
- Fit values were not changed; only model-role metadata and documentation/figure presentation were updated.

## milestone

Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.

## milestone

Copied 44 required upstream figure files into the Phase 5 figure directory.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Generated failed-classifier per-category diagnostic JSON and clean figure.

## milestone

Generated clean Phase 5 baseline and diagnostic figures.

## milestone

Wrote baseline-only final analysis note and PRL markdown.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Compiled baseline-only PAPER_PRL_v1.tex with REVTeX PRL class.

## milestone

Appended Phase 5 full-panel fixer summary to experiment_log.md.

## milestone

Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.

## milestone

Copied 44 required upstream figure files into the Phase 5 figure directory.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Generated failed-classifier per-category diagnostic JSON and clean figure.

## milestone

Generated clean Phase 5 baseline and diagnostic figures.

## milestone

Wrote baseline-only final analysis note and PRL markdown.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Compiled baseline-only PAPER_PRL_v1.tex with REVTeX PRL class.

## milestone

Appended Phase 5 full-panel fixer summary to experiment_log.md.

## milestone

Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.

## milestone

Copied 44 required upstream figure files into the Phase 5 figure directory.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Generated failed-classifier per-category diagnostic JSON and clean figure.

## milestone

Generated clean Phase 5 baseline and diagnostic figures.

## milestone

Wrote baseline-only final analysis note and PRL markdown.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Compiled baseline-only PAPER_PRL_v1.tex with REVTeX PRL class.

## milestone

Appended Phase 5 full-panel fixer summary to experiment_log.md.

## milestone

Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.

## milestone

Copied 44 required upstream figure files into the Phase 5 figure directory.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Generated failed-classifier per-category diagnostic JSON and clean figure.

## milestone

Generated clean Phase 5 baseline and diagnostic figures.

## milestone

Wrote baseline-only final analysis note and PRL markdown.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Compiled baseline-only PAPER_PRL_v1.tex with REVTeX PRL class.

## milestone

Phase 5 full-panel fixer summary already present in experiment_log.md.

## milestone

Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.

## milestone

Copied 44 required upstream figure files into the Phase 5 figure directory.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Generated failed-classifier per-category diagnostic JSON and clean figure.

## milestone

Generated clean Phase 5 baseline and diagnostic figures.

## milestone

Wrote baseline-only final analysis note and PRL markdown.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Compiled baseline-only PAPER_PRL_v1.tex with REVTeX PRL class.

## milestone

Phase 5 full-panel fixer summary already present in experiment_log.md.

## milestone

Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.

## milestone

Copied 44 required upstream figure files into the Phase 5 figure directory.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Generated failed-classifier per-category diagnostic JSON and clean figure.

## milestone

Generated clean Phase 5 baseline and diagnostic figures.

## milestone

Wrote baseline-only final analysis note and PRL markdown.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Compiled baseline-only PAPER_PRL_v1.tex with REVTeX PRL class.

## milestone

Phase 5 full-panel fixer summary already present in experiment_log.md.

## milestone

Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.

## milestone

Copied 44 required upstream figure files into the Phase 5 figure directory.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Generated failed-classifier per-category diagnostic JSON and clean figure.

## milestone

Generated clean Phase 5 baseline and diagnostic figures.

## milestone

Wrote baseline-only final analysis note and PRL markdown.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Compiled baseline-only PAPER_PRL_v1.tex with REVTeX PRL class.

## milestone

Phase 5 full-panel fixer summary already present in experiment_log.md.

## milestone

Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.

## milestone

Copied 44 required upstream figure files into the Phase 5 figure directory.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Generated failed-classifier per-category diagnostic JSON and clean figure.

## milestone

Generated clean Phase 5 baseline, NN-score, and diagnostic figures.

## milestone

Wrote baseline-only final analysis note and PRL markdown.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Compiled baseline-only PAPER_PRL_v1.tex with REVTeX PRL class.

## milestone

Phase 5 full-panel fixer summary already present in experiment_log.md.

## milestone

Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.

## milestone

Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.

## milestone

Copied 44 required upstream figure files into the Phase 5 figure directory.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.

## milestone

Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.

## milestone

Copied 44 required upstream figure files into the Phase 5 figure directory.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Generated failed-classifier per-category diagnostic JSON and clean figure.

## milestone

Generated clean Phase 5 baseline, NN-score, and diagnostic figures.

## milestone

Wrote baseline-only final analysis note and PRL markdown.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.

## milestone

Copied 44 required upstream figure files into the Phase 5 figure directory.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Generated failed-classifier per-category diagnostic JSON and clean figure.

## milestone

Generated clean Phase 5 baseline, NN-score, and diagnostic figures.

## milestone

Wrote baseline-only final analysis note and PRL markdown.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Compiled baseline-only PAPER_PRL_v1.tex with REVTeX PRL class.

## milestone

Phase 5 full-panel fixer summary already present in experiment_log.md.

## milestone

Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.

## milestone

Copied 44 required upstream figure files into the Phase 5 figure directory.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Generated failed-classifier per-category diagnostic JSON and clean figure.

## milestone

Generated clean Phase 5 baseline, NN-score, and diagnostic figures.

## milestone

Wrote baseline-only final analysis note and PRL markdown.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Compiled baseline-only PAPER_PRL_v1.tex with REVTeX PRL class.

## milestone

Phase 5 full-panel fixer summary already present in experiment_log.md.

## milestone

Reclassified result metadata: visible mass final, calibrated score failed diagnostic; fit numbers unchanged.

## milestone

Copied 44 required upstream figure files into the Phase 5 figure directory.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Generated failed-classifier per-category diagnostic JSON and clean figure.

## milestone

Generated clean Phase 5 baseline, NN-score, and diagnostic figures.

## milestone

Wrote baseline-only final analysis note and PRL markdown.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Compiled baseline-only PAPER_PRL_v1.tex with REVTeX PRL class.

## milestone

Phase 5 full-panel fixer summary already present in experiment_log.md.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Wrote focused final analysis note and PRL markdown for baseline plus D_NN outputs.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Compiled PAPER_PRL_v1.md to TeX and PDF.

## milestone

Appended focused final rerun summary to experiment_log.md.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Wrote focused final analysis note and PRL markdown for baseline plus D_NN outputs.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Wrote focused final analysis note and PRL markdown for baseline plus D_NN outputs.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Focused final rerun summary already present in experiment_log.md.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Wrote focused final analysis note and PRL markdown for baseline plus D_NN outputs.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Focused final rerun summary already present in experiment_log.md.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Wrote focused final analysis note and PRL markdown for baseline plus D_NN outputs.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Focused final rerun summary already present in experiment_log.md.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Wrote focused final analysis note and PRL markdown for baseline plus D_NN outputs.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Focused final rerun summary already present in experiment_log.md.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Wrote focused final analysis note and PRL markdown for baseline plus D_NN outputs.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Focused final rerun summary already present in experiment_log.md.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Wrote focused final analysis note and PRL markdown for baseline plus D_NN outputs.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Wrote focused final analysis note and PRL markdown for baseline plus D_NN outputs.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Wrote focused final analysis note and PRL markdown for baseline plus D_NN outputs.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Wrote focused final analysis note and PRL markdown for baseline plus D_NN outputs.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Focused final rerun summary already present in experiment_log.md.

## milestone

Focused final rerun summary already present in experiment_log.md.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Wrote focused final analysis note and PRL markdown for baseline plus D_NN outputs.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Focused final rerun summary already present in experiment_log.md.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Wrote focused final analysis note and PRL markdown for baseline plus D_NN outputs.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Focused final rerun summary already present in experiment_log.md.

## milestone

Wrote corrected cited-only Phase 5 bibliography.

## milestone

Wrote focused final analysis note and PRL markdown for baseline plus D_NN outputs.

## milestone

Compiled ANALYSIS_NOTE_5_v1.md to TeX and PDF.

## milestone

Focused final rerun summary already present in experiment_log.md.
