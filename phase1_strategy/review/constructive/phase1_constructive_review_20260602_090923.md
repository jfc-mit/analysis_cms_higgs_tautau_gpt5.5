# Phase 1 Constructive Review

Review role: constructive reviewer  
Artifact: `phase1_strategy/outputs/STRATEGY.md`  
Verdict: ITERATE

## Headline

The strategy is a credible Phase 1 basis: it correctly treats the prompt as a search/template-fit analysis, identifies the main H to tau tau backgrounds, commits to a simultaneous category fit including VBF, includes the user-requested NN/add-MET alternatives, and maps the search convention systematic sources. I do not find a Category A physics blocker in the current strategy.

However, several obligations are still too qualitative for a binding Phase 1 artifact. The most important fixes are to make the final comparison program explicit enough to satisfy the user's "comprehensive comparisons" request, to define quantitative pass/fail gates for the NN and missing-energy alternatives, and to specify control-region/validation logic before Phase 3 starts optimizing.

## Findings

### B1. The comparison targets are not yet specific enough for the user's comprehensive CMS/PDG comparison request.

Evidence from the artifact:

- The user prompt asks the final AN to "compare the final results with published results as comprehensively as the available ntuples and this analysis scope allow" and to include "previous-study results and PDG/world-average" where available.
- The strategy lists comparison references and a few global numbers: CMS 2014 `mu = 0.78 +/- 0.27` and significance language, CMS 2018 observed/expected significance and `mu = 1.09 +0.27/-0.26`, and ATLAS+CMS combined values in the reference table (`STRATEGY.md` lines 359-365).
- The fit output list only says "Comparisons to CMS JHEP 05 (2014) 104, CMS Phys. Lett. B 779 (2018) 283, and ATLAS+CMS..." (`STRATEGY.md` lines 161-170). The flagship figure list similarly says "Final signal-strength/limit/significance summary compared with CMS 2014, CMS 2018, and ATLAS+CMS..." (`STRATEGY.md` lines 372-389).

Why this weakens the strategy:

Methodology requires Phase 1 to extract published numerical results that become binding comparison targets before Phase 4a. The current table has useful anchor numbers, but it does not define the comprehensive comparison matrix the user requested. A later note writer would still have to decide what "meaningfully comparable" means. That decision should be made now.

Required fix:

Add a binding comparison-target table that enumerates every final AN comparison planned, with status and reason. At minimum include:

- This analysis's primary outputs: expected/observed `mu`, expected/observed significance, expected/observed CLs upper limit if sensitivity is weak, category yields, per-category post-fit signal/background summaries, nuisance impact ranking, and VBF/inclusive category sensitivity.
- CMS 2014 comparators: global Run 1 H to tau tau `mu` and significance, any published mu-tauh or category-specific yields/plots that can be numerically extracted, and explicit "not comparable" rows for all-channel or SVFit-only results outside this reduced scope.
- CMS 2018 comparators: 13 TeV `mu`, expected/observed significance, category/control-region method comparisons, with a clear label that the collision energy and luminosity differ.
- PDG/world-average comparators where meaningful: Higgs mass used as fixed input, H to tau tau branching fraction or coupling/signal-strength summaries if the final AN interprets `mu`, and an explicit "not applicable" row if no PDG/world-average value maps cleanly to the reduced open-data search result.

### B2. The NN and missing-energy alternatives need predeclared quantitative failure gates, not only qualitative caveats.

Evidence from the artifact:

- The strategy defines an NN discriminator, NN MET-direction regression, add-MET mass, and baseline visible mass (`STRATEGY.md` lines 148-158, 237-244).
- It acknowledges the right risks: mismodelled inputs, generator dependence, truth leakage, unphysical regression on unavailable gen-level features, and W/top mass sculpting (`STRATEGY.md` lines 242-244).
- The main rejection rule is qualitative: if an NN wins expected sensitivity but fails the MVA input modelling gate, it will not become primary until problematic inputs are calibrated or removed (`STRATEGY.md` lines 246-248).

Why this weakens the strategy:

This is close but not yet audit-ready. The user explicitly requested NN and missing-energy approaches, so the final AN must be able to conclude honestly if they fail validation. Without predeclared thresholds, Phase 3/4 can drift into subjective "good enough" decisions after seeing results.

Required fix:

Add a binding "alternative observable acceptance gates" table. Suggested gates:

- NN classifier: all inputs must have Phase 2 data/MC `chi2/ndf <= 5` or documented calibration/removal; train/test split and independent MC closure must be reported; signal injection recovery bias must be below the search-convention 20% threshold; systematic-shifted score templates must remain physically ordered and non-degenerate.
- NN MET regression: training target and allowed inputs must be stated so gen-level leakage is impossible; if genMET direction/phi or generator neutrinos are absent, the method is formally downscoped before training; mass resolution improvement over `m_vis` must be quantified on independent MC; generator/MET/tau/jet variations must not produce an unexplained dominant shape shift.
- Add-MET mass: require a W/top sculpting check, MET scale/resolution stress test, and comparison to `m_vis` with a common expected-sensitivity metric.
- All alternatives: if validation fails, preserve diagnostic figures and report the method as "tested and rejected" rather than quietly removing it from the AN.

