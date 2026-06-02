# Phase 1 Critical Review

Reviewer: critical
Timestamp: 20260602T091011Z
Artifact: `phase1_strategy/outputs/STRATEGY.md`

## Headline Verdict

ITERATE. The strategy correctly resolves the scaffold measurement/search mismatch and contains a credible search/template-fit plan, but it does not yet fully satisfy Phase 1 convention coverage. One pp-specific required systematic source from `conventions/search.md` is missing from the row-by-row enumeration, and several downstream commitments are not concrete enough to be reliably audited in Phase 3/4.

## Findings

### A1. Missing pp-specific pileup systematic in the search convention enumeration

Classification: (A) must resolve

Evidence:

- `conventions/search.md` states that for pp collider searches, beam-related sources should be replaced with "pp-specific equivalents (PDF, pileup)" and luminosity should be added as a normalization source (lines 45-48).
- The strategy's search convention table enumerates signal cross-section, signal acceptance, signal shape, ISR replacement, 4-fermion replacement, background normalization/shape, qqbar(gamma) replacement, MC statistics, detector simulation, object calibration, beam energy, luminosity, QCD scale, fragmentation, and heavy-flavour treatment (strategy lines 290-309).
- In that enumeration, pileup is neither marked "Will implement" nor "Not applicable because ...". The closest rows are detector simulation model and object calibration (strategy lines 303-304), but neither names pileup, pileup reweighting, pileup profile mismodelling, or a justification for omitting it.
- Phase 1 methodology requires the strategy to enumerate every required systematic source with "Will implement" or "Not applicable because [reason]" (methodology lines 224-226), and review methodology says Phase 1 omissions without justification are Category A (review methodology lines 301-304).

Required fix:

Add an explicit pileup row or pp detector-environment row to the search convention enumeration. It must say either "Will implement" with the intended pileup profile/weight variation or "Not applicable" with evidence that the reduced 2012 Open Data samples do not contain usable pileup information and that pileup effects are covered by another named source without double counting.

### B1. Search statistical configuration is under-specified for limits and significance

Classification: (B) should address before PASS

Evidence:

- `conventions/search.md` requires the modified frequentist CLs method for upper limit calculations (lines 22-25), defines when asymptotic approximations are acceptable and when toys are needed (lines 26-29), and specifies one-sided profile-likelihood test statistics for limits and discovery significance (lines 30-34).
- The strategy commits to a binned profile likelihood and pyhf/HistFactory workspace (strategy lines 59-63 and 134-135), expected and observed significance (lines 164-165), and upper limits if sensitivity is inadequate (lines 166-167).
- It does not explicitly bind the limit calculation to modified CLs, the discovery test to one-sided `q_0`, the upper-limit test to `mu >= 0`, or the asymptotic/toy threshold except for a general GoF statement that toy checks are used "if asymptotic assumptions are questionable" (strategy lines 353-354).

Why this matters:

The strategy will later be used to audit Phase 4. Without explicit statistical-test commitments, a Phase 4 executor could produce a pyhf fit but use a different limit convention or omit low-statistics toy validation while still appearing to satisfy the broad "profile likelihood" wording.

Required fix:

Add a short statistical configuration commitment: modified CLs for limits, one-sided `q_0` for discovery, `mu >= 0` for limit tests, asymptotic formulae only when bin counts satisfy the convention threshold, and toy validation or toys directly for low-statistics final bins.

### B2. Reference numerical targets are too global for later single-channel and category-level validation

Classification: (B) should address before PASS

Evidence:

- Phase 1 methodology requires 2-3 reference analyses, their systematic programs, and extracted published numerical results that become binding comparison targets (methodology lines 227-233).
- The strategy provides three references and global comparison numbers: CMS 2014 integrated luminosities, all-channel best-fit signal strength, and broad local significance statement (strategy line 363); CMS 2018 observed/expected significance and all-channel signal strength (line 364); ATLAS+CMS combined signal yield and H to tau tau significance (line 365).
- The analysis itself is explicitly downscoped to the `mu tau_h` final state (strategy lines 51-55 and 97-98), with baseline and VBF-enriched categories (strategy lines 209-219). The reference table does not extract channel/category-level targets such as `mu tau_h` yield or significance anchors, category definitions with thresholds used as comparison targets, or published control-region/background-normalization values that would let Phase 3/4 check whether this single-channel implementation is in the right regime.
- The strategy does plan final comparisons and quantitative explanations (strategy lines 367-370 and 443-446), but those are broad obligations rather than concrete Phase 1 numerical targets.

Why this matters:

A later result could be far from the expected single-channel sensitivity while still being "consistent" with broad all-channel Run 1/Run 2 numbers. The current targets are useful context, but not sufficient for a reviewer to assess whether the `mu tau_h` category selection and fit are reproducing the relevant reference-analysis scale.

Required fix:

Add at least two single-channel or category-level numerical targets from the CMS H to tau tau references where available: e.g. `mu tau_h` category yield/selection targets, VBF selection/category thresholds and expected sensitivity anchors, W/QCD/top control-region normalization uncertainty targets, or channel-specific signal-strength/significance values. If the publications do not provide a requested target in a directly extractable form, state that explicitly and identify the closest available comparison.

### B3. Phase 3/4 comparison criteria for alternative observables need pass/fail thresholds

Classification: (B) should address before PASS

Evidence:

