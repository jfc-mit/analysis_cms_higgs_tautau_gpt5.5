# Sensitivity Regression Ticket

Session: `investigator_sensitivity_20260602T134146Z`

## Origin

Recommended origin phase: **Phase 3 selection**, with a required Phase 4a
inference follow-through.

The immediate regression symptom is in Phase 4a:

- `phase4_inference/4a_expected/outputs/expected_results.json` reports median
  expected 95% CLs limit `mu = 11.374122822819393`.
- The same file reports expected discovery diagnostic `Z = 0.1906097504953417`
  from a signal-plus-background Asimov `q0` test.
- `phase4_inference/4a_expected/outputs/nominal_yields.json` contains only
  `25.1009` expected signal events against `9298.9615` expected background
  events across the retained categories.

The likely origin is not a single pyhf failure. A diagnostic pyhf variant scan
on the existing workspace found:

| Model variant | q0 Asimov Z |
|---|---:|
| Nominal Phase 4a workspace | 0.191 |
| No `staterror` modifiers | 0.262 |
| No `normsys` modifiers | 0.272 |
| No `staterror` or `normsys` modifiers | 0.389 |

Therefore the Phase 4a nuisance model suppresses sensitivity by roughly a
factor of two relative to a no-systematics shape-only idealization, but even
the no-systematics model remains far below the 1-2 sigma plausibility target.
The dominant origin is the Phase 3 selection/discriminant/category design and
the limited reduced open-data feature set.

The Phase 3 artifact already documented warning signs:

- `phase3_selection/outputs/SELECTION.md` says the formal [D9]
  expected-sensitivity gate was **not evaluated in Phase 3** and was left to
  Phase 4.
- `phase3_selection/outputs/variable_modeling.json` reports that `13` of `16`
  candidate MVA inputs failed the data/background-MC shape gate. The primary
  mass observable `m_vis` has `chi2/ndf = 17.98`; `m_addmet` has
  `chi2/ndf = 43.32`; `pt_tautau_proxy` has `chi2/ndf = 75.20`; and
  `n_clean_jets` has `chi2/ndf = 508.19`.
- Phase 3 downscoped the classifier before training because the majority of
  inputs failed the modelling gate. Methodology Phase 3 allows this only after
  evaluating classifier-output modelling and possible calibration if the MVA
  gives better discrimination. That has not yet been done with a Phase 4a
  expected-only metric.

## Evidence From Reference Analysis

The relevant reference is CMS-HIG-13-004, JHEP 05 (2014) 104,
arXiv:1401.5041, DOI `10.1007/JHEP05(2014)104`. The CMS result page states
that the publication used `4.9/fb` at 7 TeV and `19.7/fb` at 8 TeV, all six
tau-pair final states, and observed a local significance larger than three
standard deviations for Higgs masses between 115 and 130 GeV, with
best-fit signal strength `0.78 +/- 0.27`.

The paper methods show why the current reduced analysis is weaker:

- Events were split into mutually exclusive categories to maximize SM Higgs
  sensitivity. In the mu tau_h channel, CMS used 0-jet, 1-jet, boosted,
  loose VBF, and tight VBF categories rather than one coarse VBF, one boosted,
  and one zero-jet category.
- VBF selection used at least two jets, high `mjj`, large `delta_eta_jj`, and a
  central-jet veto. In 8 TeV data, VBF was split into loose and tight
  categories.
- The 1-jet and 2-jet categories were split using the transverse momentum of
  the Higgs candidate, and 0-jet/1-jet categories were also split by lepton or
  tau_h pT. The paper notes that boosted selections improve the tau-pair mass
  resolution and signal/background separation.
- CMS used the SVFIT tau-pair mass as the final discriminant in the sensitive
  mu tau_h categories. The paper states that SVFIT gives better separation
  between H->tau tau and Z->tau tau than visible mass alone.
- Dominant backgrounds were constrained with data-driven methods: embedded
  Z->tau tau, high-mT W+jets control regions, b-tagged top control samples,
  and same-sign or anti-isolation QCD controls. The current Phase 4a expected
  model instead uses MC-only DY/W/top templates and omits QCD, diboson,
  single-top, W4/inclusive W, associated H, and H->WW components.

The CMS mu tau_h yield table is a useful scale comparison. In 8 TeV:

| CMS 2014 mu tau_h category | Signal | Background | Central-window S/(S+B) |
|---|---:|---:|---:|
| 1-jet high-pT tau_h boosted | 16.5 | 1265 | 0.072 |
| Loose VBF tag | 4.5 | 81 | 0.17 |
| Tight VBF tag | 2.4 | 15 | 0.49 |

The current Phase 4a categories are much less pure:

