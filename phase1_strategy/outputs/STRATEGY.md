# Phase 1 Strategy: CMS 2012 Open Data H to Tau Tau Search

## Summary

This analysis will search for a Standard Model Higgs boson decaying to
$\tau\tau$ in CMS 2012 Open Data at $\sqrt{s}=8$ TeV, restricted initially to
the $\mu\tau_h$ final state. The primary result is a simultaneous
profile-likelihood shape fit across mutually exclusive event categories,
including a VBF-enriched category. The baseline final observable is the
visible di-tau mass, $m_\mathrm{vis}$, with three planned alternatives:
an NN discriminator fit, an NN-assisted missing-momentum mass observable, and
a mass observable after adding missing energy.

The local scaffold labels Phase 1 as a measurement, but the user physics
prompt specifies a signal-versus-background Higgs search with category fits.
[D1] The primary technique is therefore a search/template-fit analysis, and
`conventions/search.md` is the binding convention. Measurement-like outputs
will be auxiliary comparisons and will not replace the search result.

## Retrieval Status and Sources

SciTreeRAG MCP tools were not available in this environment, so the mandated
corpus searches could not be executed. This was recorded in
`retrieval_log.md` and `experiment_log.md`. The strategy instead uses public
authoritative sources:

| Source | Role in strategy | Key numerical/useful content |
|---|---|---|
| CMS, "Evidence for the 125 GeV Higgs boson decaying to a pair of tau leptons", JHEP 05 (2014) 104, DOI: 10.1007/JHEP05(2014)104, arXiv:1401.5041, PDF mirror: https://publikationen.bibliothek.kit.edu/1000042067/3154375 | Primary Run 1 reference analysis for 7+8 TeV H to tau tau. | 4.9 fb^-1 at 7 TeV and 19.7 fb^-1 at 8 TeV; best-fit signal strength 0.78 ± 0.27 in the abstract; local significance larger than 3 standard deviations for Higgs-mass hypotheses between 115 and 130 GeV; systematic table and category methodology. |
| CMS, "Observation of the Higgs boson decay to a pair of tau leptons with the CMS detector", Phys. Lett. B 779 (2018) 283, DOI: 10.1016/j.physletb.2018.02.004, arXiv:1708.00373, PDF: https://cds.cern.ch/record/2276465/files/scoap3-fulltext.pdf | Modern CMS H to tau tau method reference and systematic cross-check. | 35.9 fb^-1 at 13 TeV; observed significance 4.9, expected 4.7; best-fit signal strength 1.09 +0.27/-0.26; combined with the corresponding 7 and 8 TeV CMS result gives 5.9 standard deviations. |
| CERN Open Data record 12350, "Analysis of Higgs boson decays to two tau leptons using data and simulation of events at the CMS detector from 2012", https://opendata.cern.ch/record/12350 | Open-data provenance for the reduced NanoAOD outreach sample set. | Lists GluGluToHToTauTau, VBF_HToTauTau, DYJetsToLL, TTbar, W1/W2/W3JetsToLNu, and Run2012 TauPlusX reduced NanoAOD inputs, plus the GitHub analysis branch. |
| CERN Open Data record 12352, "VBF_HToTauTau dataset in reduced NanoAOD format for education and outreach", DOI: 10.7483/OPENDATA.CMS.EA1T.GVAF, https://opendata.cern.ch/record/12352 | Example sample provenance and scale. | VBF_HToTauTau is derived from `/VBF_HToTauTau_M-125_8TeV-powheg-pythia6-tauola-tauPolarOff/.../AODSIM`; record lists 491653 events in one file. |
| ATLAS and CMS, "Measurements of the Higgs boson production and decay rates...", JHEP 08 (2016) 045, DOI: 10.1007/JHEP08(2016)045, arXiv:1606.02266 | External Run 1 comparison target. | Uses approximately 5 fb^-1 at 7 TeV and 20 fb^-1 at 8 TeV per experiment; combined signal yield relative to SM 1.09 ± 0.11; H to tau tau observed significance 5.5. |