- The strategy correctly commits four approaches: baseline visible mass, NN discriminator, NN MET-direction regression, and add-MET mass (strategy lines 239-244). This satisfies the Phase 1 requirement to identify at least two approaches and includes the requested NN approaches.
- The comparison criteria are qualitative or metric families: expected sensitivity, data/MC quality, MC closure, signal injection, mass resolution comparison, and robustness checks (strategy lines 235-244).
- The strategy has one clear MVA veto principle: an NN approach cannot become primary if it wins expected sensitivity but fails input-modelling gates (strategy lines 246-248). However, it does not set concrete pass/fail thresholds for selecting the primary observable, such as maximum allowed input `chi2/ndf`, required signal-injection bias, minimum expected-sensitivity improvement needed to replace `m_vis`, or how to choose if an NN improves sensitivity but worsens GoF/control-region agreement.
- Phase 3 review methodology already contains a concrete MVA input red flag: classifier inputs with data/MC `chi2/ndf > 5` are Category A unless justified or calibrated (review methodology lines 182-186). The strategy does not import that threshold into its binding comparison plan.

Why this matters:

Without thresholds, Phase 3 can rationalize a preferred observable after seeing many diagnostics. The strategy should pre-bind the decision rule tightly enough that the Phase 3 reviewer can audit whether the primary observable was chosen by evidence rather than by narrative.

Required fix:

Add explicit decision thresholds for the approach comparison. At minimum, bind the MVA input gate to the review threshold (`chi2/ndf > 5` requires calibration/removal/justification), require signal injection bias below the search convention threshold, require acceptable GoF/control-region closure for any primary candidate, and define how large an expected-sensitivity gain is needed before replacing `m_vis`.

### C1. Decision label traceability can be improved by listing D9 in the Decisions section

Classification: (C) suggestion

Evidence:

- The strategy has a clear Decisions section listing [D1]-[D8] (strategy lines 116-138).
- [D9] appears later in the approach-comparison section (strategy lines 246-248), where it is important and binding for MVA promotion.

Suggested fix:

Add [D9] to the Decisions section or add an index of all [D] labels. This will make Phase 4a decision-label traceability easier, especially because the orchestration checklist requires re-reading all [D] commitments.

## Checks With No Blocking Finding

- Scaffold mismatch: Satisfied. The prompt is a Higgs signal-versus-background search with category fits; the strategy explicitly treats `conventions/search.md` as binding (strategy lines 14-18 and 59-71). `conventions/extraction.md` applies to closed-form tagged-yield extraction, not this binned template fit, and `conventions/unfolding.md` applies to detector-to-particle spectrum correction, which the strategy does not propose.
- Background coverage: Satisfied for Phase 1. The strategy classifies DY/Z, W+jets, QCD/multijet, ttbar, diboson/single-top, and Z→mumu/Z→ee mis-ID components with estimation or Phase 2 discovery plans (strategy lines 196-205), and separately commits to searching for diboson, single-top, QCD, extra W bins, and extra data periods (strategy lines 186-194 and 415-416).
- Tau efficiency and Z normalization sizing: Acceptable as a Phase 1 plan, pending later sourcing. The strategy states no systematic may be arbitrary (strategy lines 282-288), ties tau ID/trigger uncertainty to a 10-15% range unless a better source is found (lines 323-328), and ties DY/Z normalization to CMS 2014 values of 3% inclusive Z plus 2-14% category extrapolation while documenting the open-data limitation (lines 330-336). This is not yet a final systematic assignment, but it is sufficiently motivated for Phase 1.
- [A], [L], [D] labels: Mostly satisfied. Constraints [A1]-[A4], limitations [L1]-[L4], and decisions [D1]-[D9] are present (strategy lines 82-138 and 246-248). See C1 for traceability improvement.
- Figure checks: Not applicable. Phase 1 produced no physics figures, and the strategy explicitly states this (strategy line 393). Phase 1 review methodology also skips plot validator for strategy artifacts without figures (review methodology lines 23-25).

## Reviewer Framing Answers

1. Are all sources in the applicable conventions document implemented or justified as inapplicable? No. Pileup is missing from the pp-specific convention replacement; see A1.
2. Do 2-3 reference analyses exist, and does this analysis match their systematic coverage? Partly. Three references are tabulated with broad systematic programs (strategy lines 359-365), but single-channel/category-level numerical targets are too sparse; see B2.
3. If a competing group published next month, what would they have that we do not? A more concrete bridge from the CMS `mu tau_h` reference implementation to this reduced-open-data implementation: channel/category-level yield or sensitivity targets, explicit CLs/test-statistic configuration, and an explicit pileup treatment.
4. Are uncertainties honest in both directions? Phase 1 mostly addresses this by forbidding arbitrary sizes and warning against trivially broad validation pulls (strategy lines 282-288 and 330-336). The missing pileup source and lack of exact later thresholds still need correction.
5. Were limitations accepted without evidence of attempted improvement? For Phase 1, limitations are mostly deferred to Phase 2 data discovery with concrete checks (strategy lines 406-416). That is acceptable at strategy level, but Phase 2 must not convert missing samples or scale factors into limitations without attempted retrieval/calibration.
6. Does every result have context? No final result exists in Phase 1. The strategy provides global comparison anchors, but it needs more local single-channel/category targets before Phase 4 comparisons can be rigorous.
