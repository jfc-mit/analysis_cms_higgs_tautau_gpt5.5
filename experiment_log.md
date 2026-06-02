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

## 2026-06-02 Phase 1 fixer

- Read `agents/fixer.md`, the Phase 1 arbiter verdict, `STRATEGY.md`,
  `experiment_log.md`, and `conventions/search.md`.
- Resolved the arbiter's pileup convention finding by adding an explicit
  pileup-profile/weight row with a Phase 2 branch-inventory requirement,
  Phase 4 implementation path if pileup information exists, and a named
  reduced-open-data limitation/fallback if it does not.
- Clarified the simultaneous-fit category hierarchy so VBF is assigned first
  and the baseline is non-VBF; inclusive plots are diagnostics only and cannot
  double-count events in the likelihood.
- Added binding statistical configuration for modified CLs, one-sided
  discovery and limit test statistics, $\mu \ge 0$, and toy validation or
  direct toys when final bins do not satisfy the expected-count threshold.
- Added quantitative pass/fail gates for alternative observables and NN
  approaches: input $\chi^2/\mathrm{ndf}$, signal-injection bias, closure/GoF,
  minimum expected-sensitivity improvement, and rejection/downscope handling.
- Defined the NN missing-momentum mass target, allowed reconstructed inputs,
  no-truth-leakage rule, train/test/independent-MC/data-control validation,
  and downscope criteria when genMET/truth targets are missing.
- Strengthened the W+jets high-$m_T$ control-region plan with purity
  reporting, top/VBF contamination handling, category-wise transfer-factor
  validation where statistics allow, and larger extrapolation uncertainty for
  unsupported categories.
- Added a CR/VR taxonomy for SR, W CR/VR, QCD same-sign and anti-isolation
  regions, top CR/VR, and Z-rich validation, including orthogonality,
  subtraction/likelihood use, transfer metrics, pass/fail thresholds, and
  fallbacks.
- Added a binding final-AN comparison target matrix covering this analysis,
  CMS 2014 global/channel/category/control comparators, CMS 2018 caveated
  comparisons, ATLAS+CMS/PDG/world-average rows, VBF/non-VBF sensitivity, and
  alternative-observable comparisons.

## 2026-06-02 Phase 2 executor

- Started Phase 2 exploration execution using `agents/executor.md` as the
  governing role definition and `agents/README.md` for review/activation
  context.
- Read Phase 2 instructions, upstream Phase 1 strategy, Open Data access
  instructions, experiment/retrieval logs, and the required methodology,
  coding, tooling, and plotting references.
- DECISION: Treat Phase 1 [D1] as binding and perform Phase 2 as a
  search/template-fit exploration for CMS H to tau tau in mu tau_h, despite
  `phase2_exploration/CLAUDE.md` still saying measurement. CONFIDENCE: HIGH.
  FLAG FOR HUMAN: NO.
- Produced `phase2_exploration/plan.md` before ROOT file access or script
  writing.
- Resolved the public ROOT mirror
  `https://root.cern/files/HiggsTauTauReduced/`: it lists the prompt MC files
  but data files are `Run2012B_TauPlusX.root` and `Run2012C_TauPlusX.root`,
  not the prompt-listed `SingleMu` names. This is a Phase 2 provenance finding
  for [A3].
- Found that `uproot` access through pixi needs
  `SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt`; without it, fsspec
  reports a certificate verification failure even though system `curl` can
  reach the mirror.
- Added Phase 2 exploration and plotting scripts with pixi tasks
  `phase2-explore`, `phase2-plots`, and `all`.
- `pixi run phase2-explore` wrote sample inventory and branch diagnostics, then
  stalled during the 20k-event derived-variable survey. The active process was
  terminated and the survey was reduced to a 5k-event prototype with progress
  logging before each remote read.
- The reduced `pixi run phase2-explore` completed and wrote variable
  histograms, preselection yields, and variable separation JSON files.
- `pixi run phase2-plots` completed after replacing unavailable
  `mplhep.plot.mpl_magic` with a local legend-headroom helper. `pixi run
  lint-plots` passed after patching an explicit label.
- PDF stub test: `pixi run build-pdf` failed after pandoc/postprocess because
  `tectonic` is missing; `pdflatex` is also absent from pixi. The build task
  additionally emitted a citation warning because it does not pass
  `--bibliography=references.bib`. Phase 3/5 should add a TeX engine and fix
  the build task bibliography argument before relying on PDF compilation.
- Completed Phase 2 executor deliverables: wrote
  `phase2_exploration/outputs/EXPLORATION.md`, wrote executor self-review under
  `phase2_exploration/review/self/`, and preserved machine-readable inventory,
  diagnostics, preselection, separation, and figure outputs.
