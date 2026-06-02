# Phase 2 Executor Self-Review

## Verdict

PASS WITH DOCUMENTED LIMITATIONS for Phase 2 exploration. The primary artifact
exists, the sample inventory and data archaeology are machine-readable, figures
were produced as PDF and PNG, and plot lint passes. The PDF build test failed
for an environment/toolchain reason that is explicitly documented as a
downstream blocker.

## Checks

| Check | Status | Notes |
|---|---|---|
| Sample inventory complete | Pass | All files listed at `https://root.cern/files/HiggsTauTauReduced/` were inventoried; prompt SingleMu names return 404. |
| Tree/branch/event counts | Pass | Written to `sample_inventory.json`; all available samples have one `Events` tree. |
| Weight/flag/quality archaeology | Pass | Written to `branch_diagnostics.json`; no event weights or pileup weights found. |
| GenMET regression feasibility | Pass with strategy input | No direct GenMET and no neutrino truth branches found, so Phase 1 alternative (b) needs downscope or external truth. |
| Pileup feasibility | Pass with limitation | `PV_npvs` exists, pileup weights do not. |
| Baseline preselection | Pass | Raw 5k-slice yields produced for loose, OS low-mT, high-mT, VBF-like, and same-sign regions. |
| Variable survey | Pass | First-candidate diagnostics and MC AUC ranking produced. |
| Figures | Pass with caveat | 13 PDF/PNG pairs produced and linted. Visible mass has a low-mass spike that is flagged as a candidate-cleaning warning. |
| PDF build stub | Fail documented | `pixi run build-pdf` failed because `tectonic` and `pdflatex` are absent; task also lacks bibliography argument. |
| Experiment/session logs | Pass | Logs updated with access path, stalled run, fallback, command outcomes, and blockers. |

## Required Follow-Up Before Phase 3 Production

- Update strategy wording from SingleMu to TauPlusX or justify a different
  data retrieval path.
- Retrieve external normalization inputs: cross sections, luminosity per data
  period, and W+jets stitching.
- Mask isolation and b-tag sentinel values before MVA or selection use.
- Rebuild visible-mass and variable-input comparisons after final Phase 3
  candidate arbitration.
- Install or configure a TeX engine and add `--bibliography=references.bib` to
  the build task before any PDF gate.