| Current category | Signal | Background | Integrated S/B |
|---|---:|---:|---:|
| VBF | 1.590 | 144.926 | 0.0110 |
| Boosted | 9.170 | 2093.690 | 0.0044 |
| Zero-jet | 14.341 | 7060.345 | 0.0020 |

This is not a direct observed-result pull, because the reference combines more
channels, more luminosity, SVFIT, and full CMS calibrations. It is nevertheless
a serious quality issue: the reduced Phase 4a model does not recover even the
expected single-channel order-of-magnitude sensitivity suggested by the
reference methods.

## Impact Trace

Affected upstream artifacts:

- `phase3_selection/src/build_selection.py`: category definitions, top/b-veto
  handling, selected features, and signal-region masks.
- `phase3_selection/src/model_inputs_and_mva.py`: MVA gate, classifier
  training/calibration diagnostics, and output-score validation.
- `phase3_selection/src/compare_approaches.py`: expected-only comparison must
  be upgraded from raw MC-only separation to a Phase 4a-compatible metric.
- `phase3_selection/outputs/selected_events.npz`: may need additional
  classifier scores, refined category labels, or both.
- `phase3_selection/outputs/category_yields.json`, `cutflow.json`,
  `region_yields.json`, `variable_modeling.json`,
  `approach_comparison.json`, figures, and `SELECTION.md`.

Affected downstream artifacts:

- `phase4_inference/4a_expected/src/build_expected_model.py`: must consume the
  revised category/discriminant outputs and compare at least the baseline and
  proposed alternatives using identical normalization and nuisance assumptions.
- `phase4_inference/4a_expected/outputs/pyhf_workspace.json`,
  `templates.npz`, `nominal_yields.json`, `expected_results.json`,
  `systematics.json`, `INFERENCE_EXPECTED.md`, and figures.
- `phase4_inference/4a_expected/outputs/ANALYSIS_NOTE_4a_v1.{md,tex,pdf}`:
  must be regenerated by the note writer/typesetter after the inference
  result changes.
- Phase 4a review must restart after the revised compiled PDF exists.

## Concrete Fix Scope

Estimated scope: 6-10 agent-hours for the first remediation iteration, plus
review.

The fixer/executor should run expected-only studies using MC/Asimov inputs
only. Do not inspect or tune on the full observed signal-region data. Data may
be used only in allowed control/validation regions to evaluate modelling and
calibration, with all caveats documented before Phase 4b.

Success metric:

- Primary gate: improve the median expected 95% CLs upper limit or expected
  discovery `Z` by at least `30%` relative to the current Phase 4a baseline
  (`mu = 11.374`, `Z = 0.191`) while passing signal injection bias below 20%.
- Ambition gate: attempt to reach `Z >= 1.0` or median expected limit
  `mu <= 3.0`. If this is impossible with reduced open-data inputs, document
  at least three serious attempts and the limiting factor for each.
- Model-health gate: no final signal-region bin with expected background below
  the asymptotic validity threshold unless toy-based limits/significances are
  used or bins are merged; nuisance pulls/constraints and GoF diagnostics must
  pass search conventions.
- Blinding gate: no tuning on observed full-data SR.

### Prioritized Attempts

1. **JHEP-inspired category refinement.**
   - Split the current boosted category by `pt_tautau_proxy` and/or `tau_pt`.
   - Split VBF into loose/tight candidates using `mjj`, `delta_eta_jj`, and
     central-jet-veto-like information if available; otherwise document the
     missing central-jet veto.
   - Evaluate b-veto/top suppression using `btag_max` and top-control purity.
   - Optimize thresholds on MC/Asimov only.
   - Objective metric: expected CLs limit and q0 Asimov Z from pyhf with the
     same nuisance model as baseline, plus no-systematics diagnostic.
   - Investigator diagnostic: a simple VBF threshold scan using the current
     selected events did **not** improve sensitivity; e.g. `mjj > 500` and
     `delta_eta_jj > 3.5` gives only `S = 0.932`, `B = 57.482`,
     `S/sqrt(B) = 0.123`. Therefore this attempt must be broader than merely
     tightening the current VBF cut.

2. **Expected-only classifier/discriminant.**
   - Train at least two classifiers on MC only using available reconstructed
     variables: `m_vis`, `m_addmet`, mu/tau pT and eta, MET, `mt_mu_met`,
     `pt_tautau_proxy`, `n_clean_jets`, `mjj`, `delta_eta_jj`, `btag_max`,
     `jet1_pt`, and isolation variables.
   - Evaluate output-score templates in pyhf with baseline nuisances.
   - Produce output data/MC checks in control/validation regions and, if
     needed, attempt output-level calibration or variable removal before
     rejection.
   - Objective metric: expected CLs/q0 improvement >= 30% and signal injection
     bias < 20%; classifier output modelling must not be worse than the
     worst input-level modelling without an explicit calibration uncertainty.
   - Investigator diagnostic: a quick train/test MC-only gradient boosting
     model reached AUC `0.787` and no-systematics binned Asimov Z `0.453`,
     versus `0.389` for current m_vis bins. This is a real but modest
     improvement; a formal pyhf/nuisance study is still required.

