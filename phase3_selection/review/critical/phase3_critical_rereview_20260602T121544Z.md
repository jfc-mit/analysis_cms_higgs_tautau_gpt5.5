# Phase 3 Critical Rereview

Timestamp: 2026-06-02T12:15:44Z

Reviewer role: fresh Phase 3 critical reviewer

Artifact reviewed: `phase3_selection/outputs/SELECTION.md` and Phase 3 machine-readable outputs/scripts after commits `e0dd136`, `355120c`, and `4d2d03e`.

## Headline Verdict

FAIL. The prior critical findings A1/A2/B1/B2 are substantially resolved, and the normalization metadata now uses the requested official luminosity and CERN Open Data MC denominators. However, the Phase 3 selection implementation still accepts single-muon triggers in addition to the TauPlusX primary trigger. This contradicts the user constraint and the corrected normalization metadata, and it changes the selected signal-region event sample.

## Inputs Read

- `phase1_strategy/outputs/STRATEGY.md`
- `phase2_exploration/outputs/EXPLORATION.md`
- `phase2_exploration/outputs/local_sample_manifest.json`
- `phase3_selection/outputs/SELECTION.md`
- `phase3_selection/outputs/normalization_inputs.json`
- `phase3_selection/outputs/variable_modeling.json`
- `phase3_selection/outputs/selected_events.npz`
- `phase3_selection/outputs/category_yields.json`
- `phase3_selection/outputs/region_yields.json`
- `phase3_selection/outputs/cutflow.json`
- `phase3_selection/outputs/approach_comparison.json`
- `phase3_selection/outputs/selection_config.json`
- `phase3_selection/src/build_selection.py`
- `phase3_selection/src/model_inputs_and_mva.py`
- `phase3_selection/src/compare_approaches.py`
- `phase3_selection/src/plot_selection.py`
- Prior failed reviews:
  - `phase3_selection/review/critical/phase3_critical_review_20260602T112610Z.md`
  - `phase3_selection/review/validation/phase3_plot_validation_20260602T112429Z.md`
- Fixer logs:
  - `phase3_selection/logs/fixer_phase3_20260602T113623Z.md`
  - `phase3_selection/logs/regression_normalization_20260602T115033Z.md`

## Findings

### A1. Phase 3 selection still ORs in single-muon triggers, changing the TauPlusX selection phase space

The corrected normalization metadata says the data stream is TauPlusX, the primary trigger is `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`, and the single-muon triggers are not interchangeable without a separate selection definition. This matches the user constraint. But `phase3_selection/src/build_selection.py` still defines the event trigger mask as:

- `HLT_IsoMu24_eta2p1`
- OR `HLT_IsoMu24`
- OR `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`

This is not merely stale documentation. A targeted pixi check over the localized ROOT inputs, keeping the rest of the Phase 3 selection logic fixed, found that the current OR trigger adds selected candidates relative to the primary TauPlusX trigger alone:

| Role | Current low-mT SR | Primary-trigger low-mT SR | Extra from single-muon OR |
|---|---:|---:|---:|
| data | 11,127 | 10,758 | 369 |
| signal MC | 1,740 | 1,668 | 72 |
| background MC | 8,776 | 8,402 | 374 |

It also changes W high-mT and same-sign sideband counts:

| Role | Current W high-mT | Primary-trigger W high-mT | Current same-sign low-mT | Primary-trigger same-sign low-mT |
|---|---:|---:|---:|---:|
| data | 4,211 | 4,023 | 3,227 | 3,138 |
| signal MC | 64 | 62 | 37 | 34 |
| background MC | 6,552 | 6,283 | 1,240 | 1,200 |

Impact: `selected_events.npz`, `cutflow.json`, `category_yields.json`, `region_yields.json`, `variable_modeling.json`, and all Phase 3 figures are generated from the broader trigger OR. Those outputs are therefore not in the official TauPlusX tutorial trigger phase space specified by the user and by `normalization_inputs.json`.

Required fix: make the Phase 3 production trigger selection use `HLT_IsoMu17_eta2p1_LooseIsoPFTau20` only, then rerun Phase 3 selection, modelling, approach comparison, plots, and written counts. If the analysis intentionally keeps single-muon triggers, it needs a formally revised selection/luminosity/trigger-efficiency strategy before Phase 3 can pass; under the current user constraints that is not the allowed path.

