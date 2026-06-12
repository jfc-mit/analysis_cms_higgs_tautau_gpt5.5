# Phase 5 Constructive Review: Final AN and PRL Draft

Scope: `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.{md,tex,pdf}`,
`phase5_documentation/outputs/PAPER_PRL_v1.{md,tex,pdf}`, upstream phase
artifacts, `experiment_log.md`, applicable search conventions, and final
figures under `phase5_documentation/outputs/figures/`.

Verdict: **FAIL**. The headline numerical propagation is mostly consistent
with the machine-readable Phase 4c outputs, but the final AN is not yet a
standalone reproducible analysis note, and the retained visible-mass baseline is
not documented with enough validation detail for publication-quality review.

## Category A Findings

### A1. The final AN is not reproducible from the note alone

The analysis-note specification requires a reader to be able to reproduce every
number from the AN alone, including sample tables, validation definitions,
systematic-source subsections, statistical-method details, and a reproduction
contract. The current AN has only seven numbered content sections
(`Data And Simulation`, `Event Selection And Categories`, `QCD And W Control
Corrections`, `Optimized Score Result And Baseline`, `Comparison With Published
Results`, `Conclusion`, and `References`) across 198 markdown lines in
`ANALYSIS_NOTE_5_v1.md`.

Concrete gaps:

- `ANALYSIS_NOTE_5_v1.md:28-39` describes the data and MC in prose but has no
  structured data-period table, no MC process table with generated events,
  cross sections, denominators, and weights, and no luminosity table.
- `ANALYSIS_NOTE_5_v1.md:48-58` lists the event selection but does not give a
  cutflow table with yields after each requirement; only a cutflow figure is
  included at lines 66-69.
- `ANALYSIS_NOTE_5_v1.md:73-90` quotes W, VBF, and QCD/fake correction values
  but does not give the equations, numerator/denominator counts, transfer
  factors by category/bin, or uncertainty propagation needed to reproduce the
  values.
- `ANALYSIS_NOTE_5_v1.md:108-112` lists nuisance terms in one sentence, but
  there is no systematic-uncertainty section, no per-source motivation table, no
  per-source impact table, and no impact figures.
- There is no reproduction appendix or command sequence. The Phase 4 artifacts
  contain runnable task names, but the final AN does not tell a reader how to
  regenerate the full chain and final documents.

This is a blocking issue because the final AN currently points to results
rather than documenting the derivation of those results.

### A2. Data-driven background corrections lack final-note validation detail

The retained baseline and the failed optimized-score attempt both depend on
data-driven corrections, but the AN does not document the validation standards
required for a search background model. Search conventions require closure in
validation regions, transfer-factor stability, and goodness-of-fit checks before
using CR-derived predictions in the signal region.

Evidence:

- The full-data W scale is quoted as `0.8528 +/- 0.0370` at
  `ANALYSIS_NOTE_5_v1.md:73-77`, but the note does not give the high-mT control
  region counts or formula. The machine output
  `phase4_inference/4c_observed/outputs/wjets_highmt_scale_full.json` records
  the applied scale factor `0.8528436634946431` and status `valid`, but the AN
  does not reproduce the derivation.
- The VBF background scale is quoted as `0.5571 +/- 0.0515` at
  `ANALYSIS_NOTE_5_v1.md:79-85`. The machine output
  `phase4_inference/4c_observed/outputs/vbf_background_scale.json` records this
  as a single scale applied only to MC backgrounds in VBF. The AN does not show
  the control-region composition, closure check, or stability against alternative
  VBF-like definitions.
- The same-sign QCD/fake correction is summarized at
  `ANALYSIS_NOTE_5_v1.md:87-90` with a single transfer factor
  `0.0204 +/- 0.2533`. The machine output
  `phase4_inference/4c_observed/outputs/qcd_sideband_estimates.json` records
  explicit limitations: no anti-isolated tau branch, a transfer factor measured
  in the lowest observable bin and propagated globally, and VBF MC-background
  scaling before non-QCD subtraction. The AN does not discuss these limitations
  or quantify their impact on the baseline result.

The issue is not that the corrections are necessarily invalid; it is that the
final note does not provide enough evidence for a referee to judge whether they
are valid.

### A3. The final systematic program is not documented at Phase 5 quality

The Phase 4a systematic artifact records implemented sources, partial sources,
and downscopes: luminosity, DY/Z normalization, tau/open-data acceptance, W
control, MC statistics, signal theory/acceptance, QCD, and missing diboson/top
components. The final AN collapses this to a short list of modifiers at
`ANALYSIS_NOTE_5_v1.md:108-112` and a few limitations in the data section.

Required missing material:

- A table mapping each systematic source to its motivation, value, affected
  samples/channels, correlation model, and artifact source.
- Per-source impact on the optimized-score fit and on the retained visible-mass
  baseline.
- A statement of which systematics were re-evaluated at the final baseline
  operating point and which were transferred with quantitative justification.
- An error-budget narrative explaining whether the retained baseline is
  statistically limited, systematically limited, or limited by missing reduced
  samples.

Because the final result is explicitly a reduced Open Data study with major
missing components, the systematic section is central to the physics
credibility. Its absence is Category A.

### A4. The retained baseline is not documented as the actual result with enough detail