All numbers above are Phase 1 comparison targets or source descriptions. Any
additional constants needed for event weighting, Higgs branching fractions,
production cross sections, PDG values, or detector performance must be
retrieved from citable sources before use in Phases 2-4.

## Physics Motivation

The Higgs mechanism predicts Yukawa couplings to fermions. The $\tau\tau$
mode is the most accessible direct probe of a charged-lepton Higgs Yukawa
coupling because the branching fraction is much larger than for electrons or
muons, while the final state remains experimentally separable from fully
hadronic backgrounds. The Run 1 CMS analysis states this motivation directly:
the $\tau\tau$ mode is important because the new boson discovered near
125 GeV had already been seen mainly in bosonic channels, and the $\tau$
channel tests fermion couplings.

This open-data analysis will not aim to reproduce the full CMS publication.
[L1] The scope is limited to reduced NanoAOD-like files and initially to the
$\mu\tau_h$ final state. The analysis can still test whether the available
samples and simplified object corrections support a credible H to tau tau
shape-fit demonstration with honest uncertainties.

## Technique Selection

[D1] Use a search/template-fit analysis with a binned profile likelihood.
The parameter of interest is the signal-strength modifier $\mu$ multiplying
the Standard Model H to tau tau signal templates. The same statistical model
will be used for expected results, 10% data validation, and full observed
results.

Search conventions apply because the primary result is either a signal
strength/significance or, if sensitivity is too weak, an expected/observed
upper limit on $\mu$. The fit uses binned discriminant shapes and nuisance
parameters, matching `conventions/search.md`. `conventions/extraction.md`
does not apply because there is no closed-form double-tag or counting
extraction. `conventions/unfolding.md` does not apply because no
detector-level spectrum is corrected to a particle-level distribution.

[D2] The baseline result will be a visible-mass template fit, not an SVFit
mass fit, because the prompt requests visible mass as the key observable and
the reduced open-data sample may not contain the full MET covariance and
trigger/scale-factor information used by CMS. This is a limitation relative
to CMS JHEP 05 (2014) 104, where the svfit mass improved expected
significance by about 40% relative to visible mass in the $\mu\tau_h$
baseline comparison. The three required alternative observables will test how
much sensitivity can be recovered with the reduced information.

## Constraints, Limitations, and Binding Decisions

### Constraints

- [A1] Reduced open-data NanoAOD-like files may not include the full trigger,
  tau ID, tau trigger, and tau efficiency scale-factor machinery used in CMS
  publications.
- [A2] The prompt-provided sample list does not include every background used
  in CMS publications. Diboson, single-top, QCD/multijet, and additional
  W+jets bins must be searched for in Phase 2; absent samples become explicit
  limitations or data-driven estimates.
- [A3] The available data files in the prompt are SingleMu Run2012B/C, while
  CERN Open Data record 12350 lists TauPlusX Run2012B/C for its outreach
  analysis. Phase 2 must resolve the exact data provenance and trigger paths
  before finalizing selection.
- [A4] The analysis is constrained to $\mu\tau_h$ initially. It will not claim
  the all-channel CMS sensitivity achieved by the reference analyses.

### Limitations

- [L1] Single-channel scope weakens sensitivity and comparability to CMS
  all-channel results.
- [L2] Missing official trigger and tau efficiency scale factors require a
  deliberately enlarged tau ID/efficiency uncertainty and Z normalization
  uncertainty. These will be assigned before looking at signal-region data,
  not tuned to agreement with the Drell-Yan peak.
- [L3] The baseline visible-mass observable is less powerful than the
  reference CMS svfit mass. This is an explicit method limitation, partly
  addressed by the three alternative fit observables.
- [L4] If QCD/multijet samples or robust same-sign/anti-isolation control
  regions are unavailable, QCD will be treated as a downscoped instrumental
  background with a conservative, data-constrained uncertainty rather than
  silently omitted.

### Decisions

- [D1] Primary technique: search/template fit with profile likelihood and
  search conventions.
