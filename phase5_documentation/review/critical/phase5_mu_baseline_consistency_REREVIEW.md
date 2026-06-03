# Phase 5 Critical Re-Review: Mu Baseline Consistency Fixes

Scope: only the three prior findings:

1. `PAPER_PRL_v1.md` stale/incomplete.
2. Profile `mu` asymmetric uncertainties absent from authoritative JSON result artifacts.
3. Baseline expected limit absent from AN/PRL baseline comparison.

Verdict: **PASS**. All three prior findings are resolved.

## Checks

- Prior A1 resolved: `phase5_documentation/outputs/PAPER_PRL_v1.md` now includes the optimized-score result, observed and expected limits, gate-fail statement, and baseline comparison. Evidence: lines 3-9 quote optimized `mu = 38.380 +7.035 -6.116`, observed `mu < 50.000`, expected `mu < 1.974`, and observed validation gate `fail`; lines 11-13 quote baseline `mu = 0.438 +4.944 -0.438`, observed `mu < 10.764`, median expected `mu < 10.738`, and state that both comparison figures include the optimized attempt and frozen baseline.

- Prior A2 resolved: the authoritative JSON artifacts now contain profile-interval provenance. Evidence: `phase4_inference/4c_observed/outputs/observed_results.json:1914-1922` gives primary `profile_mu_interval` with `err_minus = 6.115738764114099`, `err_plus = 7.034615086870787`, `lower = 32.264445562758546`, `upper = 45.41479941374343`, and `mu_hat = 38.380184326872644`, matching the AN/PRL rounded `38.3802 +7.0346 -6.1157` / `38.380^{+7.035}_{-6.116}`. `phase4_inference/4c_observed/outputs/baseline_previous_result.json:156-164` gives baseline `profile_mu_interval` with `err_minus = 0.43822864200217504`, `err_plus = 4.944327747891604`, `lower = 0.0`, `upper = 5.38255638989378`, and `mu_hat = 0.43822864200217504`, matching the AN/PRL rounded `0.4382 +4.9443 -0.4382` / `0.438^{+4.944}_{-0.438}`.

- Prior B1 resolved: the baseline expected limit is now included in the AN and PRL comparison text. Evidence: the JSON baseline median expected limit is `10.737535128866` at `phase4_inference/4c_observed/outputs/baseline_previous_result.json:14-22`; the AN quotes median expected `mu < 10.7375` in the abstract at `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md:13-17`, in the result table at `ANALYSIS_NOTE_5_v1.md:114-123`, in the published-results comparison table at `ANALYSIS_NOTE_5_v1.md:169-172`, and in the conclusion at `ANALYSIS_NOTE_5_v1.md:191-194`. The PRL markdown quotes median expected `mu < 10.738` at `phase5_documentation/outputs/PAPER_PRL_v1.md:11-13`, and the PRL TeX quotes exp. `mu<10.738` at `phase5_documentation/outputs/PAPER_PRL_v1.tex:23-24`, `73-74`, and `84-90`.

No remaining Category A/B/C findings within this re-review scope.
