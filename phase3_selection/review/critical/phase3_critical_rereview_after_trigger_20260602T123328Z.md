# Phase 3 Critical Rereview After Trigger Fix

Timestamp: 2026-06-02T12:33:28Z

Reviewer role: fresh Phase 3 critical re-reviewer after trigger fix

Artifact reviewed: `phase3_selection/outputs/SELECTION.md` and Phase 3
machine-readable outputs/scripts after commit `16f4084`.

## Headline Verdict

PASS. The prior Category A trigger finding is resolved. Phase 3 production
selection now requires only `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`, the
single-muon triggers are documented only as available-but-unused alternatives,
and the regenerated yields match the primary-trigger-only event counts. I found
no unresolved Category A or Category B issues in this re-review scope.

## Inputs Reviewed

- `phase3_selection/src/build_selection.py`
- `phase3_selection/src/model_inputs_and_mva.py`
- `phase3_selection/src/compare_approaches.py`
- `phase3_selection/src/plot_selection.py`
- `phase3_selection/outputs/SELECTION.md`
- `phase3_selection/outputs/selected_events.npz`
- `phase3_selection/outputs/cutflow.json`
- `phase3_selection/outputs/category_yields.json`
- `phase3_selection/outputs/region_yields.json`
- `phase3_selection/outputs/selection_config.json`
- `phase3_selection/outputs/normalization_inputs.json`
- `phase3_selection/outputs/variable_modeling.json`
- `phase3_selection/outputs/approach_comparison.json`
- Prior critical reviews under `phase3_selection/review/critical/`
- Trigger-fixer log `phase3_selection/logs/fixer_phase3_trigger_20260602T121828Z.md`
- `phase1_strategy/outputs/STRATEGY.md`
- `phase2_exploration/outputs/EXPLORATION.md`
- `experiment_log.md`
- `pixi.toml`

## Findings

### Category A

None.

### Category B

None.

### Category C

No required Phase 3 changes. Phase 4 should preserve the current caveat that
the raw broad background-only templates are not final closure-validated fit
predictions until normalization, missing-background/QCD treatment, and
nuisance-constrained control-region modelling are implemented.

## Trigger Fix Verification

The production trigger mask is now primary-trigger-only:

- `build_selection.py` defines `PRIMARY_TRIGGER =
  "HLT_IsoMu17_eta2p1_LooseIsoPFTau20"`.
- `process_chunk` computes `trigger = scalar(arrays, PRIMARY_TRIGGER, 0.0) > 0`.
- A source assertion found no `scalar(arrays, "HLT_IsoMu24...")` production use
  and no trigger assignment that ORs in `HLT_IsoMu24` or
  `HLT_IsoMu24_eta2p1`.
- `selection_config.json` records `trigger.required =
  HLT_IsoMu17_eta2p1_LooseIsoPFTau20`.
- `normalization_inputs.json` records the same primary trigger and lists
  `HLT_IsoMu24` and `HLT_IsoMu24_eta2p1` only under
  `available_alternatives_not_used`.
- `SELECTION.md` says all analysis regions require the TauPlusX primary trigger
  and explicitly says the single-muon triggers are intentionally not ORed into
  Phase 3 selections.

The regenerated output counts match the primary-trigger-only totals identified
in the failed rereview:

| Role | Low-mT signal region | W high-mT | Same-sign low-mT |
|---|---:|---:|---:|
| data | 10,758 | 4,023 | 3,138 |
| signal MC | 1,668 | 62 | 34 |
| background MC | 8,402 | 6,283 | 1,200 |

This closes the prior Category A trigger issue.

## Prior Finding Closure

- Prior A1, modelling validation: remains resolved for Phase 3. The modelling
  artifact documents four remediation attempts, keeps the MVA downscoped because
  13 of 16 candidate inputs fail the modelling gate, and scopes raw broad
  templates as not final Phase 4 closure-validated predictions without the
  missing normalization/QCD/nuisance work.
- Prior A2, selected-event region semantics: remains resolved. `selected_events.npz`
  contains explicit boolean flags, and `is_signal_region` agrees with
  `category_yields.json`, `region_yields.json`, and the cutflow
  `low_mt_signal_region` counts for every sample.
- Prior B1, approach-comparison gate: remains resolved. `approach_comparison.json`
  records `expected_sensitivity_gate_status = not_evaluated_in_phase3`; the
  raw MC metric is diagnostic only.
- Prior B2, stale control-region counts: remains resolved. `SELECTION.md` counts
  agree with the regenerated JSON totals for W high-mT, same-sign low-mT, and
  Z-rich validation regions.
- Prior plot issues: remain resolved. `pixi run lint-plots` reports no plotting
  violations.

