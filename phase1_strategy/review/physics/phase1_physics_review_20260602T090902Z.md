# Phase 1 Physics Review: H to Tau Tau Strategy

Reviewer: Physics reviewer  
Timestamp: 2026-06-02T09:09:02Z  
Artifact: `phase1_strategy/outputs/STRATEGY.md`  
Physics prompt: `prompt.md`

## Headline Verdict

**ITERATE: physically credible strategy, but not yet an unconditional physics PASS.**

The strategy is recognizably a CMS Run 1-style $H \to \tau\tau$ search in the
$\mu\tau_h$ channel: it identifies the dominant backgrounds, commits to a
profile-likelihood template fit, includes VBF categorization, treats W+jets
with a high-$m_T$ normalization region, and acknowledges the limitations of
reduced CMS Open Data and missing trigger/tau scale factors. I would not yet
approve it without clarification of the mutually exclusive category structure
and the NN genMET-regressed mass observable, because both affect the core fit
definition.

There is no Phase 1 PDF and no Phase 1 figure set to inspect.

## Findings

### (B) The simultaneous-fit category definition is not yet unambiguous enough for approval

**Evidence from artifact:** The strategy says the final result is a
"simultaneous profile-likelihood shape fit across mutually exclusive event
categories, including a VBF-enriched category." It later defines the minimum
structure as "Baseline inclusive $\mu\tau_h$" and "VBF-enriched", with
additional "0-jet" and "Boosted/1-jet" categories if statistics permit.

**Physics concern:** A simultaneous fit cannot include an inclusive category
and a VBF category populated by the same events unless the statistical model
explicitly handles correlations, which a standard binned category fit normally
does not. The strategy probably intends "inclusive baseline" as the
non-VBF/default signal region, but the wording leaves overlap possible. This
matters because duplicate events would inflate sensitivity and distort
nuisance constraints.

**Required resolution:** Define the Phase 3 category hierarchy explicitly as
mutually exclusive, for example VBF first, then boosted/1-jet, then 0-jet or
non-VBF baseline. If a truly inclusive distribution is retained, label it as a
diagnostic plot only, not an input to the simultaneous likelihood.

### (B) The NN genMET-regressed mass observable needs a physically complete definition before approval

**Evidence from artifact:** The requested alternative (b) is implemented as
"$m_\mathrm{NNMET}$: combined mass built from visible objects and an NN
regression of genMET direction/phi." The strategy also flags risks: "truth
leakage, generator dependence, and unphysical regression on unavailable
gen-level features", and lists open issue [O5]: whether genMET direction/phi
is present.

**Physics concern:** A mass observable cannot be fully specified by only the
missing-momentum direction or $\phi$ unless the missing-momentum magnitude is
defined elsewhere. If the plan is to use reconstructed MET magnitude with an
NN-regressed direction, that should be stated. If the plan is to regress
generator-level missing momentum and use it in data, that is not a physical
observable unless the network input set is strictly reconstructed quantities
and the data application is clearly defined. This observable will be highly
model-dependent and could sculpt signal-like mass structure if trained
against Higgs simulation without strong background and closure tests.

**Required resolution:** Specify the exact four-vector construction:
which magnitude is used, whether the NN predicts $\phi$ only or both
direction and magnitude, which reconstructed inputs are allowed, and how the
observable is validated on independent simulation and data control regions.
The strategy should also state that this approach cannot become primary if it
fails closure, background modelling, or signal-injection tests, even if it has
better MC-only sensitivity.

### (B) The W+jets normalization plan is credible but should require an explicit purity and transfer-factor validation before use in the signal fit

**Evidence from artifact:** The strategy commits that "W+jets will be
normalized from data using a high-$m_T$ control region", with non-W
subtraction and a high-to-low-$m_T$ transfer uncertainty. It cites the CMS
use of $m_T>80$ GeV as a reference and states that the open-data uncertainty
will be derived from available validation.

