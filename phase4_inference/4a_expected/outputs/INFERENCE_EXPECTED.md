# Phase 4a Expected Inference: CMS 2012 Open Data H to Tau Tau Search

## Summary

Phase 4a builds an expected-only binned pyhf model for the reduced CMS 2012
Open Data H to tau tau search in the mu tau_h final state. The model uses the
Phase 3 visible-mass baseline in three mutually exclusive categories: VBF,
boosted/1-jet, and zero-jet. The observation is background-only Asimov
pseudo-data from the nominal model, so no real data signal-region distribution
or full-data observed fit result enters this phase.

The expected 95% CLs upper limit on the signal strength is
`11.374` on the background-only Asimov
sample. The median expected band from pyhf is `11.374`, with minus-one
and plus-one variations `7.958` and `16.472`. These are
single-channel reduced-open-data expectations and are not directly comparable
to the CMS all-channel Run 1 results without the missing components and
calibrations listed below.

## Method

The primary observable is visible mass, `m_vis`, with bin edges
`[0.0, 40.0, 60.0, 80.0, 100.0, 120.0, 160.0, 250.0]` GeV. The Phase 4a executor uses
`phase3_selection/outputs/selected_events.npz`, requiring `is_signal_region`
and the exclusive `category` labels `vbf`, `boosted`, and `zero_jet`. The
Phase 3 `region_exclusive` diagnostic labels are not used to form the fit
templates.

MC normalization follows `phase3_selection/outputs/normalization_inputs.json`.
Signal weights use `sigma_prod * BR(H->tautau) * L_int / N_gen`, and
background weights use `sigma * L_int / N_gen`, with `L_int = 11467/pb`. The
MC denominators are official CERN Open Data `distribution.number_events`
values, not local reduced ROOT entries or selected counts.

The workspace is written to `outputs/pyhf_workspace.json`. It includes a common
signal-strength POI `mu`, luminosity and tau/open-data acceptance normsys
modifiers, a DY normalization normsys, and per-category Barlow-Beeston-lite
staterror modifiers. The observation in the workspace is the background-only
Asimov expectation in each category.

## Expected Yields

| Category | Signal yield | Background yield | S/sqrt(B) | Minimum background bin |
| --- | --- | --- | --- | --- |
| vbf | 1.590 | 144.926 | 0.132 | 10.141 |
| boosted | 9.170 | 2093.690 | 0.200 | 101.333 |
| zero_jet | 14.341 | 7060.345 | 0.171 | 74.130 |

![Expected visible-mass templates in the VBF category. This figure shows the
Phase 4a background-only expected stack and nominal Higgs signal overlay after
official Open Data normalization. The observation used by the fit is the
Asimov background expectation rather than real collision data.](figures/expected_mvis_vbf.pdf){#fig:p4a-mvis-vbf}

![Expected visible-mass templates in the boosted category. This figure shows
the non-VBF one-or-more-jet category used in the simultaneous expected fit. The
category has the largest nonzero Higgs yield outside zero-jet, but the expected
background remains much larger than the signal.](figures/expected_mvis_boosted.pdf){#fig:p4a-mvis-boosted}

![Expected visible-mass templates in the zero-jet category. This figure shows
the DY-dominated category retained from Phase 3. It mainly constrains the
background shape and normalization in the simplified reduced-sample model,
while contributing limited Higgs discrimination.](figures/expected_mvis_zero_jet.pdf){#fig:p4a-mvis-zero}

![Expected signal-to-background ratio by category. This figure summarizes the
category-integrated nominal Higgs signal divided by the nominal background.
The VBF category has the best relative signal purity, but the absolute signal
yield is still small in the reduced sample.](figures/expected_s_over_b.pdf){#fig:p4a-sob}

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
| W+jets transfer/control | background normalization | high-mT control region | mT control region | W1/W2/W3 MC only in expected SR model; real-data CR deferred | downscoped |
| Diboson and single top | analogous pp electroweak backgrounds | included | included | no reduced samples; omitted with explicit limitation | downscoped |

![Expected nuisance summary. This figure ranks implemented rate and MC-stat
uncertainty handles by the nominal size available in the Phase 4a workspace.
It is an expected-model diagnostic, not a post-fit impact plot from observed
data.](figures/expected_nuisance_summary.pdf){#fig:p4a-nuisance-summary}

## Expected Result

The pyhf asymptotic CLs calculation gives an expected 95% upper limit of
`11.374` on `mu` for the background-only
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
| 0.0 | 0.0000 | 0 | 0 | True |
| 1.0 | 1.0000 | 0 | 0 | True |
| 2.0 | 1.9989 | -0.00113 | -0.000564 | True |
| 5.0 | 4.9992 | -0.000769 | -0.000154 | True |

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