- [D2] Primary fit observable: $m_\mathrm{vis}$ by category; alternatives
  are required cross-checks and may replace the baseline only after Phase 3
  evidence.
- [D3] Categories: at minimum inclusive/baseline and VBF-enriched categories;
  add 0-jet and boosted categories if Phase 2 confirms sufficient statistics.
- [D4] W+jets normalization: derive from data using a high-$m_T$ control
  region and include that control region in or alongside the likelihood.
- [D5] Tau ID: apply tight tau_h anti-muon veto. Tau ID/trigger efficiency
  uncertainty will be set in the 10-15% range unless Phase 2 retrieves a
  better official scale-factor source.
- [D6] Z/Drell-Yan normalization: use MC shape initially and a 10-15%
  normalization uncertainty to reflect missing trigger turn-on and tau
  efficiency effects, with Phase 4 validation against the Z peak and control
  regions. This is a limitation label [L2], not a post-hoc tuning knob.
- [D7] Statistical implementation: pyhf/cabinetry-compatible HistFactory
  workspace with MC-stat bin terms and named nuisance parameters.
- [D8] Blinding: do not inspect full-data signal-region discriminant
  distributions before Phase 4b/4c gates. Phase 3 optimization uses MC,
  control regions, and allowed validation regions only.

## Observables and Fit Outputs

Primary event-level observables:

- $m_\mathrm{vis}$: invariant mass of the visible muon and tau_h candidate
  four-vectors. This is the baseline final discriminant because it is robust
  with reduced inputs and visibly separates the broad H to tau tau signal
  from the Z to tau tau peak.
- $m_\mathrm{addMET}$: mass-like observable formed by adding the missing
  transverse momentum as a massless four-vector approximation to the visible
  system. This is required alternative (c) and will be treated as an
  empirical discriminant, not a fully reconstructed tau-pair mass.
- $m_\mathrm{NNMET}$: combined mass built from visible objects and an NN
  regression of genMET direction/phi. This is required alternative (b).
  Training must use simulation only, validate on independent MC, and test
  robustness to MET and generator systematics.
- $D_\mathrm{NN}$: NN classifier score trained to separate H to tau tau from
  backgrounds with systematics propagated through the templates. This is
  required alternative (a).

Fit outputs:

- Expected and observed best-fit signal strength $\mu$ with statistical,
  systematic, theory, and MC-stat uncertainty components where possible.
- Expected and observed local significance at the fixed Higgs mass used by
  the signal samples.
- Expected and observed upper limits on $\mu$ if sensitivity is inadequate
  for a meaningful significance claim.
- Per-category post-fit yields, nuisance pulls, constraints, and impacts.
- Comparisons to CMS JHEP 05 (2014) 104, CMS Phys. Lett. B 779 (2018) 283,
  and ATLAS+CMS JHEP 08 (2016) 045 targets, with single-channel limitations
  clearly labelled.

## Dataset and Sample Inventory Plan

The prompt lists the following expected ROOT inputs:

| Sample | Process | Role | Phase 2 provenance checks |
|---|---|---|---|
| `Run2012B_SingleMu.root`, `Run2012C_SingleMu.root` | CMS 2012 data | Collision data for $\mu\tau_h$ | Confirm trigger streams, luminosity mapping, event counts, branch schema, and whether these correspond to the CERN Open Data outreach files or another GitHub listing. |
| `GluGluToHToTauTau.root` | ggH, H to tau tau, nominal mass from sample name | Signal | Confirm parent AODSIM dataset, generator, event weights, sum of generated weights, cross-section source, and tau truth branches. |
| `VBF_HToTauTau.root` | VBF H to tau tau | Signal, VBF category anchor | CERN record 12352 identifies a VBF HToTauTau 8 TeV powheg-pythia6-tauola parent and 491653 events; Phase 2 must verify the local file matches this record. |
| `DYJetsToLL.root` | Drell-Yan to leptons | Dominant irreducible/background-like Z to tau tau component and Z peak normalization handle | Confirm whether Z to tau tau, Z to mu mu, and Z to ee components can be separated by truth labels or final-state reconstruction. |
| `TTbar.root` | top-pair production | Important reducible background with real muons, jets, MET, and possible fake tau_h | Confirm b-tag branches for veto/control and whether a top-enriched validation region can be built. |
| `W1JetsToLNu.root`, `W2JetsToLNu.root`, `W3JetsToLNu.root` | W+jets by jet bin | Reducible fake tau_h background | Confirm generator weights, jet-bin stitching requirements, and high-$m_T$ control-region purity. |

