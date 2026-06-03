# Phase 4a Expected Inference: CMS 2012 Open Data H to Tau Tau Search

## Summary

Phase 4a builds an expected-only binned pyhf model for the reduced CMS 2012
Open Data H to tau tau search in the mu tau_h final state. This rerun uses the
Phase 3 sensitivity-regression recommendation as the Phase 4a expected-primary
candidate: `mva_score_hist_gradient_boosting` in the `vbf, boosted, zero_jet` signal-region channels.
The channels are fitted simultaneously with a common signal-strength parameter.
The observation is background-only Asimov pseudo-data from the nominal model, so no real data signal-region distribution or
full-data observed fit result enters this phase.

The MVA score is an expected-primary candidate, not a final data-validated
primary observable. Phase 4b must validate score modelling and calibration
before the analysis can use this score model without qualification on data.

The expected 95% CLs upper limit on the signal strength is
`2.904` on the background-only Asimov
sample. The median expected band from pyhf is `2.904`, with minus-one
and plus-one variations `1.982` and `4.335`. The expected
discovery diagnostic is `Z = 0.787`. For comparison, the stale
visible-mass Phase 4a baseline had `Z = 0.191` and median expected limit
`mu = 11.374`, while the unmerged Phase 3 score recommendation had
`Z = 0.785` and median expected limit
`mu = 2.944`. These are single-channel
reduced-open-data expectations and are not directly comparable to the CMS
all-channel Run 1 results without the missing components and calibrations
listed below.

## Method

The expected-primary candidate observable is
`mva_score_hist_gradient_boosting`, with merged bin edges
`[0.0, 0.2, 0.35, 0.5, 0.65, 0.78, 0.88, 1.0]`. The Phase 4a executor uses
`phase3_selection/outputs/sensitivity_recommendation.json` and
`phase3_selection/outputs/sensitivity_selected_events.npz`, requiring
`is_signal_region` and the Phase 3 sensitivity categories `vbf, boosted, zero_jet`.
The Phase 3 `region_exclusive` diagnostic labels are not used to form the fit
templates.

The Phase 3 recommendation records sparse-bin handling as `Phase 3 common score-bin merging across fit categories`.
The merged model has a minimum nominal expected-background bin of
`6.899`, so no score bin remains below five expected background
events in the promoted category-preserving fit.

The W+jets normalization method is prepared through the high-`mT` control flag
`is_w_high_mt`. Phase 4a keeps the
central W scale factor at the background-only Asimov value of 1.0 and propagates
the expected control-region statistical precision as a nuisance; Phase 4b must
replace this with the observed high-`mT` transfer factor before full unblinding.

MC normalization follows `phase3_selection/outputs/normalization_inputs.json`.
Signal weights use `sigma_prod * BR(H->tautau) * L_int / N_gen`, and
background weights use `sigma * L_int / N_gen`, with `L_int = 11467/pb`. The
MC denominators are official CERN Open Data `distribution.number_events`
values, not local reduced ROOT entries or selected counts.

The workspace is written to `outputs/pyhf_workspace.json`. It includes a common
signal-strength POI `mu`, luminosity and tau/open-data acceptance normsys
modifiers, a DY normalization normsys, a W+jets high-`mT` control nuisance, and
per-category Barlow-Beeston-lite staterror modifiers. The observation in the
workspace is the background-only Asimov expectation in the score-template
channels.

## Expected Yields

| Category | Signal yield | Background yield | S/sqrt(B) | Minimum background bin |
| --- | --- | --- | --- | --- |
| vbf | 1.590 | 110.223 | 0.151 | 6.899 |
| boosted | 9.175 | 2173.547 | 0.197 | 38.699 |
| zero_jet | 14.341 | 14326.936 | 0.120 | 14.401 |

