# Phase 5 Constructive Re-review: Full-Panel Fix

Scope: `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.{md,pdf}`,
`phase5_documentation/outputs/PAPER_PRL_v1.{md,pdf}`,
`phase5_documentation/outputs/figures/`, Phase 4c observed JSON outputs, and
the prior full-panel arbiter/fixer records.

Verdict: **ITERATE**. The full-panel fix resolved the central physics-framing
problem: the visible-mass baseline is now the final result and the calibrated
classifier is confined to a rejected diagnostic role. Remaining blockers are
documentation-process issues, not evidence that the baseline result itself is
being overclaimed.

No focused investigation subagent was spawned. The remaining concerns are
document/metadata checks that can be verified directly from the markdown, TeX,
BibTeX, and JSON artifacts.

## Category A Findings

### A1. Final bibliography/reference count is below the Phase 5 threshold

The Phase 5 content gate requires at least 15 unique references before
typesetting; fewer than 15 is a Category A failure in the Phase 5 instructions.
The current `references.bib` contains 11 entries:
`cms_open_data_htt_2012`, `cms_open_data_skim`, `cms_htt_2014`,
`cms_htt_2018`, `atlas_cms_higgs_combination_2016`, `pdg_2024`,
`pdg_higgs_status_2024`, `lhc_hxswg_yellow_report_4`, `cowan_asymptotic`,
`read_cls`, and `pyhf_joss`.

This is not just a numeric gate. A final H to tau tau search note should cite
the CMS luminosity reference, CMS detector/object-performance references
relevant to muons/tau_h/MET, Higgs discovery/context papers or equivalent
review material, and the specific Open Data/NanoAOD provenance where available.
The current AN has enough citations to avoid obvious fabrication, but not enough
for Phase 5 publication-depth documentation.

Evidence:

- `phase5_documentation/outputs/references.bib` has 11 BibTeX entries.
- Parsed AN citations resolve without `??` or `[?]`, so this is a completeness
  problem rather than a broken-citation problem.

Required fix: add verified, cited references until the AN/PRL bibliography has
at least 15 real entries, then rerun the BibTeX validator and PDF build.

### A2. Three appendix subsections violate the no-empty-section rule

The analysis-note and Phase 5 instructions require every `##`/`###` section
heading to be followed by prose before any figure or table. The current appendix
bin-yield subsections are immediately followed by tables:

- `ANALYSIS_NOTE_5_v1.md:497` `## VBF Bin Yields` is followed immediately by
  the table header at line 499.
- `ANALYSIS_NOTE_5_v1.md:508` `## Boosted Bin Yields` is followed immediately
  by the table header at line 510.
- `ANALYSIS_NOTE_5_v1.md:519` `## Zero-Jet Bin Yields` is followed immediately
  by the table header at line 521.

This is a mechanical Phase 5 Category A issue. The fix is small: add 2-3
sentences under each heading explaining what the table contains, how the reader
should use it, and which validation/result figure it supports.

## Category B Findings

### B1. PRL draft still misses the required published-comparison table

The Phase 5 PRL deliverable requires, at minimum, a flagship result figure, a
table comparing the open-data result with meaningfully comparable CMS Run 1/Run
2 and PDG/world-average context, and a compact signal/background or
limit/significance summary table. The current PRL is much improved over the
prior stub: it has 62 markdown lines, two figures, a category table, a
background-model section, and honest baseline-only framing. It still has no
published-comparison table.

Evidence:

- `PAPER_PRL_v1.md:47-56` discusses CMS/ATLAS+CMS context in prose.
- The only PRL table is the category data/background/signal table at
  `PAPER_PRL_v1.md:34-39`; there is no table comparing this result with CMS
  2014, CMS 2018, ATLAS+CMS, or PDG/HXSWG context.

Required fix: add a compact comparison table mirroring the AN comparison
content, with the final visible-mass limit clearly marked as low-sensitivity
and not directly equivalent to the full CMS measurements.

### B2. PRL method/result presentation is still very thin

The PRL is now reviewable as a draft, but it remains closer to an extended
abstract than a PRL-style paper. It has no displayed statistical-model equation
or CLs definition, no compact systematic table, and no explicit expected-limit
band table. This is not the same blocker as the original skeletal PRL finding,
because the current draft does contain method, background, figures, citations,
and a result. It should still be strengthened before PASS.

Evidence:

- `PAPER_PRL_v1.md` has 62 lines, two figures, five table lines, and zero
  display equations.
- The abstract quotes the result, and `PAPER_PRL_v1.md:47-56` gives the
  interpretation, but the statistical method is only one sentence in
  `PAPER_PRL_v1.md:20-23`.

Suggested fix: add one CLs/profile-likelihood equation or concise formula
statement, a one-row expected/observed limit table, and a compact systematic
table. Keep the prose concise.

## Resolved Prior Constructive Findings

The full-panel fix materially improved the AN.

- Baseline-only framing is now honest. The abstract states
  `visible_mass_qcd_primary` is the only final-result model and that the
  classifier is a rejected diagnostic.
- Machine-readable roles are now consistent enough for the final-result path:
  `observed_results.json` contains `final_result` with model
  `visible_mass_qcd_primary` and role `final_result`, while
  `category_mu_comparison.json` labels `calibrated_score_qcd_primary` as
  `diagnostic_failed_validation`.
- Baseline numbers match the Phase 4c baseline JSON: `mu_hat = 0.4382286420`,
  observed limit `10.7644674446`, median expected limit `10.7375351289`,
  and discovery diagnostic `Z = 0.0949388888`.
- Baseline validation is now documented in the AN. The JSON gives combined
  `data/background = 0.9811787200`, `chi2/ndf = 0.7223857883`, and all
  validation flags false; the AN includes the baseline validation section,
  category table, and visible-mass validation figures.
- Data-driven background corrections now include equations and counts: W
  high-mT scale at `ANALYSIS_NOTE_5_v1.md:113-117`, VBF background scale at
  lines 122-127, and same-sign QCD/fake transfer at lines 132-139.
- The systematic section now has per-source subsections, starting with the
  source table at `ANALYSIS_NOTE_5_v1.md:189` and subsections for luminosity,
  tau/open-data acceptance, DY/Z normalization, W, VBF, QCD/fake, and MC stat.
- Figure references resolve: 31 unique `figures/*.pdf` references in the AN
  all exist under `phase5_documentation/outputs/figures/`.
- The generated TeX has no unresolved `??`, no `[?]`, no `\$\pm\$` artifact,
  no `\subfloat`, and no literal `Overfull` text in the TeX source.

## Constructive Notes

The final physics story is now the right one: this is a validated but weak
visible-mass Open Data limit, not evidence for H to tau tau and not a
successful classifier result. Preserve that framing. The next fix should be
narrow: reference completeness, appendix prose, and PRL comparison/method
compactness. No Phase 3/4 regression is indicated by this constructive
re-review.
