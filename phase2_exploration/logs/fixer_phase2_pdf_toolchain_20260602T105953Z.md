# Phase 2 PDF Toolchain Fixer Log

Session: `20260602T105953Z`

## Finding 1: Missing TeX engine

UNDERSTAND: The Phase 2 PDF stub test failed because the pixi environment did
not provide the `tectonic` executable invoked by `build-pdf`.

LOCATE: `pixi.toml` dependencies and `build-pdf` task.

FIX: Added `tectonic = ">=0.15"` to `[dependencies]` and ran `pixi install`.

VERIFY: `pixi run build-pdf` completed successfully on a temporary stub and
wrote `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.pdf`.

NEIGHBORHOOD CHECK: Confirmed the task still runs pandoc, the conventions
postprocessor, and `tectonic` in sequence.

## Finding 2: Missing bibliography argument

UNDERSTAND: `build-pdf` used `--citeproc` but did not pass the bibliography
file, producing a citation warning in the prior stub test.

LOCATE: `pixi.toml` `build-pdf` task.

FIX: Added `--bibliography=references.bib` to the pandoc invocation.

VERIFY: The repaired command shown by pixi includes
`--bibliography=references.bib` and exits successfully. The current
`references.bib` contains no citation entries, so the temporary stub could not
cite an existing key without modifying the bibliography database.

NEIGHBORHOOD CHECK: Confirmed no real `ANALYSIS_NOTE_5_v1.md` existed before
the stub test; removed only the temporary stub `.md`, generated `.tex`, and
generated `.pdf` after verification.
