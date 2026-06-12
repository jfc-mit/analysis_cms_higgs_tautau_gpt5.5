# Phase 5 BibTeX Re-validation

Session: `phase5_full_panel_bibtex_rerevalidation_20260612T185726Z`

Inputs reviewed:

- `phase5_documentation/outputs/references.bib`
- `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md`
- `phase5_documentation/outputs/PAPER_PRL_v1.md`

## Verdict

NEEDS FIX before bibliography PASS.

The previous retained-orphan Open Data metadata problem has been fixed by removing the problematic unused CMS Open Data entries, and the Yellow Report 4 DOI is now present. All citation keys used by the AN and PRL draft have matching BibTeX entries. No duplicate keys were found, and no BibTeX title contains LaTeX math.

However, two cited entries still fail metadata title validation against their DOI/arXiv records. Under the BibTeX validator rubric, title mismatches against DOI/arXiv metadata are Category A because the bibliography record no longer accurately describes the linked bibliographic record.

## Citation Coverage

Unique citation keys used by the reviewed markdown files:

- `atlas_cms_higgs_combination_2016`
- `cms_htt_2014`
- `cms_htt_2018`
- `cms_open_data_htt_2012`
- `cms_open_data_skim`
- `cowan_asymptotic`
- `lhc_hxswg_yellow_report_4`
- `pdg_higgs_status_2024`
- `pyhf_joss`
- `read_cls`

All cited keys are present in `references.bib`.

`references.bib` contains one orphan entry:

- `pdg_2024`

This retained orphan is not problematic: its DOI resolves to the 2024 PDG Review of Particle Physics metadata with matching title, year, and lead author. This is a Category C cleanup warning only.

## Prior B Issue Re-check

| Prior issue | Current status |
|---|---|
| CMS Open Data cited metadata | Partially fixed: author and year now match DOI metadata, but the BibTeX title still does not match the DOI record title. See A-001. |
| Yellow Report DOI | Resolved: `lhc_hxswg_yellow_report_4` now includes `doi = {10.23731/CYRM-2017-002}` and the DOI resolves. |
| Problematic retained orphan entries | Resolved for the previous CMS Open Data orphan entries: they are no longer present. The only retained orphan is `pdg_2024`, whose metadata resolves correctly. |
| All citations have entries | Resolved: no missing citation entries. |
| No title math | Resolved: no title field contains `$...$`, `\alpha`, `\mathrm`, or related LaTeX math commands. |
| Links resolve as expected | Mostly resolved: DOI/arXiv/CERN/PDG/GitHub targets resolve, but two resolved records expose title mismatches. |

## Findings

### A-001: `cms_open_data_htt_2012` title does not match DOI metadata

Location: `phase5_documentation/outputs/references.bib:1`

The DOI `10.7483/OPENDATA.CMS.GV20.PR5T` resolves and the author/year now match the DOI metadata: Stefan Wunsch, 2019. The title does not match. The BibTeX title is:

`HiggsTauTauReduced: CMS open data reduced samples for H to tau tau studies`

The DOI metadata title is:

`Analysis of Higgs boson decays to two tau leptons using data and simulation of events at the CMS detector from 2012`

Resolution: update the BibTeX title to match the DOI/CERN Open Data record, or remove the DOI and cite a source whose title is actually `HiggsTauTauReduced: CMS open data reduced samples for H to tau tau studies`.

### A-002: `cms_htt_2018` title does not match DOI/arXiv metadata

Location: `phase5_documentation/outputs/references.bib:29`

The DOI `10.1016/j.physletb.2018.02.004` and arXiv ID `1708.00373` both resolve to the same CMS paper. The BibTeX title is:

`Observation of the SM scalar boson decaying to a pair of tau leptons with the CMS experiment at the LHC`

The DOI/arXiv title is:

`Observation of the Higgs boson decay to a pair of tau leptons with the CMS detector`

Resolution: update the BibTeX title to the DOI/arXiv title. The current entry points to the real paper, but the retained title describes a different or pre-publication title string.

### C-001: retained orphan `pdg_2024`

Location: `phase5_documentation/outputs/references.bib:54`

`pdg_2024` is present in `references.bib` but is not cited by either reviewed markdown file. The entry itself is valid and the DOI resolves to the correct 2024 PDG Review of Particle Physics record, so this is not a blocker.

Resolution: either cite `pdg_2024` where the general PDG review is used, or remove the entry if only the Higgs-status PDF is needed.

## Per-Entry Validation Table

| Key | DOI | arXiv | Title match | Year | Status |
|---|---|---|---|---|---|
| `cms_open_data_htt_2012` | resolves: `10.7483/OPENDATA.CMS.GV20.PR5T` | none | no, DOI title differs | BibTeX 2019, DOI 2019 | A-001 |
| `cms_open_data_skim` | none | none | GitHub repository title is consistent with entry | BibTeX 2021 | OK |
| `cms_htt_2014` | resolves: `10.1007/JHEP05(2014)104` | resolves: `1401.5041` | yes | BibTeX 2014, DOI/arXiv 2014 | OK |
| `cms_htt_2018` | resolves: `10.1016/j.physletb.2018.02.004` | resolves: `1708.00373` | no, DOI/arXiv title differs | BibTeX 2018, DOI 2018, arXiv 2017 | A-002 |
| `atlas_cms_higgs_combination_2016` | resolves: `10.1007/JHEP08(2016)045` | resolves: `1606.02266` | yes after plain-text math normalization | BibTeX 2016, DOI/arXiv 2016 | OK |
| `pdg_2024` | resolves: `10.1103/PhysRevD.110.030001` | none | yes | BibTeX 2024, DOI 2024 | C-001 orphan |
| `pdg_higgs_status_2024` | none | none | PDF URL resolves | BibTeX 2024 | OK |
| `lhc_hxswg_yellow_report_4` | resolves: `10.23731/CYRM-2017-002` | resolves: `1610.07922` | yes | BibTeX 2017, DOI 2017, arXiv 2016 | OK |
| `cowan_asymptotic` | resolves: `10.1140/epjc/s10052-011-1554-0` | resolves: `1007.1727` | yes | BibTeX 2011, DOI 2011, arXiv 2010 | OK |
| `read_cls` | resolves: `10.1088/0954-3899/28/10/313` | none | yes after CLs text normalization | BibTeX 2002, DOI 2002 | OK |
| `pyhf_joss` | resolves: `10.21105/joss.02823` | none | yes | BibTeX 2021, DOI 2021 | OK |

## Validation Sources Used

- DOI content negotiation through `https://doi.org/{doi}` with CSL JSON.
- arXiv API records through `https://export.arxiv.org/api/query?id_list={eprint}`.
- CERN Open Data page `https://opendata.cern.ch/record/12350`.
- PDG page `https://pdg.lbl.gov/2024/`.
- PDG Higgs review PDF `https://pdg.lbl.gov/2024/reviews/rpp2024-rev-higgs-boson.pdf`.
- GitHub repository page `https://github.com/cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis`.

