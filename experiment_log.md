# 2026-06-02 Method update plan: category-preserving stronger score model

User changed direction: do not update the Phase 4a note yet; directly replace
the inclusive-score expected-primary model with a category-preserving
score-template model. Plan:

1. Inspect available fast model stacks and compare MC-only candidates without
   using observed full-data signal-region distributions.
2. Keep the Phase 3 VBF, boosted, and zero-jet categories as final pyhf
   channels; within each channel use score-binned templates.
3. Try a lightweight transformer/attention candidate only if the current pixi
   environment supports it quickly. Otherwise document why it was not attempted
   and compare the strongest fast available models, including xgboost and
   sklearn tree ensembles.
4. Merge adjacent score bins within each category until every expected
   background fit bin has at least five events, unless impossible.
5. Regenerate Phase 3 recommendation artifacts and Phase 4a expected-only
   pyhf outputs, keeping the official Open Data luminosity, official MC N_gen
   denominators, signal sigma_prod * BR normalization, TauPlusX trigger scope,
   and background-only Asimov observations unchanged.
6. Verify with the relevant pixi tasks, lint plots, whitespace check, and commit
   with a conventional commit.

## 2026-06-02T15:18:31Z

Phase 3/4a executor resumed from checkpoint `7c15b68`. The checkpointed Phase
4a model uses an inclusive MVA score channel; the current method request
requires a category-preserving simultaneous fit including VBF. The continuation
will inspect transformer feasibility in the existing pixi environment, compare
baseline mass, transformer score, genMET-regression feasibility, and add-MET
mass candidates with expected-only metrics, then rebuild Phase 4a from the
selected category-preserving recommendation without using observed full-data
signal-region optimization.

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

## 2026-06-02 Phase 2 data-localization fixer

- Read `agents/fixer.md` and `agents/executor.md` as the governing role
  definitions for a targeted Phase 2 localization fix.
- Created analysis-local `data/` and `mc/` directories for reduced ROOT files
  and updated `.gitignore` so local ROOT data are not committed.
- Started resumable downloads from
  `https://root.cern.ch/files/HiggsTauTauReduced/` for all currently confirmed
  reduced data and MC samples: Run2012B/C TauPlusX data; ggH and VBF H to tau
  tau signal; DYJetsToLL, TTbar, and W1/W2/W3JetsToLNu backgrounds.
- Added `phase2_exploration/src/localize_samples.py` and pixi task
  `phase2-local-manifest` to validate local file sizes and `Events` tree
  accessibility with uproot and to write
  `phase2_exploration/outputs/local_sample_manifest.json`.
- Updated `phase2_exploration/src/explore_samples.py` so Phase 2 exploration
  prefers local `data/` and `mc/` files when present and falls back to the ROOT
  HTTPS mirror otherwise.
- DECISION: Paper-level MC components named or implied by CMS JHEP 05 (2014)
  104 and CMS Phys. Lett. B 779 (2018) 283 but absent from the reduced mirror
  do not block the current reduced-sample analysis. They are recorded as
  `missing-reduced` or `deferred-AOD-conversion` and must be discussed as
  limitations in the final analysis note and final summary. CONFIDENCE: HIGH.
  FLAG FOR HUMAN: NO.
- DECISION: Phase 3 must implement mutually exclusive sensitivity categories
  inspired by CMS JHEP 05 (2014) 104 and CMS Phys. Lett. B 779 (2018) 283,
  including VBF, boosted/1-jet, and 0-jet or non-VBF baseline categories where
  reduced statistics support them, and must fit all retained categories
  simultaneously. Required handles include jet multiplicity, `m_jj`,
  `|Delta eta_jj|`, `pT_tautau` or a documented available proxy, b-tag/top
  controls, and W/QCD control-region variables. CONFIDENCE: HIGH. FLAG FOR
  HUMAN: NO.

## 2026-06-02 Phase 2 plot fixer

