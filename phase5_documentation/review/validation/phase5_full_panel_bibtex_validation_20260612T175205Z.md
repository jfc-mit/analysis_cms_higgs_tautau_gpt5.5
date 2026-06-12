# Phase 5 BibTeX Validation

Session: `phase5_full_panel_bibtex_validation_20260612T175205Z`

Inputs reviewed:

- `phase5_documentation/outputs/references.bib`
- `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md`
- `phase5_documentation/outputs/PAPER_PRL_v1.md`

## Verdict

NEEDS FIX before bibliography PASS.

No Category A issues were found: every citation key used in the Markdown has a matching BibTeX entry, no cited DOI or arXiv identifier failed to resolve, and no cited entry appears fabricated.

Category B metadata issues remain in cited or retained bibliography entries.

## Citation Coverage

The analysis note contains 11 unique bibliography citations:

- `atlas_cms_higgs_combination_2016`
- `cms_htt_2014`
- `cms_htt_2018`
- `cms_open_data_htt_2012`
- `cms_open_data_skim`
- `cowan_asymptotic`
- `lhc_hxswg_yellow_report_4`
- `pdg_2024`
- `pdg_higgs_status_2024`
- `pyhf_joss`
- `read_cls`

`PAPER_PRL_v1.md` contains no bibliography citation tokens.

All cited keys are present in `references.bib`. No duplicate BibTeX keys were found. Required fields are present for all 22 entries. No title fields contain LaTeX math commands.

## Findings

### B-001: `cms_open_data_htt_2012` metadata does not match DOI record

Category: B

Location: `phase5_documentation/outputs/references.bib:1`

The DOI `10.7483/OPENDATA.CMS.GV20.PR5T` resolves to the expected CMS Open Data record title, so this is not a fabricated citation. However, the DOI metadata identifies the record as a 2019 software record authored by Stefan Wunsch. The BibTeX entry currently uses `author = {CMS Collaboration}` and `year = {2021}`.

Resolution: update the BibTeX author/year to match the public DOI metadata, or cite a different record whose metadata supports the current author/year.

### B-002: `lhc_hxswg_yellow_report_4` is missing an available DOI

Category: B

Location: `phase5_documentation/outputs/references.bib:199`

The arXiv record `1610.07922` resolves to the expected Yellow Report 4 title. The arXiv metadata also lists DOI `10.23731/CYRM-2017-002`, but the BibTeX entry lacks a `doi` field.

Resolution: add `doi = {10.23731/CYRM-2017-002}`.

### B-003: retained CMS Open Data orphan entries have DOI year mismatches

Category: B

Locations:

- `phase5_documentation/outputs/references.bib:10`
- `phase5_documentation/outputs/references.bib:19`
- `phase5_documentation/outputs/references.bib:28`
- `phase5_documentation/outputs/references.bib:37`
- `phase5_documentation/outputs/references.bib:46`
- `phase5_documentation/outputs/references.bib:55`
- `phase5_documentation/outputs/references.bib:64`
- `phase5_documentation/outputs/references.bib:73`
- `phase5_documentation/outputs/references.bib:82`
- `phase5_documentation/outputs/references.bib:91`

These entries are not cited by the reviewed Markdown files, but they remain in `references.bib`. Their DOIs resolve to real CMS Open Data records, but the BibTeX years disagree with DOI metadata:

- `cms_open_data_lumi_2012`: BibTeX 2017, DOI metadata 2020.
- `cms_open_data_run2012b_tauplusx`: BibTeX 2021, DOI metadata 2019.
- `cms_open_data_run2012c_tauplusx`: BibTeX 2021, DOI metadata 2019.
- `cms_open_data_ggh_htt`: BibTeX 2021, DOI metadata 2019.
- `cms_open_data_vbf_htt`: BibTeX 2021, DOI metadata 2019.
- `cms_open_data_dyjets`: BibTeX 2021, DOI metadata 2019.
- `cms_open_data_ttbar`: BibTeX 2021, DOI metadata 2019.
- `cms_open_data_w1jets`: BibTeX 2021, DOI metadata 2019.
- `cms_open_data_w2jets`: BibTeX 2021, DOI metadata 2019.
- `cms_open_data_w3jets`: BibTeX 2021, DOI metadata 2019.

Resolution: either remove these uncited entries or update their metadata before retaining them.

### C-001: orphaned BibTeX entries

Category: C

The following 11 entries are present in `references.bib` but are not cited by either reviewed Markdown file:

- `cms_lum_13_001`
- `cms_open_data_dyjets`
- `cms_open_data_ggh_htt`
- `cms_open_data_lumi_2012`
- `cms_open_data_run2012b_tauplusx`
- `cms_open_data_run2012c_tauplusx`
- `cms_open_data_ttbar`
- `cms_open_data_vbf_htt`
- `cms_open_data_w1jets`
- `cms_open_data_w2jets`
- `cms_open_data_w3jets`

Resolution: remove unused bibliography entries unless they are expected to be cited in a later revision.

## Per-Entry Validation Table

| Key | DOI | arXiv | Title match | Year | Status |
|---|---|---|---|---|---|
| `atlas_cms_higgs_combination_2016` | resolves: `10.1007/JHEP08(2016)045` | resolves: `1606.02266` | yes | BibTeX 2016, DOI 2016 | OK |
| `cms_htt_2014` | resolves: `10.1007/JHEP05(2014)104` | resolves: `1401.5041` | yes | BibTeX 2014, DOI 2014 | OK |
| `cms_htt_2018` | resolves: `10.1016/j.physletb.2018.02.004` | resolves: `1708.00373` | yes | BibTeX 2018, DOI 2018 | OK |
| `cms_open_data_htt_2012` | resolves: `10.7483/OPENDATA.CMS.GV20.PR5T` | none | yes | BibTeX 2021, DOI 2019 | B-001 |
| `cms_open_data_skim` | none | none | source URL resolves through raw GitHub content | BibTeX 2021 | OK |
| `cowan_asymptotic` | resolves: `10.1140/epjc/s10052-011-1554-0` | resolves: `1007.1727` | yes | BibTeX 2011, DOI 2011 | OK |
| `lhc_hxswg_yellow_report_4` | missing from BibTeX; arXiv lists `10.23731/CYRM-2017-002` | resolves: `1610.07922` | yes | BibTeX 2017, report DOI 2017 | B-002 |
| `pdg_2024` | resolves: `10.1103/PhysRevD.110.030001` | none | yes | BibTeX 2024, DOI 2024 | OK |
| `pdg_higgs_status_2024` | none | none | PDF URL resolves | BibTeX 2024 | OK |
| `pyhf_joss` | resolves: `10.21105/joss.02823` | none | yes | BibTeX 2021, DOI 2021 | OK |
| `read_cls` | resolves: `10.1088/0954-3899/28/10/313` | none | yes | BibTeX 2002, DOI 2002 | OK |

## Public Artifact Scan

The reviewed Markdown files contain no obvious non-analysis provenance language matching the scan terms used in this validation pass.

## Validation Sources Used

- DOI content negotiation through `https://doi.org/{doi}`
- arXiv API records through `https://export.arxiv.org/api/query?id_list={eprint}`
- CERN Open Data record page for `https://opendata.cern/record/12350`
- CERN Document Server pages for `https://cds.cern.ch/record/1598864` and `https://cds.cern.ch/record/2215893`
- PDG 2024 Higgs review PDF URL
- Raw GitHub URL for `cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis` 2012 `skim.cxx`
