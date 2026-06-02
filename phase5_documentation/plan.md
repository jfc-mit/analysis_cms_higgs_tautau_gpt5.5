# Phase 5 Documentation Plan

Session: executor_phase5_documentation_20260602T162932Z

## Inputs Read

- `agents/executor.md`
- `phase5_documentation/CLAUDE.md`
- Phase 1-3 primary artifacts
- Phase 4a/4b/4c JSON outputs and Phase 4c analysis note
- Upstream Phase 4c bibliography

## Gaps To Close

1. Phase 5 currently has only a stub bibliography and no final AN or paper.
2. Existing figures need to be aggregated into `phase5_documentation/outputs/figures/`.
3. A publication-style comparison figure is required for significances and a second comparison for signal-strength or limit context is feasible from existing numbers.
4. The final AN must be more complete than the short Phase 4c note, but this fast pass will remain concise and explicitly document the open-data validation caveat.
5. The PRL-style draft must avoid internal phase jargon in its main text and must not claim CMS-quality evidence.

## Implementation Plan

1. Copy or symlink existing Phase 2-4 figures into the Phase 5 figure directory with stable filenames.
2. Write a Phase 5 generation script that:
   - reads upstream JSON files,
   - generates CMS-style comparison figures,
   - merges the upstream bibliography into Phase 5,
   - writes `ANALYSIS_NOTE_5_v1.md` and `PAPER_PRL_v1.md`,
   - compiles both markdown files through pandoc, post-processing, and tectonic.
3. Add reproducibility tasks to `pixi.toml` for Phase 5 docs and include them in `all` only after verifying the task is stable enough.
4. Append milestones and caveats to the session log and `experiment_log.md`.
5. Verify:
   - `pixi run lint-plots`,
   - figure-reference existence for both markdown documents,
   - `git diff --check`,
   - nonzero PDF outputs,
   - paper caveat grep confirming the draft does not overclaim CMS-quality evidence.
6. Commit with a conventional Phase 5 commit message.

## Physics Interpretation Policy

Both documents will quote `mu_hat = 7.6642`, observed 95% CLs upper limit
`mu < 13.3226`, and observed diagnostic `Z = 2.9776`, but will label them as
simplified open-data diagnostics. The 10% and full-data score-template
validation statuses are flagged, so these values are not CMS-quality evidence
for Higgs boson decay to tau pairs.
