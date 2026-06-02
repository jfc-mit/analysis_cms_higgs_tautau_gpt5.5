# Phase 1 Critical Re-Review After Iterate Fix

Reviewer: critical re-reviewer  
Timestamp: 2026-06-02T09:26:05Z  
Artifact: `phase1_strategy/outputs/STRATEGY.md`  
Original arbiter verdict: `phase1_strategy/review/arbiter/phase1_arbiter_20260602T091405Z.md`  
Fixer log: `phase1_strategy/logs/fixer_phase1_strategy_20260602T091902Z.md`

## Headline Verdict

**PASS.**

The arbiter-required Phase 1 fixes are resolved in `STRATEGY.md`. I find no remaining Category A or B issue blocking Phase 1 advancement. The fixed artifact now satisfies the Phase 1 review focus from `methodology/06-review.md` section 6.4: backgrounds are complete for this scope, the systematic plan enumerates the search convention sources, the reference analyses are tabulated, and the strategy commits to multiple Phase 3 selection/observable approaches with quantitative gates.

Phase 1 has no produced figures, selections, validation tests, or fit results, so the figure physics checks, numerical result consistency checks, GoF checks, and regression-trigger result checks are not applicable at this phase.

## Arbiter Fix Verification

| Arbiter item | Re-review finding | Evidence |
|---|---|---|
| 1. Add pileup convention coverage. | **Resolved.** The search convention enumeration now includes an explicit pileup row with implementation and fallback paths. | `STRATEGY.md:377` starts the convention table; `STRATEGY.md:385` states "Pileup profile and weights" with "Will implement if NanoAOD supports it; otherwise limitation", requires Phase 2 pileup branch inventory, Phase 4 propagation if available, and a no-double-counting limitation if unavailable. |
| 2. Define mutually exclusive fit categories. | **Resolved.** The artifact now prevents overlapping simultaneous-fit categories. | `STRATEGY.md:123` commits to "mutually exclusive VBF-enriched and non-VBF baseline categories." `STRATEGY.md:267-273` states the model fits mutually exclusive categories, gives binding assignment order with VBF first, and says an inclusive baseline plot is diagnostic only if it duplicates fit events. |
| 3. Add explicit statistical configuration. | **Resolved.** CLs, one-sided test statistics, and low-statistics toy policy are now bound. | `STRATEGY.md:195-210` defines a binned profile likelihood, modified CLs as `CL_s = CL_s+b/CL_b`, one-sided `q_0` with `q_0 = 0` for negative fitted signal strength, `mu >= 0` for limits, asymptotics only above about five expected events per final SR bin, and toy validation or direct toys for low-stat final bins. |
| 4. Add quantitative alternative-observable gates. | **Resolved.** Gates are quantitative and specify rejection handling. | `STRATEGY.md:427-439` requires input data/MC `chi2/ndf <= 5`, closure and GoF p > 0.05, signal injection at 0x, 1x, 2x, and 5x with <20% bias, and at least 10% expected-sensitivity improvement before replacing `m_vis`. |
| 5. Specify NN genMET/missing-momentum construction and leakage controls. | **Resolved.** The observable is physically defined enough for Phase 1 and has downscope criteria. | `STRATEGY.md:159-176` defines `m_NNMET`, targets tau-neutrino missing transverse momentum, constructs a massless missing-momentum four-vector with longitudinal component set to zero, restricts inputs to reconstructed quantities present in data, forbids gen-level/sample-label/truth-match leakage, and downscopes the observable if genMET/neutrino truth is absent or leakage cannot be excluded. |
| 6. Add CR/VR taxonomy. | **Resolved.** The plan now covers SR, W, QCD, top, and Z-rich regions with orthogonality and pass/fail rules. | `STRATEGY.md:349-367` defines the control and validation region plan. `STRATEGY.md:354-355` requires orthogonality and pre-unblinding transfer-factor definitions. Rows at `STRATEGY.md:360-367` cover SR, W high-mT CR, W VR, QCD same-sign CR, QCD anti-isolation CR/VR, Top CR, Top VR, and Z-rich VR with metrics and fallback handling. |
| 7. Strengthen W+jets normalization requirements. | **Resolved.** The W plan now includes purity, subtraction, category transfer validation, and uncertainty fallback. | `STRATEGY.md:318-346` adds a dedicated W+jets high-mT normalization plan. It requires post-subtraction W purity (`STRATEGY.md:332-333`), category-wise high-to-low-mT transfer validation where possible (`STRATEGY.md:338-342`), and a larger category-extrapolation uncertainty when statistics are insufficient (`STRATEGY.md:340-342`). The W CR/VR rows at `STRATEGY.md:361-362` repeat closure and transfer requirements. |
| 8. Add binding final-AN comparison target matrix. | **Resolved.** The final AN comparison obligations are now explicit and include internal, CMS, ATLAS+CMS/PDG, category, and alternative-observable targets. | `STRATEGY.md:475-494` defines the binding comparison matrix. It includes this analysis expected/observed outputs (`STRATEGY.md:485-487`), CMS 2014 global and `mu tau_h`/category/control anchors (`STRATEGY.md:488-490`), CMS 2018 (`STRATEGY.md:491`), ATLAS+CMS/PDG/world-average context (`STRATEGY.md:492`), VBF/non-VBF sensitivity (`STRATEGY.md:493`), and alternative observables (`STRATEGY.md:494`). |
| 9. Low-cost traceability improvements. | **Resolved where important.** [D9] is now in the Decisions list, and uncertainty-inflation checks are explicitly present. | `STRATEGY.md:140-145` lists [D9]. `STRATEGY.md:367` requires investigation if validation pulls are below 0.5 sigma, and `STRATEGY.md:423-425` says the 10-15% DY/Z uncertainty must not make validation pulls trivially small. |

