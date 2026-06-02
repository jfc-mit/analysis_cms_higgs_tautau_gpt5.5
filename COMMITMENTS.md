# Commitments Tracker

Reconstruction status: reconstructed at Phase 4a start because
`COMMITMENTS.md` was absent when the Phase 4a executor began.

Source: `phase1_strategy/outputs/STRATEGY.md`, especially labels [A1]-[A4],
[L1]-[L4], [D1]-[D9], search convention enumeration, reference-driven
systematics, alternative-observable gates, and downstream obligations.

Status key:

- `[x]` resolved or addressed in current phase context.
- `[D]` formally downscoped with documented justification.
- `[ ]` still pending for later phases.

## Decisions

- [x] [D1] Search/template-fit analysis with profile likelihood and search
  conventions. Phase 4a uses a pyhf binned template workspace.
- [x] [D2] Primary observable is `m_vis` by category. Phase 4a builds the
  expected model on visible mass.
- [x] [D3] Fit categories are mutually exclusive VBF, boosted/1-jet, and
  zero-jet. Phase 4a uses the Phase 3 exclusive `category` labels.
- [D] [D4] W+jets normalization from data using high-mT control region.
  Phase 4a is expected-only and blinded, so it does not use real high-mT data
  to tune W. It documents the available Phase 3 high-mT handle and carries W
  control-region normalization to Phase 4b/4c.
- [x] [D5] Tight tau_h anti-muon veto. Implemented in Phase 3 selection and
  inherited by Phase 4a templates.
- [x] [D6] DY/Z normalization uncertainty 10-15% for missing trigger/tau scale
  factors. Phase 4a implements a 15% DY/Z constrained normalization nuisance.
- [x] [D7] pyhf-compatible HistFactory workspace with MC-stat bin terms.
  Phase 4a creates `pyhf_workspace.json` with Barlow-Beeston-lite staterror
  modifiers.
- [x] [D8] Blinding. Phase 4a uses Asimov/pseudo-data only and does not use
  real signal-region observed results.
- [D] [D9] Alternative observables and NN gates. Phase 3 downscoped the NN
  classifier and NN genMET regression; Phase 4a retains visible mass primary
  and records add-MET as diagnostic only unless expected-sensitivity
  comparison with nuisances is implemented later.

## Constraints and Limitations

- [x] [A1] Reduced NanoAOD files lack full trigger/tau efficiency machinery.
  Phase 4a includes this as a tau/open-data acceptance nuisance and limitation.
- [x] [A2] Prompt sample list misses full paper-level backgrounds. Phase 4a
  limitations table names missing QCD, diboson, single-top, W4/inclusive W,
  embedded Z, associated Higgs, HWW, and extra DY components.
- [x] [A3] Data provenance resolved as TauPlusX Run2012B/C rather than
  prompt-listed SingleMu. Phase 4a follows the Phase 3 TauPlusX trigger scope.
- [x] [A4] Scope constrained to mu tau_h. Phase 4a expected results are
  labelled single-channel reduced-open-data results.
- [x] [L1] Single-channel scope weakens sensitivity. Carried to Phase 4a
  limitations.
- [x] [L2] Missing official trigger/tau scale factors. Phase 4a implements and
  documents enlarged tau/DY uncertainties.
- [x] [L3] Visible-mass baseline is less powerful than CMS SVFit. Phase 4a
  states this method limitation.
- [D] [L4] QCD/multijet unavailable as reduced MC. Phase 4a does not invent a
  fake QCD template from real signal-region data; it carries QCD sideband
  treatment to later blinded data-validation phases.

## Search Convention and Systematic Commitments

- [x] Signal cross-section theory uncertainty: signal normalization source is
  recorded; dedicated theory nuisance is downscoped unless a citable variation
  is implemented in Phase 4a.
- [D] Signal acceptance and shape: full tau/JES/MET/generator shape variations
  are downscoped in Phase 4a due unavailable variation samples/scale-factor
  machinery; limitations are carried explicitly.
- [D] Pileup profile and weights: no pileup weights exist in reduced files;
  downscoped to qualitative PV_npvs limitation.
- [D] PDF and QCD scale variations: no event-level PDF/scale weights or
  alternative generators in the reduced files; downscoped with citation need.
- [x] Background normalization: DY, luminosity, tau/open-data acceptance, and
  MC statistics are implemented; W/QCD/top-specific data constraints are
  deferred/downscoped for expected-only 4a.
- [D] Background shape: no real-data SR shape tuning or sideband-derived QCD
  shape in Phase 4a; shape systematics requiring unavailable variations are
  documented as limitations.
- [x] MC statistics: Phase 4a includes per-category Barlow-Beeston-lite
  staterror modifiers.
- [D] Detector/object calibration: tau efficiency/open-data acceptance is
  implemented as a sourced rate nuisance; full TES, muon, JES/JER, MET, b-tag,
  and pileup variations are downscoped pending citable reduced-sample inputs.
- [x] Luminosity: 2.6% CMS 2012 luminosity nuisance implemented for
  MC-normalized predictions.

## Phase 4a Validation Commitments

- [x] Expected CLs upper limit. Phase 4a wrote `expected_results.json`.
- [x] Signal injection at 0x, 1x, 2x, 5x. Phase 4a wrote `signal_injection.json`.
- [x] Nuisance pull/constraint checks on Asimov. Phase 4a records fitted nuisance deltas in `expected_results.json`.
- [x] Chi2/ndf and limited toy GoF. Phase 4a wrote `gof_validation.json`.
- [x] Systematic completeness table versus conventions and reference analyses. Phase 4a wrote it in `systematics.json` and `INFERENCE_EXPECTED.md`.
- [x] Machine-readable nominal templates/yields, workspace, expected summary,
  systematics, injections, GoF, and limitations. Phase 4a populated `outputs/`.
