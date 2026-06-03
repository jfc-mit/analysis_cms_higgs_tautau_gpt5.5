# Phase 5 Critical Review: Optimized-Score and Baseline Consistency

Review scope: final AN/PRL propagation of the optimized-score result and the previous visible-mass baseline; numerical consistency of `mu_hat`, asymmetric uncertainties, 95% CLs limits, expected limits, and gate status across the Phase 5 AN/PRL drafts and Phase 4c JSON result artifacts.

Verdict: **FAIL** due to Category A findings.

## Category A Findings

### A1. `PAPER_PRL_v1.md` is stale/incomplete and omits the required baseline comparison and validation-gate interpretation

The PRL markdown output contains only the optimized calibrated-score fit:

- `phase5_documentation/outputs/PAPER_PRL_v1.md:3-6` states only `mu = 38.380 +7.035 -6.116`, observed limit `mu < 50.000`, and median expected limit `1.974`.
- The same file has only 6 total lines and contains no baseline `mu = 0.438...`, no baseline 95% CLs limit, no "gate fail" statement, and no statement that the validated result is the frozen visible-mass baseline.

This conflicts with the required Phase 5 documentation state and with the PRL TeX:

- `phase5_documentation/outputs/PAPER_PRL_v1.tex:21-23` states that the optimized score fails the gate and gives the previous visible-mass baseline `mu=0.438^{+4.944}_{-0.438}`, 95% CLs `mu<10.764`.
- `phase5_documentation/outputs/PAPER_PRL_v1.tex:83-90` repeats the primary expected limit, observed limit, optimized `mu`, gate failure, and baseline retention.

Because both `.md` and `.tex` are final outputs in the review scope, the PRL markdown must not remain stale. This is a blocking documentation inconsistency.

### A2. The quoted asymmetric `mu` uncertainties are not present in the scoped JSON result artifacts

The final AN and PRL quote asymmetric profile-likelihood intervals:

- `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:13-17` quotes optimized `mu = 38.3802 +7.0346 -6.1157` and baseline `mu = 0.4382 +4.9443 -0.4382`.
- `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:118` repeats the optimized interval as a `q(mu)=1` interval.
- `phase5_documentation/outputs/PAPER_PRL_v1.tex:19-23` quotes the same optimized and baseline asymmetric intervals, rounded to three decimals.

However, the scoped result JSONs do not contain those interval values:

- `phase4_inference/4c_observed/outputs/observed_results.json:1746-1765` contains primary `z_value = 12.469838725635482`, `mu_hat = 38.380184326872644`, expected band `[0.9950816985, 1.4126708245, 1.9735117796, 2.9107104020, 4.1765740322]`, and observed limit `50.0`, but no interval endpoints or asymmetric errors.
- `phase4_inference/4c_observed/outputs/baseline_previous_result.json:3-22` contains baseline `z_value = 0.09493888883239246`, `mu_hat = 0.43822864200217504`, expected band `[5.4271068787, 7.4538206192, 10.7375351289, 15.7353539553, 22.4849409859]`, and observed limit `10.764467444563975`, but no interval endpoints or asymmetric errors.
- Parser check of the scoped JSON fit objects found only `['discovery_diagnostic', 'interpretation', 'mu_hat', 'npars', 'observed_upper_limit', 'parameters', 'status']` for both primary and baseline observed fits, and the `observed_upper_limit` object contains only `['expected_band_minus2_minus1_median_plus1_plus2', 'method', 'observed_limit', 'result_count', 'scan', 'status']`.

Therefore the asymmetric uncertainties cannot be numerically checked against the specified authoritative JSON artifacts. Since these intervals are quoted as final result numbers, the JSON provenance must be added or the AN/PRL must cite the artifact that actually contains the interval calculation.

## Category B Findings

### B1. Baseline expected limit is present in JSON but absent from the AN/PRL baseline comparison

The frozen baseline JSON gives the expected 95% CLs band:

- `phase4_inference/4c_observed/outputs/baseline_previous_result.json:14-22` gives the median expected baseline limit `10.737535128866` and observed limit `10.764467444563975`.

The final AN and PRL include the baseline `mu_hat` and observed limit but omit the baseline expected limit:

- `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:123`, `171-172`, and `194` quote baseline `mu` and observed `95% CLs mu < 10.7645`, but not expected `mu < 10.7375`.
- `phase5_documentation/outputs/PAPER_PRL_v1.tex:23`, `73`, and `89-90` quote the same baseline `mu` and observed limit, but not the baseline expected limit.

Given this review scope explicitly includes expected limits, the baseline expected limit should be reported wherever the baseline result is compared numerically to the optimized score, or the text should state that the comparison is intentionally restricted to `mu_hat` and observed limit.

## PASS Checks

- Optimized-score central value, observed 95% CLs limit, expected median limit, and significance are numerically consistent between JSON and the final AN/PRL TeX: JSON has `mu_hat = 38.380184326872644`, `z_value = 12.469838725635482`, median expected limit `1.9735117795854344`, and observed limit `50.0` at `observed_results.json:1746-1765`; AN quotes `38.3802`, `12.4698`, expected `1.9735`, and observed `50.0000` at `ANALYSIS_NOTE_5_v1.md:116-122`; PRL TeX quotes rounded `38.380`, `12.470`, expected `1.974`, and observed `50.000` at `PAPER_PRL_v1.tex:72` and `83-88`.
- Baseline central value, observed limit, significance, and validation pass status are consistent between `baseline_previous_result.json` and the final AN/PRL TeX: JSON has `mu_hat = 0.43822864200217504`, `z_value = 0.09493888883239246`, observed limit `10.764467444563975`, and `score_modeling_status = pass` at `baseline_previous_result.json:3-22` and `170-192`; AN quotes `mu = 0.4382 +4.9443 -0.4382`, `95% CLs mu < 10.7645`, and significance `0.095` at `ANALYSIS_NOTE_5_v1.md:123`, `171-172`, and `194`; PRL TeX quotes rounded `mu=0.438^{+4.944}_{-0.438}`, `95% CLs mu<10.764`, and significance `0.095` at `PAPER_PRL_v1.tex:23`, `73`, and `89-90`.
- Gate status is correctly interpreted in the AN and PRL TeX: primary JSON has `combined_ratio_failure = true`, `high_score_shape_failure = true`, and `score_modeling_status = flagged` at `observed_results.json:2634-2656`; AN states the optimized-score gate is `fail` and keeps the visible-mass baseline at `ANALYSIS_NOTE_5_v1.md:122` and `125-129`; PRL TeX states the fit fails the observed validation gate and retains the baseline at `PAPER_PRL_v1.tex:21-23` and `87-90`.
- Add-MET, BDT, and `m_addmet` diagnostics are not presented as final methods in the scoped final AN/PRL files. A case-insensitive search of `ANALYSIS_NOTE_5_v1.md`, `PAPER_PRL_v1.md`, and `PAPER_PRL_v1.tex` for `add[-_ ]?met`, `m_addmet`, `bdt`, and `boosted decision` found no matches except `ANALYSIS_NOTE_5_v1.md:119`, where `q0 Z` is explicitly labelled `diagnostic only`.
