# Phase 1 Fixer Log

Timestamp: 2026-06-02T09:19:02Z

Inputs read:

- `agents/fixer.md`
- `phase1_strategy/review/arbiter/phase1_arbiter_20260602T091405Z.md`
- `phase1_strategy/outputs/STRATEGY.md`
- `experiment_log.md`
- `conventions/search.md`

## Finding 1: pileup convention coverage

Understand: `conventions/search.md` requires pp-specific replacements
including pileup. The strategy enumerated pp systematics but did not name
pileup or justify inapplicability.

Locate: `Systematic Uncertainty Plan` / `Search Convention Enumeration`.

Fix: Added a `Pileup profile and weights` row requiring Phase 2 inventory of
pileup branches/weights, Phase 4 variation if supported, and a documented
reduced-open-data limitation if unsupported.

Verify: The strategy now explicitly names pileup and gives both implementation
and fallback paths without inventing a numerical uncertainty.

## Finding 2: mutually exclusive categories

Understand: A simultaneous fit cannot include overlapping baseline inclusive
and VBF categories.

Locate: `Constraints, Limitations, and Binding Decisions` and `Candidate
Categories and Simultaneous Fit`.

Fix: Changed [D3] to mutually exclusive VBF-enriched and non-VBF baseline
categories. Added binding assignment order and stated inclusive distributions
are diagnostics only when they duplicate fit events.

Verify: A neighborhood check found and fixed the leftover ambiguous
`inclusive/baseline` phrase in [D3].

## Finding 3: statistical configuration

Understand: The strategy needed explicit CLs/test-statistic/asymptotic-toy
rules from `search.md`.

Locate: New `Statistical Configuration` section.

Fix: Added modified CLs, one-sided `q0`, `q0 = 0` for negative fitted signal
strength, `mu >= 0` for limit tests, the > about five expected events
asymptotic threshold, and toy validation/direct toys for low-stat final bins.

Verify: The added section binds the Phase 4 statistical choices before
unblinding.

## Finding 4: alternative-observable gates

Understand: MVA and alternative observable choices needed quantitative
accept/reject criteria.

Locate: `Selection and Fit Approaches to Compare` and new `Alternative
Observable Acceptance Gates`.

Fix: Added thresholds for input data/MC chi2/ndf, signal-injection bias,
GoF/closure, minimum 10% expected-sensitivity gain over `m_vis`, and explicit
rejection/downscope outcomes.

Verify: Each alternative row now points to the gates and the standalone gate
table gives pass/fail handling.

## Finding 5: NN genMET/missing-momentum construction

Understand: The NN-assisted mass needed a physical target, input rules, and
data-application leakage protection.

Locate: `Observables and Fit Outputs`.

Fix: Defined the preferred truth target as the tau-neutrino missing transverse
momentum vector, specified the massless transverse four-vector construction,
limited inputs to reconstructed quantities available in data, forbade truth
leakage, and added validation/downscope criteria.

Verify: The strategy now states that missing truth targets or unavoidable
leakage prevent the observable from replacing `m_vis`.

## Finding 6: W+jets high-mT plan

Understand: The W control-region strategy needed purity, contamination, and
category-transfer requirements.

Locate: `W+jets High-mT Normalization Plan` and `Control and Validation
Region Plan`.

Fix: Added the high-mT concept, post-subtraction purity reporting, top/VBF
contamination handling, category-wise transfer validation where possible, and
larger extrapolation uncertainty when category statistics are limited.

Verify: The W CR/VR rows now include transfer-factor metrics and pass/fail
fallbacks.

## Finding 7: CR/VR definitions

Understand: Region taxonomy needed enough detail for downstream audit.

Locate: New `Control and Validation Region Plan`.

Fix: Added rows for SR, W CR/VR, QCD same-sign and anti-isolation CR/VR, top
CR/VR, and Z-rich VR, with selection differences, dominant process,
subtraction/likelihood use, transfer or validation metric, thresholds,
orthogonality, and fallbacks.

Verify: The table covers DY/Z, W+jets, top, and QCD/instrumental backgrounds
and binds p > 0.05 closure/GoF thresholds where applicable.

## Finding 8: final-AN comparison matrix

Understand: The final note needed binding comparison targets beyond global
CMS numbers and explicit non-comparability labels.

Locate: `Reference Analysis Table`.

Fix: Added `Binding Final-AN Comparison Target Matrix` with internal expected
and observed outputs, 10%/full validation history, CMS 2014 global and
extractable channel/category/control targets, CMS 2018 caveated targets,
ATLAS+CMS/PDG/world-average context, VBF/non-VBF sensitivity, and alternative
observable comparisons.

Verify: The matrix names the source for each target and requires exact
single-channel numbers to be extracted from named sources in later phases
rather than fabricated in Phase 1.

## Regression and Neighborhood Check

No numerical results, scripts, figures, or fit outputs changed. No downstream
number propagation was required.

Neighborhood check: searched the edited strategy for pileup/PDF, statistical
settings, category exclusivity, NN leakage/downscope, quantitative gates, CR/VR
taxonomy, and comparison matrix terms. Fixed one remaining ambiguous category
phrase in [D3]. Existing cited numerical values were left unchanged.