Additional samples to request/search in Phase 2:

- Diboson and single-top simulation, because CMS references include them as
  smaller but non-negligible backgrounds.
- QCD/multijet samples or data sideband handles. If no QCD MC exists, the
  same-sign and anti-isolation sidebands become the primary instrumental
  estimate.
- Run2012A/D or TauPlusX data if the user wants closer parity to the open-data
  outreach record and if the analysis scope allows expansion.

## Background Classification

| Background | Classification | Expected relative importance | Strategy |
|---|---|---|---|
| Z/gamma* to tau tau | Irreducible | Dominant in $\mu\tau_h$ before categorization; strongly reduced in VBF but still central to shape modelling. CMS JHEP 05 (2014) 104 identifies Drell-Yan Z to tau tau as the largest background in $\mu\tau_h$, $e\tau_h$, $\tau_h\tau_h$, and $e\mu$. | Use DY MC shape initially; normalize with a constrained nuisance. Validate at the Z peak and in low-$m_\mathrm{vis}$ sidebands. Assign 10-15% normalization uncertainty due to missing scale factors [D6]. |
| W+jets | Reducible | Significant in $\mu\tau_h$ when W decays to a muon and a jet fakes tau_h. CMS Phys. Lett. B 779 (2018) 283 uses $m_T>80$ GeV W control regions in $\mu\tau_h$ and $e\tau_h$. | Use high-$m_T$ control region to normalize [D4]. Transfer to low-$m_T$ signal region with a transfer-factor uncertainty. |
| QCD/multijet | Instrumental/reducible | Potentially important if jets fake muons or tau_h; exact size depends on isolation and same-sign sidebands. | Prefer same-sign and anti-isolation data sidebands. If unavailable, include as limitation [L4] and build a conservative sideband-derived estimate. |
| ttbar | Reducible | Important in events with jets, b jets, MET, and real muons; especially relevant in boosted/VBF-like topologies. | MC shape with b-veto and a top-enriched validation region if b-tag branches exist. |
| Diboson and single top | Reducible/irreducible small backgrounds | Smaller than DY/W/top in this channel but present in CMS reference analyses. | Add simulation if available; otherwise assign a justified normalization uncertainty and document omission. |
| Z to mu mu / Z to ee with object mis-ID | Reducible/instrumental | Can enter through lepton or tau_h misidentification; Z to mu mu is particularly relevant to tau anti-muon veto validation. | Tight tau_h anti-muon veto [D5]; validate fake components using same-sign/sideband or truth categories where available. |

## Candidate Categories and Simultaneous Fit

[D3] The minimum category structure is:

- Baseline inclusive $\mu\tau_h$: opposite-sign muon and tau_h candidates,
  low transverse mass signal region, standard object selections, and tight
  tau_h anti-muon veto.
- VBF-enriched: at least two jets, high dijet mass, large rapidity separation,
  and/or high visible-plus-MET transverse momentum. CMS 2018 used VBF
  selections with at least two jets, $m_{jj}>300$ GeV in $\mu\tau_h$, and
  $p_T^{\tau\tau}>50$ GeV; these values are reference starting points, not
  final cut values until Phase 2 confirms branch availability and Phase 3
  optimizes on expected sensitivity.

Additional categories if statistics permit:

- 0-jet: DY-dominated control-like category useful for constraining tau ID,
  Z normalization, and visible-mass modelling.
- Boosted/1-jet: one or more jets but not VBF; useful for ggH sensitivity and
  W/top validation.