- Read `agents/fixer.md`, the Phase 2 plot-validation report,
  `phase2_exploration/src/plot_exploration.py`, `EXPLORATION.md`,
  `methodology/appendix-plotting.md`, and this experiment log before making
  targeted plotting fixes.
- RESOLVED: Replaced rendered sample, feature, and variable identifiers with
  publication-quality display labels in `plot_exploration.py`; verified
  regenerated PNGs no longer show sample-name underscores or code-style
  variable labels in the failed diagnostics.
- RESOLVED: Replaced raw event-count and preselection-yield `ax.plot` calls
  with `mh.histplot(..., histtype="errorbar")` using explicit Poisson
  uncertainties. File size remains a metadata point diagnostic with an inline
  code justification.
- RESOLVED: Moved the preselection-yield legend outside the data region and
  confirmed no marker/legend overlap remains in `preselection_yield_summary.png`.
- RESOLVED: Changed the visible-mass diagnostic to log-y rendering so the
  low-mass spike no longer compresses the rest of the distribution.
- RESOLVED: Replaced the cramped mixed open-data/open-simulation label with
  `Open Data + Open Sim.` and an `8 TeV` right label; visually checked
  `branch_feature_availability.png`, `sample_event_count_file_size.png`,
  `preselection_yield_summary.png`, `visible_mass_slice.png`,
  `variable_separation_ranking.png`, and `muon_pt_slice.png`.
- Verification: `pixi run phase2-plots` completed; `pixi run lint-plots`
  passed with "No plotting violations found in 3 file(s)." No ROOT files were
  touched and no new data processing was run.

## 2026-06-02 Phase 2 PDF toolchain fixer

- Read `agents/fixer.md`, the Phase 2 artifact, Phase 2 self-review,
  `pixi.toml`, `phase5_documentation/outputs/references.bib`, and this
  experiment log before making scoped PDF toolchain changes.
- RESOLVED: Added `tectonic` to the pixi conda-forge dependencies because the
  existing `build-pdf` task invokes `tectonic`.
- RESOLVED: Updated `build-pdf` to pass `--bibliography=references.bib` with
  `--citeproc` when compiling `ANALYSIS_NOTE_5_v1.md`.
- Ran `pixi install`; the default environment installed successfully.
- Verified `pixi run build-pdf` on a temporary Phase 5 stub note. The command
  exited successfully and wrote `ANALYSIS_NOTE_5_v1.pdf`; the temporary stub
  markdown, generated TeX, and generated PDF were then removed. The existing
  `references.bib` file contains no citation entries, so the stub used inline
  math but no real citation key.
# 2026-06-02T11:05:16Z - Phase 3 executor start

Read the Phase 3 executor template, activation matrix, phase instructions,
Phase 1/2 artifacts, and search conventions. Phase 3 will implement the
Phase 1 [D1] search/template-fit strategy despite the scaffolded measurement
label in `phase3_selection/CLAUDE.md`. Wrote the required
`phase3_selection/plan.md` before implementation.

# 2026-06-02T11:19:30Z - Phase 3 selection implementation

Implemented full-file Phase 3 processing over all localized reduced samples.
Retained mutually exclusive VBF, boosted/1-jet, and zero-jet categories with
VBF assigned first. Aggregate selected raw counts are data 83/2261/8783,
signal 395/772/573, and background 246/2896/5634 in VBF/boosted/zero-jet.

DECISION: Keep visible mass as the Phase 4 primary observable and retain
add-MET mass as an alternative cross-check.
ALTERNATIVES: Add-MET mass had a lower combined raw MC-only separation metric
than visible mass; NN classifier was downscoped because 13 of 16 candidate
inputs failed the data/MC modelling gate; NN genMET regression was downscoped
because no GenMET/neutrino truth target exists in the reduced files.
CONFIDENCE: HIGH for Phase 3 processing; MEDIUM for eventual sensitivity
until Phase 4 resolves normalization and systematics.
FLAG FOR HUMAN: YES, because MVA downscope and missing normalization inputs
affect the final analysis scope.

