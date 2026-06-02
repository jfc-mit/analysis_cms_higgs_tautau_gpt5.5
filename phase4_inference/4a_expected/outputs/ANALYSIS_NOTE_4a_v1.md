---
title: "CMS Open Data H to tau tau Search in the mu tauh Final State: Phase 4a Expected Results"
author: "Analysis my_analysis"
date: "2026-06-02"
bibliography: references.bib
---

# Change Log {-}

**Phase 4a v1**

- Initial AN version (Phase 4a).
- Updated the Phase 4a expected note to the current categorized score-template model: a simultaneous pyhf fit over `vbf`, `boosted`, and `zero_jet` channels using `mva_score_hist_gradient_boosting` binned as `[0.0, 0.2, 0.35, 0.5, 1.0]`.
- Added the current Asimov expected CLs limit, discovery diagnostic, signal-injection validation, limited GoF toy study, systematic program, candidate-comparison context, missing-component limitations, and reproduction contract.
- Recorded that 10% data validation and full observed signal-region results are intentionally absent until the Phase 4b and Phase 4c gates.

# Introduction

This note documents a reduced-sample search for a Standard Model Higgs boson decaying to a pair of tau leptons in CMS 2012 Open Data. The analyzed final state contains one reconstructed muon and one hadronically decaying tau candidate, denoted mu tauh in this note. The analysis follows the logic of the CMS Run 1 H to tau tau searches while remaining explicit about the limitations of the reduced outreach NanoAOD-like files used here [@cms_htt_2014; @cms_htt_2018; @cms_open_data_htt_2012].

The primary result in this Phase 4a document is expected-only. The fit observation is background-only Asimov pseudo-data derived from the nominal Monte Carlo templates, not the full collision-data signal-region distribution. The observed 10% validation result will be added in Phase 4b, and the full observed signal-region result will be added only after the Phase 4b human unblinding gate.

The Phase 1 strategy decision [D1] defines this work as a search/template-fit analysis rather than a measurement. The parameter of interest is the signal-strength modifier $\mu$, which scales the Standard Model H to tau tau signal templates. Because the reduced sample set is single-channel, uses visible mass rather than the full CMS SVFit reconstruction, and lacks several paper-level background and calibration components, the expected sensitivity reported here is a reduced-open-data benchmark rather than an attempt to reproduce the all-channel CMS Run 1 result.

The current model is a simultaneous pyhf score-template fit in three mutually exclusive channels: `vbf`, `boosted`, and `zero_jet`. The fitted observable is `mva_score_hist_gradient_boosting`, using score-bin edges `[0.0, 0.2, 0.35, 0.5, 1.0]` from `nominal_yields.json`. The Phase 4a expected median 95% CLs upper limit is $\mu = 4.199$, with an Asimov observed-on-background limit of $\mu = 4.199$. The discovery diagnostic on signal-plus-background Asimov data gives $Z = 0.526$, so this configuration remains an expected-limit result, but it is the current expected-primary candidate pending Phase 4b score-modelling validation.

# Data Samples

The data and simulation inputs are the reduced CMS Open Data H to tau tau files localized in Phase 2 from the public reduced ROOT mirror associated with the CERN Open Data H to tau tau outreach analysis [@cms_open_data_htt_2012]. Phase 2 resolved the data stream to TauPlusX Run2012B and Run2012C, not the prompt-listed SingleMu files. Phase 3 then required the TauPlusX trigger `HLT_IsoMu17_eta2p1_LooseIsoPFTau20` in all analysis regions.

The normalization uses the integrated luminosity value `L_int = 11.467/fb = 11467/pb` recorded in `phase3_selection/outputs/normalization_inputs.json`. That JSON traces the value to the CMS Open Data H to tau tau tutorial `skim.cxx` and to the 2012 CMS open-data luminosity records [@cms_open_data_skim; @cms_open_data_lumi_2012]. The luminosity uncertainty is `2.6%`, sourced from CMS PAS LUM-13-001 and implemented as a correlated normalization nuisance for MC-normalized predictions [@cms_lum_13_001].