The statistical model will fit all categories simultaneously. Control regions
for W+jets high-$m_T$, QCD same-sign/anti-isolation, and top-enriched b-tagged
events should either be included in the pyhf workspace or used to derive
pre-fit constraints with uncertainties propagated into the workspace.

## Selection and Fit Approaches to Compare

Phase 3 must implement and compare at least the following approaches using a
common expected-sensitivity metric, preferably expected $\mu$ uncertainty,
expected CLs limit, or expected discovery significance from Asimov/pseudo-data.

| Approach | Final observable | Strength | Cost/risk | Phase 3 comparison criterion |
|---|---|---|---|---|
| Baseline visible mass | $m_\mathrm{vis}$ in each category | Robust, transparent, prompt-requested, low dependence on missing MET covariance. | Lower separation than svfit or MVA; larger overlap with DY. | Expected sensitivity and data/MC quality in validation regions. |
| NN discriminator | $D_\mathrm{NN}$ classifier score | Uses correlations among visible kinematics, jets, MET, $m_T$, and VBF variables. | Sensitive to mismodelled inputs; must propagate systematics through score templates. | Input-variable data/MC quality gate, MC closure, signal injection, and expected fit sensitivity. |
| NN MET-direction regression | $m_\mathrm{NNMET}$ | Attempts to recover mass information lost to tau neutrinos using simulation truth. | Risk of truth leakage, generator dependence, and unphysical regression on unavailable gen-level features. | Independent MC validation, mass resolution comparison, closure under MET/jet/tau variations. |
| Add-MET mass | $m_\mathrm{addMET}$ | Simple approximation to a combined mass using available missing energy. | Not a physically complete tau-pair mass; may sculpt W/top backgrounds. | Expected sensitivity, robustness to MET scale/resolution, and comparison to visible mass. |

[D9] If an NN approach wins expected sensitivity but fails the MVA input
modelling gate, it will not become primary until the problematic inputs are
calibrated or removed. A high MC-only AUC is insufficient.

## Core Selection Commitments

- Opposite-sign muon and tau_h signal selection; same-sign retained for QCD
  sideband where useful.
- Low transverse mass signal region, with high-$m_T$ W+jets control region.
  CMS 2018 used $m_T>80$ GeV for W+jets control and $m_T<50$ GeV for signal
  selection in the relevant channels; Phase 3 will evaluate these as reference
  values using expected sensitivity and control-region purity.
- Tight tau_h anti-muon veto [D5].
- Additional loose-lepton veto if branches permit, to keep $\mu\tau_h$
  mutually exclusive from multi-lepton top/diboson-like events.
- b-jet veto for the primary signal region if b-tag branches exist; b-tagged
  sideband for top validation if statistics permit.

## W+jets High-mT Normalization Plan

[D4] W+jets will be normalized from data using a high-$m_T$ control region.
The control selection will match the signal selection except for the transverse
mass inversion. CMS Phys. Lett. B 779 (2018) 283 defines W-enriched control
regions with $m_T>80$ GeV and states that they control W+jets yields in
$\mu\tau_h$ and $e\tau_h$. This analysis will:

1. Define the low-$m_T$ signal region and high-$m_T$ W control region before
   inspecting full signal-region data.
2. Subtract non-W backgrounds using MC or sideband estimates.
3. Derive a W normalization factor and uncertainty from the control region.
4. Propagate the high-to-low-$m_T$ transfer uncertainty to the fit. CMS 2018
   quotes a 5-10% uncertainty for this transfer in its 13 TeV analysis, derived
   from a Z to mu mu based method; this analysis will not copy that value
   blindly but will use it as a reference target while deriving an open-data
   uncertainty from available validation.

## Systematic Uncertainty Plan

No systematic variation may be arbitrary. Every variation size must come from
a retrieved measurement, a published uncertainty, a data-control-region fit,
or a documented closure/stability result. If Phase 2/4 cannot source a value,
the uncertainty must be labelled as a limitation and tested through validation,
not tuned to improve agreement.

### Search Convention Enumeration

