# Phase 3 Selection: CMS 2012 Open Data H to Tau Tau Search

## Summary

Phase 3 implements the Phase 1 [D1] search/template-fit strategy for the
reduced CMS 2012 Open Data $\mu\tau_h$ H to tau tau analysis. The scaffolded
Phase 3 file still calls this a measurement, but Phase 1 and the user prompt
define a search with simultaneous category fits, so `conventions/search.md`
is the binding convention.

The production selection uses all localized reduced samples from Phase 2:
Run2012B/C TauPlusX data and the seven available MC files for ggH, VBF, DY,
ttbar, and W1/W2/W3+jets. Missing paper-level components remain explicit
limitations: QCD/multijet MC, diboson, single top, embedded Z to tau tau,
W4/inclusive W+jets, additional DY categories, associated Higgs production,
and H to WW are not included or silently substituted.

All analysis regions require the TauPlusX primary trigger
`HLT_IsoMu17_eta2p1_LooseIsoPFTau20`. The reduced files also contain
`HLT_IsoMu24` and `HLT_IsoMu24_eta2p1`, but those single-muon triggers define
a different higher-pT muon phase space and are intentionally not ORed into the
Phase 3 signal or control selections.

## Binding Decisions Addressed

| Decision | Phase 3 implementation |
|---|---|
| [D1] Search/template fit | Implemented selection, control regions, raw templates, and machine-readable summaries for a binned multi-category search. |
| [D2] Visible-mass baseline | Retained `m_vis` as the Phase 4 primary observable. |
| [D3] Categories | Implemented mutually exclusive VBF, boosted/1-jet, and zero-jet categories with VBF assigned first. |
| [D4] W high-mT normalization | Built a high-mT W control region and raw yield inputs; no manual tuning to data was performed. |
| [D5] Tight tau anti-muon veto | Required `Tau_idAntiMuTight > 0` in the tau_h candidate definition. |
| [D6] DY/Z uncertainty scope | Kept DY as MC shape with Z-rich validation diagnostics; enlarged 10-15% normalization remains a Phase 4 nuisance choice requiring citable implementation. |
| [D7] pyhf-compatible future fit | Produced category and region yields plus selected-event summaries with unambiguous signal-region and validation/control flags suitable for Phase 4 template building. |
| [D8] Blinding | Did not optimize category thresholds on full-data SR agreement. Full-data selected SR shapes are produced as Phase 3 processing diagnostics, not fitted results. |
| [D9] Alternative gate | Compared visible mass and add-MET mass with a diagnostic common MC-only metric; the formal expected-sensitivity gate remains a Phase 4 task because it requires normalization, nuisance parameters, and a statistical model. |

## Object and Event Selection

Muon candidates require `Muon_pt > 20 GeV`, `|Muon_eta| < 2.1`,
`Muon_tightId > 0`, and finite `Muon_pfRelIso04_all < 0.20`. The selected
muon is the highest-pt passing candidate in the event.

Tau_h candidates require `Tau_pt > 20 GeV`, `|Tau_eta| < 2.3`,
`Tau_idDecayMode > 0`, `Tau_idIsoTight > 0`, `Tau_idAntiMuTight > 0`, finite
tau relative isolation, and `Delta R(mu,tau) > 0.5` from the selected muon.
The tau isolation requirement is intentionally based on the reduced tight ID
branch while retaining the mandatory tight anti-muon veto; missing official
trigger/tau scale factors are not compensated by hand.

Jets use `Jet_pt > 30 GeV`, `|Jet_eta| < 4.7`, and `Delta R > 0.5` from both
selected leptons. `Jet_btag < 0` is treated as an invalid sentinel, and the
maximum valid b-tag score is retained as a top handle rather than as a
calibrated b-tag decision.

The signal-region candidate set requires a muon-tau pair passing
`HLT_IsoMu17_eta2p1_LooseIsoPFTau20`, opposite-sign charges, and
`mT(mu,MET) < 40 GeV`. The W control region requires opposite-sign pairs with
`mT(mu,MET) > 80 GeV`, the QCD sideband uses same-sign low-mT pairs, the
Z-rich validation region uses opposite-sign low-mT events with
`60 < m_vis < 120 GeV`, and the top handle requires a selected pair with a
positive valid b-tag score.

