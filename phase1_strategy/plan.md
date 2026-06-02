# Phase 1 Strategy Plan

Session: executor_phase1_strategy_20260602T085932Z

## Scope and Scaffold Reconciliation

The local Phase 1 scaffold labels this as a measurement analysis, but the
physics prompt asks for a Higgs boson search in $H \to \tau\tau$ with a
shape/template fit, category structure, signal extraction, and comparison to
CMS search publications. I will treat the physics prompt as authoritative and
write the strategy for a search/template-fit analysis. Measurement-like
outputs will be labelled as auxiliary comparisons only.

## Retrieval Plan

SciTreeRAG MCP tools are not exposed in this execution environment. I will
record that limitation in `retrieval_log.md`, `experiment_log.md`, and the
session log, then use authoritative public sources:

- CMS Phys. Lett. B 779 (2018) 283, including final Run 1 $H \to \tau\tau$
  signal-strength/significance targets and systematic-program context.
- CMS JHEP 05 (2014) 104, including 7+8 TeV category and fit methodology,
  $m_{\tau\tau}$ discriminants, and systematic-program context.
- CMS Open Data records and/or official CMS/CERN sample listings for the 2012
  8 TeV SingleMu data and NanoAOD/ROOT sample provenance.
- HEPData records, INSPIRE/arXiv abstracts, and official CMS pages where they
  provide numerical comparison targets.
- PDG or official Higgs combination references only if a numerical
  world-average comparison target is needed in Phase 1.

Every numerical constant or comparison target included in `STRATEGY.md` will
be sourced to one of these public references. I will not quote constants from
memory.

## Expected Samples

The strategy will inventory the prompt-listed samples and their expected
roles:

- Data: `Run2012B_SingleMu.root`, `Run2012C_SingleMu.root`.
- Signal: `GluGluToHToTauTau.root`, `VBF_HToTauTau.root`.
- Dominant irreducible/reducible backgrounds: `DYJetsToLL.root`,
  `TTbar.root`, `W1JetsToLNu.root`, `W2JetsToLNu.root`,
  `W3JetsToLNu.root`.
- Additional samples to look for in Phase 2 if available: diboson,
  single-top, QCD-enriched or data sideband handles, extra W+jets bins,
  and additional Run2012 periods.

The strategy will keep exact file paths and event counts as Phase 2
obligations because Phase 1 does not inspect ROOT contents.

## Applicable Conventions

Primary convention: `conventions/search.md`, because the primary result is a
shape-based search for a fixed Higgs signal in background-rich final states,
with profile-likelihood/CLs/significance outputs.

Non-applicable conventions to explicitly document:

- `conventions/extraction.md`: not primary, because no closed-form
  branching-fraction or double-tag extraction is planned.
- `conventions/unfolding.md`: not primary, because no detector-level
  distribution will be unfolded to a particle-level spectrum.

The strategy will enumerate every required systematic source in
`conventions/search.md` with "Will implement" or "Not applicable because".

## Artifact Structure

`phase1_strategy/outputs/STRATEGY.md` will include:

- Summary and physics motivation.
- Technique selection and scaffold mismatch resolution.
- Constraints [A], limitations [L], and binding decisions [D].
- Observable and final fit observable definitions.
- Dataset/sample inventory and provenance plan.
- Background classification and relative-importance expectations.
- Candidate categories, including baseline and VBF categories, and a
  simultaneous fit plan.
- Selection/fit approaches: baseline visible-mass fit and the three
  requested alternatives: NN discriminator, NN genMET-direction/phi
  regression for combined mass, and mass after adding missing energy.
- W+jets high-$m_T$ data-normalization plan.
- Tight tau_h anti-muon veto commitment.
- Systematic uncertainty plan from search conventions and reference
  analyses, including the required 10-15% tau efficiency/ID limitation and
  10-15% Z normalization uncertainty limitation.
- Reference-analysis table for 2-3 published analyses, including CMS
  Phys. Lett. B 779 (2018) 283 and JHEP 05 (2014) 104, with comparable
  numerical targets.
- Phase 2-5 downstream obligations, validation targets, and open issues.
- Flagship figure list and methodology diagrams.

## Phase 1 Scripts and Figures

No analysis scripts or physics figures are expected in Phase 1. Phase 1 is a
strategy and literature/artifact phase. The flagship figures will be planned
here and produced in later phases. If retrieval requires small helper scripts,
they will be avoided unless necessary; public web retrieval will be documented
in `retrieval_log.md`.