| Convention source | Status | Phase 4 implementation plan |
|---|---|---|
| Signal cross-section theory uncertainty | Will implement | Use LHC Higgs Cross Section Working Group or CMS reference values for ggH and VBF rate/theory uncertainties. Do not invent values. |
| Signal acceptance | Will implement | Vary object selections/scales and compare ggH/VBF acceptance; include generator/model limitation if only one generator is available. |
| Signal shape | Will implement | Propagate tau energy scale, MET, jet energy scale, and NN-score variations to signal templates. Alternative observables are cross-checks, not a substitute for shape systematics. |
| ISR modeling | Not applicable as LEP-specific dominant beam systematic; pp equivalent will implement | For pp, replace with parton shower/underlying-event, jet modelling, and production-mode acceptance uncertainties, following CMS reference analyses. |
| 4-fermion backgrounds | Not applicable as LEP-specific category | For pp, diboson and single-top are the analogous electroweak backgrounds; include if samples exist or assign sourced normalization uncertainty. |
| Background normalization | Will implement | DY 10-15% [D6, L2], W from high-$m_T$ data [D4], top from MC/control region, QCD from sidebands, diboson/single-top from MC with sourced uncertainties. |
| Background shape | Will implement | Shape variations for DY, W, QCD sidebands, top, and NN-score templates. Use sideband/template comparisons where possible. |
| qqbar(gamma) modeling | Not applicable as LEP-specific row; pp DY modelling will implement | Use DY modelling uncertainties and category extrapolation uncertainties instead. |
| MC statistics | Will implement | Include bin-by-bin MC statistical nuisance parameters, e.g. Barlow-Beeston-lite/pyhf `staterror`. |
| Detector simulation model | Will implement | Data/MC comparisons for all candidate input variables; mismodelled MVA inputs must be calibrated, removed, or downscoped. |
| Object calibration | Will implement | Tau energy scale, tau ID/efficiency, muon ID/trigger, muon scale if non-negligible, jet energy scale/resolution, MET scale/resolution, b-tag/mistag if used. |
| Beam energy | Not applicable | LHC beam-energy uncertainty is not expected to dominate this open-data shape fit; no mass scan precision measurement is planned. |
| Luminosity | Will implement | Use citable CMS 2012 luminosity uncertainty if MC-normalized components enter the fit. CMS JHEP 05 (2014) 104 quotes 2.6% for its 8 TeV analysis; Phase 2/4 must verify applicability to this open-data sample before use. |
| QCD scale variations | Will implement | Use published scale variations for Higgs signal and relevant simulation-normalized backgrounds when available. |
| Fragmentation model | Will implement as model limitation/cross-check where possible | Evaluate with available alternative samples or assign a model uncertainty from reference analyses; document if no alternative generator exists. |
| Heavy flavour treatment | Will implement if b-tag veto/top modelling used | Propagate b-tag/mistag and top-background modelling uncertainties; heavy-flavour fragmentation only if it materially affects selected backgrounds. |

### Reference-Driven Systematics

CMS JHEP 05 (2014) 104 Table 3 lists the following relevant sources for Run 1
H to tau tau: tau energy scale, tau ID and trigger, lepton-to-tau and
jet-to-tau misidentification, electron/muon ID and trigger, electron and jet
energy scales, missing transverse energy scale, b-tag efficiencies, Z
normalization and category extrapolation, W+jets normalization, top,
diboson, QCD multijet, reducible-background shape/rate, luminosity, PDFs,
scale variation, underlying event/parton shower, and limited event counts.
This analysis will map each source to the reduced $\mu\tau_h$ scope or mark
it inapplicable with evidence.

[D5] Tau ID/trigger efficiency uncertainty: assign a 10-15% nuisance range
unless a better citable open-data scale-factor source is found. This is
consistent in scale with the reference CMS Run 1 table, where tau ID and
trigger variations change acceptances by 6-19%, but the final value for this
analysis must be justified by the missing-scale-factor limitation and Phase 4
validation rather than copied blindly.

