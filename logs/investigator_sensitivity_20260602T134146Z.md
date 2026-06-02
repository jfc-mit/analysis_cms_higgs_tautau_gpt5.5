# Investigator Session: Sensitivity Regression

Timestamp: 2026-06-02T13:41:46Z

## Reads

- `agents/investigator.md`
- `methodology/06-review.md` section 6.7
- `methodology/03-phases.md` Phase 3 and Phase 4a
- `conventions/search.md`
- Phase 1 strategy, Phase 3 selection/review/log artifacts, Phase 4a expected
  inference outputs, `COMMITMENTS.md`, and `experiment_log.md`
- CMS-HIG-13-004 public result page and arXiv source for JHEP 05 (2014) 104

## Diagnostics

- Confirmed Phase 4a baseline: expected median CLs limit `mu = 11.374122822819393`
  and expected discovery diagnostic `Z = 0.1906097504953417`.
- Confirmed nominal weighted yields: VBF `S = 1.590`, `B = 144.926`; boosted
  `S = 9.170`, `B = 2093.690`; zero-jet `S = 14.341`, `B = 7060.345`.
- Ran in-memory pyhf diagnostic variants without modifying code:
  nominal `Z = 0.191`; no staterror `Z = 0.262`; no normsys `Z = 0.272`;
  no staterror or normsys `Z = 0.389`.
- Ran expected-only one-off category/variable diagnostics from
  `selected_events.npz`; simple VBF tightening did not improve sensitivity.
- Ran a quick MC-only classifier diagnostic using existing selected features:
  gradient boosting AUC `0.787`, no-systematics binned Asimov Z `0.453`.
  This is a modest improvement over current no-systematics `m_vis` Z `0.389`,
  but not enough by itself to reach the 1-2 sigma target.

## Output

Wrote `phase3_selection/REGRESSION_TICKET_sensitivity.md` and appended
`regression_log.md`. No analysis code was modified.