## Phase 1 Essential Checks

### Backgrounds

**PASS.** The strategy covers the major and missing-background risks for a CMS 2012 `mu tau_h` H to tau tau search. It identifies the prompt-listed MC samples and provenance checks at `STRATEGY.md:221-223`, requires searches for diboson, single-top, QCD/multijet, and additional W/data samples at `STRATEGY.md:227-232`, and classifies DY, W+jets, QCD/multijet, ttbar, diboson/single-top, and Z to mu mu/ee fakes at `STRATEGY.md:239-244`.

The QCD handling is no longer a conditional afterthought: `STRATEGY.md:241` prefers same-sign and anti-isolation sidebands, `STRATEGY.md:363-364` defines the QCD CR/VR rows, and `STRATEGY.md:111-113` labels the fallback as limitation [L4] if robust sidebands are unavailable.

### Search Convention Enumeration

**PASS.** The search convention table at `STRATEGY.md:377-398` covers every source in `conventions/search.md` with either "Will implement" or an inapplicability/pp-equivalent explanation. It includes signal cross-section, acceptance, shape, ISR pp replacement, pileup, PDF, LEP 4-fermion pp replacement, background normalization and shape, qqbar/DY modelling, MC statistics, detector simulation, object calibration, beam energy, luminosity, QCD scales, fragmentation, and heavy-flavour treatment.

This resolves the original Category A pileup omission. The pileup row at `STRATEGY.md:385` is appropriately conditional because Phase 2 still must inventory whether reduced NanoAOD files contain pileup observables or weights.

### Reference and Comparison Targets

**PASS.** Three reference analyses are tabulated at `STRATEGY.md:462-468`: CMS JHEP 05 (2014) 104, CMS Phys. Lett. B 779 (2018) 283, and ATLAS+CMS JHEP 08 (2016) 045. The table includes method parity, systematic program, and numerical comparison anchors. The final-AN comparison matrix at `STRATEGY.md:475-494` also handles the user's request for comprehensive comparisons by distinguishing directly comparable internal results from global CMS/PDG/world-average context.

Residual watch item, not a blocker: exact CMS 2014 single-channel/category values are deferred to Phase 2/5 extraction (`STRATEGY.md:489-490`). That is acceptable at Phase 1 because the artifact names the source and makes extraction a binding downstream obligation rather than inventing numbers.

