# Phase 3 Critical Review

Timestamp: 2026-06-02T11:26:10Z

Reviewer role: critical reviewer

Artifact reviewed: `phase3_selection/outputs/SELECTION.md`

## Headline Verdict

FAIL. Phase 3 implements the basic category structure and records several limitations honestly, but Category A issues remain. The primary background/modeling validation fails the Phase 3 alarm threshold, and the machine-readable selected-event `region` field is inconsistent with the documented signal-region counts in a way that can cause Phase 4 to build or plot the wrong templates.

## Inputs Read

- `agents/critical_reviewer.md`
- `prompt.md`
- `phase1_strategy/outputs/STRATEGY.md`
- `phase2_exploration/outputs/EXPLORATION.md`
- `phase3_selection/outputs/SELECTION.md`
- `experiment_log.md`
- `methodology/06-review.md` sections 6.3 and 6.4 Phase 3
- `methodology/03-phases.md` Phase 3 material
- `conventions/search.md`
- Phase 3 JSON outputs and scripts under `phase3_selection/outputs/` and `phase3_selection/src/`

## Findings

### A1. Primary background/modeling validation fails the Phase 3 alarm band, with no remediation attempts documented

Methodology `06-review.md` Phase 3 says the processing review must check whether the background model closes and states: `chi2/ndf > 3` is Category A. The MVA input modeling output is also the only quantitative data/background-MC shape validation provided for the primary and alternative observables.

Evidence:

- `phase3_selection/outputs/variable_modeling.json` reports `fail_count = 13` of `candidate_input_count = 16`, with `majority_failed = true` at lines 3-5.
- The primary observable `m_vis` has `chi2/ndf = 17.304161215540933` in validation/control regions, reported at `variable_modeling.json` lines 319-329.
- The add-MET alternative has `chi2/ndf = 43.38433875974739`, reported at `variable_modeling.json` lines 366-376.
- Several core selection/control variables are far above the alarm band: `mt_mu_met = 110.25827649992759`, `met_pt = 80.67791086982733`, `n_clean_jets = 512.9756258563599`, and `btag_max = 338.6228300364724` in `variable_modeling.json`.
- The executor log documents the failure and immediate downscope, but not remediation: it says 13 of 16 variables failed and the classifier was downscoped. It does not document three remediation attempts, calibration attempts, rebinning/stability checks, alternative sideband definitions, missing-component subtraction, or a formal closure test.

This is not only an NN issue. The primary visible-mass observable itself fails the validation-region shape modeling gate by a factor of about 5.8 above the `chi2/ndf > 3` Category A threshold. Missing QCD/diboson/single-top/normalization inputs are honestly documented, but they do not make the current background model close. Phase 4 should not proceed from these templates until the executor either fixes the modeling, documents and runs remediation attempts, or formally regresses/downscopes the affected fit strategy.

### A2. `selected_events.npz` region labels are not consistent with the documented signal region and can make downstream Phase 4 templates wrong

The artifact says Phase 4 should treat `selected_events.npz` and related files as the source of Phase 3 category definitions and raw selected counts. However, the `region` string in `selected_events.npz` is overwritten by validation labels after assigning `"signal"`.

Evidence:

- In `phase3_selection/src/build_selection.py`, `low_mt` is the signal-region boolean at line 300. The region string is then assigned `"signal"` at line 322, but overwritten by `"top_btag_handle"` and `"z_rich"` at lines 325-326.
- The raw signal-region counts in `region_yields.json` are computed from the `low_mt` boolean, not from `region == "signal"` (`build_selection.py` lines 394-395).
- A direct consistency check of `selected_events.npz` gives:
  - data: `low_mt` = 11127, but `region == "signal"` = 4281
  - signal MC: `low_mt` = 1740, but `region == "signal"` = 168
  - background MC: `low_mt` = 8776, but `region == "signal"` = 2708
  - `low_mt & z_rich` overlap = 11701 events across roles
- `phase3_selection/src/plot_selection.py` uses `signal_region = selected["region"] == "signal"` at line 221 for the muon, tau, MET, mT, `pt_tautau_proxy`, jet multiplicity, `mjj`, and `delta_eta_jj` diagnostics. Those figures therefore exclude Z-rich and top-handled low-mT signal-region events while their captions call them signal-region diagnostics.

This is a Category A blocker because Phase 4 could reasonably use `region == "signal"` and silently drop most low-mT selected events from signal-region diagnostics or templates. The fix is not cosmetic: the machine-readable event summary needs either non-overwriting boolean region flags or explicitly exclusive region semantics, and the plots/documentation must use the same definition as the category/template counts.

