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

## 2026-06-02 Phase 2 executor

- SciTreeRAG MCP tools were still unavailable in this execution environment.
  Phase 2 therefore used public CERN/CMS/ROOT web sources and direct ROOT file
  metadata via uproot as fallback retrieval.
- Resolved reduced H to tau tau ROOT files from the public ROOT mirror:
  `https://root.cern/files/HiggsTauTauReduced/`.
- Used CERN Open Data record context from Phase 1 for the reduced H to tau tau
  outreach sample provenance, including records 12350 and 12352.
- Blocker: object-definition and known-data-quality corpus queries could not be
  performed through SciTreeRAG. Phase 3 should retrieve official object
  definitions, luminosity, cross sections, and scale-factor documentation from
  authoritative CMS/CERN sources before production selection and normalization.