### Selection and Approach Plan

**PASS.** Phase 1 identifies at least four approaches: baseline visible mass, NN discriminator, NN MET-direction regression, and add-MET mass. The comparison table at `STRATEGY.md:286-293` defines strengths, risks, and common metrics. The primary replacement gate at `STRATEGY.md:427-439` prevents narrative-driven Phase 3 selection.

Categories are also acceptable after the fix. `STRATEGY.md:248-263` defines VBF-enriched, non-VBF baseline, optional 0-jet, and boosted/1-jet categories; `STRATEGY.md:267-273` makes the simultaneous-fit assignment mutually exclusive.

### Labels and Traceability

**PASS.** Constraint, limitation, and decision labels are present and useful. Constraints [A1]-[A4] are listed at `STRATEGY.md:87-95`; limitations [L1]-[L4] at `STRATEGY.md:101-113`; decisions [D1]-[D9] at `STRATEGY.md:118-145`. The original [D9] traceability suggestion is fixed by the decision list entry at `STRATEGY.md:140-145`.

### Systematic Motivation and Honesty

**PASS.** The artifact explicitly forbids arbitrary systematic sizing at `STRATEGY.md:371-375`, requiring a retrieved measurement, published uncertainty, data-control-region fit, or closure/stability result. The tau ID and DY/Z normalization uncertainties remain in the prompt-requested 10-15% range but are now framed as limitations rather than tuning knobs: tau ID at `STRATEGY.md:412-417`, DY/Z at `STRATEGY.md:419-425`, and the over-inflation check at `STRATEGY.md:367` and `STRATEGY.md:423-425`.

## New Contradictions or Unreviewed Commitments

No blocking contradiction found.

- The scaffold calls the analysis a measurement, but `STRATEGY.md:14-18` explicitly resolves this in favor of the user physics prompt as a search/template-fit analysis and binds `conventions/search.md`. This is consistent with `conventions/search.md`, whose "When this applies" section covers significance/limit and shape-based discriminant searches.
- The strategy keeps `m_vis` as the baseline (`STRATEGY.md:120-122`) while allowing alternatives to replace it only after predefined gates (`STRATEGY.md:140-145`, `STRATEGY.md:427-439`). That is not a contradiction; it is a controlled Phase 3 decision.
- The enlarged 10-15% tau/DY uncertainties could become over-conservative, but the strategy now requires validation against trivial pulls (`STRATEGY.md:367`, `STRATEGY.md:423-425`). This is an honest-uncertainty guard rather than an unreviewed tuning commitment.

## Regression Checklist

Phase 1 has no executed validation tests, fit, systematics impacts, GoF toys, binning, figures, or extracted results. Therefore:

- Validation test failures without remediation: not applicable.
- Single systematic >80% of total uncertainty: not applicable.
- GoF toy distribution inconsistent with observed chi2: not applicable.
- Flat-prior gate excluding >50% of bins: not applicable.
- Tautological comparison presented as independent validation: not applicable.
- Visually identical independent distributions: not applicable.
- Result >30% relative deviation from a well-measured reference: not applicable.
- Binding Phase 1 decisions silently replaced: not applicable yet; [D1]-[D9] are now explicit downstream commitments.
- Fit chi2 identically zero: not applicable.

No phase regression is triggered.

## Non-Blocking Watch Items for Later Phases

1. Phase 2 must resolve the data-stream ambiguity: prompt-listed SingleMu files versus CERN record 12350 TauPlusX provenance is explicitly open at `STRATEGY.md:93-95` and `STRATEGY.md:575-576`.
2. Phase 2/4 must source every numerical constant before use, consistent with `STRATEGY.md:35-38`; the Phase 1 artifact intentionally leaves future weights, cross sections, branching fractions, and detector performance values to citable retrieval.
3. Phase 4a review should enforce the convention completeness table against `STRATEGY.md:377-398` and the reference-driven systematics list at `STRATEGY.md:402-408`.

## Final Decision

**PASS.** No Category A or B findings remain after the ITERATE fix.
