# Retrieval Log

## 2026-06-02 Phase 1 executor

- SciTreeRAG MCP tools (`search_lep_corpus`, `compare_measurements`,
  `get_paper`) were not exposed in this execution environment, so the
  mandated corpus calls could not be executed directly.
- Fallback plan: use authoritative public web sources where possible,
  prioritizing CMS publications, CERN Open Data records, HEPData, INSPIRE,
  arXiv, and PDG/official Higgs references for numerical comparison targets.
- Retrieved fallback sources:
  - CMS JHEP 05 (2014) 104, DOI 10.1007/JHEP05(2014)104, arXiv:1401.5041,
    PDF mirror https://publikationen.bibliothek.kit.edu/1000042067/3154375.
  - CMS Phys. Lett. B 779 (2018) 283, DOI 10.1016/j.physletb.2018.02.004,
    arXiv:1708.00373, PDF https://cds.cern.ch/record/2276465/files/scoap3-fulltext.pdf.
  - CERN Open Data record 12350,
    https://opendata.cern.ch/record/12350.
  - CERN Open Data record 12352,
    https://opendata.cern.ch/record/12352.
  - ATLAS+CMS JHEP 08 (2016) 045, DOI 10.1007/JHEP08(2016)045,
    arXiv:1606.02266.