![Expected MVA score templates in the promoted signal-region categories. This figure
shows the Phase 4a background-only expected stack and nominal Higgs signal
overlay after official Open Data normalization. The fit observation is the
Asimov background expectation rather than real collision data, and the score
model remains pending Phase 4b data-validation of score modelling and
calibration.](figures/expected_mva_score_vbf.pdf){#fig:p4a-mva-score}

![Expected signal-to-background ratio by score channel. This figure summarizes
the category-integrated nominal Higgs signal divided by the nominal background.
It is a compact diagnostic for the inclusive score-template workspace and not a
replacement for Phase 4b score-shape validation.](figures/expected_s_over_b.pdf){#fig:p4a-sob}

## Systematics

Every implemented systematic is either sourced from the normalization metadata
or bound by the Phase 1/user open-data strategy. No arbitrary post-hoc
background inflation was introduced.

| Source | Conventions | CMS 2014 | CMS 2018 | This | Status |
| --- | --- | --- | --- | --- | --- |
| Signal cross-section theory | required | scale/PDF/UE/PS | signal theory and acceptance | normalization source recorded; dedicated theory NP downscoped | downscoped |
| Signal acceptance/shape | required | tau/JES/MET/generator shape | shape uncertainties in categories | tau/open-data acceptance rate NP only | partial |
| Luminosity | pp normalization source | 2.6% at 8 TeV | luminosity NP | 2.6% normsys on MC-normalized samples | implemented |
| DY/Z normalization | background normalization | inclusive Z plus category extrapolation | DY control constraints | 15% normsys on DYJetsToLL | implemented |
| Tau ID/trigger/open-data acceptance | object calibration | tau ID/trigger range in reference table | tau ID/trigger effects | 15% correlated rate NP | implemented |
| MC statistics | required | limited event counts | bin-by-bin MC stat | per-category Barlow-Beeston-lite staterror modifiers | implemented |
| QCD multijet | background normalization and shape | data-driven estimate | data-driven estimate | missing reduced sample; sideband deferred to data-validation phases | downscoped |
| W+jets transfer/control | background normalization | high-mT control region | mT control region | expected high-mT control-region normalization method prepared; real-data central value deferred to Phase 4b | partial |
| Diboson and single top | analogous pp electroweak backgrounds | included | included | no reduced samples; omitted with explicit limitation | downscoped |

![Expected nuisance summary. This figure ranks implemented rate and MC-stat
uncertainty handles by the nominal size available in the Phase 4a workspace.
It is an expected-model diagnostic, not a post-fit impact plot from observed
data.](figures/expected_nuisance_summary.pdf){#fig:p4a-nuisance-summary}

## Expected Result

The pyhf asymptotic CLs calculation gives an expected 95% upper limit of
`2.904` on `mu` for the background-only
Asimov dataset. The scan range was 0 to 50, and the POI bound in the workspace
is also 0 to 50. The expected discovery-sensitivity diagnostic status is
`evaluated`.

## Validation

Signal injection was evaluated at 0x, 1x, 2x, and 5x nominal signal using
Asimov pseudo-data generated by the nominal workspace. The recovery gate is a
20% relative-bias requirement for nonzero injections and a near-zero absolute
bias requirement for the 0x injection.

| Injected mu | Fitted mu | Abs. bias | Rel. bias | Pass |
| --- | --- | --- | --- | --- |
| 0.0 | 0.0008 | 0.000777 | 0 | True |
| 1.0 | 1.0000 | -7.25e-09 | -7.25e-09 | True |
| 2.0 | 2.0018 | 0.00179 | 0.000897 | True |
| 5.0 | 5.0009 | 0.00094 | 0.000188 | True |

![Signal-injection recovery. This figure compares the injected and fitted
signal strength in Asimov pseudo-data. The points lie on the diagonal within
the predeclared tolerance, showing that the workspace can recover injected
signals under its own nominal assumptions.](figures/signal_injection_recovery.pdf){#fig:p4a-injection}

The GoF toy study uses `500` Poisson toys generated from the
background-only expected templates and a saturated-statistic calculation. The
combined Asimov saturated statistic is `0.000`,
and the fraction of toys with statistic greater than or equal to the Asimov
value is `1.000`. Because
Asimov data equal the model expectation by construction, this is a toy
generation and plumbing validation rather than an independent closure test.

![Limited toy GoF distribution. This figure shows the saturated-statistic
distribution for Poisson toys drawn from the expected background model. The
Asimov statistic is marked at zero by construction, so the plot checks the toy
machinery but does not validate agreement with real data.](figures/gof_toys.pdf){#fig:p4a-gof-toys}

## Limitations and Downscopes

The broad raw Phase 3 background-only templates were not final
closure-validated fit predictions until normalization, missing-background
treatment, QCD/control-region constraints, and nuisance modelling were added.
Phase 4a adds official normalization, pyhf nuisance structure, and MC-stat
terms, but it does not solve all paper-level missing inputs.

The following missing or deferred components are carried to the analysis note:
embedded Z to tau tau, QCD multijet, diboson WW/WZ/ZZ, single top, W4 or
inclusive W+jets, associated WH/ZH/ttH, H to WW, additional DY categories, and
other TauPlusX eras. They are not silently approximated in the Phase 4a
workspace. The machine-readable details are in
`outputs/limitations_downscope.json`, with 16
manifest entries.

## Code Reference

Reproduce this executor output with:

| Command | Purpose |
|---|---|
| `pixi run phase4a-model` | Build weighted templates, pyhf workspace, expected fits, systematics, limitations, and this markdown artifact. |
| `pixi run phase4a-plots` | Render Phase 4a figures from machine-readable outputs only. |
| `pixi run phase4a-validate` | Validate JSON files, NPZ contents, pyhf workspace construction, figures, and blinding flags. |
| `pixi run phase4a-all` | Run the full Phase 4a executor chain. |

## Machine-Readable Outputs

- `outputs/templates.npz`
- `outputs/nominal_yields.json`
- `outputs/pyhf_workspace.json`
- `outputs/expected_results.json`
- `outputs/systematics.json`
- `outputs/signal_injection.json`
- `outputs/gof_validation.json`
- `outputs/limitations_downscope.json`
