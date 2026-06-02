# Phase 3 Selection / Processing Plan

Session: `executor_phase3_selection_20260602T110516Z`

## Governing Inputs

This phase implements the Phase 1 search/template-fit strategy, not the
measurement label in the scaffolded `phase3_selection/CLAUDE.md`. Binding
inputs are `prompt.md`, Phase 1 decisions [D1]-[D9],
`phase2_exploration/outputs/EXPLORATION.md`,
`phase2_exploration/outputs/local_sample_manifest.json`, and
`conventions/search.md`.

The available reduced samples are exactly the localized Run2012B/C TauPlusX
data files and the seven MC files under `mc/`. Missing paper-level components
from Phase 2, including QCD/multijet MC, diboson, single top, associated Higgs
production, H to WW, W4/inclusive W+jets, embedded Z to tau tau, and additional
DY categories, will remain explicit limitations. They will not be silently
included or approximated by manual scaling.

## Scripts

1. `phase3_selection/src/build_selection.py`
   - Read all local ROOT files through `uproot` with `awkward`/`numpy`.
   - Build one muon and one tau_h candidate per event using final object
     definitions and overlap removal.
   - Derive event variables: visible mass, add-MET mass, muon-MET transverse
     mass, visible-plus-MET transverse momentum proxy, jet multiplicity,
     leading-dijet mass, leading-dijet `|Delta eta_jj|`, b-tag flags,
     charges, isolation, and region/category labels.
   - Assign mutually exclusive signal-region categories in this order:
     `vbf`, then `boosted`, then `zero_jet`. If a category has unstable
     statistics, mark it as merge/downscope evidence in the outputs.
   - Assign orthogonal control/validation regions: high-mT W CR, same-sign
     QCD sideband, Z-rich validation region, and b-tag/top handle.
   - Write selected event summaries to a compact `.npz` artifact and JSON
     summaries: `cutflow.json`, `category_yields.json`,
     `region_yields.json`, `normalization_inputs.json`, and
     `selection_config.json`.

2. `phase3_selection/src/model_inputs_and_mva.py`
   - Read the selected summaries, not ROOT files.
   - Produce an MVA input-quality table using validation/control regions.
     For every candidate input, compute data-vs-MC shape `chi2/ndf` using
     raw shape-normalized MC because external normalization is unresolved.
   - Remove candidate inputs with `chi2/ndf > 5` unless they are strictly
     category-defining variables and the artifact documents the reason.
   - Train a primary classifier and an alternative architecture when enough
     passing inputs and MC statistics remain. The default primary is
     `MLPClassifier`; the alternative is `HistGradientBoostingClassifier`.
   - Save model metadata and validation artifacts in
     `phase3_selection/outputs/models/`, including split seed, input list,
     training/test ROC AUC, and downscope status if the quality gate fails.
   - Formally downscope NN genMET regression unless this phase finds a direct
     truth target. Phase 2 found no `GenMET` and no neutrino generator
     particles in the reduced files, so the expected outcome is downscope.

3. `phase3_selection/src/compare_approaches.py`
   - Compare at least two qualitatively distinct Phase 1 approaches using the
     same selected events and categories:
       - baseline visible-mass template selection;
       - add-MET mass template selection;
       - NN/BDT classifier score template if the MVA gate passes.
   - Use raw, shape-normalized templates and an MC-only expected separation
     metric such as binned Asimov `sum S^2/(B+1)` or `S/sqrt(B+1)` per
     category. This is a Phase 3 ranking metric only, not a final expected
     limit, because normalization inputs are not yet fully resolved.
   - Write `approach_comparison.json` and document which observable is kept
     as Phase 4 primary under [D9].

4. `phase3_selection/src/plot_selection.py`
   - Produce CMS-style PDF and PNG figures for final object kinematics,
     cutflow/yields, W high-mT CR, same-sign sideband, Z-rich validation,
     visible mass by category, add-MET mass by category, jet/VBF variables,
     MVA input quality, and MVA scores if applicable.
   - Use `mplhep` CMS labels, `(10, 10)` figures, no titles, no grids, no
     absolute font sizes, and save both PDF and PNG.

## Selection Definitions

Muon candidate:
- `Muon_pt > 20 GeV`, `|Muon_eta| < 2.1`, tight ID if available, and finite
  relative isolation with a baseline isolation requirement. Sentinel isolation
  values are excluded from the candidate pool.

Tau_h candidate:
- `Tau_pt > 20 GeV`, `|Tau_eta| < 2.3`, tight anti-muon veto
  `Tau_idAntiMuTight > 0`, finite isolation, and a tau isolation working point
  chosen from available reduced branches. A deliberately loose retained tau
  selection is used because the prompt and Phase 1 [D5]/[D6] require enlarged
  tau/Z uncertainties due to missing official scale factors, but the tight
  anti-muon veto remains mandatory.