## Normalization Provenance Check

The normalization metadata still satisfies the user constraints:

- Data luminosity is `L_int = 11.467/fb = 11467/pb`.
- The luminosity source is the CMS Open Data H to tau tau tutorial `skim.cxx`,
  with CERN Open Data record 12350 as the reduced-analysis context.
- CERN Open Data record 1054 is recorded as the official 2012 luminosity source
  and documents the pxl-preferred, HFOC-fallback rule.
- `no_circular_derivation = true`; luminosity is not derived from local ROOT
  entries, selected event counts, generated MC counts, or data/MC
  back-calculation.
- Data records 12358 and 12359 provide official parent reduced-record event
  counts for Run2012B/C TauPlusX.
- MC records 12351-12357 use `CERN Open Data distribution.number_events` as
  normalization denominators.
- Per-local-entry MC weights equal
  `cross_section_pb * 11467 / record_number_events`.
- The luminosity uncertainty is 2.6% from CMS PAS LUM-13-001.

## Internal Consistency Checks

The selected-event, category, region, and cutflow surfaces are internally
consistent after the rerun:

- All compact selected events have the saved `trigger` flag true.
- `low_mt` and `is_signal_region` are identical.
- Every signal-region event has exactly one fit category among `vbf`, `boosted`,
  and `zero_jet`.
- No non-signal-region event has a non-`none` fit category.
- Per-sample `selected_events.npz` category counts match `category_yields.json`.
- Per-sample `selected_events.npz` region-flag counts match
  `region_yields.json`.
- Per-sample `cutflow.json` `low_mt_signal_region` counts match the
  `region_yields.json` `signal` counts.
- Cutflows are monotonically non-increasing for all samples.
- `plot_selection.py` uses boolean flags, not the old overwritten `region`
  string, for signal-region and control/validation plots.

Aggregate exclusive category totals are:

| Role | VBF | Boosted/1-jet | Zero-jet |
|---|---:|---:|---:|
| data | 79 | 2,213 | 8,466 |
| signal MC | 387 | 748 | 533 |
| background MC | 240 | 2,818 | 5,344 |

## Regression Checklist

- Validation test failures without three documented remediation attempts: no.
  `variable_modeling.json` records four attempts.
- Any single systematic > 80% of total uncertainty: not applicable in Phase 3.
- Any GoF toy distribution inconsistent with observed chi2: not applicable in
  Phase 3.
- Any flat-prior gate excluding > 50% of bins: not applicable in Phase 3.
- Any tautological comparison presented as independent validation: no finding.
- Any visually identical distributions that should be independent: no finding.
- Any result with > 30% relative deviation from a well-measured reference value:
  not applicable; Phase 3 has no final physics result.
- All binding commitments from Phase 1 fulfilled or formally deferred: yes for
  Phase 3 scope. The search/template-fit processing, visible-mass baseline,
  VBF/boosted/zero-jet categories, W high-mT handle, tight tau anti-muon veto,
  DY/Z validation handle, pyhf-compatible summaries, blinding caveats, and
  diagnostic alternative-observable comparison are implemented or explicitly
  deferred to Phase 4 where the strategy requires statistical modelling.
- Fit chi2 identically zero: not applicable in Phase 3.
- Circular luminosity derivation: no finding; the metadata explicitly records
  non-circular luminosity provenance.
- Severe modelling failures hidden without Phase 4 blockers: no finding. The
  broad raw background-model limitations remain explicit in `SELECTION.md`.

## Verification Commands

- `git status --short`
- `git log --oneline -5`
- `find phase3_selection -maxdepth 3 -type f | sort`
- `nl -ba phase3_selection/src/build_selection.py`
- `nl -ba phase3_selection/outputs/SELECTION.md`
- `nl -ba phase3_selection/review/critical/phase3_critical_review_20260602T112610Z.md`
- `nl -ba phase3_selection/review/critical/phase3_critical_rereview_20260602T121544Z.md`
- `grep -RIn "IsoMu24\\|IsoMu17_eta2p1_LooseIsoPFTau20\\|PRIMARY_TRIGGER\\|available_alternatives_not_used" ...`
- `grep -RIn "HLT_IsoMu24.*|\\||.*HLT_IsoMu24\\|scalar(arrays, .*HLT_IsoMu24\\|trigger =" ...`
- `pixi run py - <<'PY' ... selected-events/category/region/cutflow/normalization consistency checks ... PY`
- `pixi run py - <<'PY' ... trigger implementation assertion ... PY`
- `pixi run lint-plots`
- `git diff --check`
- `git show --stat --oneline --decorate --name-only 16f4084`

## Verdict

PASS. No unresolved Category A or Category B findings remain in this Phase 3
critical re-review scope.