# 2026-06-02T11:19:30Z - Phase 3 validation

Ran `pixi run phase3-all` successfully. Ran `pixi run lint-plots`; it passed
with no plotting violations. Wrote
`phase3_selection/outputs/SELECTION.md` and all required machine-readable
outputs.

# 2026-06-02T11:36:23Z - Phase 3 fixer

- Read `agents/fixer.md`, Phase 3 critical review, Phase 3 plot validation,
  Phase 3 scripts/outputs, `experiment_log.md`, and the plotting standards.
- RESOLVED A1: added a quantitative validation remediation loop to
  `variable_modeling.json`. The mixed validation/control union still fails
  for `m_vis` (`chi2/ndf = 17.30`) and add-MET (`43.38`), but the separate
  region checks identify W high-mT (`2.24`) and Z-rich (`1.17`) visible-mass
  handles that are below the alarm threshold. The broad raw templates are now
  explicitly scoped as not final Phase 4 closure-validated predictions until
  normalization, missing-background/QCD treatment, and control-region nuisance
  modelling are added.
- RESOLVED A2: added explicit selected-event fields `is_signal_region`,
  `region_exclusive`, `is_z_rich`, `is_top_btag_handle`, `is_w_high_mt`,
  `is_same_sign`, and `is_same_sign_low_mt`; updated plots to use
  `is_signal_region` rather than an exclusive diagnostic label.
- RESOLVED B1: reframed the visible-mass vs add-MET comparison as a diagnostic
  raw MC-only metric. The formal Phase 1 [D9] expected-sensitivity gate remains
  a Phase 4 task requiring normalization, nuisance parameters, and a pyhf model.
- RESOLVED B2: corrected `SELECTION.md` control-region counts from
  `region_yields.json`: W high-mT is 4211 data and 6552 raw background MC;
  same-sign QCD sideband is 3227 data and 1240 raw background MC.
- RESOLVED plot findings: replaced `Open Data + Open Sim.` with
  `Open Data + Open Simulation`, added legend headroom, padded
  `approach_comparison.png`, and replaced mechanical MVA variable labels with
  publication-quality labels. `pixi run lint-plots` passed.
- BINDING LUMINOSITY CHECK: checked CERN Open Data record 12350 and the
  localized Run2012B/C TauPlusX reduced-file metadata. No exact integrated
  luminosity for these localized reduced files was found, and no luminosity was
  computed from event counts or back-calculated from MC/data. Updated
  `normalization_inputs.json` and `SELECTION.md` to keep exact integrated
  luminosity as a blocking input; Phase 4 cannot quote luminosity-normalized
  yields without a citable CMS/Open Data source.
- Verification: reran `pixi run phase3-all`; ran `pixi run lint-plots`; ran a
  selected-event consistency check showing `is_signal_region` agrees with
  `category_yields.json` and `region_yields.json` for data, signal, and
  background.

# 2026-06-02T11:58:45Z - Phase 2/3 normalization provenance regression fixer

- CORRECTION TO 2026-06-02T11:36:23Z LUMINOSITY CHECK: the local ROOT `Events`
  entries are reduced/skimmed processing entries and must not be compared to
  CERN Open Data `distribution.number_events` to declare samples incomplete.
  The local files remain the Phase 2/3 analysis inputs.
- Updated normalization provenance to the user-authoritative model: data
  luminosity is `L_int = 11.467/fb = 11467/pb` from the CMS Open Data H to tau
  tau tutorial `skim.cxx` for Run2012B+C TauPlusX; CERN Open Data record 1054
  supplies the official 2012 luminosity source and the `pxl`-preferred,
  HFOC-fallback rule; CMS PAS LUM-13-001 supplies the 2.6% luminosity
  uncertainty.