**Physics concern:** This is the right physics idea, but in the reduced
sample list the W+jets samples are split only into W1/W2/W3 jets, and the
strategy has not yet required a quantitative high-$m_T$ purity threshold or a
closure test of the transfer factor across jet/VBF categories. This is
especially important because the VBF region can have different W+jets
composition and top contamination than the inclusive low-jet region.

**Required resolution:** Add an explicit Phase 3/4 requirement to report W CR
purity after non-W subtraction, derive or validate transfer factors separately
for the categories used in the fit where statistics allow, and assign a larger
category-extrapolation uncertainty when the VBF transfer is statistics-limited.

### (C) The treatment of QCD/multijet is acceptable for Phase 1 but should be made less conditional downstream

**Evidence from artifact:** The strategy says QCD/multijet should be handled
with "same-sign and anti-isolation data sidebands" and, if unavailable, as a
downscoped instrumental background with a conservative data-constrained
uncertainty. It also lists QCD samples or data sideband handles as Phase 2
items to search for.

**Physics comment:** This is a reasonable Phase 1 plan. However, QCD fakes can
be non-negligible in $\mu\tau_h$, and the final search will be hard to approve
if QCD is effectively omitted. The same-sign and anti-isolated handles should
be treated as a central background-estimation path, not only as a fallback.

### (C) The reference-comparison framing is honest, but the strategy should emphasize single-channel sensitivity limits whenever quoting all-channel numbers

**Evidence from artifact:** The strategy tabulates CMS JHEP 05 (2014) 104,
CMS Phys. Lett. B 779 (2018) 283, and the ATLAS+CMS Run 1 combination, and
states that these are "comparison anchors" rather than pass/fail
expectations.

**Physics comment:** This is physically meaningful. CMS JHEP 05 (2014) 104 is
the closest Run 1 methodological reference. The 13 TeV observation paper and
ATLAS+CMS combination are useful but less directly comparable because of
energy, luminosity, channels, and reconstruction differences. The current
wording already acknowledges this; downstream tables should not visually
imply that a single-channel open-data $\mu\tau_h$ result is expected to match
the all-channel CMS/combined sensitivities.

## Requested Focus Checks

- **Physically sound $H \to \tau\tau$ search strategy:** Mostly yes. The
profile-likelihood template fit, $\mu\tau_h$ final state, visible-mass
baseline, and Higgs signal-strength/limit/significance outputs are sound for
CMS 2012 Open Data.
- **Backgrounds and control regions:** Credible at Phase 1. DY, W+jets, QCD,
ttbar, diboson/single-top, and Z to mu mu fakes are correctly identified.
W+jets and QCD need concrete validation in later phases.
- **VBF categorization and simultaneous fit:** Directionally adequate, but the
category exclusivity ambiguity is a blocking physics clarity issue before
PASS.
- **Four requested final observables:** Baseline visible mass, NN
discriminator, and add-MET mass are coherently planned. The NN genMET mass
requires a sharper physical definition and closure strategy.
- **Mandated tight anti-muon veto:** Handled honestly through [D5] and fake
background validation.
- **Mandated W+jets high-$m_T$ normalization:** Included and physically
appropriate, with a needed purity/transfer-factor validation requirement.
- **Loosened tau efficiency and 10-15% Z normalization uncertainty:** Treated
honestly as pre-declared limitations, not post-hoc tuning knobs. The strategy
explicitly says these uncertainties must not make validation pulls trivially
small.
- **Reference comparisons:** Meaningful, provided they remain framed as
limited-comparability anchors.

## Publication-Approval Summary

I would approve this strategy after iteration on the two main fit-definition
issues: mutually exclusive categories and the NN genMET mass construction.
The rest of the strategy is appropriately skeptical about reduced Open Data,
missing scale factors, and simplified mass reconstruction, and it gives
credible downstream validation hooks for the dominant physics risks.
