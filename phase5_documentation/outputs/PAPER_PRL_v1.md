# A CMS Open Data Search for H to Tau Tau in the Mu Tau_h Final State

## Abstract

A reduced CMS 2012 Open Data search for Higgs boson decays to tau pairs is
performed in the `mu tau_h` final state. The final result is a visible-mass
template fit in VBF, boosted, and zero-jet categories. The fit finds
`mu = 0.438 +4.944
-0.438` and sets an observed 95% CLs upper limit
`mu < 10.764`, with median expected limit
`mu < 10.738`. The result is a low-sensitivity Open Data limit, not
evidence for a Standard Model-strength signal.

## Data and Method

The analysis uses public Run2012B/C TauPlusX reduced data and the available
ggH, VBF, DY, ttbar, and W+jets simulation samples from the CMS Open Data
Higgs-to-tau-tau reduced mirror [@cms_open_data_htt_2012]. Events pass the
muon plus hadronic-tau trigger, tight muon and tau selections, opposite-sign
charge, and a low-transverse-mass signal-region requirement. The statistical
model is a simultaneous binned pyhf/HistFactory likelihood with a common
signal-strength modifier `mu` [@pyhf_joss].

## Background Model

W+jets is constrained by a high-`mT` control region, VBF-category MC
backgrounds are scaled by a VBF-like non-signal control region, and the
reducible QCD/fake contribution is estimated from same-sign low-`mT` data
after non-QCD subtraction. The systematic model includes luminosity,
tau/open-data acceptance, DY/Z normalization, W and VBF control terms,
same-sign QCD transfer, and MC statistical uncertainties.

| Category | Data | Background | Signal | Chi2/ndf |
|---|---:|---:|---:|---:|
| VBF | 78 | 96.28 | 1.590 | 1.449 |
| Boosted | 2183 | 2364.39 | 9.170 | 0.605 |
| Zero-jet | 8451 | 8456.81 | 14.341 | 0.113 |

![Final visible-mass CLs limit summary. The expected band and observed marker
show that the reduced Open Data analysis has no Standard Model resolving
power.](figures/phase5_baseline_limit_summary.pdf){#fig:prl-limit}

![Visible-mass validation in the VBF category. This category has the largest
local residual tension but does not invalidate the combined weak-limit
interpretation.](figures/phase5_baseline_visible_vbf.pdf){#fig:prl-vbf}

## Result and Interpretation

The combined visible-mass validation gives data/background =
0.981 and chi2/ndf =
0.722. The optimized classifier study has
better expected sensitivity but fails its observed validation gate
(`fail`), so it is not used as a final result. Published CMS and
ATLAS+CMS H to tau tau analyses use more channels and fuller calibration
programs; this reduced analysis should be read as a reproducibility-oriented
Open Data limit [@cms_htt_2014; @cms_htt_2018; @atlas_cms_higgs_combination_2016].

## References

This markdown draft uses the same bibliography file as the final analysis note:
[@cms_open_data_htt_2012; @cms_htt_2014; @cms_htt_2018; @atlas_cms_higgs_combination_2016;
@pyhf_joss; @read_cls; @cowan_asymptotic].