- Updated MC normalization denominators to CERN Open Data records 12351-12357
  `distribution.number_events`, not local ROOT entries. Recorded the official
  record id, DOI, file key, file size, `N_gen`, cross section, formula, and
  per-entry absolute weight in `phase3_selection/outputs/normalization_inputs.json`.
- Linked data records 12358 and 12359 in the Phase 2 manifest as official
  parent reduced NanoAOD records for Run2012B/C TauPlusX event counts. The data
  luminosity is not back-calculated from those event counts.
- Updated `phase2_exploration/src/localize_samples.py` and regenerated
  `phase2_exploration/outputs/local_sample_manifest.json` schema v2 so local
  tree entries and official Open Data event counts are separate fields.
- Updated `phase1_strategy/outputs/STRATEGY.md`,
  `phase2_exploration/outputs/EXPLORATION.md`, and
  `phase3_selection/outputs/SELECTION.md` to remove stale claims that reduced
  local entries imply incomplete samples or unresolved luminosity.
- Did not rerun full Phase 3 event selection: selected events, cutflows,
  category yields, and region yields depend on reconstructed branch masks and
  selection thresholds, none of which changed. This regression changed only
  normalization provenance metadata and prose.
- Verification passed: `pixi run py phase2_exploration/src/localize_samples.py`;
  `pixi run py - <<'PY' ... JSON and normalization metadata checks ... PY`;
  `pixi run lint-plots`; `git diff --check`.

# 2026-06-02T12:18:28Z - Phase 3 TauPlusX trigger fixer

- Addressed the Category A trigger finding from
  `phase3_critical_rereview_20260602T121544Z.md`: Phase 3 no longer ORs
  `HLT_IsoMu24_eta2p1` or `HLT_IsoMu24` into the analysis trigger selection.
- Before policy: selected events passed `HLT_IsoMu24_eta2p1` OR `HLT_IsoMu24`
  OR `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`. After policy: all Phase 3 analysis
  regions require only the TauPlusX primary trigger
  `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`.
- Kept trigger provenance metadata in `selection_config.json` and
  `normalization_inputs.json`: the single-muon triggers are available in the
  reduced files but intentionally not used because they define a different
  higher-pT muon phase space.
- Reran `pixi run phase3-all`, regenerating `selected_events.npz`, cutflow,
  category/region yields, variable modelling, approach comparison, and all
  Phase 3 figures. New low-mT signal-region totals are data 10,758, signal MC
  1,668, and background MC 8,402.
- Updated `phase3_selection/outputs/SELECTION.md` with the primary-trigger
  policy and regenerated yield/modeling numbers.
- Corrected `region_yields.json` category bookkeeping so category counts are
  defined on the same compact selected-event summary surface used by
  `selected_events.npz`.
- Verification passed: `pixi run phase3-all`; `pixi run lint-plots`;
  `git diff --check`; JSON validity checks for 14 Phase 2/3 output JSON files;
  selected-event/category/region consistency check with 108 comparisons using
  the independent region flags; trigger implementation assertion confirming the
  production mask uses only the primary TauPlusX trigger.

## 2026-06-02T12:57:43Z

Phase 4a expected-only model built from Phase 3 selected MC using official Open Data normalization. No real data signal-region observed result was used; the observation is background-only Asimov pseudo-data.

## 2026-06-02T12:59:29Z

Phase 4a expected-only model built from Phase 3 selected MC using official Open Data normalization. No real data signal-region observed result was used; the observation is background-only Asimov pseudo-data.

## 2026-06-02T14:15:07Z

Phase 3 sensitivity regression fixer ran expected-only category, observable, MVA, nuisance, and missing-component scans. Best variant `mva_hist_gradient_boosting_score_single_category` reached Z=0.596 versus Phase 4a baseline Z=0.191; see `phase3_selection/outputs/sensitivity_recommendation.json`.

## 2026-06-02T14:34:08Z

