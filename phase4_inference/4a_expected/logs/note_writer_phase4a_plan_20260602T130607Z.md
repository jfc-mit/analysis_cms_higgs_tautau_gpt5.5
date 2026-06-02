# Phase 4a Note Writer Plan

Timestamp: 2026-06-02T13:06:07Z

## Role and Scope

This note-writer pass produces `phase4_inference/4a_expected/outputs/ANALYSIS_NOTE_4a_v1.md` and `phase4_inference/4a_expected/outputs/references.bib`.
The note is expected-only: the Phase 4a observation is background-only Asimov pseudo-data from the nominal MC templates, and no observed full-data signal-region results will be presented.
The analysis is treated as a search/template-fit analysis under Phase 1 decision [D1] and `conventions/search.md`; any phase-local measurement wording is stale.

## Inputs Read

- Role and local instructions: `agents/note_writer.md`, `AGENTS.md`.
- Methodology: `methodology/analysis-note.md`, `methodology/05-artifacts.md`, `methodology/appendix-plotting.md`, `methodology/appendix-checklist.md`.
- Convention: `conventions/search.md`.
- Upstream artifacts and logs: `prompt.md`, `phase1_strategy/outputs/STRATEGY.md`, `phase2_exploration/outputs/EXPLORATION.md`, `phase2_exploration/outputs/local_sample_manifest.json`, `phase2_exploration/outputs/FINAL_AN_SAMPLE_LIMITATION_OBLIGATIONS.md`, `phase3_selection/outputs/SELECTION.md`, `COMMITMENTS.md`, and `experiment_log.md`.
- Numerical sources: `phase3_selection/outputs/category_yields.json`, `phase3_selection/outputs/region_yields.json`, `phase3_selection/outputs/normalization_inputs.json`, `phase3_selection/outputs/variable_modeling.json`, `phase4_inference/4a_expected/outputs/expected_results.json`, `phase4_inference/4a_expected/outputs/nominal_yields.json`, `phase4_inference/4a_expected/outputs/systematics.json`, `phase4_inference/4a_expected/outputs/signal_injection.json`, `phase4_inference/4a_expected/outputs/gof_validation.json`, and `phase4_inference/4a_expected/outputs/limitations_downscope.json`.

## Figure Inventory

Required main-text figures:
- Phase 2 provenance and feature availability: `sample_event_count_file_size.pdf`, `branch_feature_availability.pdf`.
- Phase 3 selection and region validation: `cutflow_summary.pdf`, `category_yields.pdf`, `w_high_mt_control_mt.pdf`, `qcd_same_sign_mvis.pdf`, `z_rich_validation_mvis.pdf`.
- Phase 3 selected-variable diagnostics: `mu_pt.pdf`, `tau_pt.pdf`, `met_pt.pdf`, `mt_mu_met.pdf`, `pt_tautau_proxy.pdf`, `clean_jet_multiplicity.pdf`, `vbf_dijet_mass.pdf`, `vbf_delta_eta_jj.pdf`.
- Phase 3 approach/downscope diagnostics: `approach_comparison.pdf`, `mva_input_modeling_chi2.pdf`.
- Phase 4a expected fit figures: `expected_mvis_vbf.pdf`, `expected_mvis_boosted.pdf`, `expected_mvis_zero_jet.pdf`, `expected_s_over_b.pdf`, `expected_nuisance_summary.pdf`, `signal_injection_recovery.pdf`, `gof_toys.pdf`.

Optional appendix figures:
- Phase 2 first-candidate variable survey plots are included in an appendix figure group because they document early feasibility and branch range checks but are superseded by Phase 3 final-candidate plots.
- Phase 3 visible-mass and add-MET mass template diagnostics by category are included in an appendix because the Phase 4a expected templates supersede visible mass for the primary model, while the add-MET panels document the downscoped alternative.

Figure placement will use `<!-- COMPOSE: ... -->` comments before related groups as requested. Captions will be 2-5 interpretive sentences with pandoc-crossref labels.

## Section Structure

The AN will use the full stable Phase 4a structure:

1. `# Change Log {-}` first content section, initialized with "Initial AN version (Phase 4a)."
2. `# Introduction` with search motivation, open-data scope, reference-analysis context, and expected-only staging.
3. `# Data Samples` with data summary table, MC sample table, normalization provenance, missing sample inventory, and provenance figures.
4. `# Event Selection` with trigger policy, object definitions, region definitions, category definitions, cutflow, control/validation regions, and selected-variable figures.
5. `# Template Construction and Statistical Model` as the search-analysis analogue of correction methodology, including displayed equations for MC weights, bin yields, likelihood, profile likelihood ratio, CLs, signal injection, and saturated GoF.
6. `# Systematic Uncertainties` with one subsection per implemented source and a downscoped-source table.
7. `# Cross-Checks and Validation` with signal injection, GoF toy caveat, Phase 3 validation remediation, MVA gate, and alternative-observable handling.
8. `# Expected Results` with nominal yields, expected CLs band, discovery diagnostic, and expected template figures.
9. `# Comparison to Prior Results and Theory` with quantitative context against CMS 2014, CMS 2018, and combined Run 1 references, explicitly caveated as not a direct observed comparison.
10. `# Conclusions` stating the Phase 4a expected-only result and that observed results are deferred.
11. `# Future Directions` listing concrete Phase 4b/4c/5 additions.
12. `# Known Limitations and Open Questions` with major limitations and quantitative or scoped impacts where available.
13. Appendices: limitation index, numerical source map, sample lookup tables, auxiliary figures, reproduction contract, and note self-check.

## Required Tables

- Change Log group for Phase 4a v1.
- Data sample table: Run2012B/C TauPlusX luminosity, official record events, local entries, record IDs/DOIs.
- MC sample table: process, generator, cross section, `N_gen`, local entries, weight, record ID/DOI.
- Selection/category raw yields by sample or role.
- Control/validation-region raw yields summary.
- Expected nominal yield table by category with signal, background, S/sqrt(B), and minimum background bin.
- Expected CLs result table with observed-on-Asimov and median band.
- Signal injection table.
- GoF toy summary table.
- Implemented systematic summary table.
- Systematic completeness table versus search conventions and CMS references.
- Downscoped limitation table and missing sample/component table.
- Citation/source map table for external numeric inputs.

## Systematic Subsections

Implemented systematic subsections will use the physical-origin, evaluation-method, numerical-impact, and interpretation template:

- Luminosity normalization (`lumi_2012`, 2.6%).
- DY/Z normalization (`dy_norm_open_data`, 15%).
- Tau trigger/ID/open-data acceptance (`tau_open_data_acceptance`, 15%).
- Per-category MC statistical uncertainty (`staterror`, per-bin sqrt(sum weights squared)).

Downscoped systematic and model limitations will be grouped after the implemented subsections: tau energy scale, muon efficiency scale, JES/JER/MET, pileup, PDF/scale/UE/PS, QCD multijet, and missing paper-level sample components.

## Change Log Entries

`# Change Log {-}` will contain:

**Phase 4a v1**
- Initial AN version (Phase 4a).
- Added expected-only visible-mass pyhf template-fit model, Asimov expected CLs limit, discovery diagnostic, signal injection, GoF toy caveat, systematic program, limitations, and reproduction contract.
- Recorded that 10% validation and full observed signal-region results are intentionally absent until Phase 4b and Phase 4c unblinding gates.

## Verification Plan

- Verify all referenced figures exist from the AN file's directory.
- Run a markdown/numeric self-check using pixi Python: count display equations, markdown figures, table labels, systematic subsections, comparison statements, and source-value consistency for key JSON numbers.
- Run `git diff --check`.
- Commit only note-writer outputs with `docs(phase4a): draft expected analysis note`.

## Milestone Log

- 2026-06-02T13:06:07Z: Produced the required note-writing plan before drafting the AN.
- 2026-06-02T13:xx: Drafted `phase4_inference/4a_expected/outputs/ANALYSIS_NOTE_4a_v1.md` and `phase4_inference/4a_expected/outputs/references.bib`.
- 2026-06-02T13:xx: Self-check passed with 16 display equations, 40 figure references, 19 table labels, 4 implemented systematic subsections of 4, 2 quantitative comparison statements, 526 words in the statistical-method section, implemented systematic subsection word counts of 159, 192, 182, and 155, no missing figure files, no sparse figure captions, and no key JSON value mismatches.
- 2026-06-02T13:xx: `references.bib` contains 20 entries and no title fields with LaTeX math delimiters.