The AN correctly states that the optimized score fails the observed validation
gate and that the visible-mass baseline is retained:
`ANALYSIS_NOTE_5_v1.md:125-129` and `191-195`. However, the note gives almost
all detailed figures and validation prose to the failed optimized-score model.

Evidence:

- The result table at `ANALYSIS_NOTE_5_v1.md:116-123` gives six rows for the
  optimized score and only one compact row for the visible-mass baseline.
- The validation figures at `ANALYSIS_NOTE_5_v1.md:131-148` are all
  optimized-score category diagnostics; no visible-mass category validation
  figures are included in the AN, even though the baseline is the retained
  result.
- The baseline machine output has a passing validation summary:
  `baseline_previous_result.json` records combined `chi2/ndf = 0.7224`,
  `data/background = 0.9812`, and `score_modeling_status = pass`. These numbers
  are not presented in the final AN.

To pass, the retained baseline needs its own method subsection, category yield
table, visible-mass validation plots, GoF summary, nuisance summary, and
comparison to the failed optimized attempt. A reader should not have to infer
the validated result from a single table row.

## Category B Findings

### B1. Public-facing process-history wording weakens the standalone framing

The AN and PRL draft should read as current analysis outputs, not a chronology
of earlier iterations. Current wording includes:

- `ANALYSIS_NOTE_5_v1.md:21-24`: "Phase 5 v3 updates..." and "previous
  visible-mass result as a frozen baseline".
- `ANALYSIS_NOTE_5_v1.md:123`: "Frozen baseline visible-mass result" and
  "previous primary result before this update".
- `ANALYSIS_NOTE_5_v1.md:150-153`: "frozen previous visible-mass baseline".
- `PAPER_PRL_v1.md:11-13`: "previous visible-mass result" and "frozen
  baseline".

The physics content can remain the same, but the prose should be recast as a
standalone model comparison: "validated visible-mass baseline" versus
"optimized classifier model rejected by the validation gate."

### B2. The comparison with published CMS results is quantitative but not yet interpretive enough

The AN includes a useful comparison table at `ANALYSIS_NOTE_5_v1.md:169-177`,
but it does not compute pulls or resolving power. The retained baseline has
`mu = 0.4382 +4.9443 -0.4382`, observed limit `mu < 10.7645`, and expected
limit `mu < 10.7375`, while CMS Run 1 reports `mu = 0.78 +/- 0.27` and CMS
2018 reports about `mu = 1.09 +/- 0.27`.

The AN should explicitly state:

- The retained baseline is statistically compatible with the published signal
  strengths because its uncertainty is much larger than the CMS publication
  precision.
- Its expected limit near `mu < 10.74` means it has no Standard Model resolving
  power; it cannot distinguish `mu = 1` from background at publication-analysis
  precision.
- The optimized-score attempt would have good expected sensitivity
  (`mu < 1.9735`) but is rejected because the observed fit gives
  `mu_hat = 38.3802` and `Z = 12.4698`, with validation failures recorded in
  the machine output.

This would make the comparison honest and more useful to a journal referee.

### B3. The PRL draft is too skeletal to review as a paper draft

`PAPER_PRL_v1.md` is 14 lines and contains no citations, figures, method
description, background-model description, or result table. It states the
optimized-score failure and retained baseline correctly, but it is not yet a
paper draft in any meaningful sense. At minimum, it needs the final result
table, the validated-baseline figure, one comparison figure, concise method
prose, and citations matching the AN.

### B4. The optimized-score failure could be made clearer in the final figures

The AN text says the optimized score fails, but the current figure set still
labels several optimized-score plots as "primary" and includes final comparison
figures centered on the failed model. This is visible in figure references such
as `observed_primary_score_vbf.pdf`, `phase5_primary_vs_baseline_mu.pdf`, and
`phase5_significance_comparison.pdf`.

For clarity, rename captions and labels around the analysis decision:
"optimized classifier attempt" for the rejected model and "validated
visible-mass baseline" for the retained result. Include at least one figure
showing the baseline visible-mass agreement in the main results section.

## Category C Suggestions

- Add a compact "analysis decision table" with columns: model, expected limit,
  observed `mu_hat`, observed limit, validation status, final role. This would
  make the baseline-retention logic transparent.
- In the abstract, replace the long inline baseline number with a short
  sentence plus a result table reference once the AN has a proper results table.
- Add a small schematic of the control-region flow: high-mT W scale,
  VBF-like background scale, same-sign QCD/fake transfer, and signal-region fit.

## Standalone Artifact Check

I did not find non-analysis source names in the final AN or PRL markdown/TeX
files. The public-facing issue is instead generic process-history wording such
as "Phase 5 v3", "previous", and "frozen", which should be rewritten into
standalone analysis language.

## Positive Elements To Preserve

- The AN does not hide the optimized-score failure: it quotes
  `mu_hat = 38.3802`, observed limit `mu < 50.0000`, `Z = 12.4698`, and gate
  `fail` at `ANALYSIS_NOTE_5_v1.md:116-123`.
- The baseline headline numbers match the machine output: `baseline_previous_result.json`
  gives `mu_hat = 0.43822864200217504`, observed limit `10.764467444563975`,
  median expected limit `10.737535128866`, and passing validation summary; the
  AN quotes these rounded values at `ANALYSIS_NOTE_5_v1.md:16-17`,
  `123`, `171-172`, and `194-195`.
- The final comparison table correctly warns that the reduced Open Data result
  is not directly equivalent to the full CMS publication measurements.
