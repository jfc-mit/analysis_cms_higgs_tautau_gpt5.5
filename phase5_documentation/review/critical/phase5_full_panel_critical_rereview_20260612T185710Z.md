# Phase 5 Critical Re-review

Session: `20260612T185710Z`

Scope: re-review after arbiter ITERATE fix of the Phase 5 final AN, PRL draft,
references, figures, and Phase 4c observed/baseline machine-readable outputs.

Verdict: **ITERATE**.

The fixer resolved the most visible presentation failure: the AN and PRL now
lead with the visible-mass baseline, and the optimized classifier is described
as a rejected diagnostic. However, three Category A blockers remain: unqualified
machine-readable top-level result fields still point to the failed score model,
the required baseline systematic impact ranking is explicitly absent, and the
required observed-data combined GoF toy p-value is explicitly absent. These were
not optional polish items; they were part of the arbiter's required fix list and
the search-convention validation program.

## Resolved Or Substantially Improved

- **Headline model role in prose is fixed.** `ANALYSIS_NOTE_5_v1.md:10` states
  that `visible_mass_qcd_primary` is the only final-result model and quotes
  `mu = 0.4382 +4.9443 -0.4382`, observed `mu < 10.7645`, expected median
  `mu < 10.7375`. `PAPER_PRL_v1.md:6-11` likewise presents the visible-mass
  fit as the final result and describes it as a low-sensitivity Open Data limit.

- **Baseline numbers are internally consistent where the note uses
  `baseline_previous_result.json`.** The JSON gives `mu_hat =
  0.43822864200217504`, profile interval lower `0.0`, upper
  `5.38255638989378`, observed limit `10.764467444563975`, expected band
  `[5.427106878746744, 7.453820619170937, 10.737535128866,
  15.735353955271256, 22.4849409859314]`
  (`baseline_previous_result.json:3-22`). The AN final-result table quotes the
  same values rounded to four decimals (`ANALYSIS_NOTE_5_v1.md:391-416`).

- **Baseline validation values match the baseline JSON.** The JSON combined
  validation has data/background `0.981178720007985`, chi2/ndf
  `0.7223857883360273`, and all validation flags false
  (`baseline_previous_result.json:181-198`). The AN quotes data/background
  `0.9812`, chi2/ndf `0.7224`, and no category or combined validation flag
  (`ANALYSIS_NOTE_5_v1.md:346`).

- **The PRL draft is now reviewable at the level of a short proceedings-style
  draft.** It has an abstract, data/method section, background-model section,
  result/interpretation section, one numerical table, two figures, and citations
  (`PAPER_PRL_v1.md:1-62`). This resolves the prior "13-line stub" failure.

- **The final-result figures are cleaner.** I visually inspected the contact
  sheet of all 31 PNGs plus the new baseline VBF and limit plots directly. The
  new `phase5_baseline_visible_vbf.png` has no visible ratio-panel `x` artifact;
  it shows the documented VBF deficit with the data/background point near 0.285
  in one bin, matching the AN text at `ANALYSIS_NOTE_5_v1.md:354`. The headline
  limit plot shows only the visible-mass final result and does not include the
  rejected score model.

## Category A Findings

### A1. Unqualified top-level result fields in `observed_results.json` still point to the failed score model

The fix added correct final-result metadata, but it did not remove or update
the stale top-level aliases that a downstream reader or script would naturally
use.

Evidence:

- `observed_results.json:1159` sets `"final_result_model":
  "visible_mass_qcd_primary"` and `observed_results.json:2240` sets
  `"primary_model": "visible_mass_qcd_primary"`.
- But the unqualified top-level `observed_fit` block at
  `observed_results.json:2069-2088` has `mu_hat = 38.380184326872644` and
  observed limit `50.0`, i.e. the failed score result.
- The unqualified top-level `validation_summary` at
  `observed_results.json:2967-2983` has `model_label =
  "calibrated_score_qcd_primary"`, `combined_ratio_failure = true`, and
  `high_score_shape_failure = true`.
- The separate `score_diagnostic_fit` block repeats the same score numbers at
  `observed_results.json:2681-2700`, confirming the top-level fields are score
  aliases, not the baseline final result.
- The baseline final-result values exist only in nested/alternate blocks:
  `observed_results.json:879-899` and `baseline_previous_result.json:3-22`.

Why this blocks PASS:

The arbiter required current machine-readable result metadata to make the
baseline the final result and demote the score model. The metadata now contains
a correct `final_result` block, but the legacy top-level aliases still leak the
failed score model as "observed_fit" and "validation_summary." This is not just
prose stale wording; it is a durable machine-readable ambiguity that can
regenerate a score-as-primary result in downstream documentation or checks.

Required fix:

