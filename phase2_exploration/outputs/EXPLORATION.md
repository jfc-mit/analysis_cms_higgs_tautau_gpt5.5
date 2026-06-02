# Phase 2 Exploration: CMS 2012 Open Data H to Tau Tau Search

## Summary

Phase 2 resolved the reduced CMS Open Data H to tau tau sample access path,
inventoried the ROOT schemas, checked branch/flag non-triviality, and produced
5k-event prototype surveys for the mu tau_h search planned in Phase 1. The
prompt-listed MC files are available from the public ROOT mirror
`https://root.cern/files/HiggsTauTauReduced/`; the data files available there
are `Run2012B_TauPlusX.root` and `Run2012C_TauPlusX.root`, not
`Run2012B_SingleMu.root` or `Run2012C_SingleMu.root`. The exploration confirms
that tau anti-muon IDs, tau isolation IDs, muon IDs/isolation, MET covariance,
jets, and b-tag branches are present, while event weights, pileup weights, and
direct GenMET branches are absent.

## Data Source Resolution

Remote access works through uproot over HTTPS when the pixi environment is run
with `SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt`. Without that variable,
fsspec raises a certificate verification error even though system `curl` can
reach the ROOT mirror. No local EOS mount was available in this execution
environment. After the user-requested Phase 2 scope change, the confirmed
reduced files are localized under `data/` and `mc/` in the analysis root, and
`phase2_exploration/src/explore_samples.py` now prefers those local paths when
present with the HTTPS mirror as fallback.

The public mirror lists:

| Sample | Role | Events | Size [MB] | Status |
|---|---:|---:|---:|---|
| `GluGluToHToTauTau.root` | signal | 47,696 | 20.5 | available |
| `VBF_HToTauTau.root` | signal | 49,165 | 24.2 | available |
| `DYJetsToLL.root` | background | 3,045,887 | 926.0 | available |
| `TTbar.root` | background | 642,310 | 353.7 | available |
| `W1JetsToLNu.root` | background | 2,978,480 | 1,073.5 | available |
| `W2JetsToLNu.root` | background | 3,069,385 | 1,217.3 | available |
| `W3JetsToLNu.root` | background | 1,524,114 | 655.0 | available |
| `Run2012B_TauPlusX.root` | data | 3,564,750 | 1,088.1 | available |
| `Run2012C_TauPlusX.root` | data | 5,130,317 | 1,549.0 | available |

`Run2012B_SingleMu.root` and `Run2012C_SingleMu.root` return HTTP 404 at the
same mirror. This resolves Phase 1 open issue [O1] in favor of the CERN reduced
TauPlusX outreach inputs and is a strategy-revision input for the prompt's
SingleMu wording.

## Local Sample Manifest and Paper-Level Coverage

The machine-readable local manifest is
`phase2_exploration/outputs/local_sample_manifest.json`. It records source
URLs, local paths, expected and observed file sizes, validation status, `Events`
tree entry counts when available, and paper-level components that are not in
the reduced mirror. The current local reduced sample policy is to use all
available 2012 CMS Open Data reduced files relevant to this mu tau_h H to tau
tau analysis now, and to defer full AOD conversion until a later phase
demonstrates the additional sample is needed.

Confirmed reduced files are:

| Directory | Samples |
|---|---|
| `data/` | `Run2012B_TauPlusX.root`, `Run2012C_TauPlusX.root` |
| `mc/` | `GluGluToHToTauTau.root`, `VBF_HToTauTau.root`, `DYJetsToLL.root`, `TTbar.root`, `W1JetsToLNu.root`, `W2JetsToLNu.root`, `W3JetsToLNu.root` |