### B3. Control-region and validation-region definitions are too under-specified for W, QCD, and top.

Evidence from the artifact:

- W+jets normalization is committed to a high-`mT` control region (`STRATEGY.md` lines 125-126 and 264-277).
- QCD is planned through same-sign and anti-isolation sidebands if available (`STRATEGY.md` lines 111-113, 190-192, 202).
- Top validation is planned with a b-tagged sideband if branches exist (`STRATEGY.md` lines 203, 229-231, 259-261).
- The required validation plan says W high-`mT`, QCD sidebands, top-enriched, and Z-rich categories must pass quantitative tests where statistics permit (`STRATEGY.md` lines 338-354).

Why this weakens the strategy:

The strategy identifies the right regions but does not yet define the region taxonomy, orthogonality, transfer-factor checks, or fallback rules. Search conventions warn that validation regions must cover the interpolation between CRs and SRs, and that unstable transfer factors are a pitfall. This matters here because W+jets, QCD fakes, and top are exactly the backgrounds most likely to bias a reduced open-data mu-tauh search.

Required fix:

Add a region-definition table before Phase 2/3 with:

- SR, W CR, W VR, QCD same-sign CR, QCD anti-isolation CR/VR, top CR/VR, and Z-rich VR.
- Selection differences relative to SR: charge, tau isolation/ID, `mT`, b-tag, jet/VBF requirements, and whether the region enters the likelihood or only derives a nuisance prior.
- Expected dominant process, subtraction method, transfer factor, closure metric, and pass/fail threshold.
- Explicit orthogonality rules so the same event cannot enter incompatible regions.
- Fallbacks if b-tag, tau isolation, same-sign statistics, or QCD samples are absent.

### B4. The statistical convention commitments should explicitly include CLs, test-statistic, and low-statistics toy validation triggers.

Evidence from the artifact:

- The strategy says the fit will use a binned profile likelihood, pyhf/HistFactory, MC-stat terms, best-fit `mu`, local significance, and upper limits if sensitivity is inadequate (`STRATEGY.md` lines 57-63, 161-168, 132-133).
- The approach comparison metric mentions expected `mu` uncertainty, expected CLs limit, or expected discovery significance (`STRATEGY.md` lines 234-238).
- The GoF plan says toy-based checks are used if asymptotic assumptions are questionable (`STRATEGY.md` lines 353-354).

Why this weakens the strategy:

The search convention requires modified frequentist CLs for upper limits, one-sided profile-likelihood statistics, and toy validation or toy limits when low statistics make asymptotics questionable. The strategy is compatible with this, but the commitments are scattered and not explicit enough to bind Phase 4 implementation.

Required fix:

Add a short "statistical configuration" subsection:

- Upper limits use modified CLs, not simple CL_s+b.
- Discovery significance uses one-sided `q0` with `q0 = 0` when `mu_hat < 0`.
- Limits use a one-sided profile-likelihood ratio with `mu >= 0`.
- Any final SR/category bin with expected count below about 5 triggers toy validation of asymptotic limits/significances or direct toy-based inference.
- GoF reports per-region `chi2/ndf` plus a toy-based combined p-value when the asymptotic approximation is suspect.

### C1. Add a compact commitments table for Phase 4 traceability.

The strategy already labels decisions [D1]-[D9], limitations [L1]-[L4], and open issues [O1]-[O5]. To make later reviews less error-prone, add a table mapping each decision/limitation to the phase where it must be resolved and the artifact section expected to close it. This is not a blocker, but it would help the arbiter enforce Phase 1 traceability.

### C2. Strengthen the anti-tuning language around the 10-15% tau and DY uncertainties.

The strategy correctly says the 10-15% tau and DY/Z uncertainties are predeclared limitations, not tuning knobs (`STRATEGY.md` lines 106-109, 323-336). It would be stronger to add a concrete honesty check: if these enlarged uncertainties make all Z/DY validation pulls less than 0.5 sigma, Phase 4 must investigate whether the uncertainty is inflated rather than declaring validation passed.

## Review Questions Answered

- Conventions coverage: The systematic source enumeration covers the search convention rows and adapts LEP-specific rows to pp equivalents. The missing pieces are statistical-configuration specificity and more detailed validation-region design, classified above as B rather than A.
- Reference analyses: Three references are tabulated with systematics and global numbers. The comparison target list is not comprehensive enough for the user request, hence B1.
- Competing group risk: A competing analysis would likely have a clearer table of comparable CMS/PDG targets and a stricter validation protocol for MVA/missing-energy observables. Those are fixable in Phase 1.
- Honest uncertainty framing: The strategy explicitly warns not to tune 10-15% uncertainties to the Drell-Yan peak. It should add an inflation check so large uncertainties do not make validation vacuous.

## Recommendation

ITERATE Phase 1. No strategy rewrite is needed, but the executor should add the four Category B clarifications before the arbiter considers PASS.