The machine-readable event summary keeps overlapping region semantics
explicit. `is_signal_region` is the low-mT opposite-sign signal-candidate
membership used for category and template counts. `region_exclusive` is a
single diagnostic label for mutually exclusive validation/control displays,
while `is_z_rich`, `is_top_btag_handle`, `is_w_high_mt`, `is_same_sign`, and
`is_same_sign_low_mt` are boolean handles that can overlap where the physics
definitions overlap. Phase 4 should not use `region_exclusive` as a substitute
for signal-region membership.

![Cutflow summary. This plot shows raw event counts after each selection step,
summed by role across the localized data, signal MC, and background MC files.
The cutflow is monotonically non-increasing for every sample and for each role
aggregate, satisfying the Phase 3 cutflow gate.](figures/cutflow_summary.pdf){#fig:p3-cutflow}

## Exclusive Categories

Signal-region events are assigned to exactly one fit category:

1. VBF first: at least two clean jets, leading-dijet mass above 300 GeV, and
   leading-dijet `|Delta eta|` above 2.5.
2. Boosted/1-jet next: non-VBF events with at least one clean jet.
3. Zero-jet last: remaining non-VBF signal-region events.

The raw selected yields are:

| Role | VBF | Boosted/1-jet | Zero-jet |
|---|---:|---:|---:|
| Data | 79 | 2213 | 8466 |
| Signal MC | 387 | 748 | 533 |
| Background MC | 240 | 2818 | 5344 |

These categories are mutually exclusive by construction and are retained for a
simultaneous Phase 4 fit. Inclusive plots are diagnostics only and are not an
additional category.

![Exclusive category yields. The figure summarizes raw data, signal MC, and
background MC counts in the retained VBF, boosted/1-jet, and zero-jet
categories. The VBF category is statistically populated in both VBF signal and
data, so it is retained rather than merged at Phase 3.](figures/category_yields.pdf){#fig:p3-category-yields}

## Control and Validation Regions

The W high-mT control region contains 4023 data events across Run2012B/C and
6283 raw background MC events before any production normalization. This region
is prepared for Phase 4 W normalization but is not used to hand-scale W+jets in
Phase 3.

The same-sign QCD sideband contains 3138 data events and 1200 raw background
MC events. No reduced QCD MC exists, so this region is the available data
handle for the instrumental QCD/fake contribution.

The Z-rich validation region contains 5514 data events and 4396 raw background
MC events. It is retained to validate the DY/Z shape and category
extrapolation under the documented missing scale-factor limitation.

![W high-mT control region. The figure compares the normalized muon-MET
transverse-mass shape in the high-mT control region for data, signal MC, and
background MC. It prepares the W+jets control handle required by Phase 1 [D4],
but the MC has not been normalized to data.](figures/w_high_mt_control_mt.pdf){#fig:p3-wcr}

![Same-sign QCD sideband. This normalized visible-mass comparison uses
same-sign low-mT events as the available QCD/fake-tau sideband because no
reduced QCD MC sample is present. The sideband is a Phase 4 input for
data-driven QCD treatment and is not claimed to be a complete QCD estimate in
Phase 3.](figures/qcd_same_sign_mvis.pdf){#fig:p3-qcd-ss}

![Z-rich validation mass. This normalized visible-mass comparison uses the
opposite-sign low-mT Z-rich window to test the DY/Z modelling handle. The
comparison motivates keeping the enlarged DY/tau uncertainty from Phase 1
instead of tightening normalization assumptions without scale factors.](figures/z_rich_validation_mvis.pdf){#fig:p3-zrich}

## Kinematic and Category Diagnostics

The final selected objects are physically populated in all retained samples.
The selected-event summaries include muon, tau, MET, transverse mass,
visible-mass, add-MET mass, jet, dijet, b-tag-handle, region, and category
variables.

![Selected muon transverse momentum. The figure shows the normalized selected
muon pt distribution in the low-mT signal-region candidate set. It is a final
candidate diagnostic after trigger, object ID, tau anti-muon veto, and
opposite-sign selection rather than the Phase 2 first-candidate survey.](figures/mu_pt.pdf){#fig:p3-mupt}

![Selected tau transverse momentum. The figure shows the normalized selected
tau_h pt distribution after final candidate arbitration and overlap removal.
It checks that the retained tight anti-muon and tau isolation requirements do
not produce an empty or obviously pathological tau candidate spectrum.](figures/tau_pt.pdf){#fig:p3-taupt}

![Missing transverse momentum. This normalized selected-event MET comparison
supports the transverse-mass and add-MET observables used in this phase. It
also documents one of the variables that failed the MVA input modelling gate
and therefore was not used in a promoted classifier.](figures/met_pt.pdf){#fig:p3-met}

![Muon-MET transverse mass. This signal-region diagnostic shows the normalized
transverse-mass shape after the low-mT selection has been applied. The same
quantity defines the high-mT W control region, so it is kept as a region
variable rather than promoted to an MVA input.](figures/mt_mu_met.pdf){#fig:p3-mt}

![Visible-plus-MET transverse momentum proxy. The figure shows the normalized
visible+MET pt proxy available in both data and MC. It supports boosted
topology studies but failed the MVA input modelling gate in the current raw
shape comparison.](figures/pt_tautau_proxy.pdf){#fig:p3-pttautau}

![Clean jet multiplicity. The figure shows the clean-jet multiplicity after
signal-region selection and lepton-overlap removal. It motivates keeping
separate zero-jet, boosted/1-jet, and VBF categories, while the strong data/MC
shape difference prevents using it as a promoted MVA input in Phase 3.](figures/clean_jet_multiplicity.pdf){#fig:p3-njet}

![Leading dijet mass. The figure shows the normalized leading-dijet mass in
events with at least two clean jets. This variable passes the Phase 3 MVA
modelling gate and is also part of the VBF category definition inspired by the
CMS reference analyses.](figures/vbf_dijet_mass.pdf){#fig:p3-mjj}

![Leading dijet pseudorapidity separation. The figure shows the normalized
leading-dijet `|Delta eta|` distribution in events with at least two clean
jets. It passes the MVA input-quality gate and is retained as a core VBF
selection variable.](figures/vbf_delta_eta_jj.pdf){#fig:p3-detajj}

## Approach Comparison

Two template-observable approaches were fully implemented and compared with a
common diagnostic MC-only binned separation metric over the same exclusive
categories. Visible mass gives a combined raw metric of 60.63, while add-MET
mass gives 58.37. This comparison is not the Phase 1 [D9] expected-sensitivity
gate: it uses raw unweighted MC counts and no nuisance-constrained likelihood.
Visible mass remains the Phase 4 primary observable, and add-MET mass is
retained as a cross-check/alternative template candidate whose formal expected
sensitivity can only be evaluated after Phase 4 normalization and systematics
are implemented.

The NN classifier approach was evaluated through the required input-modelling
gate before training. Thirteen of 16 candidate inputs had data/background-MC
shape `chi2/ndf > 5` in validation/control regions; only tau isolation, dijet
mass, and dijet `|Delta eta|` passed. Because a majority failed, the NN/BDT
classifier is formally downscoped at Phase 3 rather than trained and promoted
on poorly modelled inputs.

The NN genMET regression approach is also formally downscoped. Phase 2 found
no direct `GenMET` branch and no neutrino generator-particle truth target in
the reduced MC files, so the requested truth target is absent. The add-MET
mass observable is the retained reconstructed-MET alternative.

![Approach comparison. The figure compares the visible-mass and add-MET-mass
approaches with the same diagnostic raw MC-only binned separation metric across
the exclusive categories. It supports keeping visible mass as the Phase 4
baseline, but it does not execute the predeclared expected-sensitivity gate
because no normalized pyhf model exists yet.](figures/approach_comparison.pdf){#fig:p3-approach}

![MVA input modelling gate. The figure shows validation/control-region
data-vs-background-MC shape `chi2/ndf` for each candidate classifier input.
Most candidate inputs exceed the predeclared threshold of 5, so the MVA is
downscoped rather than used as a primary Phase 4 observable.](figures/mva_input_modeling_chi2.pdf){#fig:p3-mva-gate}

## Validation Remediation

The pre-review validation mixed W high-mT, same-sign, Z-rich, and top-enriched
handles into a single data-vs-background-MC shape test. That mixed union still
fails for the primary visible mass with `chi2/ndf = 17.98` and for add-MET mass
with `chi2/ndf = 43.32`, so the broad raw background model is not a final
closure test for Phase 4.

Three concrete remediation attempts were run and written to
`variable_modeling.json`. First, the validation/control handles were evaluated
separately instead of mixing incompatible shapes: visible-mass `chi2/ndf` is
3.27 in same-sign, 5.76 in the top b-tag handle, 2.40 in W high-mT, and 1.41 in
Z-rich. Second, the mixed primary-observable union was rebinned coarsely; this
did not improve closure (`chi2/ndf = 38.92` for visible mass). Third, the
Z-rich visible-mass window was evaluated as the DY shape handle and gives
`chi2/ndf = 1.41` with 5514 data and 4396 raw background-MC events.

The Phase 3 conclusion is therefore scoped: the category definitions,
selected-event flags, and Z-rich/W-handle shape diagnostics are usable inputs,
but the raw background-only templates are not closure-validated final Phase 4
fit predictions. Phase 4 must add citable normalizations, QCD/missing-background
treatment, and nuisance-constrained control-region modelling before quoting
expected or observed fit results.

## Template Figures

The primary and alternative mass templates are saved by category for Phase 4.
They are shape-normalized Phase 3 diagnostics because external luminosity,
cross-section, and stitching inputs remain unresolved.

![Visible mass in the VBF category. This normalized template diagnostic shows
the primary observable in the VBF-enriched category. The category is VBF-first
and exclusive, so these events do not also enter boosted or zero-jet
templates.](figures/visible_mass_vbf.pdf){#fig:p3-mvis-vbf}

![Visible mass in the boosted category. This normalized template diagnostic
shows the primary observable in non-VBF events with at least one clean jet.
It is retained as the ggH-sensitive non-VBF jet category for the simultaneous
Phase 4 fit.](figures/visible_mass_boosted.pdf){#fig:p3-mvis-boosted}

![Visible mass in the zero-jet category. This normalized template diagnostic
shows the primary observable in non-VBF events with no clean jets. The
category is DY-rich and will help constrain shape and normalization components
in the Phase 4 model.](figures/visible_mass_zero_jet.pdf){#fig:p3-mvis-zero}

![Add-MET mass in the VBF category. This normalized diagnostic shows the
add-MET alternative observable in the VBF-enriched category. It is retained
for Phase 4 cross-checks but not promoted over visible mass.](figures/addmet_mass_vbf.pdf){#fig:p3-addmet-vbf}

![Add-MET mass in the boosted category. This normalized diagnostic shows the
add-MET alternative observable in the boosted/1-jet category. The shape is
available for Phase 4 studies if systematic propagation supports it.](figures/addmet_mass_boosted.pdf){#fig:p3-addmet-boosted}

![Add-MET mass in the zero-jet category. This normalized diagnostic shows the
add-MET alternative observable in the zero-jet category. It completes the
category-by-category alternative template set required by the Phase 1
comparison plan.](figures/addmet_mass_zero_jet.pdf){#fig:p3-addmet-zero}

## Normalization Status

Absolute-normalization provenance is resolved for the Phase 3 reduced inputs
and recorded in `normalization_inputs.json`. The local ROOT `Events` entries are
treated only as processing, shape, and cutflow entries; they are not data
luminosity inputs and are not MC generation denominators. No luminosity was
computed from local entries, selected counts, generated MC counts, or data/MC
back-calculation.

The data luminosity is `L_int = 11.467/fb = 11467/pb`, the value used in the CMS
Open Data H to tau tau tutorial `skim.cxx` for Run2012B+C TauPlusX in CERN Open
Data record 12350. CERN Open Data record 1054 supplies the official 2012
luminosity source and the rule to use Pixel Luminosity Telescope (`pxl`) values
when available, with HFOC only for lumi sections where `pxl` is missing. The
Run2012B and Run2012C parent reduced data records are records 12358 and 12359,
with 35,647,508 and 51,303,171 official reduced NanoAOD events respectively;
their local mirror entries may be skimmed and are not interpreted as missing
data. CMS PAS LUM-13-001 gives the 2.6% luminosity uncertainty applied to
MC-based predictions.

MC absolute weights use CERN Open Data records 12351-12357
`distribution.number_events` as denominators. Signal files contain only
H->tautau events selected by the generator decay filter, so signal
normalization uses `sigma_prod * BR(H->tautau)`, not inclusive Higgs production
cross section alone:

| Sample | Record | `N_gen` | Cross section [pb] | Weight |
|---|---:|---:|---:|---:|
| GluGluToHToTauTau | 12351 | 476,963 | 1.338 | 0.03217 |
| VBF_HToTauTau | 12352 | 491,653 | 0.1001 | 0.002335 |
| DYJetsToLL | 12353 | 30,458,871 | 3503.7 | 1.319 |
| TTbar | 12354 | 6,423,106 | 252.9 | 0.4515 |
| W1JetsToLNu | 12355 | 29,784,800 | 6381.2 | 2.457 |
| W2JetsToLNu | 12356 | 30,693,853 | 2039.8 | 0.7621 |
| W3JetsToLNu | 12357 | 15,241,144 | 612.5 | 0.4608 |

Phase 4 still must implement official trigger, muon, tau, b-tag, and pileup
scale-factor prescriptions where available, W+jets control-region treatment or
stitching for W1/W2/W3 without inclusive WJets or W4, and the data-driven QCD
sideband estimate. No MC sample was manually scaled to data in Phase 3.

## Machine-Readable Outputs

Phase 3 produced:

- `phase3_selection/outputs/selected_events.npz`
- `phase3_selection/outputs/cutflow.json`
- `phase3_selection/outputs/category_yields.json`
- `phase3_selection/outputs/region_yields.json`
- `phase3_selection/outputs/variable_modeling.json`
- `phase3_selection/outputs/approach_comparison.json`
- `phase3_selection/outputs/normalization_inputs.json`
- `phase3_selection/outputs/selection_config.json`
- `phase3_selection/outputs/models/model_metadata.json`

The selected-event summary is compact and stores only candidate/region
variables, not full event arrays. Phase 4 should treat these files as the
source of Phase 3 category definitions and raw selected counts. For signal
templates, use `is_signal_region` and the mutually exclusive `category` field;
use `region_exclusive` only for diagnostic displays and the explicit boolean
region flags for validation/control handles.

## Commands and Validation

Commands run successfully:

| Command | Outcome |
|---|---|
| `pixi run phase3-all` | Passed; regenerated selection, MVA gate, approach comparison, and figures. |
| `pixi run py phase2_exploration/src/localize_samples.py` | Passed; regenerated the Phase 2 local manifest with separate local-entry and official-record metadata. |
| `pixi run py - <<'PY' ... JSON and normalization metadata checks ... PY` | Passed; touched JSON files parse and weights equal `sigma * 11467 / N_gen` using official record denominators. |
| `pixi run lint-plots` | Passed with no plotting violations in seven files. |
| `git diff --check` | Passed with no whitespace errors. |

Pre-review checks:

- At least two approaches compared quantitatively: visible mass and add-MET
  mass were fully compared; NN classifier and NN genMET were downscoped with
  explicit gate evidence.
- Category exclusivity: VBF assigned first, then boosted/1-jet, then zero-jet.
- Cutflow monotonicity: satisfied for all samples and role aggregates.
- MVA input modelling: performed before training; majority failure triggered
  downscope.
- W/QCD/Z/top handles: implemented as raw regions/handles for Phase 4.
- Missing paper-level samples and remaining scale-factor/control-region inputs:
  documented as limitations, not patched by manual scaling.
- Region semantics: `is_signal_region` agrees with `category_yields.json` and
  `region_yields.json`; exclusive validation labels do not overwrite signal
  membership.
- Luminosity: no circular luminosity derivation was performed; Phase 3 uses
  `L_int = 11.467/fb` from the CMS Open Data H to tau tau tutorial context,
  record 1054 luminosity handling, and the 2.6% CMS PAS LUM-13-001 uncertainty.

## Open Blockers for Phase 4

1. Implement systematic variations from cited sources, especially tau
   ID/trigger, muon trigger/ID, jet/MET, b-tag/top, DY/Z normalization, W
   transfer, QCD sideband, MC statistics, and luminosity.
2. Resolve W+jets exclusive-bin treatment or control-region constraints for
   W1/W2/W3 without inclusive WJets or W4, and verify theory citations for all
   cross sections/branching fractions in the Phase 4 note.
3. Convert the raw W high-mT, same-sign QCD, top handle, and Z-rich validation
   regions into a statistically consistent pyhf model or pre-fit constraints.
4. Validate asymptotic assumptions or use toys if any final Phase 4 template
   bins have low expected counts after normalization.

## Sensitivity Regression Remediation

A Phase 3 sensitivity regression pass was added after the Phase 4a expected
model returned `Z = 0.191` and a median expected
limit of `mu = 11.374`. The remediation uses
only MC and Asimov expectations for selection, category, binning, and
classifier choices. It does not tune on observed full-data signal-region
discriminant distributions.

The scan covers JHEP-inspired loose/tight VBF and boosted/tau-pT splits,
top/b-veto exploratory handling, `m_vis`, `m_addmet`, `pt_tautau_proxy`, and
two expected-only classifiers. Machine-readable results are written to
`sensitivity_scan.json`, `mva_sensitivity.json`,
`sensitivity_recommendation.json`, `sensitivity_selected_events.npz`, and
`missing_component_feasibility.json`.

![Expected-only sensitivity variant summary. This figure ranks the strongest
selection, category, observable, and classifier variants by Asimov discovery
sensitivity using only simulated signal and background templates. The dashed
reference line is the Phase 4a visible-mass baseline, so the comparison is an
optimization diagnostic and not an observed-data result.](figures/sensitivity_variant_summary.pdf){#fig:p3-sensitivity-variant-summary}

![Gradient-boosted classifier score templates. The figure shows the expected
signal and background score distributions in the signal region after applying
the official Open Data normalization inputs. The classifier was trained only on
MC, and Phase 4b must validate the score modelling before this expected-only
gain can be promoted as a primary result.](figures/mva_score_templates.pdf){#fig:p3-mva-score-templates}

![Sensitivity nuisance diagnostic. The figure compares the visible-mass
baseline and the strongest classifier-score candidate under nominal, reduced,
and removed nuisance-parameter configurations. These curves are diagnostic
stress tests of the expected model only; configurations with removed or
reduced nuisances are not final statistical results.](figures/sensitivity_nuisance_audit.pdf){#fig:p3-sensitivity-nuisance-audit}

The best expected-only variant is the Gradient-boosted classifier score, inclusive signal region with Asimov
discovery `Z = 0.596`. Its median expected CLs limit is
`3.977` where evaluated. Relative to the Phase 4a
baseline this is a `Z` improvement factor of
`3.12`. The expected signal and
background totals are `25.106` and
`9338.225`, with integrated `S/B =
0.0027` and `S/sqrt(B) =
0.260`.

The MVA improvement remains gated. The classifier is trained only on MC, but
Phase 3 already found severe data/background-MC input-shape disagreements for
most candidate variables. Therefore a classifier score can be carried to
Phase 4a as an expected-only candidate, but Phase 4b must validate score
modelling in control/validation regions or assign an explicit calibration
uncertainty before using it as an unqualified primary result.

The missing-component feasibility check found no current reduced ROOT files
for QCD multijet, diboson, single top, W4/inclusive W, associated H, H to WW,
extra DY jet categories, or embedded Z to tau tau. These components remain
limitations and were not approximated with paper-level yields or fabricated
templates.

Phase 4a rerun instruction: update the expected-model executor to read
`phase3_selection/outputs/sensitivity_recommendation.json` and
`phase3_selection/outputs/sensitivity_selected_events.npz`. Rebuild templates
using the recommended observable/category labels and the same official
normalization, then regenerate `expected_results.json`, `INFERENCE_EXPECTED.md`,
the analysis-note markdown, TeX, and PDF before restarting the full Phase 4a
review.
