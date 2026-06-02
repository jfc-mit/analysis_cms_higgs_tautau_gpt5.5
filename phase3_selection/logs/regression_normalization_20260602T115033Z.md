# Phase 2/3 Normalization Provenance Regression Plan

## Scope

Correct the mistaken interpretation of local ROOT `Events` entries as official
data/MC normalization counts. The local `data/` and `mc/` files are the current
analysis inputs, but their tree entries may be skimmed or reduced processing
entries. They must not be used as data luminosity inputs or MC generation
denominators.

## Intended Edits

1. Update Phase 3 normalization metadata to use:
   - `L_int = 11467 pb^-1`, from the CMS Open Data H to tau tau tutorial
     `skim.cxx` for Run2012B+C TauPlusX.
   - Official CERN Open Data record 1054 for the luminosity source and the
     `pxl`-preferred, `hfoc`-fallback rule.
   - CMS PAS LUM-13-001 for the 2.6% 2012 luminosity uncertainty.
   - CERN Open Data records 12351-12357 `distribution.number_events` as MC
     denominators, with DOI, file key, size, and official event count recorded.
   - CERN Open Data records 12358-12359 as the parent reduced data event-count
     records, not as luminosity back-calculation inputs.
2. Update Phase 2 manifest/prose so `events` from local ROOT files are clearly
   local processing entries. Add official record metadata for the confirmed
   reduced samples.
3. Update Phase 1/2/3 prose that still says the Run2012B/C luminosity or MC
   denominators are unresolved solely because local reduced files lack embedded
   metadata.
4. Keep selected-event content unchanged. The Phase 3 selection and category
   definitions use reco branches and boolean masks only; this regression changes
   absolute-weight provenance metadata and documentation. Event selection will
   not be rerun unless code inspection finds selected arrays depend on the wrong
   normalization model.

## Verification Plan

Run through pixi where applicable:

- JSON validity check for touched JSON artifacts.
- Targeted check that the Phase 3 normalization metadata helper returns weights
  computed with `L_int = 11467 pb^-1` and official `N_gen` denominators.
- Rerun Phase 2 manifest generation if its generator changes.
- `pixi run lint-plots` if plot captions/text are changed.
- `git diff --check`.

## Execution Notes

- Confirmed CERN Open Data API metadata for records 1054 and 12350-12359:
  records 12351-12359 provide the DOI, one distribution, official
  `distribution.number_events`, and file size values used in the corrected
  artifacts.
- Confirmed the CMS Open Data H to tau tau tutorial `skim.cxx` contains
  `integratedLuminosity = 11.467 * 1000.0` for Run2012B+C and uses
  `HLT_IsoMu17_eta2p1_LooseIsoPFTau20` as the trigger filter.
- Updated `phase3_selection/src/build_selection.py` so future regeneration
  writes normalization provenance from official records rather than marking
  luminosity unresolved.
- Regenerated `phase3_selection/outputs/normalization_inputs.json` from the
  metadata helper only.
- Updated `phase2_exploration/src/localize_samples.py` to schema v2 and
  regenerated `phase2_exploration/outputs/local_sample_manifest.json`; the
  manifest now separates `local_events_tree_entries` from official Open Data
  record event counts.
- Updated Phase 1/2/3 prose to remove the stale interpretation that smaller
  local ROOT entries imply incomplete samples or unresolved luminosity.

## Event-Selection Rerun Decision

No full Phase 3 event-selection rerun was required for this correction.
`selected_events.npz`, cutflows, category yields, and region yields are produced
from reconstructed branches and boolean masks in the local ROOT files. The
regression changes only provenance metadata and prose for absolute weights:
`L_int`, official data records, official MC `N_gen` denominators, and the
luminosity uncertainty. Since no selection threshold, branch, category rule, or
stored selected-event field changed, rerunning event selection would only
rewrite deterministic selection outputs and compressed binary files without
changing their physics content.

## Verification Results

- `pixi run py phase2_exploration/src/localize_samples.py`: passed; regenerated
  the schema v2 local sample manifest.
- `pixi run py - <<'PY' ... JSON and normalization metadata checks ... PY`:
  passed; touched JSON files parse and metadata weights equal
  `sigma * 11467 / N_gen` with official record denominators.
- `pixi run lint-plots`: passed with no plotting violations in seven files.
- `git diff --check`: passed with no whitespace errors.
