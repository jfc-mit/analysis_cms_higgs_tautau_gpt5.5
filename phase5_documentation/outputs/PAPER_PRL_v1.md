---
title: "Search for Higgs boson decays to tau pairs in the muon plus hadronic-tau final state with CMS Open Data"
author: "Analysis my_analysis"
date: "2026-06-13"
---

# Abstract

A search for Standard Model Higgs boson decays to tau pairs is performed in the
$\mu\tau_h$ final state using the localized CMS 2012 TauPlusX Open Data and
simulation samples. Events are split into VBF, boosted, and zero-jet categories
and interpreted with binned pyhf/HistFactory likelihoods. The visible-mass
baseline gives $\hat{\mu}=2.474^{+3.452}_{-2.474}$,
an observed 95% CLs upper limit $\mu<5.926$, and a
median expected limit $\mu<3.692$. The retained $D_{NN}$ classifier
score gives $\hat{\mu}=1.616^{+1.961}_{-1.616}$,
an observed 95% CLs upper limit $\mu<3.577$, and a
median expected limit $\mu<1.807$.

# Introduction

The CMS Run-1 analysis in JHEP 05 (2014) 104 and the later combined measurement
in Phys. Lett. B 779 (2018) 283 use multiple final states, full detector
calibrations, and embedded background methods. This reduced Open Data analysis
keeps the central structure needed for a reproducible single-channel search:
category splitting, control-derived background constraints, and a simultaneous
binned likelihood for the signal-strength modifier $\mu$.

# Data, Selection, And Model

The analysis uses Run2012B and Run2012C TauPlusX data and the available ggH,
VBF, DY+jets, top-pair, and W+jets simulation samples. Events are selected with
one muon and one hadronic-tau candidate and are divided into VBF, boosted, and
zero-jet categories. The baseline observable is $m_{vis}$; the multivariate
observable is the XGBoost classifier score $D_{NN}$ in 20 uniform bins.

# Results

The visible-mass baseline gives $\hat{\mu}=2.474^{+3.452}_{-2.474}$
and $\mu<5.926$ at 95% CLs. The $D_{NN}$ result gives
$\hat{\mu}=1.616^{+1.961}_{-1.616}$
and $\mu<3.577$ at 95% CLs.

![Observed signal-strength summary for the visible-mass baseline, $D_{NN}$
result, CMS 2014 result, and CMS 2018 result. Each row uses black observed
points with horizontal uncertainties, green and yellow expected one- and
two-standard-deviation bands, a black dashed median-expected marker, and the
common Standard Model line at $\mu=1$.](figures/observed_limit_significance_summary.pdf)

# Discussion

The $D_{NN}$ observable has the smaller median expected upper limit and is
therefore the more sensitive of the two retained tools in this rerun. The
analysis is statistically limited and remains substantially weaker than the
published multi-channel CMS results, but it demonstrates a complete Open Data
template-fit chain with explicit machine-readable workspaces.