[D6] DY/Z normalization uncertainty: assign a 10-15% nuisance range unless a
better data-driven Z normalization constraint is obtained. CMS JHEP 05 (2014)
104 used a 3% inclusive Z yield plus category extrapolation uncertainties of
2-14% with embedded samples and full calibration machinery. This open-data
analysis lacks those inputs, so the enlarged uncertainty is a documented
limitation [L2]. Phase 4 must validate that it covers the Z peak and category
extrapolation without making all validation pulls trivially small.

## Required Validation Plan

Search-convention validation requirements:

- Closure in validation regions: W high-$m_T$, QCD same-sign/anti-isolation,
  top-enriched, and Z-rich categories must pass quantitative tests where
  statistics permit.
- Signal injection: inject 0x, 1x, 2x, and 5x expected Higgs signal into
  pseudo-data and recover $\mu$ within the convention tolerance.
- Nuisance pulls and constraints: any pull above 2 sigma or unexpected
  constraint must be investigated.
- Impact ranking: top impacts should be physically plausible, expected to
  include tau ID/efficiency, DY normalization/category extrapolation,
  W normalization/transfer, MC statistics in VBF, jet/MET effects, and signal
  theory/acceptance.
- Goodness-of-fit: report per-region and combined GoF; toy-based checks if
  asymptotic assumptions are questionable.
- Look-elsewhere effect: not primary because the Higgs mass hypothesis is
  fixed by the signal samples and reference analyses. State this explicitly
  rather than scanning masses without a global correction.

## Reference Analysis Table

| Reference | Method parity target | Systematic program | Comparable numerical targets |
|---|---|---|---|
| CMS JHEP 05 (2014) 104 | Global binned likelihood over categories/channels; final variables are $m_{\tau\tau}$ or $m_\mathrm{vis}$ in most channels, BDT-derived discriminant in ee/mumu; data-driven major backgrounds. This analysis matches the profile-likelihood/category structure but is downscoped to $\mu\tau_h$ and visible-mass baseline. | Tau energy/ID/trigger, lepton ID/trigger, jet/MET/b-tag, DY normalization and category extrapolation, W/top/diboson/QCD/reducible rates and shapes, luminosity, PDF, scale, UE/PS, MC statistics. | 4.9 fb^-1 at 7 TeV and 19.7 fb^-1 at 8 TeV; best-fit H to tau tau signal strength 0.78 ± 0.27 in the abstract; local significance larger than 3 standard deviations for Higgs-mass hypotheses between 115 and 130 GeV. |
| CMS Phys. Lett. B 779 (2018) 283 | Maximum-likelihood fits in 2D planes, categories targeting ggH and VBF, W/QCD/top control regions. This analysis adopts category/control-region logic but uses simpler 1D or NN-derived observables. | Object reconstruction/ID, tau energy/decay-mode effects, background normalization/shape, signal theory, MC statistics; MC-stat uncertainty contributes substantially in VBF-like categories. | 35.9 fb^-1 at 13 TeV; observed significance 4.9, expected 4.7; $\mu=1.09^{+0.27}_{-0.26}$; combined with CMS 7/8 TeV reaches 5.9 standard deviations. |
| ATLAS+CMS JHEP 08 (2016) 045 | External combined Run 1 benchmark, not a method template for the single-channel open-data fit. | Cross-experiment combination with production/decay parameterisations and experiment-specific nuisance correlations. | Approximately 5 fb^-1 at 7 TeV and 20 fb^-1 at 8 TeV per experiment; combined signal yield relative to SM 1.09 ± 0.11; H to tau tau observed significance 5.5. |

These targets are not pass/fail expectations for a single-channel reduced
open-data analysis. They are comparison anchors. Phase 4/5 must quantify why
the open-data sensitivity differs, including channel coverage, sample size,
missing scale factors, and simpler mass reconstruction.

## Flagship Figure List

Planned flagship figures for the final AN:

1. Visible mass in the baseline $\mu\tau_h$ category, pre-fit and post-fit,
   with stacked backgrounds and Higgs signal overlay.
