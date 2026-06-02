# Phase 2 Exploration Plan

Session: `executor_phase2_exploration_20260602T093019Z`

## Scope

Phase 1 resolved this analysis as a CMS 2012 Open Data H to tau tau
search/template-fit analysis in the mu tau_h final state. The Phase 2
exploration therefore treats `conventions/search.md` and Phase 1 decisions
[D1]-[D9] as binding, despite the scaffold text still saying measurement.

## Data Source Resolution

1. Resolve the prompt-listed file names against local repository listings,
   local filesystem paths, and CERN Open Data records.
2. Use `cern-opendata-access.md` access order: local/EOS path if mounted,
   otherwise XRootD `root://eospublic.cern.ch//eos/opendata/cms/...`; avoid
   copying or downloading large ROOT files until metadata and file sizes are
   known.
3. Query authoritative public CERN Open Data records and associated GitHub
   file listings for the reduced NanoAOD outreach dataset, parent datasets,
   file URLs, record DOIs, event counts, and provenance.
4. Record SciTreeRAG unavailability in `retrieval_log.md`; use CERN/CMS public
   documentation as fallback citations for object definitions, data quality,
   and sample provenance.

## Files To Inspect First

Inspect metadata in this order, stopping at metadata and small slices before
any broad processing:

1. `VBF_HToTauTau.root` because Phase 1 already identified CERN Open Data
   record 12352 and an event-count anchor.
2. `GluGluToHToTauTau.root` to confirm signal schema and truth target support.
3. `DYJetsToLL.root` because it anchors the dominant Z/DY background and the
   visible-mass/Z-rich validation.
4. `Run2012B_SingleMu.root` and `Run2012C_SingleMu.root` to resolve the
   SingleMu-versus-TauPlusX provenance issue [A3].
5. `W1JetsToLNu.root`, `W2JetsToLNu.root`, `W3JetsToLNu.root`, and `TTbar.root`
   for W high-mT CR and top/b-tag feasibility.

## Metadata and Schema Discovery

For every available sample:

- Identify file access path, size, CERN record or parent dataset where known.
- List ROOT trees, event counts, branch names, branch types, jagged structure,
  and aliases/title metadata.
- Inventory object branches: muons, taus, electrons, jets, b-tagging, MET,
  genMET, generator particles, triggers, IDs, isolation, decay modes, charges.
- Save machine-readable schema output to
  `phase2_exploration/outputs/sample_inventory.json`.

## Branch, Weight, and Flag Archaeology

For every branch whose name suggests weight, flag, quality, trigger, ID,
filter, pileup, generator, tau anti-muon, b-tag, MET, or luminosity:

- On a ~1000 event slice, compute finite fraction, min, max, mean, standard
  deviation, and unique values for low-cardinality branches.
- Identify non-trivial weights and flags that are not all 1/0.
- Explicitly inventory pileup branches and weights to satisfy the Phase 1
  pileup fix.
- Record output to `phase2_exploration/outputs/branch_diagnostics.json`.

## Normalization Information To Retrieve

Phase 2 will retrieve or flag gaps for:

- Sample event counts and sum of generator weights, if present.
- Cross sections and luminosity metadata from file metadata, CERN Open Data
  records, associated analysis repository listings, or citable CMS/Higgs
  references.
- Published CMS 2012 luminosity and uncertainty source for later Phase 4 use.
- W+jets jet-bin normalization/stitching information if available.
- Missing QCD, diboson, single-top, Run2012A/D, TauPlusX, or additional W bins.

If exact xsec/lumi inputs cannot be sourced in Phase 2, baseline yields will be
reported as raw or internally weighted counts, and Phase 3 will receive a
blocking normalization-resolution item before production templates.

## Object and Variable Survey

Use small slices first, then scale only as needed for stable diagnostic
figures. Candidate event quantities:

- Muon and tau_h candidate counts, charges, pt, eta, phi, isolation, ID, tau
  anti-muon and tau ID branch values.
- Opposite-sign/same-sign mu-tau availability.
- Visible mass, deltaR, deltaEta, deltaPhi.
- MET and genMET quantities, transverse mass mT(mu, MET), add-MET mass.
- Jet multiplicity, leading/subleading jet pt and eta, dijet mass, deltaEta_jj,
  b-tag variables.
- Trigger and event-quality flags.
- Truth labels and generator final-state information for signal/background
  separation and genMET direction/phi regression.

## GenMET Regression Feasibility

Check whether MC contains:

- Direct `GenMET` or equivalent magnitude and phi branches.
- Generator-particle neutrino branches sufficient to derive a tau-neutrino
  missing-momentum target.
- Truth-matching or generator mother/status information to avoid target
  ambiguity.

Check that every proposed NN input also exists in data. If the target is absent
or reconstructed-only data inputs are insufficient, flag Phase 1 alternative
(b) as a strategy revision/downscope input.

## Baseline Preselection Feasibility

Define loose exploratory masks only for feasibility, not final optimized cuts:

- At least one muon candidate and one tau_h candidate.
- Opposite-sign and same-sign counts separately.
- Tight tau_h anti-muon branch availability and candidate values.
- Low-mT and high-mT partitions for prospective SR/W CR.
- Jet bins for non-VBF/VBF feasibility; b-tag availability for top CR.

Estimate raw and, where possible, weighted yields per sample after these masks.

## Planned Figures

All figures will be written to `phase2_exploration/outputs/figures/` as PDF and
PNG with CMS Open Data/Open Simulation labels and draft captions in
`EXPLORATION.md`.

Planned initial figures:

1. Sample event-count and file-size summary.
2. Muon pt and eta distributions for data/MC slices.
3. Tau_h pt and eta distributions for data/MC slices.
4. MET and genMET comparisons where available.
5. Visible mass after loose mu tau_h candidate construction.
6. mT(mu, MET) with low-mT/high-mT regions indicated in caption text.
7. Jet multiplicity.
8. Dijet mass and deltaEta_jj for events with at least two jets.
9. Signal-versus-background separation rankings for candidate variables.
10. Branch availability heatmap or summary plot for required Phase 1 features.

## PDF Build Stub Test

Create `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md` only if no real
file already exists, include one math expression and one existing citation from
`references.bib`, run `pixi run build-pdf`, document the result, then delete
the stub and generated `.tex`/`.pdf` if it was created by this test.

## Artifact Structure

Expected outputs:

- `phase2_exploration/outputs/EXPLORATION.md`
- `phase2_exploration/outputs/sample_inventory.json`
- `phase2_exploration/outputs/branch_diagnostics.json`
- `phase2_exploration/outputs/preselection_yields.json`
- `phase2_exploration/outputs/variable_separation.json`
- `phase2_exploration/outputs/figures/*.pdf`
- `phase2_exploration/outputs/figures/*.png`
- `phase2_exploration/review/self/executor_self_review_20260602T093019Z.md`
- Session log entries in
  `phase2_exploration/logs/executor_phase2_exploration_20260602T093019Z.md`

Scripts will be added under `phase2_exploration/src/` and exposed as pixi
tasks. The `all` task will be added or updated once scripts exist.