Candidate arbitration:
- Pick the highest-pt muon passing the muon mask.
- Pick the highest-pt tau passing the tau mask and separated from the muon by
  `Delta R > 0.5`.
- Opposite-sign, low-mT events define the signal-region candidate set.

Jet and b-tag handling:
- Use jets with `pt > 30 GeV`, `|eta| < 4.7`, separated from the selected muon
  and tau by `Delta R > 0.5`.
- Treat `Jet_btag < 0` as a sentinel/invalid b-tag value. Define a top handle
  from valid high b-tag values using a documented threshold scan and retain
  the exact threshold in `selection_config.json`.

## Category Hierarchy

Categories are mutually exclusive and assigned only among selected
opposite-sign low-mT signal-region events:

1. `vbf`: at least two clean jets, high leading-dijet mass, large
   `|Delta eta_jj|`, and a visible/add-MET `pT_tautau` proxy requirement if it
   improves expected MC separation without destabilizing yields.
2. `boosted`: non-VBF events with at least one clean jet and elevated
   visible/add-MET `pT_tautau` proxy.
3. `zero_jet`: non-VBF, non-boosted events with zero clean jets.

Inclusive distributions are diagnostic only and will not be advertised as an
additional simultaneous-fit category.

## Validation Gates

- Cutflow must be monotonically non-increasing per sample.
- Categories must be exclusive: no selected event may be assigned to more than
  one fit category.
- MVA input-quality gate: `chi2/ndf <= 5` in validation/control regions where
  statistics permit, else calibrate, remove, or justify/downscope.
- Control-region closure diagnostics will be reported as raw and
  shape-normalized because exact production normalization is unresolved. Any
  failed gate with a proposed primary observable will receive documented
  remediation attempts or will downscope that observable.
- No full-data signal-region optimization will use observed data yields.
  Category thresholds are anchored to Phase 1 reference values and MC-only
  expected sensitivity.

## Normalization Plan

Phase 3 will attempt to resolve citable external inputs for the 8 TeV CMS
luminosity, ggH/VBF production cross sections, branching fraction, DY/W/top
cross sections, and W jet-bin stitching. If exact citable inputs cannot be
resolved within this executor run, outputs will be raw and shape-normalized,
and `normalization_inputs.json` plus `SELECTION.md` will list the exact Phase 4
blockers. No MC sample will be manually scaled to data, and W normalization
will be prepared through the high-mT CR yield structure rather than tuned by
hand.

## Artifacts

Primary artifact:
- `phase3_selection/outputs/SELECTION.md`

Machine-readable outputs:
- `selected_events.npz`
- `cutflow.json`
- `category_yields.json`
- `region_yields.json`
- `variable_modeling.json`
- `approach_comparison.json`
- `normalization_inputs.json`
- `selection_config.json`
- `models/model_metadata.json`

Figures:
- PDF+PNG pairs in `phase3_selection/outputs/figures/` with 2+ sentence
  captions in `SELECTION.md`.

Pixi:
- Add independent Phase 3 tasks for every script.
- Update `all` to run Phase 2 localization/exploration/plots and Phase 3
  selection/plotting chain.

Final checks:
- Run all Phase 3 pixi tasks.
- Run `pixi run lint-plots`.
- Append `experiment_log.md` and
  `phase3_selection/logs/executor_phase3_selection_20260602T110516Z.md`.

## 2026-06-02T15:18:31Z Continuation Plan

This continuation resumes from checkpoint commit `7c15b68` and addresses the
user-requested modern-method update without using observed full-data
signal-region performance.

1. Inspect the current dependency stack for transformer feasibility. If a
   suitable stack is present, train a compact tabular/event transformer with a
   short epoch budget and validation split; otherwise document the missing
   stack and keep the strongest fast available model as fallback.
2. Preserve the Phase 3 `vbf`, `boosted`, and `zero_jet` categories in every
   fit-candidate recommendation. Inclusive-score variants may remain in the
   comparison table as diagnostics, but cannot be selected as the final method
   for this request.
3. Compare the baseline categorized visible-mass model, category-preserving
   transformer score fit, genMET direction regression if target branches exist,
   and add-MET mass comparator using expected-only pyhf sensitivity metrics.
4. Write updated candidate-comparison JSON/artifact content with feature
   lists, channel/category definitions, binning, sparse-bin handling, expected
   discovery Z, expected median CLs limit where evaluated, feasibility notes,
   W high-mT normalization status, anti-muon veto status, and Z/tau nuisance
   treatment.
5. Regenerate Phase 3 sensitivity outputs and figures, then hand the selected
   category-preserving recommendation to Phase 4a.