The broader CMS H to tau tau MC programs in CMS JHEP 05 (2014) 104
(DOI:10.1007/JHEP05(2014)104) and CMS Phys. Lett. B 779 (2018) 283
(DOI:10.1016/j.physletb.2018.02.004) include or discuss components beyond the
reduced mirror. CMS JHEP 05 (2014) 104 describes ggH and VBF signal samples,
associated WH/ZH and ttH Higgs production, Z+jets, W+jets, ttbar+jets,
diboson, and single-top simulation, plus embedded Z to tau tau samples and
data-driven QCD estimates. CMS Phys. Lett. B 779 (2018) 283 documents
Drell-Yan, W+jets, QCD multijet, ttbar, diboson, single-top, and H to WW
background treatment in the later 13 TeV analysis context. The reduced mirror
does not list separate files for embedded Z to tau tau, Z to mumu/ee fake
components, QCD/multijet, WW/WZ/ZZ, single top, WH/ZH/ttH, H to WW, inclusive
WJets, W4Jets, or additional DY jet/mass categories; these are marked
`missing-reduced` or `deferred-AOD-conversion` in the manifest rather than
downloaded as full AOD blindly.

These missing paper-level components are not blockers for the current reduced
sample analysis if their status remains documented. They are binding downstream
documentation obligations: the final analysis note and final summary must name
each unavailable paper-level component used in the CMS reference analyses,
state that no corresponding reduced 2012 CMS Open Data sample or suitable
substitute was available here, and discuss the limitation or impact on this
open-data result. This applies in particular to embedded Z to tau tau, separate
Z to mumu/ee fake components, QCD/multijet simulation, diboson WW/WZ/ZZ, single
top, WH/ZH/ttH, H to WW, W4/inclusive W+jets, and additional DY categories as
recorded in `local_sample_manifest.json`.

## Downstream Category Obligations

The Phase 3 selection must implement mutually exclusive sensitivity categories
inspired by CMS JHEP 05 (2014) 104 and CMS Phys. Lett. B 779 (2018) 283, then
fit all retained categories simultaneously. At minimum, Phase 3 must evaluate:

| Category obligation | Required variables or handles | Phase 2 availability |
|---|---|---|
| VBF-enriched category | Jet multiplicity, leading-dijet invariant mass `m_jj`, leading-dijet `|Delta eta_jj|`, central-jet/top rejection where feasible | `nJet`, `Jet_pt`, `Jet_eta`, `Jet_phi`, `Jet_mass`, and `Jet_btag` are present. |
| Boosted or 1-jet category | Jet multiplicity and Higgs-candidate transverse momentum, using `pT_tautau` when reconstructible or a documented visible/add-MET proxy if not | Muon, tau, MET, and jet four-vector branches are present for visible/add-MET proxies. |
| 0-jet or non-VBF baseline | Orthogonal catch-all category after assigning VBF and boosted/1-jet candidates, with no event double counting | Jet multiplicity is present in data and MC. |
| Top-control handle | b-tag requirement or veto and high-jet-multiplicity checks | `Jet_btag` is present but includes sentinel values, so Phase 3 must define a validity mask. |
| W+jets/QCD handles | Muon-MET transverse mass, same-sign, and anti-isolation control or validation regions | Muon, tau, charge, isolation, and MET branches are present; isolation sentinels must be masked. |

If the reduced statistics do not support all categories with stable templates,
Phase 3 may merge or downscope categories only after documenting the yield and
stability checks. The simultaneity requirement remains binding: retained VBF,
boosted/1-jet, and 0-jet/non-VBF categories must be fit together rather than
reported as independent standalone fits.

## Schema Inventory

All available MC files contain one `Events` tree with 69 branches. The two data
files contain one `Events` tree with 62 branches; the missing data-only
difference is generator information. The event model is reduced NanoAOD-like:
flat event branches for run/luminosity/event, triggers, primary vertex and MET,
plus jagged `Muon_*`, `Tau_*`, `Jet_*`, and, for MC, `GenPart_*` arrays.

Required Phase 1 feature availability:

| Feature | MC | Data | Phase 3 implication |
|---|---:|---:|---|
| Tau tight anti-muon branch | yes | yes | [D5] tight tau anti-muon veto is feasible. |
| Tau isolation ID branches | yes | yes | Tau ID working-point studies are feasible. |
| Muon ID/isolation branches | yes | yes | Baseline muon cleaning is feasible. |
| MET pt/phi/covariance | yes | yes | mT, add-MET mass, and MET-aware studies are feasible. |
| Jet pt/eta/phi/mass | yes | yes | Jet bins and VBF candidate variables are feasible. |
| Jet b-tag branch | yes | yes | Top CR/veto studies are feasible. |
| Generator particles | yes | no | MC truth studies feasible; data application must use reco-only inputs. |
| Direct GenMET branch | no | no | NN genMET regression cannot use direct GenMET. |
| Event or generator weights | no | no | Production normalization needs external xsec/lumi and raw event counts. |
| Pileup weights | no | no | Separate pileup reweighting is not supported by these ntuples. |
| Primary vertex count `PV_npvs` | yes | yes | Pileup-sensitive validation can use vertex multiplicity only. |

The full machine-readable inventory is in
`phase2_exploration/outputs/sample_inventory.json`.

![Sample event counts and file sizes. The plot summarizes full event counts and
HTTP HEAD file sizes for the reduced H to tau tau files used in Phase 2. It
shows why Phase 2 used bounded remote slices: several backgrounds and data
files are around or above one GB, while the signal samples are small enough for
rapid metadata checks.](figures/sample_event_count_file_size.pdf){#fig:p2-samples}

![Branch feature availability. The heatmap marks whether each sample contains
the branch classes required by the Phase 1 strategy, including generator
particles, tau anti-muon ID, b-tagging, MET covariance, and weights. The main
feasibility gaps are direct GenMET, event weights, and pileup weights; the core
mu tau_h selection and VBF branch requirements are present.](figures/branch_feature_availability.pdf){#fig:p2-availability}

## Branch and Flag Archaeology

The branch diagnostics scanned all trigger, ID, isolation, generator, MET,
pileup-like, b-tag, charge, and count branches on a 5k-event slice per sample.
Trigger and object-ID branches are non-trivial booleans in both data and MC.
The tau tight anti-muon branch is non-trivial, with means of 0.88 in Run2012B
TauPlusX and 0.93 in Run2012C TauPlusX on the diagnostic slice. Tau isolation
working points are also non-trivial; for example `Tau_idIsoTight` has slice
means of 0.103 in Run2012B and 0.062 in Run2012C.

No event-level `weight`, generator-weight, cross-section, luminosity, or pileup
weight branches were found. `PV_npvs` is present and non-trivial in all samples,
so vertex-multiplicity comparisons can test pileup modelling qualitatively, but
Phase 4 cannot implement a conventional pileup-weight nuisance unless an
external reduced-sample prescription is found. `Jet_btag` is non-trivial and
ranges from the sentinel value −10 to approximately 1, so Phase 3 must define a
valid-value mask before using b-tag thresholds.

Muon and tau isolation branches include sentinel values such as −999. Phase 3
must mask or understand those values before using isolation as an MVA input or
selection variable. This is especially important for NN input modelling: a
sentinel-driven separation would be a detector/reconstruction artifact rather
than a robust physics discriminant.

The full diagnostics are in
`phase2_exploration/outputs/branch_diagnostics.json`.

## GenMET and NN Regression Feasibility

The files do not contain direct `GenMET_pt` or `GenMET_phi` branches. MC files
do contain `GenPart_pt`, `GenPart_eta`, `GenPart_phi`, `GenPart_mass`,
`GenPart_pdgId`, and `GenPart_status`, with PDG IDs limited in the inspected
branches to electrons, muons, and taus. Neutrino PDG IDs were not present in
the reduced generator-particle branch diagnostics. Therefore the Phase 1
alternative (b), training an NN to regress genMET direction/phi, is not
directly feasible from these files as stated.

Phase 3 may still test a reconstructed-MET-assisted mass observable and a
generic NN discriminator using reconstructed-only inputs available in data.
However, any "NN genMET" observable must be formally downscoped unless a
separate source supplies truth missing momentum or neutrino-level information.
This is a strategy-revision input.

## Pileup Treatment Feasibility

No pileup-weight branch exists in any sample. `PV_npvs` is present in both data
and MC and can support data/MC validation of vertex multiplicity, but the
standard pileup reweighting and pileup up/down nuisance path from Phase 1 is
not supported by the reduced files alone. Phase 4 should treat pileup as a
reduced-open-data limitation unless a citable external pileup profile and a
method to map it onto these ntuples are retrieved.

## Baseline Preselection Feasibility

A loose exploratory preselection was applied on 5k-event slices only:
leading muon and leading tau candidate present; muon pt > 20 GeV and
|eta| < 2.1; tau pt > 20 GeV and |eta| < 2.3; and `Tau_idAntiMuTight > 0`.
The baseline search-like diagnostic additionally requires opposite-sign
mu-tau and mT(mu, MET) < 40 GeV. A high-mT W-control diagnostic uses
mT(mu, MET) > 80 GeV, and a rough VBF-like diagnostic requires at least two
jets, dijet mass > 300 GeV, and |Delta eta_jj| > 2.5.

| Sample | Loose accept | OS low-mT | High-mT W CR | VBF-like | SS loose |
|---|---:|---:|---:|---:|---:|
| GluGluToHToTauTau | 138 | 82 | 6 | 12 | 11 |
| VBF_HToTauTau | 136 | 75 | 11 | 37 | 21 |
| DYJetsToLL | 26 | 13 | 3 | 0 | 8 |
| TTbar | 283 | 75 | 43 | 19 | 113 |
| W1JetsToLNu | 17 | 1 | 2 | 0 | 10 |
| W2JetsToLNu | 32 | 3 | 5 | 0 | 13 |
| W3JetsToLNu | 60 | 11 | 8 | 5 | 24 |
| Run2012B_TauPlusX | 152 | 51 | 1 | 5 | 83 |
| Run2012C_TauPlusX | 155 | 53 | 6 | 12 | 77 |

These are raw slice counts, not luminosity-normalized yields. They show that
the mu tau_h baseline, same-sign sideband, W high-mT region, top/b-tag studies,
and VBF-enriched category are structurally feasible. The W high-mT slice has
low data statistics in Run2012B, so Phase 3 should use larger data slices for
CR design after normalization inputs are resolved.

![Preselection yield summary. The plot shows raw counts in each exploratory
region on 5k-event slices, so it is a feasibility survey rather than a
normalized prediction. The VBF-like region is populated in VBF signal and
TTbar, and the same-sign loose region is well populated in data, supporting
Phase 3 control-region development.](figures/preselection_yield_summary.pdf){#fig:p2-yields}

## Variable Survey

The Phase 2 variable survey produced first-candidate distributions for muon
pt, tau pt, MET, visible mass, add-MET mass, mT, jet multiplicity, dijet mass,
and dijet |Delta eta|. These plots are exploratory slice diagnostics; they are
not final candidate-cleaned or luminosity-normalized comparisons. The visible
mass plot in particular has a first-bin spike from loose first-candidate
construction and must be revisited in Phase 3 with object ordering, overlap
removal, and final candidate selection.

Single-variable signal-versus-background ROC AUC was evaluated on the loose
accepted MC slice. The strongest simple discriminator was dijet |Delta eta|
with abs(AUC − 0.5) = 0.196, followed by mT(mu, MET) at 0.150, jet
multiplicity at 0.105, add-MET mass at 0.088, and deltaR(mu, tau) at 0.065.
Visible mass had only modest single-variable separation on this slice
abs(AUC − 0.5) = 0.039, which is expected for a reduced first-candidate survey
and does not invalidate it as the baseline transparent template observable.

![Leading muon transverse momentum. This normalized slice comparison uses the
leading muon candidate before final candidate arbitration. The distribution is
adequate for branch and range validation, but Phase 3 must repeat the
comparison after final muon ID and overlap removal before using muon pt in an
MVA.](figures/muon_pt_slice.pdf){#fig:p2-muon-pt}

![Leading tau transverse momentum. This normalized slice comparison uses the
leading tau_h candidate and the reduced tau ID branches. The branch range is
physical and populated in all sample classes, supporting tau candidate studies
with tighter Phase 3 ID definitions.](figures/tau_pt_slice.pdf){#fig:p2-tau-pt}

![Missing transverse momentum. This normalized slice comparison validates the
availability and basic range of reconstructed MET in data and MC. It supports
mT and add-MET mass studies, but no direct GenMET branch exists for the
requested genMET regression target.](figures/met_pt_slice.pdf){#fig:p2-met}

![Visible mass. This first-candidate exploratory distribution shows that a
visible-mass observable can be constructed from the reduced muon and tau
branches. The prominent low-mass spike is a candidate-cleaning warning, so
Phase 3 must rebuild this plot after final object selection before optimizing
the template fit.](figures/visible_mass_slice.pdf){#fig:p2-mvis}

![Add-MET mass. This mass-like diagnostic adds reconstructed missing
transverse momentum as a massless transverse four-vector to the visible mu-tau
system. The observable is constructible in both data and MC, so Phase 3 can
compare it with visible mass under the Phase 1 alternative-observable gates.](figures/addmet_mass_slice.pdf){#fig:p2-addmet}

![Muon-MET transverse mass. The mT distribution is available for both signal
region and high-mT W-control-region construction. The variable also ranks high
in the simple MC separation survey, so Phase 3 should treat it as both a
region-defining variable and an MVA input candidate subject to data/MC checks.](figures/mt_mu_met_slice.pdf){#fig:p2-mt}

![Jet multiplicity. Jet multiplicity is present in all samples and separates
VBF/TTbar-like topologies from lower-jet backgrounds in the prototype survey.
The plot supports Phase 3 category construction, with final binning to be set
after normalized yields are available.](figures/jet_multiplicity_slice.pdf){#fig:p2-njet}

![Dijet mass. The dijet mass diagnostic can be constructed from the leading two
jet four-vectors in the reduced files. It is essential for the VBF-enriched
category, but low slice counts mean Phase 3 should evaluate it with larger MC
statistics and final object cleaning.](figures/dijet_mass_slice.pdf){#fig:p2-mjj}

![Dijet pseudorapidity separation. The leading-dijet |Delta eta| variable is
the strongest simple discriminator in the Phase 2 MC slice. This supports the
Phase 1 VBF category plan, subject to final Phase 3 validation and binning.](figures/dijet_deltaeta_slice.pdf){#fig:p2-detajj}

![Variable separation ranking. The ranking uses single-variable ROC AUC on the
loose accepted MC slice and is therefore a screening tool, not an optimization
result. VBF-related variables and mT rank highest, while visible mass remains
important as the transparent baseline template observable from Phase 1.](figures/variable_separation_ranking.pdf){#fig:p2-separation}

## Normalization Status

The reduced ROOT files contain neither event weights nor embedded
cross-section/luminosity metadata. Phase 2 therefore reports raw event counts
and raw slice yields only. Phase 3 must retrieve citable cross sections,
integrated luminosities for the TauPlusX periods, and any W+jets jet-bin
stitching prescription before production-normalized templates are built.

This is a blocking normalization item for Phase 3, not a reason to manually
scale MC to data. The Phase 1 strategy requires W+jets normalization from the
high-mT data region and DY/Z normalization uncertainty in the 10-15% range; the
absence of file weights means those choices must be implemented using external
normalization inputs plus data-driven CR constraints.

## Data Quality Findings

No empty core object branch class was found among muons, taus, jets, MET, or
triggers. The quality caveats are:

- Prompt SingleMu data files are not available at the resolved mirror; the
  available data stream is TauPlusX.
- Muon and tau isolation branches contain sentinel values such as −999 and
  must be masked before MVA use.
- `Jet_btag` contains sentinel −10 values and must be validity-masked.
- No event weights, pileup weights, or direct GenMET branches are present.
- The first-candidate visible-mass diagnostic shows a large low-mass spike,
  indicating that Phase 3 candidate arbitration and object cleaning are
  required before interpreting mass shapes.

## PDF Build Test

The independent Phase 2 PDF stub test did not pass. The exact command was
`pixi run build-pdf`. Pandoc and `postprocess_tex.py` ran, but the task failed
with `tectonic: command not found`; a direct check also found no `pdflatex` in
the pixi environment. The build task additionally emitted a citeproc warning
because it does not pass `--bibliography=references.bib`.

Phase 3 or Phase 5 must add a TeX engine to `pixi.toml` and repair the build
task bibliography argument before the analysis-note PDF gates. The temporary
stub markdown, generated TeX, and temporary BibTeX entry were removed after the
test.

## Strategy Revision Inputs

1. Phase 1/prompt assumed or named SingleMu data files. Phase 2 found only
   TauPlusX Run2012B/C at the resolved H to tau tau reduced mirror. The
   strategy should be updated to describe the actual TauPlusX data stream and
   its trigger implications.
2. Phase 1 alternative (b) asked for genMET direction/phi regression. Phase 2
   found no direct GenMET branch and no neutrino generator-particle branches in
   the reduced MC schema. This alternative should be downscoped unless an
   external truth target is supplied.
3. Phase 1 planned pileup treatment if supported. Phase 2 found `PV_npvs` but
   no pileup weights. Pileup can be validated qualitatively through vertex
   multiplicity, but a standard pileup-weight nuisance is not supported by the
   reduced files alone.
4. Phase 1 expected production normalization in later phases. Phase 2 found no
   embedded event weights or xsec/lumi metadata. Phase 3 must resolve external
   normalization inputs before production templates or pyhf workspaces.
5. The PDF toolchain is incomplete because no TeX engine is installed in pixi
   and the build task does not pass the bibliography file.

## Code Reference

Commands run:

| Command | Outcome |
|---|---|
| `pixi run phase2-explore` | Completed after reducing the prototype to 5k events per sample. |
| `pixi run phase2-plots` | Completed after replacing unavailable `mplhep.plot.mpl_magic` with a local helper. |
| `pixi run lint-plots` | Passed with no violations in two scripts. |
| `pixi run build-pdf` | Failed: `tectonic: command not found`; `pdflatex` also absent. |

Machine-readable outputs:

- `phase2_exploration/outputs/sample_inventory.json`
- `phase2_exploration/outputs/branch_diagnostics.json`
- `phase2_exploration/outputs/variable_histograms.json`
- `phase2_exploration/outputs/preselection_yields.json`
- `phase2_exploration/outputs/variable_separation.json`

Scripts:

- `phase2_exploration/src/explore_samples.py`
- `phase2_exploration/src/plot_exploration.py`

## Pre-Review Self-Check

- Sample inventory: complete for the resolved mirror files; SingleMu prompt
  files explicitly checked and found unavailable.
- Data quality and archaeology: weight, flag, trigger, ID, generator, MET,
  pileup-like, and b-tag branches scanned on bounded slices.
- Object definitions: branch-level support for muon, tau, jet, MET, b-tag, and
  triggers established; official scale-factor/object-definition citations still
  need retrieval because SciTreeRAG tools were unavailable.
- Variable survey: produced first-candidate diagnostic figures and MC
  single-variable separation ranking.
- Baseline yields: raw 5k-slice preselection yields produced; normalized yields
  blocked by missing external xsec/lumi/weight inputs.
- PDF build: attempted and failed due missing TeX engine; blocker documented.
- Experiment log and session log: updated throughout.
- Plot lint: `pixi run lint-plots` passed.