3. **Alternative observable and binning model.**
   - Build Phase 4a pyhf models for `m_addmet`, `pt_tautau_proxy`, and
     possibly a two-dimensional category-plus-mass scheme using the same
     expected-only Asimov data.
   - Optimize bin edges on MC only, requiring enough expected background per
     bin or toy validation.
   - Compare with identical nuisance assumptions and signal injection tests.
   - Investigator diagnostic: current coarse `m_addmet` bins are worse than
     `m_vis` in the no-systematics diagnostic (`Z = 0.352` versus `0.389`),
     so gains likely require different binning or combination with categories,
     not a simple observable swap.

4. **Phase 4a model audit.**
   - Re-evaluate the MC-stat implementation. The current workspace uses one
     per-category `staterror` modifier shared by samples in each category; the
     fixer should verify whether this represents the intended total-template
     Barlow-Beeston-lite treatment or should be per-sample/per-bin or total
     background only.
   - Evaluate whether the `15%` DY and tau/open-data acceptance nuisances are
     over-constraining the expected-only diagnostic relative to documented
     control-region constraints. Do not reduce them arbitrarily; any change
     needs a citable or data-driven justification and must be propagated to
     the AN.
   - Add W high-mT and top control constraints to the expected model if they
     can be built without observed SR tuning. QCD remains deferred unless a
     sideband-only expected/validation procedure is defined.

5. **Missing-component feasibility check.**
   - Confirm whether reduced samples for QCD, diboson, single top, W4 or
     inclusive W, associated H, and H->WW can be localized or produced through
     the approved open-data workflow.
   - If unavailable, keep them documented as limitations. Do not fabricate
     samples or use paper-level yields as pseudo-events.

If all attempts fail, the allowed outcome is a revised Phase 4a note that
documents the sensitivity campaign, shows the best expected-only model, and
states quantitatively why the reduced mu tau_h open-data analysis cannot reach
1-2 sigma without SVFIT/embedding/additional channels/calibrations/samples.

## Downstream Cascade

Required rerun sequence:

1. Phase 3 executor in plan mode, focused on sensitivity remediation.
2. Phase 3 scripts and outputs if categories, features, classifier scores, or
   selected-event summaries change.
3. Phase 3 review with critical reviewer and plot validator.
4. Phase 4a executor to rebuild all expected templates/workspaces/results.
5. Phase 4a note writer and typesetter; compile PDF before review.
6. Full Phase 4a 4-bot+bib review panel on the compiled PDF.

The existing Phase 1 strategy does not need to be rewritten unless the fixer
proposes abandoning [D2] visible mass as the baseline without retaining it as a
comparison, or formally changing the [D9] gate.

Phase 4b must not start until the revised Phase 4a result passes review.

## Regression Triggers Met

- **Human-gate sensitivity regression:** the user flagged a physically
  implausible sensitivity scale compared with CMS-HIG-13-004. This is a valid
  regression investigation trigger even though it is not a direct observed
  data pull.
- **Data/MC disagreement on observable or MVA inputs:** Phase 3 records
  large validation/control-region data/background-MC disagreements for
  candidate inputs and even the primary `m_vis` observable.
- **Upstream improvement cascade:** improving category definitions,
  discriminants, or model treatment changes every downstream Phase 4a
  template, figure, result, and AN number.
- **Binding commitment pressure:** Phase 1 [D9] required an expected-sensitivity
  gate for alternative observables/MVA. Phase 3 left it unresolved for Phase 4,
  and the current Phase 4a model did not complete a full pyhf comparison of the
  alternatives before accepting very low sensitivity.

## Sources Used

- CMS-HIG-13-004 public result page:
  https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-13-004/index.html
- JHEP DOI: https://doi.org/10.1007/JHEP05(2014)104
- arXiv:1401.5041 source/PDF: https://arxiv.org/abs/1401.5041
- Local artifacts:
  `phase1_strategy/outputs/STRATEGY.md`,
  `phase3_selection/outputs/SELECTION.md`,
  `phase3_selection/outputs/selected_events.npz`,
  `phase3_selection/outputs/variable_modeling.json`,
  `phase3_selection/outputs/approach_comparison.json`,
  `phase4_inference/4a_expected/outputs/expected_results.json`,
  `phase4_inference/4a_expected/outputs/nominal_yields.json`,
  `phase4_inference/4a_expected/outputs/pyhf_workspace.json`,
  and `phase4_inference/4a_expected/src/build_expected_model.py`.
