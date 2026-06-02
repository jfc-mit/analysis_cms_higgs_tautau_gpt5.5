# Phase 3 trigger-finding fixer log

Timestamp: 2026-06-02T12:18:28Z

## Plan

1. Inspect the Phase 3 selection trigger implementation and nearby metadata/prose without touching ROOT inputs.
2. Narrow the production trigger mask to `HLT_IsoMu17_eta2p1_LooseIsoPFTau20` only, while preserving metadata that `HLT_IsoMu24` and `HLT_IsoMu24_eta2p1` are present but intentionally excluded because they define a different higher-pT single-muon phase space.
3. Update Phase 3 artifacts/prose and any narrowly incorrect Phase 1/2 text about trigger policy if present.
4. Rerun `pixi run phase3-all` to regenerate selected samples, yields, modelling outputs, plots, and Phase 3 prose.
5. Verify with `pixi run lint-plots`, `git diff --check`, JSON validity checks, and an independent selected-event consistency check comparing event flags to `category_yields.json` and `region_yields.json`.
6. Append `experiment_log.md`, record before/after trigger policy and verification results in this log, then commit with `fix(phase3): restrict selection to tauplusx trigger`.

## Review finding addressed

This fixes the Category A trigger finding from `phase3_critical_rereview_20260602T121544Z.md`: the previous Phase 3 production selection ORed `HLT_IsoMu24_eta2p1`, `HLT_IsoMu24`, and `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`, adding candidates outside the required TauPlusX primary-trigger phase space.

## Execution

### Before/after trigger policy

- Before: `phase3_selection/src/build_selection.py` accepted events passing
  `HLT_IsoMu24_eta2p1` OR `HLT_IsoMu24` OR
  `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`.
- After: the production trigger mask is only
  `HLT_IsoMu17_eta2p1_LooseIsoPFTau20` for all Phase 3 signal, control, and
  validation regions.
- Metadata retained: `selection_config.json` and `normalization_inputs.json`
  record that `HLT_IsoMu24` and `HLT_IsoMu24_eta2p1` are present in the reduced
  files but intentionally not used because they define a different higher-pT
  single-muon phase space.

### Code and artifact updates

- Updated `phase3_selection/src/build_selection.py` to use the TauPlusX primary
  trigger only.
- Added explicit trigger policy metadata to `selection_config.json` and
  `normalization_inputs.json`.
- Regenerated Phase 3 selected events, yields, modelling outputs, and figures
  with `pixi run phase3-all`.
- Updated `phase3_selection/outputs/SELECTION.md` trigger prose and regenerated
  yield/diagnostic numbers.
- Corrected `region_yields.json` category bookkeeping so category counts are
  computed on the same compact selected-event summary surface used by
  `selected_events.npz`; this made the requested independent consistency check
  auditable.

### Regenerated selected counts

- Low-mT signal-region totals: data 10,758; signal MC 1,668; background MC
  8,402.
- Exclusive category totals:
  - Data: VBF 79, boosted/1-jet 2,213, zero-jet 8,466.
  - Signal MC: VBF 387, boosted/1-jet 748, zero-jet 533.
  - Background MC: VBF 240, boosted/1-jet 2,818, zero-jet 5,344.
- Control/validation totals: W high-mT data 4,023 and background MC 6,283;
  same-sign low-mT data 3,138 and background MC 1,200; Z-rich data 5,514 and
  background MC 4,396.

### Verification

- `pixi run phase3-all`: passed; rerun after the trigger fix and the
  region-yields bookkeeping correction.
- `pixi run lint-plots`: passed; no plotting violations found.
- `git diff --check`: passed.
- `pixi run py - <<'PY' ... JSON validity ... PY`: passed for 14 Phase 2/3
  output JSON files.
- `pixi run py - <<'PY' ... selected-events/category/region consistency ... PY`:
  passed, 108 comparisons using `is_signal_region`, `is_w_high_mt`,
  `is_same_sign_low_mt`, `is_z_rich`, and `is_top_btag_handle` against
  `category_yields.json` and `region_yields.json`.
- `pixi run py - <<'PY' ... trigger implementation assertion ... PY`: passed;
  the production mask uses only the primary TauPlusX trigger.

## Result

The Category A trigger finding from
`phase3_critical_rereview_20260602T121544Z.md` is resolved. No ROOT files were
downloaded or overwritten.