## Prior Finding Closure

- Prior A1, modelling validation: resolved for Phase 3 processing. `variable_modeling.json` now records four remediation attempts, keeps the MVA downscoped because 13/16 candidate inputs fail the modelling gate, and documents that raw broad background templates are not final closure-validated Phase 4 predictions without additional normalization, QCD/missing-background treatment, and nuisance modelling.
- Prior A2, selected-event region semantics: resolved. `selected_events.npz` now has `is_signal_region` and explicit boolean region flags. `is_signal_region` agrees with both `category_yields.json` and `region_yields.json` for data, signal, and background.
- Prior B1, approach-comparison gate: resolved. `approach_comparison.json` and `SELECTION.md` now label the raw MC metric as diagnostic only and set `expected_sensitivity_gate_status = not_evaluated_in_phase3`.
- Prior B2, control-region count disagreement: resolved. The written W high-mT, same-sign, and Z-rich counts agree with `region_yields.json`.
- Prior plot Category A issues: resolved by lint. `pixi run lint-plots` reports no plotting violations in seven files.

## Normalization Provenance Check

The normalization regression itself satisfies the requested provenance:

- `normalization_inputs.json` uses `L_int = 11.467/fb = 11467/pb`.
- The luminosity source is the CMS Open Data H to tau tau tutorial `skim.cxx` in the record 12350 context, and `no_circular_derivation = true`.
- Data records 12358 and 12359 record the official event counts 35,647,508 and 51,303,171 as parent data-record metadata, not luminosity inputs.
- MC records 12351-12357 use `CERN Open Data distribution.number_events` as the denominator.
- The per-local-entry absolute weights equal `cross_section_pb * 11467 / record_number_events`.
- Signal samples are documented as H to tau tau only, with signal normalization using `sigma_prod * BR(H->tautau)`.
- The 2.6% 2012 luminosity uncertainty is attributed to CMS PAS LUM-13-001.

The blocker is that the event selection does not yet use the trigger phase space implied by that normalization metadata.

## Phase 1/2 Regression Check

Phase 1 and Phase 2 corrected the stale interpretation of local ROOT entries:

- `STRATEGY.md` no longer claims local samples are incomplete solely because entries differ from official record counts.
- `EXPLORATION.md` separates local reduced/skimmed `Events` entries from official CERN Open Data event counts and says local entries are not normalization denominators.
- `local_sample_manifest.json` records both `local_events_tree_entries` and `official_open_data_record.distribution_number_events` for the localized records.

The trigger issue is traceable to Phase 3 execution rather than to those Phase 1/2 normalization-provenance corrections. It requires rerunning Phase 3 outputs after the trigger definition is corrected.

## Regression Checklist

- Validation test failures without three documented remediation attempts: no. The modelling artifact documents four attempts.
- Any single systematic > 80% of total uncertainty: not applicable in Phase 3.
- GoF toy distribution inconsistent with observed chi2: not applicable in Phase 3.
- Flat-prior gate excluding > 50% of bins: not applicable in Phase 3.
- Tautological comparison presented as independent validation: no finding.
- Visually identical distributions that should be independent: no finding.
- Result > 30% relative deviation from a well-measured reference value: not applicable; no final physics result yet.
- Binding Phase 1 commitments fulfilled or formally deferred: mostly yes, but Phase 3 violates the trigger/normalization phase-space constraint supplied for this rereview.
- Fit chi2 identically zero: not applicable in Phase 3.

## Verification Commands

- `git status --short`
- `git log --oneline --decorate -n 12`
- `pixi run py - <<'PY' ... prior review and fixer log reads ... PY`
- `pixi run py - <<'PY' ... normalization JSON weight checks ... PY`
- `pixi run py - <<'PY' ... selected-event/category/region consistency checks ... PY`
- `pixi run py - <<'PY' ... trigger OR versus primary-trigger scan over localized ROOT inputs ... PY`
- `pixi run lint-plots`
- `git diff --check`

## Verdict

FAIL. Category A issue A1 remains unresolved.