### B1. The approach-comparison metric is common but not yet defensible as an expected-sensitivity gate

Phase 1 [D9] requires an alternative observable to improve expected sensitivity by at least 10% in expected mu uncertainty, expected CLs limit, or expected discovery significance. Phase 3 instead compares raw unweighted MC histograms.

Evidence:

- `phase1_strategy/outputs/STRATEGY.md` lines 140-145 define the [D9] gate in terms of expected sensitivity.
- `phase3_selection/src/compare_approaches.py` lines 40-47 computes `sum S/sqrt(B+1)` and `sqrt(sum S^2/(B+1))` from raw histogram counts.
- `compare_approaches.py` lines 52-55 labels the comparison as `raw unweighted MC counts; Phase 3 ranking only`.
- `approach_comparison.json` reports visible mass = 61.66831665147916 and add-MET mass = 59.22994198789599 at lines 24 and 52, but no expected mu uncertainty, CLs limit, discovery significance, injection recovery, or GoF is provided.

Using the same raw samples for both observables gives a useful diagnostic, and it is enough to avoid promoting add-MET as primary. It is not enough to claim the Phase 1 [D9] expected-sensitivity gate has been executed. The artifact should state that the expected-sensitivity part of [D9] remains a Phase 4 task, not complete Phase 3 evidence.

### B2. Machine-readable JSON and `SELECTION.md` disagree on control-region counts

Evidence:

- `SELECTION.md` lines 90-91 says the W high-mT control region has 4211 data events and 6520 raw background MC events.
- Summing `region_yields.json` background samples gives 6552 raw background MC events in `w_high_mt`: DY 136 + TTbar 4092 + W1 611 + W2 1096 + W3 617.
- `SELECTION.md` line 95 says the same-sign QCD sideband has 3227 data events and 1711 raw background MC events.
- Summing `region_yields.json` background samples gives 1240 raw background MC same-sign events: DY 527 + TTbar 189 + W1 128 + W2 244 + W3 152.
- The Z-rich validation count is consistent: `SELECTION.md` line 99 reports 5763 data and 4617 background MC, matching the JSON sums.

This is not as severe as A2 because the JSON exists and can be used as the source of truth. It still must be fixed before PASS because the written artifact is stale or internally inconsistent for two control-region counts.

## Checks That Passed

- Category exclusivity is implemented at the boolean category level: `build_selection.py` assigns VBF first, then boosted, then zero-jet at lines 306-319. Category sums match the artifact: data 83/2261/8783, signal 395/772/573, background 246/2896/5634 in VBF/boosted/zero-jet.
- Cutflow monotonicity passes for all samples. I checked the ordered steps in `cutflow.json`; no sample has a later count larger than the previous step.
- The tight tau anti-muon veto is implemented: `Tau_idAntiMuTight > 0` is required in `build_selection.py` tau selection and is recorded in `selection_config.json`.
- The genMET regression downscope is justified by Phase 2: `EXPLORATION.md` reports no direct `GenMET_pt`/`GenMET_phi` and no neutrino generator-particle truth target in the reduced branch diagnostics; `variable_modeling.json` records the formal downscope.
- Missing paper-level components and normalization inputs are documented rather than manually tuned. `normalization_inputs.json` reports `status = blocking_for_phase4_absolute_templates`, `resolved_in_phase3 = false`, and states that no MC sample has been manually scaled to data.

## Required Fixes Before Re-Review

1. Resolve A1 by running a proper Phase 3 background/modeling remediation loop or formally revising the strategy. At minimum, the primary `m_vis` validation-region shape failure must be addressed with documented attempts and quantitative post-remediation results.
2. Resolve A2 by making region definitions unambiguous and internally consistent. Phase 4 inputs must not be able to confuse low-mT signal membership with exclusive validation/control labels.
3. Resolve B1 by reframing the raw approach comparison as diagnostic only, or replacing it with a Phase 1 [D9]-compatible expected-sensitivity metric.
4. Resolve B2 by regenerating or correcting `SELECTION.md` control-region counts from the current JSON source of truth.

## Final Answer to Reviewer Framing

A competing H to tau tau group would have a validated background model for the primary observable, a control-region closure result with `chi2/ndf` below the Phase 3 alarm band, and unambiguous machine-readable region definitions suitable for a simultaneous category fit. This Phase 3 artifact does not yet have those, so it should not advance as PASS.