Make the unqualified top-level `observed_fit` and `validation_summary` aliases
refer to the validated visible-mass final result, or remove them and require
consumers to use `final_result`. Keep score values only under explicit
diagnostic names such as `score_diagnostic_fit` and
`score_diagnostic_validation_summary`.

### A2. Required baseline systematic impact ranking is still absent

The AN now describes the retained nuisance sources, but it explicitly states
that source-by-source impacts are not available. Search conventions require an
impact ranking, and the arbiter required a baseline-specific impact ranking
before re-review.

Evidence:

- `conventions/search.md:113-118` requires nuisance pulls/constraints and
  impact ranking.
- The arbiter's required action 5 demanded baseline-specific "nuisance
  pulls/constraints, impact ranking, injection recovery, observed/expected CLs
  limits" (`phase5_full_panel_arbiter_20260612T180429Z.md`, required fixer
  actions).
- The AN's systematic figure caption says it is "not an impact ranking" and
  that exact source-by-source impacts are not available
  (`ANALYSIS_NOTE_5_v1.md:199`).
- Each systematic subsection repeats that the final artifact does not store a
  source-by-source refit impact on `mu` (`ANALYSIS_NOTE_5_v1.md:217`,
  `237`, `257`, `277`, `297`, `317`, `337`).
- The error-budget narrative is explicitly qualitative and says the current
  machine outputs do not store source-by-source impact refits
  (`ANALYSIS_NOTE_5_v1.md:342`).
- The limitations section says a future extension should produce an impact JSON
  (`ANALYSIS_NOTE_5_v1.md:461`).

Why this blocks PASS:

This was a prior Category A/B cluster: final model systematic documentation,
baseline-specific validation, and the mandatory regression checklist item "any
single systematic > 80% of total uncertainty?" The current note cannot answer
the >80% dominance check quantitatively because no source-by-source impacts
exist. A qualitative statement that no single documented source dominates is
not evidence.

Required fix:

Run and store a baseline nuisance-impact evaluation for the final
`visible_mass_qcd_primary` workspace. At minimum, provide a JSON/table with
each retained nuisance, its variation or profiling prescription, change in
`mu_hat`, change in observed/expected limit, and fractional contribution or
rank. Then update the systematic figure and AN prose from that artifact.

### A3. Required observed-data combined GoF toy p-value is absent

The note reports chi2/ndf and a discovery diagnostic p-value, but the search
conventions require a combined GoF toy p-value for the final fit. The AN
explicitly says no full observed-data toy ensemble is stored.

Evidence:

- `conventions/search.md:121-122` requires "chi2/ndf in each region" and "a
  toy-based p-value for the combined fit" with acceptable `p > 0.05`.
- The AN says no full observed-data toy ensemble is stored in the current Phase
  5 artifacts (`ANALYSIS_NOTE_5_v1.md:183`).
- The GoF figure is only an expected-stage artifact; the caption says the final
  observed baseline note does not claim a full observed-data toy ensemble
  (`ANALYSIS_NOTE_5_v1.md:383`).
- The limitations section repeats that no full observed-data GoF toy ensemble
  is stored (`ANALYSIS_NOTE_5_v1.md:463`).
- The final result section's p-value is the discovery diagnostic p-value
  `0.4622` for `q0`, not a combined GoF toy p-value
  (`ANALYSIS_NOTE_5_v1.md:403`).

Why this blocks PASS:

The baseline chi2/ndf values are plausible, but the required validation is not
complete. The zero-jet chi2/ndf is low (`0.113`, `ANALYSIS_NOTE_5_v1.md:346`),
which is precisely the kind of case where a toy distribution or stronger GoF
validation is needed to distinguish conservative overcoverage from a
pathological covariance or circular validation.

Required fix:

Produce an observed-data combined GoF toy ensemble, or a documented replacement
accepted by the methodology, for the final visible-mass baseline. Store the toy
distribution and observed statistic, quote the p-value, and state PASS/FAIL.

## Category B Findings

### B1. The final AN still lacks the required Phase 1 limitation/decision index

The AN discusses some limitations in prose, but it does not include the
appendix-level limitation index collecting all Phase 1 constraints, limitations,
and decisions with labels `[A1]`, `[L1]`, `[D1]`, etc.

Evidence:

- `methodology/analysis-note.md:265-280` requires a limitation index appendix
  collecting all Phase 1 labels and their impact/mitigation.
- Searching the final AN finds no `[D#]`, `[L#]`, `[A#]`, or "Limitation Index"
  entries. The note has a short unlabelled limitations section at
  `ANALYSIS_NOTE_5_v1.md:457-463`.
- Phase 1 defines binding decisions including visible mass as the baseline
  (`STRATEGY.md:73-80`), category/likelihood decisions (`STRATEGY.md:118-137`),
  and the alternative-observable gate (`STRATEGY.md:140-145`,
  `STRATEGY.md:295-299`).

Impact:

I can verify the most important decision, [D9], from the current artifacts:
the AN keeps the classifier as rejected (`ANALYSIS_NOTE_5_v1.md:422-434`) and
the final metadata has a visible-mass `final_result_model`
(`observed_results.json:1159`). But a referee cannot trace all Phase 1
commitments from the final note alone. This weakens the standalone Phase 5
package and should be fixed before PASS.

### B2. The reproduction contract is still too thin for the AN completeness test

The note now has a command table, but it lacks the full reproduction contract
required by the analysis-note spec.

Evidence:

- `methodology/analysis-note.md:287-296` requires environment setup, exact pixi
  task sequence with expected outputs, workflow DAG, manual steps, and runtime
  estimates.
- The AN gives only a command/purpose table at `ANALYSIS_NOTE_5_v1.md:467-478`
  plus a source-artifact table at `ANALYSIS_NOTE_5_v1.md:480-489`. It does not
  list expected outputs per command, runtime estimates, a DAG, or manual data
  setup requirements.

Impact:

This is improved over the previous version, but it still does not let an
unfamiliar physicist reproduce every number from the AN alone.

### B3. Some retained supporting figures still have older figure-style issues

The new headline figures are substantially cleaner, but the retained appendix
figures still include older labels and style choices. This should be handled by
the plot validator, but the final AN includes those figures and therefore they
remain part of the Phase 5 package.

Evidence:

- The AN includes the supporting figures in Appendix D
  (`ANALYSIS_NOTE_5_v1.md:544-568`).
- Visual inspection of `mt_mu_met.png` and `qcd_same_sign_mvis.png` shows the
  older combined label "Open Data + Open Simulation" rather than the standard
  open-data/open-simulation label pattern, and `mt_mu_met.png` uses a compact
  code-like axis label for transverse mass. These are not as severe as the
  prior ratio-panel artifact in the final baseline plots, but they are still
  retained public figures.

Impact:

Not a standalone blocker relative to A1-A3, but the final rendering/plot pass
should either regenerate or explicitly accept these as appendix diagnostics.

## Mandatory Regression Checklist

| Checklist item | Status | Critical re-review assessment |
|---|---|---|
| Any validation test failures without 3 documented remediation attempts? | **Yes if top-level `observed_fit`/`validation_summary` are treated as the result; no if only `final_result` is used.** | The failed classifier remains in top-level aliases with `mu_hat = 38.38`, observed limit `50.0`, and validation flags true. Fix A1. No Phase 3/4 regression is required if the score aliases are fully demoted. |
| Any single systematic > 80% of total uncertainty? | **Not assessable.** | The AN explicitly lacks source-by-source impact refits (`ANALYSIS_NOTE_5_v1.md:342`, `461`). This is A2 and prevents the checklist from being completed. |
| Any GoF toy distribution inconsistent with observed chi2? | **Not assessable.** | No observed-data combined GoF toy ensemble is stored (`ANALYSIS_NOTE_5_v1.md:183`, `383`, `463`). This is A3. |
| Any flat-prior gate excluding > 50% of bins? | Not found in reviewed artifacts. | No evidence of a flat-prior bin-exclusion gate in the scoped outputs. |
| Any tautological comparison presented as independent validation? | Mostly resolved. | The score-vs-baseline material is now framed as a rejected diagnostic, not independent validation (`ANALYSIS_NOTE_5_v1.md:422-436`). |
| Any visually identical distributions that should be independent? | Not found in the re-review contact sheet. | No duplicate independent-distribution claim identified in the retained Phase 5 figures. |
| Any result with > 30% relative deviation from a well-measured reference value? | Resolved for the final result; still true for rejected score diagnostic. | The final baseline is interpreted as a weak limit with expected limit `10.7375`, not as a precision `mu` measurement (`ANALYSIS_NOTE_5_v1.md:442-455`). The rejected score `mu = 38.3802` is confined to the diagnostic section. |
| All binding commitments [D1]-[D9] fulfilled? | Partly assessable; [D9] appears fulfilled, full traceability missing. | [D9] required alternatives to replace visible mass only after validation (`STRATEGY.md:140-145`, `295-299`); the AN follows this. But the final AN lacks the required decision/limitation index, so complete label traceability remains B1. |
| Is the fit chi2 identically zero or within numerical precision? | No, but low zero-jet chi2 remains a caution. | Baseline combined chi2/ndf is `0.7224` and zero-jet chi2/ndf is `0.113` (`ANALYSIS_NOTE_5_v1.md:346`). Not identically zero, but the missing observed GoF toy p-value keeps this from being fully closed. |

## Final Assessment

The Phase 5 fix is directionally correct but incomplete. The visible-mass
baseline can be the final result, and the note now tells that story. It cannot
PASS until the machine-readable aliases stop leaking the failed score model and
the required baseline impact ranking plus observed GoF toy validation are added
or formally replaced by methodology-compliant artifacts.
