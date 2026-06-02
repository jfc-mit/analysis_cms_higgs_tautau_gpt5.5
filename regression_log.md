# Regression Log

## 2026-06-02T13:41:46Z - Sensitivity regression investigation

Investigator session: `investigator_sensitivity_20260602T134146Z`

Trigger: the expected Phase 4a discovery diagnostic is only `Z = 0.191` and
the median expected CLs limit is `mu = 11.374`, much weaker than the
order-of-magnitude sensitivity suggested by CMS-HIG-13-004 for a full Run 1
H->tau tau analysis.

Verdict: regression ticket written in
`phase3_selection/REGRESSION_TICKET_sensitivity.md`. The recommended origin
phase is Phase 3 selection/discriminant/category design, with a secondary
Phase 4a model-audit component.

Required cascade: re-run Phase 3 sensitivity remediation, Phase 3 review,
Phase 4a expected model, Phase 4a note writing/typesetting, and full Phase 4a
review before advancing to Phase 4b.