Table: Collision-data sample summary. The official event counts and luminosities come from `phase3_selection/outputs/normalization_inputs.json`, which records CERN Open Data records 12358 and 12359. Local entries are reduced processing entries in the localized ROOT files and are not used as luminosity inputs. {#tbl:data-samples}

| Period | Data file | Stream | Official events | Local entries | Luminosity [/fb] | Record |
|---|---|---|---:|---:|---:|---|
| 2012B | Run2012B_TauPlusX.root | TauPlusX | 35,647,508 | 3,564,750 | 4.4117 | 12358 [@cms_open_data_run2012b_tauplusx] |
| 2012C | Run2012C_TauPlusX.root | TauPlusX | 51,303,171 | 5,130,317 | 7.0552 | 12359 [@cms_open_data_run2012c_tauplusx] |
| B+C | combined | TauPlusX | 86,950,679 | 8,695,067 | 11.4670 | tutorial context [@cms_open_data_htt_2012; @cms_open_data_skim] |

The simulation samples cover the two available H to tau tau signal production modes and the dominant available backgrounds. The MC denominator for every simulated process is the official CERN Open Data `distribution.number_events` value recorded in `normalization_inputs.json`; it is not the local reduced `Events` tree entry count, and it is not back-calculated from data. Signal normalization uses the production cross section times the H to tau tau branching fraction because the signal files are decay-filtered H to tau tau samples.

Table: Simulation sample summary and absolute weights. Cross sections, generated-event denominators, record identifiers, and per-local-entry weights are read from `phase3_selection/outputs/normalization_inputs.json`. The Higgs signal cross sections are H to tau tau effective cross sections and are traced in the JSON to the LHC Higgs Cross Section Working Group input [@lhc_hxswg_yellow_report_4]. {#tbl:mc-samples}

| Sample | Process | Generator | Cross section [pb] | N_gen | Weight | Record |
|---|---|---|---:|---:|---:|---|
| GluGluToHToTauTau | ggH H to tau tau | Powheg+Pythia6 | 1.338 | 476,963 | 0.03217 | 12351 [@cms_open_data_ggh_htt] |
| VBF_HToTauTau | VBF H to tau tau | Powheg+Pythia6 | 0.1001 | 491,653 | 0.002335 | 12352 [@cms_open_data_vbf_htt] |
| DYJetsToLL | Z/gamma* to ll | MadGraph+Pythia6 | 3503.7 | 30,458,871 | 1.319 | 12353 [@cms_open_data_dyjets] |
| TTbar | ttbar | MadGraph+Pythia6 | 252.9 | 6,423,106 | 0.4515 | 12354 [@cms_open_data_ttbar] |
| W1JetsToLNu | W to lnu + 1 jet | MadGraph+Pythia6 | 6381.2 | 29,784,800 | 2.457 | 12355 [@cms_open_data_w1jets] |
| W2JetsToLNu | W to lnu + 2 jets | MadGraph+Pythia6 | 2039.8 | 30,693,853 | 0.7621 | 12356 [@cms_open_data_w2jets] |
| W3JetsToLNu | W to lnu + 3 jets | MadGraph+Pythia6 | 612.5 | 15,241,144 | 0.4608 | 12357 [@cms_open_data_w3jets] |

The broader CMS H to tau tau analyses use additional ingredients that are not present in the reduced mirror. The missing or deferred components include embedded Z to tau tau, QCD multijet samples, diboson, single top, W4 and inclusive W+jets, associated Higgs production, H to WW, additional DY categories, and Run2012A/D TauPlusX. These are not silently substituted in this Phase 4a expected model; their impacts are carried explicitly in @tbl:missing-components and in the limitation index.

Table: Missing or deferred paper-level components. The entries are read from `phase4_inference/4a_expected/outputs/limitations_downscope.json`, which propagates the Phase 2 final-AN sample-limitation obligations. {#tbl:missing-components}

| Component | Role | Status | Expected Phase 4a impact |
|---|---|---|---|
| Run2012A_TauPlusX | data | deferred-AOD-conversion | Not included in the reduced B+C luminosity and observed-data validation scope. |
| Run2012D_TauPlusX | data | deferred-AOD-conversion | Not included in the reduced B+C luminosity and observed-data validation scope. |
| DYJetsToTauTau_embedded | background | missing-reduced | DY tau response cannot use the embedded-sample method of the CMS reference analyses. |
| DYJets_ZToMuMu_EE_fakes | background | missing-reduced | Separate lepton-to-tau fake components are not modelled as independent templates. |
| QCD_Multijet | background | missing-reduced | Instrumental fake-tau background is deferred to sideband validation phases. |
| WW, WZ, ZZ | background | deferred-AOD-conversion | Diboson contributions are omitted from the expected workspace. |
| SingleTop | background | deferred-AOD-conversion | Single-top contribution is omitted from the expected workspace. |
| W4JetsToLNu, WJetsToLNu_inclusive | background | missing-reduced | W+jets stitching is limited to W1/W2/W3 samples. |
| DY jet/mass-binned categories | background | missing-reduced | DY modelling uses the inclusive reduced DYJetsToLL file. |
| WH, ZH, ttH H to tau tau | signal | deferred-AOD-conversion | Associated-production signal acceptance is not part of the signal model. |
| HToWW | background | deferred-AOD-conversion | H to WW contamination is not modelled as a separate component. |

<!-- COMPOSE: side-by-side -->

![Sample size and local-entry inventory. The Phase 2 plot summarizes local reduced ROOT `Events` entries and file sizes for the localized H to tau tau inputs. The analysis uses these local entries for processing and template filling, while official Open Data record counts from @tbl:mc-samples provide MC normalization denominators.](../../../phase2_exploration/outputs/figures/sample_event_count_file_size.pdf){#fig:p2-samples}

![Feature availability in the reduced files. The Phase 2 heatmap records whether the data and MC files contain the branch classes needed for trigger, object selection, jets, MET, and generator studies. It motivates the current reduced-sample scope: the mu tauh selection and VBF categories are feasible, while direct GenMET, event weights, and pileup weights are absent.](../../../phase2_exploration/outputs/figures/branch_feature_availability.pdf){#fig:p2-availability}

# Event Selection

The event selection follows the Phase 3 output and is summarized here because the Phase 4a templates are built directly from the Phase 3 selected-event summary. All signal, control, and validation regions require `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`. The available single-muon triggers `HLT_IsoMu24` and `HLT_IsoMu24_eta2p1` are not ORed into the analysis because they define a different higher-pT muon phase space.

Muon candidates require transverse momentum greater than `20 GeV`, pseudorapidity magnitude below `2.1`, tight muon ID, and finite relative isolation below `0.20`. Tauh candidates require transverse momentum greater than `20 GeV`, pseudorapidity magnitude below `2.3`, decay-mode ID, tight isolation ID, the tight anti-muon veto, finite tau relative isolation, and separation from the selected muon. Jets require transverse momentum greater than `30 GeV`, pseudorapidity magnitude below `4.7`, and separation from the selected leptons.

The signal-region candidate set requires an opposite-sign muon-tauh pair and transverse mass $m_T(\mu, MET) < 40 GeV$. The W control handle uses opposite-sign events with $m_T(\mu, MET) > 80 GeV$; the QCD sideband uses same-sign low-$m_T$ events; the Z-rich validation handle uses opposite-sign low-$m_T$ events with `60 < m_vis < 120 GeV`; and the top handle uses events with a positive valid b-tag score. The Phase 4a expected model uses only the signal-region category templates, while the control and validation handles remain documented inputs for Phase 4b and Phase 4c.

Table: Phase 3 raw selected counts by category and sample. Counts are read from `phase3_selection/outputs/category_yields.json` and are unweighted processing counts, not luminosity-normalized yields. {#tbl:raw-category-yields}

| Sample | Role | VBF | Boosted | Zero-jet |
|---|---|---:|---:|---:|
| Run2012B_TauPlusX | data | 34 | 858 | 3,183 |
| Run2012C_TauPlusX | data | 45 | 1,355 | 5,283 |
| GluGluToHToTauTau | signal | 23 | 249 | 439 |
| VBF_HToTauTau | signal | 364 | 499 | 94 |
| DYJetsToLL | background | 34 | 802 | 4,432 |
| TTbar | background | 170 | 1,513 | 88 |
| W1JetsToLNu | background | 4 | 37 | 350 |
| W2JetsToLNu | background | 16 | 238 | 348 |
| W3JetsToLNu | background | 16 | 228 | 126 |

Table: Phase 3 control and validation raw counts. The data totals are from Run2012B and Run2012C combined, and the signal and background totals are summed over the available reduced MC files. These regions are not used to unblind signal-region results in Phase 4a. {#tbl:region-yields}

| Region or handle | Data | Signal MC | Background MC | Phase 4a role |
|---|---:|---:|---:|---|
| Signal-region candidate | 10,758 | 1,668 | 8,402 | Template source for expected model |
| W high-mT | 4,023 | 62 | 6,283 | Deferred W normalization/validation handle |
| QCD same-sign | 3,138 | 34 | 1,200 | Deferred instrumental-background sideband |
| Z-rich | 5,514 | 1,261 | 4,396 | DY/Z validation handle |
| Top b-tag handle | 6,689 | 1,150 | 12,508 | Top-enriched validation handle |

Signal-region events are assigned to exactly one fit category. The VBF category is assigned first using at least two clean jets, leading-dijet mass above `300 GeV`, and leading-dijet absolute pseudorapidity separation above `2.5`. Non-VBF events with at least one clean jet enter the boosted category, and the remaining non-VBF events enter the zero-jet category.

<!-- COMPOSE: side-by-side -->

![Phase 3 cutflow summary. The plot shows raw event counts after each selection step, grouped by data, signal MC, and background MC. The cutflow is monotonic and demonstrates that the reduced TauPlusX trigger, object IDs, tight tau anti-muon veto, opposite-sign requirement, and low-mT selection leave populated inputs for the expected fit.](../../../phase3_selection/outputs/figures/cutflow_summary.pdf){#fig:p3-cutflow}

![Exclusive category yields. The figure shows raw selected event counts in the VBF, boosted, and zero-jet categories retained for the simultaneous fit. It verifies that the VBF category remains populated after the trigger fix, while the boosted and zero-jet categories provide the dominant event counts.](../../../phase3_selection/outputs/figures/category_yields.pdf){#fig:p3-category-yields}

<!-- COMPOSE: 1x3 grid -->

![W high-mT control-region diagnostic. This Phase 3 normalized shape comparison documents the available W+jets control handle based on high muon-MET transverse mass. The Phase 4a expected model does not tune W+jets to real data, so this figure is a staging diagnostic for Phase 4b and Phase 4c.](../../../phase3_selection/outputs/figures/w_high_mt_control_mt.pdf){#fig:p3-wcr}

![Same-sign QCD sideband diagnostic. This Phase 3 visible-mass comparison uses same-sign low-mT events as the available fake-tau sideband because no reduced QCD multijet MC sample exists. It is not treated as a complete QCD template in Phase 4a, and the missing-QCD limitation is carried explicitly.](../../../phase3_selection/outputs/figures/qcd_same_sign_mvis.pdf){#fig:p3-qcd-ss}

![Z-rich validation mass. This Phase 3 visible-mass comparison tests the DY/Z modelling handle in the opposite-sign low-mT Z-rich window. The best visible-mass validation chi2 per degree of freedom is `1.409`, supporting use of the DY shape as an input while retaining the enlarged DY and tau open-data uncertainties.](../../../phase3_selection/outputs/figures/z_rich_validation_mvis.pdf){#fig:p3-zrich}

<!-- COMPOSE: 3x3 grid -->

![Selected muon transverse momentum. The Phase 3 plot uses final selected muons after trigger, ID, isolation, object arbitration, and signal-region requirements. It documents the muon kinematic phase space entering the Phase 4a templates rather than the looser first-candidate survey from Phase 2.](../../../phase3_selection/outputs/figures/mu_pt.pdf){#fig:p3-mupt}

![Selected tauh transverse momentum. The Phase 3 plot verifies that the tight tau isolation and tight anti-muon veto leave a physically populated tauh spectrum. This object definition is inherited without modification by the Phase 4a expected model.](../../../phase3_selection/outputs/figures/tau_pt.pdf){#fig:p3-taupt}

![Missing transverse momentum. The Phase 3 MET comparison documents the reconstructed missing-momentum input used for transverse mass and add-MET diagnostics. It also illustrates why MET-sensitive alternative observables remain cross-checks rather than promoted primary fit variables in this reduced model.](../../../phase3_selection/outputs/figures/met_pt.pdf){#fig:p3-met}

![Muon-MET transverse mass. This distribution is shown after the low-mT signal-region requirement and documents the variable that separates the signal-region candidate set from the high-mT W control handle. The same quantity is deliberately not used as an MVA discriminant after Phase 3 validation failures in the broader input set.](../../../phase3_selection/outputs/figures/mt_mu_met.pdf){#fig:p3-mt}

![Visible-plus-MET transverse momentum proxy. This Phase 3 diagnostic records the available proxy for the boosted topology. The raw data/MC modelling was not sufficient for MVA promotion, but the variable remains part of the category and alternative-observable context.](../../../phase3_selection/outputs/figures/pt_tautau_proxy.pdf){#fig:p3-pttautau}

![Clean jet multiplicity. The figure motivates the three retained fit categories by showing the selected-event jet multiplicity. The visible data/MC shape difference is one reason the analysis uses transparent category boundaries and avoids a trained classifier in Phase 4a.](../../../phase3_selection/outputs/figures/clean_jet_multiplicity.pdf){#fig:p3-njet}

![Leading dijet mass. The selected dijet-mass distribution supports the VBF-enriched category definition and was one of the few candidate MVA inputs to pass the Phase 3 modelling gate. The category threshold at `300 GeV` is therefore retained as a transparent VBF-like requirement.](../../../phase3_selection/outputs/figures/vbf_dijet_mass.pdf){#fig:p3-mjj}

![Leading dijet pseudorapidity separation. This selected-event distribution supports the VBF category requirement on the leading-dijet absolute eta separation. It also passed the Phase 3 MVA input-quality gate, but the classifier path was still downscoped because most other inputs failed.](../../../phase3_selection/outputs/figures/vbf_delta_eta_jj.pdf){#fig:p3-detajj}

# Template Construction and Statistical Model

The Phase 4a statistical model is a binned template fit in the classifier score `mva_score_hist_gradient_boosting`. The current workspace preserves the Phase 3 event categories and fits `vbf`, `boosted`, and `zero_jet` channels simultaneously. The score-bin edges are `[0.0, 0.2, 0.35, 0.5, 1.0]`, read from `phase4_inference/4a_expected/outputs/nominal_yields.json`; the observation vector is the background-only Asimov expectation, not observed signal-region data.

This is the current cohesive method. The older visible-mass and inclusive-score fits are retained only as comparison history in @tbl:method-comparison and the Change Log. The inclusive score comparison has a higher expected-only diagnostic `Z = 0.590`, but it collapses the categories into `inclusive_sr`; the user-requested Phase 4a method preserves `vbf`, `boosted`, and `zero_jet`, so the category-preserving HGB score model is the primary expected candidate.

The per-entry MC weight for a background sample $s$ is

$$
w_s = \frac{\sigma_s L_{int}}{N_{gen,s}}.
$$

For signal samples, the stored cross section is the H to tau tau effective cross section, so the source JSON writes the same expression as

$$
w_s = \frac{\sigma_{prod,s} B(H \to \tau\tau) L_{int}}{N_{gen,s}}.
$$

The expected bin yield in category $c$ and score bin $b$ is the sum of weighted entries over the samples that belong to a process group:

$$
\nu_{cb}(\mu,\theta) =
\mu \sum_{s \in S} \nu_{cbs}^{sig}(\theta)
+ \sum_{p \in B} \nu_{cbp}^{bkg}(\theta).
$$

Here $\mu$ is the signal-strength modifier, $\theta$ denotes nuisance parameters, $S$ denotes the two available Higgs signal samples, and $B$ denotes the available background processes. The nominal background-only Asimov observation is

$$
n^{A}_{cb} = \nu_{cb}(\mu=0,\theta=0).
$$

The likelihood is a HistFactory-style product of Poisson terms and nuisance constraints implemented with pyhf version `0.7.6` [@pyhf_joss]. In schematic form,

$$
L(\mu,\theta) =
\prod_{c,b} \mathrm{Pois}(n_{cb} | \nu_{cb}(\mu,\theta))
\prod_k \pi_k(\theta_k).
$$

The profile likelihood ratio for a tested signal strength is

$$
\lambda(\mu) =
\frac{L(\mu,\hat{\hat{\theta}}_{\mu})}
{L(\hat{\mu},\hat{\theta})},
$$

where $\hat{\hat{\theta}}_{\mu}$ are the profiled nuisance parameters at fixed $\mu$, and hats without double hats denote the unconditional maximum-likelihood estimates. Upper limits use the modified frequentist CLs construction [@read_cls] with asymptotic formulae [@cowan_asymptotic],

$$
CL_s(\mu) =
\frac{p_{s+b}(\mu)}{1 - p_b(\mu)}.
$$

The reported 95% upper limit is the value of $\mu$ for which

$$
CL_s(\mu) = 0.05.
$$

The discovery diagnostic uses the one-sided $q_0$ statistic, with the convention that downward fitted signal strengths do not count as discovery evidence:

$$
q_0 =
\begin{cases}
-2 \ln \lambda(0), & \hat{\mu} \ge 0, \\
0, & \hat{\mu} < 0.
\end{cases}
$$

The signal-injection validation creates Asimov pseudo-data at specified injected signal strengths and refits $\mu$. The bias is computed as

$$
\Delta\mu = \hat{\mu}_{fit} - \mu_{inj},
$$

and the relative bias for nonzero injections is

$$
\delta_{\mu} =
\frac{\hat{\mu}_{fit} - \mu_{inj}}{\mu_{inj}}.
$$

The GoF plumbing check uses a saturated statistic for Poisson templates. For an observed or pseudo-observed count $n_b$ and expectation $\nu_b$, the per-bin contribution is

$$
t_b = 2 \left[\nu_b - n_b + n_b \ln\left(\frac{n_b}{\nu_b}\right)\right],
$$

with the logarithmic term set to zero when $n_b = 0$. The Phase 4a Asimov saturated statistic is identically zero by construction because $n^A_b = \nu_b$, so the GoF toy distribution validates toy generation and statistic plumbing rather than data/model agreement.

Table: Phase 4a workspace configuration. Values are read from `expected_results.json` and `nominal_yields.json`. {#tbl:workspace-config}

| Quantity | Value | Source |
|---|---:|---|
| pyhf version | 0.7.6 | `expected_results.json` |
| Parameter of interest | mu | `expected_results.json` |
| Number of parameters | 17 | `expected_results.json` |
| Fit channels | 3 | `nominal_yields.json` |
| Score bins per channel | 4 | `nominal_yields.json` |
| Score-bin edges | `[0.0, 0.2, 0.35, 0.5, 1.0]` | `nominal_yields.json` |
| POI scan range | 0 to 50 | `expected_results.json` |
| Observation source | background-only Asimov | `expected_results.json` |

# Systematic Uncertainties

The Phase 4a systematic program is deliberately narrower than the CMS reference analyses. It implements sources that can be justified from the reduced open-data inputs and the predeclared Phase 1 strategy. Detector-shape variations requiring unavailable scale-factor machinery or shifted reduced inputs are documented as downscoped limitations instead of being replaced by arbitrary variations.

Table: Implemented Phase 4a nuisance parameters. Values are read from `phase4_inference/4a_expected/outputs/systematics.json`. {#tbl:implemented-systematics}

| Nuisance | Type | Size | Applies to | Source in artifact |
|---|---|---|---|---|
| `lumi_2012` | normsys | 2.6% | all MC-normalized samples | CMS PAS LUM-13-001 |
| `dy_norm_open_data` | normsys | 15% | DYJetsToLL | Phase 1 [D6] and user 10-15% requirement |
| `wjets_high_mt_control` | normsys | 2.637% | W1/W2/W3JetsToLNu | expected high-mT W+jets control precision |
| `tau_open_data_acceptance` | normsys | 15% | all selected MC templates | Phase 1 [D5]/[L2] and CMS Run 1 tau range |
| per-category staterror | staterror | sqrt(sum weights squared) per bin | selected MC templates | finite selected MC counts and official weights |

Table: Systematic completeness against search conventions and CMS references. The row content is copied from `systematics.json` and maps the current reduced-sample implementation to `conventions/search.md`, CMS JHEP 05 (2014) 104, and CMS Phys. Lett. B 779 (2018) 283. {#tbl:systematic-completeness}

| Source | Convention | CMS 2014 | CMS 2018 | This analysis | Status |
|---|---|---|---|---|---|
| Signal cross-section theory | required | scale/PDF/UE/PS | signal theory and acceptance | normalization source recorded; dedicated theory NP downscoped | downscoped |
| Signal acceptance/shape | required | tau/JES/MET/generator shape | shape uncertainties in categories | tau/open-data acceptance rate NP only | partial |
| Luminosity | pp normalization | 2.6% at 8 TeV | luminosity NP | 2.6% normsys on MC samples | implemented |
| DY/Z normalization | background norm | inclusive Z plus category extrapolation | DY control constraints | 15% normsys on DYJetsToLL | implemented |
| Tau ID/trigger/open-data acceptance | object calibration | tau ID/trigger range | tau ID/trigger effects | 15% correlated rate NP | implemented |
| MC statistics | required | limited event counts | bin-by-bin MC stat | per-category staterror modifiers | implemented |
| QCD multijet | background norm/shape | data-driven estimate | data-driven estimate | missing reduced sample; sideband deferred | downscoped |
| W+jets transfer/control | background norm | high-mT control region | mT control region | expected high-mT control scaffold with central SF=1 | partial |
| Diboson and single top | pp electroweak backgrounds | included | included | no reduced samples; omitted | downscoped |

### Luminosity Normalization

The luminosity nuisance represents the normalization uncertainty on all MC-based predictions. Its physical origin is the uncertainty in the integrated luminosity assigned to the 2012 Run2012B+C TauPlusX data sample. The implemented size is `2.6%`, read from `systematics.json` and traced through `normalization_inputs.json` to CMS PAS LUM-13-001 [@cms_lum_13_001].

The evaluation is a correlated normalization variation. For each affected template, the nuisance scales the nominal expected yield by a multiplicative factor corresponding to the luminosity uncertainty. In the schematic yield expression, the variation propagates through the luminosity factor in the MC weight:

$$
w_s(\theta_L) = w_s(0)(1 + 0.026\theta_L).
$$

The numerical impact is visible in the expected nuisance summary figure and in the workspace configuration: `lumi_2012` is one of the rate constraints in the `17`-parameter pyhf model. Its impact is subdominant relative to the larger open-data acceptance and DY normalization nuisances because the luminosity uncertainty is much smaller. It remains mandatory because it is a real external normalization uncertainty on simulation-normalized predictions.

### DY/Z Normalization

The DY/Z normalization nuisance covers the dominant Z/gamma* background in the score-template fit. Its physical origin is the incomplete reduced-open-data calibration path: the available reduced files lack the full trigger turn-on, tau efficiency scale-factor, and embedded Z to tau tau machinery used in the CMS reference analysis. Phase 1 decision [D6] required a `10-15%` DY/Z normalization uncertainty before unblinding, and Phase 4a implements the high end, `15%`, as `dy_norm_open_data`.

The variation applies only to the DYJetsToLL template. It is not derived by scaling DY to the observed signal region or by fitting the Drell-Yan peak in full data. In the model, the DY contribution in each category and bin is multiplied by a constrained factor:

$$
\nu_{cb}^{DY}(\theta_{DY}) =
\nu_{cb}^{DY}(0)(1 + 0.15\theta_{DY}).
$$

The numerical impact is largest in the zero-jet channel, where the nominal background total is `7068.898` expected events. This source is physically expected to matter because the zero-jet channel is DY-rich and the Z-rich validation handle contains `5514` data events at Phase 3. The interpretation is conservative but predeclared: Phase 4b must verify whether the `15%` prior covers the 10% validation sample without making all pulls trivially small.

### W+jets High-mT Control Normalization

The W+jets nuisance represents the expected precision of the high-mT W control-region normalization scaffold. Its physical origin is the reducible W+jets background in events where a W decay supplies the muon and a jet-like object passes the tauh selection. Phase 4a uses the Phase 3 `is_w_high_mt` control flag but does not use real control-region data to set a central scale factor.

The Phase 4a central W scale factor is fixed to `1.0` in the expected-only model. The nuisance size is the expected W+jets high-mT control statistical precision, `2.637%`, read from `systematics.json`; the corresponding normsys factors are `hi = 1.0263711789977958` and `lo = 0.9736288210022043`. Phase 4b must replace or validate the central value with observed high-mT data after the 10% data-validation gate.

### Tau Trigger, Tau ID, and Open-Data Acceptance

The tau/open-data acceptance nuisance represents missing efficiency and acceptance corrections for the reduced TauPlusX analysis. Its physical origin is broader than a single detector effect: the reduced files do not provide the full official tau trigger, tau ID, tau energy, and muon-tau trigger scale-factor machinery used in the CMS Run 1 analyses. Phase 1 [D5] and [L2] predeclared a `10-15%` uncertainty range; Phase 4a implements `15%` as `tau_open_data_acceptance`.

The evaluation is a correlated rate uncertainty on all selected MC templates. It is intentionally not a shape variation, because no citable reduced-sample detector-variation machinery or shifted template production exists at this phase. The propagated rate model is

$$
\nu_{cb}^{MC}(\theta_{\tau}) =
\nu_{cb}^{MC}(0)(1 + 0.15\theta_{\tau}).
$$

The numerical impact is larger than luminosity and comparable in size to the DY normalization prior, but broader in scope because it affects signal and background MC. This is an honest reduced-sample limitation: it prevents overclaiming precision, but it cannot replace a true tau efficiency, trigger, and tau energy scale program. Phase 4b and Phase 5 must either source a more specific correction path or keep the limitation prominent.

### MC Statistical Uncertainty

The MC statistical nuisance accounts for finite selected MC counts after category and score binning. Its physical origin is the limited number of reduced events in each process, especially for the small VBF channel and for high-score bins. The implementation uses per-category Barlow-Beeston-lite `staterror` modifiers in pyhf, with bin uncertainties derived from the weighted sum of squared MC weights.

For a bin filled by events with weights $w_i$, the MC statistical variance is

$$
\sigma_{MC,b}^2 = \sum_i w_i^2.
$$

The numerical impact is embedded in each category's `staterror` modifier and summarized in `expected_nuisance_summary.pdf`. The smallest expected background bin is `13.617` events in the VBF channel, so the asymptotic expected limit is not forced into a low-count toy-only regime by the final score binning. MC statistics are represented for the included samples, but the missing sample set can still bias the composition even when finite-sample uncertainty is modelled.

### Downscoped Systematic Sources

Several convention and reference-analysis sources are not implemented in Phase 4a because the reduced inputs do not support them without inventing variations. The downscoped list is read from `systematics.json`. These sources remain analysis limitations, not unmodelled surprises.

Table: Downscoped systematic and model sources. Each source is carried to the limitations section and Phase 4b/5 obligations. {#tbl:downscoped-systematics}

| Source | Reason | Impact |
|---|---|---|
| tau_energy_scale | no reduced tau energy scale variation or scale-factor prescription | could shift score-template inputs through tau kinematics |
| muon_efficiency_scale | no official reduced-file muon trigger/ID scale factors | rate uncertainty partly covered but not separately measured |
| JES_JER_MET | no shifted reduced inputs or variation machinery | VBF and boosted acceptances may be understated |
| pileup | PV_npvs exists but no pileup weights/profile weights | qualitative validation limitation |
| PDF_scale_UE_PS | no event-level PDF/scale weights or alternative generators | theory and acceptance uncertainties are not separated |
| QCD_multijet | no reduced QCD MC and no Phase 4a data sideband tuning | instrumental fake component omitted from expected workspace |
| missing paper-level samples | no reduced files for several CMS components | background composition and sensitivity are incomplete |

![Expected nuisance summary. This Phase 4a diagnostic ranks implemented rate and MC-stat uncertainty handles in the expected workspace. It is not an observed-data post-fit impact plot; it shows the nuisance structure available before 10% validation and full unblinding.](figures/expected_nuisance_summary.pdf){#fig:p4a-nuisance-summary}

# Cross-Checks and Validation

The Phase 4a validation suite checks the expected model under its own assumptions. It does not claim data closure in the signal region, because the Phase 4a observation is Asimov pseudo-data. The checks therefore answer a narrower question: whether the expected workspace, scan, signal injection, and toy machinery behave coherently before data validation.

The method-comparison context is read from `sensitivity_recommendation.json` and `mva_sensitivity.json`. The baseline categorized visible-mass model gives `Z = 0.1906097504953417` and median expected limit `11.404384834571836`. The add-MET mass comparison gives `Z = 0.1636083293830189`. The selected category-preserving HGB score gives Phase 3 scan `Z = 0.5264362537642254` and median expected limit `4.24380622771541`; the updated Phase 4a pyhf workspace gives `Z = 0.5264171907925044` and median expected limit `4.199448081748937`.

Table: Candidate method comparison. Values are read from `phase3_selection/outputs/sensitivity_recommendation.json`, `phase3_selection/outputs/mva_sensitivity.json`, and `phase4_inference/4a_expected/outputs/expected_results.json`. {#tbl:method-comparison}

| Candidate | Channels | Observable | Z | Median limit | Status |
|---|---|---|---:|---:|---|
| Baseline categorized visible mass | `vbf`, `boosted`, `zero_jet` | `m_vis` | 0.190610 | 11.404385 | comparison baseline |
| Add-MET mass | `vbf`, `boosted`, `zero_jet` | `m_addmet` | 0.163608 | not evaluated | comparison only |
| HGB score, categorized | `vbf`, `boosted`, `zero_jet` | `mva_score_hist_gradient_boosting` | 0.526436 | 4.243806 | selected Phase 3 candidate |
| HGB score, Phase 4a workspace | `vbf`, `boosted`, `zero_jet` | `mva_score_hist_gradient_boosting` | 0.526417 | 4.199448 | current expected-primary candidate |
| MLP score, categorized | `vbf`, `boosted`, `zero_jet` | `mva_score_mlp` | 0.338149 | not evaluated | comparison only |
| XGBoost score, categorized | `vbf`, `boosted`, `zero_jet` | `mva_score_xgboost` | 0.313006 | not evaluated | comparison only |
| HGB score, inclusive | `inclusive_sr` | `mva_score_hist_gradient_boosting` | 0.590234 | not evaluated | comparison-only; categories not preserved |

The transformer option was preferred by the user, but it was not attempted in this quick Phase 4a method update because `mva_sensitivity.json` records no available `torch`, `pytorch_tabular`, or `tabpfn` stack in the current pixi environment. The reduced selected-event artifact also makes genMET direction/phi regression infeasible: `genmet_regression_feasibility` records no genMET or genMET-phi target branch, only reconstructed `met_pt`. Training a genMET-direction regressor without a target would fabricate labels, so no transformer or genMET-regression result is claimed.

The Phase 3 tight tau anti-muon veto is implemented. The machine-readable `tau_antimuon_veto` record states that the tau candidate selection requires `Tau_idAntiMuTight > 0` in `phase3_selection/src/build_selection.py`; the selected-event summary keeps selected tau variables rather than a separate veto flag.

Table: Signal-injection recovery. Values are read from `phase4_inference/4a_expected/outputs/signal_injection.json`. The pass criterion is relative bias below 20% for nonzero injections and near-zero absolute bias for the zero injection. {#tbl:signal-injection}

| Injected mu | Fitted mu | Abs. bias | Rel. bias | Pass |
|---:|---:|---:|---:|---|
| 0.0 | 0.000324 | 0.000324 | 0.000000 | true |
| 1.0 | 1.000000 | 0.000000 | 0.000000 | true |
| 2.0 | 1.997675 | −0.002325 | −0.001163 | true |
| 5.0 | 5.000482 | 0.000482 | 0.000096 | true |

![Signal-injection recovery. The Phase 4a injection study fits Asimov pseudo-data generated at injected signal strengths `0`, `1`, `2`, and `5`. The recovered signal strengths lie on the diagonal within the predeclared tolerance, which validates the workspace response under nominal model assumptions.](figures/signal_injection_recovery.pdf){#fig:p4a-injection}

The GoF toy study uses `500` Poisson toys generated from the background-only expected templates. Since the Asimov observation equals the model expectation, the saturated statistic is `0.000` in every category and the toy fraction greater than or equal to the Asimov statistic is `1.000`. This is a useful plumbing check but a deliberately limited validation: it cannot demonstrate agreement between real data and the model.

Table: Limited GoF toy summary. Values are read from `phase4_inference/4a_expected/outputs/gof_validation.json`. The p-like fraction is the fraction of Poisson toys with saturated statistic greater than or equal to the Asimov statistic. {#tbl:gof-summary}

| Category | NDF | Asimov stat | Pearson chi2/ndf | Toy count | Toy mean | Toy median | Toy p95 | Fraction >= Asimov |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| VBF | 4 | 0.000 | 0.000 | 500 | 4.012 | 3.412 | 9.926 | 1.000 |
| Boosted | 4 | 0.000 | 0.000 | 500 | 3.683 | 3.178 | 8.178 | 1.000 |
| Zero-jet | 4 | 0.000 | 0.000 | 500 | 4.019 | 3.313 | 9.479 | 1.000 |
| Combined | 12 | 0.000 | 0.000 | 500 | 11.932 | 11.295 | 20.159 | 1.000 |

![Limited toy GoF distribution. The toy distribution is generated from background-only expected templates and compared with the Asimov saturated statistic. The vertical marker at zero is expected by construction, so the figure validates toy generation and statistic evaluation rather than real-data agreement.](figures/gof_toys.pdf){#fig:p4a-gof-toys}

<!-- COMPOSE: side-by-side -->

![Approach comparison. The Phase 3 plot compares visible mass and add-MET mass using the same raw MC-only binned separation metric across the exclusive categories. It remains comparison context for the current score-template result rather than the Phase 4a primary model.](../../../phase3_selection/outputs/figures/approach_comparison.pdf){#fig:p3-approach}

![MVA input modelling gate. The Phase 3 gate compares validation/control-region data and background-MC shapes for candidate classifier inputs. Most candidate inputs exceed the predeclared chi2/ndf threshold of `5`, so the HGB score is carried as an expected-primary candidate pending Phase 4b score-modelling validation and calibration.](../../../phase3_selection/outputs/figures/mva_input_modeling_chi2.pdf){#fig:p3-mva-gate}

<!-- COMPOSE: side-by-side -->

![Expected-only sensitivity variant summary. This Phase 3 diagnostic ranks the strongest expected-only selection, category, observable, and classifier variants using simulated templates. It documents why the category-preserving HGB score was selected for the current Phase 4a expected workspace even though the inclusive score comparison is retained only as comparison context.](../../../phase3_selection/outputs/figures/sensitivity_variant_summary.pdf){#fig:p3-sensitivity-variant-summary}

![Gradient-boosted classifier score templates. This Phase 3 plot shows expected signal and background score distributions after official Open Data normalization inputs. It is an expected-only MVA diagnostic; Phase 4b must validate score modelling before the score fit can be used without qualification on data.](../../../phase3_selection/outputs/figures/mva_score_templates.pdf){#fig:p3-mva-score-templates}

# Expected Results

The expected-result tables and plots in this section are derived from `expected_results.json` and `nominal_yields.json`. They are Asimov/MC expected results only. No observed full-data signal-region result, observed signal strength, or observed full-data post-fit template is presented in this Phase 4a note.

The expected yields are small for signal relative to background in all categories. The VBF channel has the largest integrated S/B, `0.010528`, but contains only `1.590` expected signal events and `150.995` expected background events. The zero-jet channel has the largest expected signal yield, `14.341`, but it is embedded in `7068.898` expected background events.

Table: Nominal expected yields by category. Values are read from `phase4_inference/4a_expected/outputs/nominal_yields.json`. {#tbl:expected-yields}

| Category | Signal yield | Background yield | S/B | S/sqrt(B) | Minimum background bin |
|---|---:|---:|---:|---:|---:|
| VBF | 1.590 | 150.995 | 0.010528 | 0.129 | 13.617 |
| Boosted | 9.175 | 2118.332 | 0.004331 | 0.199 | 93.004 |
| Zero-jet | 14.341 | 7068.898 | 0.002029 | 0.171 | 32.318 |

<!-- COMPOSE: 1x3 grid -->

![Expected HGB score templates in the VBF channel. This Phase 4a plot shows the background-only expected stack and nominal Higgs signal overlay after official Open Data normalization. The fit observation is the Asimov background expectation, not real collision data, and the minimum expected background score bin remains `13.617`.](figures/expected_mva_score_vbf.pdf){#fig:p4a-score-vbf}

![Expected HGB score templates in the boosted channel. This Phase 4a plot shows the non-VBF category with at least one clean jet. The channel has the largest expected S/sqrt(B) among the three retained channels, but the expected signal remains much smaller than the background.](figures/expected_mva_score_boosted.pdf){#fig:p4a-score-boosted}

![Expected HGB score templates in the zero-jet channel. This Phase 4a plot shows the DY-dominated score-template channel retained from Phase 3. The channel supplies the largest absolute expected signal yield and the largest background constraint in the simplified reduced-sample model.](figures/expected_mva_score_zero_jet.pdf){#fig:p4a-score-zero}

![Expected signal-to-background ratio. This figure summarizes the category-integrated nominal Higgs signal divided by nominal background. The VBF channel has the largest integrated S/B, while the boosted channel has the largest S/sqrt(B) because of its balance of signal yield and background size.](figures/expected_s_over_b.pdf){#fig:p4a-sob}

The asymptotic modified-frequentist CLs calculation scans $\mu$ from `0` to `50`. The expected median 95% upper limit is `4.199`, with the minus-two, minus-one, plus-one, and plus-two expected bands listed in @tbl:expected-limit. The Asimov observed-on-background limit is numerically equal to the median expected limit within rounding, as expected for a background-only Asimov observation.

Table: Expected 95% CLs upper limit on signal strength. Values are read from `phase4_inference/4a_expected/outputs/expected_results.json`. {#tbl:expected-limit}

| Quantity | mu |
|---|---:|
| Expected minus-two band | 2.144 |
| Expected minus-one band | 2.920 |
| Expected median | 4.199 |
| Expected plus-one band | 6.146 |
| Expected plus-two band | 8.817 |
| Observed-on-background Asimov | 4.199 |

The expected discovery diagnostic is intentionally modest. The pyhf asymptotic $q_0$ test on signal-plus-background Asimov data gives `p = 0.2993` and `Z = 0.5264`. This is numerically compatible with a low-sensitivity expected-limit result rather than with an expected discovery claim, and it is consistent with the small expected S/sqrt(B) values in @tbl:expected-yields.

Table: Expected discovery diagnostic. Values are read from `expected_results.json`. {#tbl:discovery-diagnostic}

| Method | p-value | Z | Status |
|---|---:|---:|---|
| pyhf asymptotic q0 on signal-plus-background Asimov | 0.2993 | 0.5264 | evaluated |

# Comparison to Prior Results and Theory

The most relevant Run 1 reference is CMS JHEP 05 (2014) 104, which reported evidence for H to tau tau using 7 TeV and 8 TeV data, multiple channels, CMS calibrations, embedded backgrounds, and a full category/control-region program [@cms_htt_2014]. That publication quotes a global best-fit signal strength of `0.78 ± 0.27` and local significance above `3` standard deviations in the Higgs-mass range used in the strategy artifact. This Phase 4a reduced mu tauh expected limit of $\mu = 4.199$ is weaker by a factor of about `5.38` relative to a Standard Model signal-strength target of `0.78`, but the comparison is a sensitivity-scale context, not a direct observed-data pull.

CMS Phys. Lett. B 779 (2018) 283 reported H to tau tau observation at 13 TeV with `35.9/fb`, observed significance `4.9`, expected significance `4.7`, and signal strength `1.09` with uncertainties near `0.27` [@cms_htt_2018]. The current reduced expected discovery diagnostic of `Z = 0.526` is lower by a factor of about `8.93` relative to the `4.7` expected significance from that 13 TeV analysis. The comparison is quantitative but not a compatibility test because the energy, luminosity, channels, reconstruction, and training/calibration programs differ.

The ATLAS+CMS Run 1 combination reported a combined Higgs signal yield relative to the Standard Model of `1.09 ± 0.11` and an H to tau tau observed significance of `5.5` in the Phase 1 strategy's reference table [@atlas_cms_higgs_combination_2016]. The Phase 4a expected limit is therefore not competitive with world-level Higgs coupling precision. Its purpose is to provide a transparent open-data score-template search model with honest limitations and a reproducible statistical workflow.

Table: Prior-result context. External reference numbers are from the cited publications as recorded in the Phase 1 strategy, while this-analysis numbers are from Phase 4a JSON. {#tbl:prior-context}

| Source | Quantity | Value | Comparison status |
|---|---|---:|---|
| This Phase 4a note | expected 95% CLs limit on mu | 4.199 | internal expected result |
| This Phase 4a note | expected discovery Z | 0.526 | internal expected diagnostic |
| CMS 2014 Run 1 | global best-fit mu | 0.78 ± 0.27 | global observed context, not direct pull |
| CMS 2014 Run 1 | local H to tau tau significance | > 3 sigma | global observed context |
| CMS 2018 13 TeV | observed significance | 4.9 | different energy and dataset |
| CMS 2018 13 TeV | expected significance | 4.7 | about 8.93 times larger than this expected Z |
| CMS 2018 13 TeV | signal strength | 1.09 | global observed context |
| ATLAS+CMS Run 1 | combined signal yield relative to SM | 1.09 ± 0.11 | world-level coupling context |
| ATLAS+CMS Run 1 | H to tau tau observed significance | 5.5 | global observed context |

# Conclusions

Phase 4a has produced an expected-only pyhf template model for the reduced CMS 2012 Open Data H to tau tau search in the mu tauh final state. The model uses `mva_score_hist_gradient_boosting` in simultaneous `vbf`, `boosted`, and `zero_jet` channels, official Open Data normalization metadata, a 2.6% luminosity nuisance, 15% DY and tau/open-data acceptance nuisances, a 2.637% expected W high-mT control nuisance, and per-category MC statistical uncertainties. The expected median 95% CLs upper limit is $\mu = 4.199$, and the expected discovery diagnostic is $Z = 0.526$.

The result should be interpreted as a reduced-open-data expected sensitivity benchmark and not as a full CMS reproduction. It is not yet an observed result. Phase 4b will add 10% data validation with a compiled PDF and human gate, including score-modelling validation and observed high-mT W control checks; Phase 4c will add full observed signal-region results only after approval.

# Future Directions

The next required step is Phase 4b 10% data validation. That phase must compare the 10% observed result to the expected score-template model, validate the Z-rich, W high-mT, QCD same-sign, top, VBF, and category-stability handles, and recompile the analysis note PDF before human review. It must not silently tune the signal-region background model to improve agreement.

Phase 4c must then compare the full observed result to both the Phase 4a expectation and the Phase 4b 10% validation result. If data-level nuisance pulls, score-modelling checks, or GoF tests reveal a physics issue traceable to earlier phases, the regression protocol must be triggered. Phase 5 should add final typesetting, figure compositing, more complete comparison plots, and any additional citable calibration or detector variation inputs that can be implemented without violating the reduced-sample scope.

# Known Limitations and Open Questions

The dominant limitation is missing detector and efficiency correction machinery. The reduced files do not include the full trigger, tau ID, tau trigger, tau energy scale, muon efficiency, pileup, JES/JER, MET, or b-tag variation workflow used in the CMS reference analyses. Phase 4a represents this with a 15% tau/open-data acceptance nuisance and explicit downscope rows, but this is not a substitute for source-specific detector systematics or score-shape variations.

The second limitation is missing background and signal components. The expected workspace omits QCD multijet, diboson, single top, W4 or inclusive W+jets, embedded Z to tau tau, associated Higgs, H to WW, and additional DY categories. The largest practical consequence is that the expected background composition is incomplete relative to the CMS papers, especially for fake-tau and electroweak backgrounds.

The third limitation is expected-only blinding. Phase 4a uses background-only Asimov pseudo-data, so the GoF statistic is identically zero by construction and cannot validate real data agreement. This is correct for Phase 4a, but the limitation must be removed by 10% validation and full observed fits in later phases.

The fourth limitation is score-model validation. The HGB score improves expected sensitivity in MC, but Phase 3 already documented broad data/background-MC input-shape failures. The score fit is therefore an expected-primary candidate pending Phase 4b validation, not an unqualified observed-data primary result.

# Appendix A: Limitation Index

Table: Limitation and decision index propagated to Phase 4a. Labels originate in Phase 1 and are tracked through `COMMITMENTS.md` and current Phase 3/4 machine-readable outputs. {#tbl:limitation-index}

| Label | Description | Phase 4a status | Impact |
|---|---|---|---|
| [D1] | Search/template-fit strategy | fulfilled | simultaneous pyhf score-template model built |
| [D2] | Visible mass baseline observable | superseded by Phase 3 expected-sensitivity regression | visible mass retained as comparison baseline, not current primary |
| [D3] | VBF, boosted, zero-jet categories | fulfilled | simultaneous three-channel fit preserved |
| [D4] | W high-mT data normalization | partial in 4a | expected central SF=1 with 2.637% nuisance; observed control update deferred to 4b |
| [D5] | Tight tau anti-muon veto | fulfilled | `Tau_idAntiMuTight > 0` in Phase 3 tau selection |
| [D6] | DY/Z 10-15% uncertainty | fulfilled | 15% DY norm nuisance |
| [D7] | pyhf workspace with MC stat terms | fulfilled | 17-parameter pyhf model |
| [D8] | Blinding | fulfilled | real signal-region data not used |
| [D9] | Alternative observable gate | updated | HGB score selected as expected-primary candidate; add-MET, MLP, XGBoost, inclusive score retained as comparisons |
| [L1] | Single-channel scope | carried | sensitivity weaker than CMS all-channel |
| [L2] | Missing trigger/tau scale factors | carried | 15% tau/open-data acceptance nuisance |
| [L3] | Visible mass weaker than SVFit | carried | visible mass baseline superseded by expected-only score candidate |
| [L4] | QCD/multijet unavailable | carried | fake background deferred to sideband validation |
# Appendix B: Numerical Source Map

The AN numerical values are rendered from JSON outputs and external cited records. Result values are not transcribed from prose artifacts. Table @tbl:numeric-source-map maps the main numerical classes to their machine-readable sources.

Table: Numerical source map. This table is intended as the audit bridge between the note and the machine-readable artifacts. {#tbl:numeric-source-map}

| Numerical class | Source file | Example fields |
|---|---|---|
| Expected CLs limit and discovery diagnostic | `phase4_inference/4a_expected/outputs/expected_results.json` | expected band, Asimov limit, p-value, Z |
| Nominal yields and binning | `phase4_inference/4a_expected/outputs/nominal_yields.json` | score-bin edges, category yields, S/B, S/sqrt(B) |
| Systematics | `phase4_inference/4a_expected/outputs/systematics.json` | nuisance sizes, completeness table, downscopes |
| Signal injection | `phase4_inference/4a_expected/outputs/signal_injection.json` | injected mu, fitted mu, biases |
| GoF toys | `phase4_inference/4a_expected/outputs/gof_validation.json` | toy count, medians, p95, Asimov statistic |
| Missing components | `phase4_inference/4a_expected/outputs/limitations_downscope.json` | missing sample list and statuses |
| Selection raw yields | `phase3_selection/outputs/category_yields.json`, `region_yields.json` | category and region counts |
| Method comparison | `phase3_selection/outputs/sensitivity_recommendation.json`, `mva_sensitivity.json` | candidate Z values, median limits, feasibility records |
| Normalization inputs | `phase3_selection/outputs/normalization_inputs.json` | luminosity, N_gen, cross sections, weights |

# Appendix C: Auxiliary Phase 2 Figures

The Phase 2 figures in this appendix document early feasibility and branch-range checks. They are superseded by Phase 3 final-candidate plots for the selected-event model, but they remain useful provenance for why visible mass, add-MET, transverse mass, jet multiplicity, and VBF variables were considered.

<!-- COMPOSE: 3x3 grid -->

![Phase 2 leading muon transverse momentum. This first-candidate slice check validated the presence and range of the muon branches before final object arbitration. It is included as provenance, while the final selected muon distribution in @fig:p3-mupt is the analysis-level diagnostic.](../../../phase2_exploration/outputs/figures/muon_pt_slice.pdf){#fig:p2-muon-pt}

![Phase 2 leading tau transverse momentum. This first-candidate plot confirmed that the tau candidate branches are populated in data and MC. The final tauh selection used for templates is documented by @fig:p3-taupt.](../../../phase2_exploration/outputs/figures/tau_pt_slice.pdf){#fig:p2-tau-pt}

![Phase 2 MET diagnostic. This plot established that reconstructed MET is available in the reduced files and can support transverse-mass and add-MET studies. It also helped identify the absence of direct GenMET needed for the requested NN genMET regression.](../../../phase2_exploration/outputs/figures/met_pt_slice.pdf){#fig:p2-met}

![Phase 2 visible-mass diagnostic. This first-candidate visible-mass plot showed that $m_{vis}$ can be constructed but also warned about loose candidate-cleaning artifacts. Phase 3 rebuilt the mass templates after final object selection before Phase 4a used them.](../../../phase2_exploration/outputs/figures/visible_mass_slice.pdf){#fig:p2-mvis}

![Phase 2 add-MET mass diagnostic. This plot demonstrated that a reconstructed-MET-assisted mass-like observable is available in both data and MC. The observable remains a documented alternative, but it is not the Phase 4a primary fit observable.](../../../phase2_exploration/outputs/figures/addmet_mass_slice.pdf){#fig:p2-addmet}

![Phase 2 transverse-mass diagnostic. This first-candidate distribution motivated the low-mT signal-region and high-mT W control-region definitions. The final selected transverse-mass behavior is shown in @fig:p3-mt.](../../../phase2_exploration/outputs/figures/mt_mu_met_slice.pdf){#fig:p2-mt}

![Phase 2 jet multiplicity diagnostic. This plot supported the feasibility of category construction with zero-jet, boosted, and VBF-like topologies. Final clean-jet multiplicity is documented by @fig:p3-njet.](../../../phase2_exploration/outputs/figures/jet_multiplicity_slice.pdf){#fig:p2-njet}

![Phase 2 dijet mass diagnostic. The first-candidate survey showed that leading-dijet mass is available and populated enough to study a VBF-like category. The final VBF diagnostic is shown in @fig:p3-mjj.](../../../phase2_exploration/outputs/figures/dijet_mass_slice.pdf){#fig:p2-mjj}

![Phase 2 dijet eta-separation diagnostic. This plot identified leading-dijet eta separation as one of the strongest simple discriminators in the early survey. The final selected distribution in @fig:p3-detajj supports the retained VBF category.](../../../phase2_exploration/outputs/figures/dijet_deltaeta_slice.pdf){#fig:p2-detajj}

![Phase 2 variable separation ranking. The ranking summarized single-variable raw MC separation in the exploratory slice. It explains why VBF-related quantities, transverse mass, jet multiplicity, add-MET mass, and visible mass remained under consideration before Phase 3 validation.](../../../phase2_exploration/outputs/figures/variable_separation_ranking.pdf){#fig:p2-separation}

# Appendix D: Auxiliary Phase 3 Template Figures

The Phase 3 template figures in this appendix are shape-normalized diagnostics produced before the Phase 4a expected model added official Open Data normalization and nuisance parameters. They document the visible-mass baseline and add-MET alternative by category; both are comparison inputs for the current score-template result.

<!-- COMPOSE: 2x3 grid -->

![Phase 3 visible mass in the VBF category. This normalized diagnostic shows the primary observable before Phase 4a absolute normalization. The current Phase 4a score-template fit supersedes it for the expected statistical model.](../../../phase3_selection/outputs/figures/visible_mass_vbf.pdf){#fig:p3-mvis-vbf}

![Phase 3 visible mass in the boosted category. This normalized diagnostic shows the primary observable in the non-VBF one-or-more-jet category. The current Phase 4a score-template fit supersedes it for the expected fit.](../../../phase3_selection/outputs/figures/visible_mass_boosted.pdf){#fig:p3-mvis-boosted}

![Phase 3 visible mass in the zero-jet category. This normalized diagnostic shows the DY-rich zero-jet mass shape before Phase 4a absolute weighting. The current Phase 4a score-template fit is the model input used for the expected result.](../../../phase3_selection/outputs/figures/visible_mass_zero_jet.pdf){#fig:p3-mvis-zero}

![Phase 3 add-MET mass in the VBF category. This alternative-observable diagnostic is retained for audit because add-MET mass was required by the user prompt. It is not promoted over the HGB score in Phase 4a.](../../../phase3_selection/outputs/figures/addmet_mass_vbf.pdf){#fig:p3-addmet-vbf}

![Phase 3 add-MET mass in the boosted category. This diagnostic shows the add-MET alternative in the boosted category. The expected comparison does not outperform the HGB score, so it remains an auxiliary study.](../../../phase3_selection/outputs/figures/addmet_mass_boosted.pdf){#fig:p3-addmet-boosted}

![Phase 3 add-MET mass in the zero-jet category. This diagnostic completes the category-by-category add-MET audit trail. It supports the documented alternative-observable study but does not enter the Phase 4a expected result.](../../../phase3_selection/outputs/figures/addmet_mass_zero_jet.pdf){#fig:p3-addmet-zero}

# Appendix E: Reproduction Contract

The analysis is managed through pixi. A reproducer should install the environment and then run the phase tasks in order. The Phase 4a expected model is reproducible without looking at observed full-data signal-region results because it uses selected MC templates and background-only Asimov pseudo-data.

Table: Reproduction command sequence. Commands and expected outputs are based on `pixi.toml` and the phase artifacts. {#tbl:reproduction}

| Step | Command | Expected outputs |
|---|---|---|
| Environment | `pixi install` | default pixi environment |
| Phase 2 localization manifest | `pixi run phase2-local-manifest` | local sample manifest |
| Phase 2 exploration | `pixi run phase2-explore` and `pixi run phase2-plots` | exploration JSON and figures |
| Phase 3 selection | `pixi run phase3-all` | selected events, category yields, region yields, figures |
| Phase 4a model | `pixi run phase4a-model` | templates, pyhf workspace, expected JSON |
| Phase 4a plots | `pixi run phase4a-plots` | expected template and validation figures |
| Phase 4a validation | `pixi run phase4a-validate` | JSON, workspace, and figure checks |
| Full Phase 4a executor chain | `pixi run phase4a-all` | complete Phase 4a executor outputs |

The workflow DAG is: localized ROOT files and Open Data normalization records feed Phase 2 inventory and Phase 3 selection; Phase 3 selected-event summaries feed Phase 4a weighted templates; weighted templates feed the pyhf workspace; the workspace feeds expected CLs, discovery diagnostics, injection tests, GoF toys, and Phase 4a figures; this note renders the JSON and figure artifacts into analysis prose.

# Appendix F: Note Writer Self-Check

This self-check is updated by the note writer before handoff to the typesetter. The source files are `ANALYSIS_NOTE_4a_v1.md`, `references.bib`, and the JSON files listed in @tbl:numeric-source-map.

Table: Self-check targets and current status. The final counts are reported in the note-writer final status message after mechanical verification. {#tbl:self-check}

| Check | Target or rule | Status |
|---|---|---|
| Display equations | at least 8 | drafted above target |
| Figure references | at least 20 | drafted above target |
| Table references | at least 5 | drafted above target |
| Implemented systematic subsections | 4 of 4 | complete |
| Expected-only blinding statement | required | present in introduction, results, and limitations |
| Figure file existence | all referenced PDFs | verified after drafting |
| Numerical source consistency | key JSON values match rounded note values | verified after drafting |

# References {-}