2. Visible mass in the VBF-enriched category, pre-fit and post-fit, with
   category-specific S/B interpretation.
3. W+jets high-$m_T$ control-region distribution/yield comparison showing the
   data-derived W normalization.
4. VBF discriminant summary: $m_{jj}$ and $\Delta\eta_{jj}$ or equivalent
   selection variables for signal and backgrounds, preferably as separate
   CMS-style figures composed in the AN.
5. NN discriminator template and validation plot, including input-modelling
   quality and systematic-shift overlays.
6. Alternative mass observable comparison: $m_\mathrm{vis}$,
   $m_\mathrm{addMET}$, and $m_\mathrm{NNMET}$ expected sensitivity and shape.
7. Final signal-strength/limit/significance summary compared with CMS 2014,
   CMS 2018, and ATLAS+CMS combination targets, with limitations labelled.
8. Nuisance impact ranking and pull/constraint plot for the final fit.

Phase 1 produces no physics figures. These figures are Phase 2-5 obligations.

## Planned Methodology Diagrams

- Analysis-region schematic: signal regions, W high-$m_T$ control region,
  QCD same-sign/anti-isolation sideband, and top validation region.
- Fit workflow diagram: samples to templates, categories/control regions to
  pyhf workspace, nuisance parameters, and final $\mu$/limit outputs.
- Alternative-observable diagram: visible mass, add-MET mass, NN MET-regressed
  mass, and NN discriminator comparison path.

## Downstream Obligations

Phase 2:

- Resolve exact ROOT file paths, branch schemas, event counts, sum of weights,
  parent datasets, and trigger/data stream provenance.
- Confirm whether SingleMu or TauPlusX open-data inputs are available and
  appropriate.
- Inventory all weight/flag branches and truth labels.
- Produce data/MC comparisons for every candidate MVA input before any MVA is
  trained.
- Identify whether QCD, diboson, single-top, additional W bins, and additional
  data periods are available.

Phase 3:

- Implement baseline and alternative selections/observables.
- Compare all four required approaches quantitatively before selecting the
  primary observable.
- Build W high-$m_T$ normalization and at least one validation region.
- Preserve failed-approach diagnostic figures if any approach is rejected.

Phase 4a:

- Build the expected pyhf/cabinetry-compatible workspace.
- Re-read search conventions and reference systematics.
- Produce systematic completeness table comparing conventions, CMS 2014,
  CMS 2018, and this analysis.
- Run closure, injection, GoF, and impact tests.

Phase 4b:

- Validate on 10% data with compiled PDF before human gate.
- Check Z peak, W control region, VBF category stability, and NN input
  modelling on 10% data.
- Present limitations [L1]-[L4] and uncertain decisions to the human.

Phase 4c/5:

- Fit full data only after human approval.
- Compare full results to expected and 10% results.
- Compare final signal strength/significance/limit to reference targets with
  a quantitative explanation of sensitivity differences.

## Open Issues

- [O1] Exact open-data sample paths and whether prompt-listed SingleMu files
  or CERN record 12350 TauPlusX files are the intended data source.
- [O2] Availability of official or citable CMS 2012 tau ID, tau trigger, and
  muon trigger scale factors for the reduced files.
- [O3] Availability of QCD, diboson, single-top, and additional W+jets samples.
- [O4] Whether the reduced files contain enough jet/MET/tau decay-mode
  information for robust VBF categorization and NN alternatives.
- [O5] Whether genMET direction/phi is present in the simulation files. If it
  is absent, required alternative (b) needs a documented downscope or a
  derived truth target from available generator-level neutrinos.

## Pre-Review Self-Check

- Corpus/RAG: unavailable; fallback public retrieval logged.
- Backgrounds classified: yes.
- At least two qualitatively different approaches: yes, four total.
- MVA included: yes, NN discriminator and NN MET regression.
- Search conventions enumerated: yes.
- Reference analyses tabulated: yes, three references with numerical targets.
- Constraint [A], limitation [L], and decision [D] labels defined: yes.
- No Phase 1 scripts or figures expected: yes.