Phase 3 plot-label fixer addressed the sensitivity plot validation failure by
replacing raw/internal plotted labels with display labels, moving the
gradient-boosted classifier score legend out of the plotted data region, and
adding the three sensitivity figures to `SELECTION.md` with expected-only
interpretive captions. Physics logic, MVA training, scores, and sensitivity
ranking were intentionally left unchanged.

## 2026-06-02T14:54:52Z

Phase 4a sensitivity rerun built the expected-primary candidate from Phase 3 `mva_score_hist_gradient_boosting` in `inclusive_sr`, using official Open Data normalization and background-only Asimov pseudo-data. The high-score tail bins were merged to remove the single expected-background bin below five events. No real data signal-region observed result was used, and the MVA remains pending Phase 4b score-modelling validation/calibration.

## 2026-06-02T14:55:40Z

Phase 4a sensitivity rerun built the expected-primary candidate from Phase 3 `mva_score_hist_gradient_boosting` in `inclusive_sr`, using official Open Data normalization and background-only Asimov pseudo-data. The high-score tail bins were merged to remove the single expected-background bin below five events. No real data signal-region observed result was used, and the MVA remains pending Phase 4b score-modelling validation/calibration.

## 2026-06-02T14:57:41Z

Phase 4a sensitivity rerun built the expected-primary candidate from Phase 3 `mva_score_hist_gradient_boosting` in `inclusive_sr`, using official Open Data normalization and background-only Asimov pseudo-data. The high-score tail bins were merged to remove the single expected-background bin below five events. No real data signal-region observed result was used, and the MVA remains pending Phase 4b score-modelling validation/calibration.

## 2026-06-02T15:37:43Z

Phase 4a sensitivity rerun built the expected-primary candidate from Phase 3 `mva_score_hist_gradient_boosting` in simultaneous `vbf, boosted, zero_jet` channels, using official Open Data normalization and background-only Asimov pseudo-data. Score bins were merged using expected background only to keep each fit bin above five expected background events where possible. No real data signal-region observed result was used, and the MVA remains pending Phase 4b score-modelling validation/calibration.

## 2026-06-02T15:39:41Z

Phase 4a sensitivity rerun built the expected-primary candidate from Phase 3 `mva_score_hist_gradient_boosting` in simultaneous `vbf, boosted, zero_jet` channels, using official Open Data normalization and background-only Asimov pseudo-data. Score bins were merged using expected background only to keep each fit bin above five expected background events where possible. No real data signal-region observed result was used, and the MVA remains pending Phase 4b score-modelling validation/calibration.

## 2026-06-02T16:06:00Z

User added final documentation requirement: after Phase 4c full results, Phase 5 must produce both the full AN and a PRL-style paper draft (`phase5_documentation/outputs/PAPER_PRL_v1.{md,tex,pdf}`). The paper must include CMS-publication-style figures and tables for the main result and comparisons to meaningfully comparable CMS published H to tau tau results and available PDG/world-average context.

## 2026-06-02T16:14:28Z

Phase 4b executor built deterministic 10% data validation using `(run * 1000003 + luminosityBlock * 9176 + event) % 10 == 0` on data rows only. W high-mT scale = 0.8433 ± 0.0868; score modelling status = flagged.

## 2026-06-02T16:15:22Z

Phase 4b executor built deterministic 10% data validation using `(run * 1000003 + luminosityBlock * 9176 + event) % 10 == 0` on data rows only. W high-mT scale = 0.8433 ± 0.0868; score modelling status = flagged.

## 2026-06-02T16:15:34Z

Phase 4b executor built deterministic 10% data validation using `(run * 1000003 + luminosityBlock * 9176 + event) % 10 == 0` on data rows only. W high-mT scale = 0.8433 ± 0.0868; score modelling status = flagged.

## 2026-06-02T16:25:20Z

Phase 4c executor used all available Run2012B/C TauPlusX data from `sensitivity_selected_events.npz` with no post-unblinding retuning. Full high-mT W scale = 0.8528 ± 0.0370; full score modelling status = flagged. Phase 4b warning remains carried to Phase 5.
