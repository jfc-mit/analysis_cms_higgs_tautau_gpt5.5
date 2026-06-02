# Phase 3 Plot Validation After Trigger Fix

Timestamp: 20260602T123315Z

Validator: fresh Phase 3 plot revalidator after trigger fix

Scope: review-only rereview of regenerated Phase 3 figures and
plot/provenance text after commit `16f4084`. No implementation files were
modified.

Headline verdict: PASS. No unresolved Category A or Category B findings.

## Inputs Reviewed

- `phase3_selection/outputs/SELECTION.md`
- `phase3_selection/outputs/selection_config.json`
- `phase3_selection/outputs/normalization_inputs.json`
- `phase3_selection/src/plot_selection.py`
- `phase3_selection/src/build_selection.py`
- `phase3_selection/outputs/figures/*.pdf`
- `phase3_selection/outputs/figures/*.png`
- prior plot rereview artifact
  `phase3_selection/review/validation/phase3_plot_validation_rereview_20260602T121228Z.md`

## Verification Commands

| Command | Outcome |
|---|---|
| `pixi run lint-plots` | Passed: no plotting violations found. |
| `pixi run py - <<'PY' ... markdown figure-reference check ... PY` | Passed: 21 unique figure references, 21 PDFs, 21 PNGs, no missing targets, no unreferenced PDFs, no duplicate figure labels or duplicate references. |
| `pixi run py - <<'PY' ... PNG readability and dimensions ... PY` | Passed: all 21 PNGs are readable, nonblank-sized, and have four-channel image data. |
| `montage phase3_selection/outputs/figures/*.png ... /tmp/phase3_trigger_rereview_contact.png` | Produced a temporary contact sheet outside the repository for visual inspection. |
| `grep -RIn "HLT_IsoMu24\|IsoMu24_eta2p1\|IsoMu17_eta2p1_LooseIsoPFTau20\|single-muon\|ORed\|OR\|local ROOT\|local entries\|back-calculation\|source_url\|2012/skim.cxx\|blob/2012/skim.cxx" ...` | Used for targeted trigger/provenance string audit. No blocking issue found. |
| `grep -RIn "set_title\|tight_layout\|constrained_layout\|Open Simulation\|Open Data" phase3_selection/src/plot_selection.py phase3_selection/outputs/SELECTION.md` | Confirmed Open Data/Open Simulation label strings and no `set_title`, `tight_layout`, or `constrained_layout` usage in the Phase 3 plotting source. |
| `git diff --check` | Passed. |

## Plot Findings

No Category A findings.

No Category B findings.

Category C findings: none.

Checks performed:

- `pixi run lint-plots` passes.
- All regenerated Phase 3 figure references in `SELECTION.md` resolve to
  existing PDFs, and each referenced PDF has a matching PNG.
- Visual inspection of all 21 regenerated PNGs found CMS labels on every plot.
  Mixed data/MC plots use `CMS Open Data + Open Simulation`, and the MC-only
  approach comparison uses `CMS Open Simulation`.
- No plot titles are used; captions remain in `SELECTION.md`.
- Legends are present and not clipped in the regenerated figures.
- The approach-comparison plot has visible x-axis padding and is not pinned to
  the plot-frame edges.
- The MVA input modelling plot uses explicit labels such as `Visible+MET p_T
  proxy`, `Leading jet p_T`, and `Maximum b-tag score` instead of mechanically
  converted branch names.
- No ratio-panel spacing issue is applicable because the Phase 3 figures are
  single-panel plots.

## Trigger and Provenance Findings

No Category A findings.

No Category B findings.

Category C findings: none.

Checks performed:

- `SELECTION.md` states that all analysis regions require only
  `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`.
- `SELECTION.md`, `selection_config.json`, and `normalization_inputs.json`
  document `HLT_IsoMu24` and `HLT_IsoMu24_eta2p1` only as available
  alternatives intentionally excluded from the TauPlusX selection definition.
- `phase3_selection/src/build_selection.py` computes the event trigger mask
  from `PRIMARY_TRIGGER = "HLT_IsoMu17_eta2p1_LooseIsoPFTau20"` only; the
  single-muon triggers are not ORed into the selected-event mask.
- Plot/provenance text no longer implies a single-muon trigger OR selection.
  The only `ORed` reference is the explicit statement that the single-muon
  triggers are intentionally not ORed into Phase 3 selections.
- `SELECTION.md` and `normalization_inputs.json` state that local ROOT
  `Events` entries are processing, shape, and cutflow entries only, not data
  luminosity inputs or MC generation denominators.
- `SELECTION.md` and `normalization_inputs.json` state that no luminosity was
  computed from local entries, selected counts, generated MC counts, or data/MC
  back-calculation.
- `normalization_inputs.json` retains the tutorial source URL on the `2012`
  branch:
  `https://github.com/cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis/blob/2012/skim.cxx`.

## Verdict

PASS. The regenerated Phase 3 figures and plot/provenance text satisfy the
after-trigger-fix rereview scope, with no unresolved Category A or Category B
findings.
