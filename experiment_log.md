# Experiment Log

## 2026-06-02 Orchestrator setup

- Logged the physics prompt in `prompt.md` and preserved the user's added comparison requirements for the final analysis note.
- Repaired the analysis-local symlink targets for `agents/`, `methodology/`, and `conventions/` so subagents can read the mandated role definitions and methodology files from `/sandbox/work/jfc/src`.
- Identified Phase 1 as the next required phase because no phase artifacts exist yet.

## 2026-06-02 Phase 1 executor

- Started Phase 1 strategy execution using `agents/executor.md` as the
  governing role definition and `agents/README.md` for review/activation
  context.
- Read Phase 1 methodology and conventions before writing strategy prose.
- DECISION: Treat the user physics prompt as authoritative over the scaffold:
  this analysis is a search/template-fit Higgs analysis, not a primary
  measurement. CONFIDENCE: HIGH. FLAG FOR HUMAN: NO.
- Produced `phase1_strategy/plan.md` before drafting the strategy artifact.
- SciTreeRAG MCP tools were unavailable, so public CMS/CERN/arXiv sources were
  used for Phase 1 retrieval. Retrieval limitation is documented in
  `retrieval_log.md`.
- DECISION: Bind the baseline result to a simultaneous profile-likelihood
  shape fit in $\mu\tau_h$ categories, with visible mass as the baseline
  observable and the three user-requested NN/add-MET alternatives as required
  Phase 3 comparisons. CONFIDENCE: HIGH. FLAG FOR HUMAN: NO.
- DECISION: Assign tau ID/efficiency and DY/Z normalization uncertainties in
  the 10-15% range unless better official scale-factor sources are retrieved;
  this is a pre-declared limitation due to missing scale factors, not a tuning
  knob for the Drell-Yan peak. CONFIDENCE: MEDIUM. FLAG FOR HUMAN: YES.
- Produced `phase1_strategy/outputs/STRATEGY.md`.
