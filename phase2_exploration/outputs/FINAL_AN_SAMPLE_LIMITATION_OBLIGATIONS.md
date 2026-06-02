# Final AN Sample-Limitation Obligations

Phase 2 localized all currently confirmed reduced 2012 CMS Open Data samples
available from the ROOT H to tau tau reduced mirror for the mu tau_h analysis.
The final analysis note and final summary must also state that the broader CMS
reference analyses used or discussed paper-level components that are not
available in this reduced sample set.

For every `missing-reduced` or `deferred-AOD-conversion` entry in
`phase2_exploration/outputs/local_sample_manifest.json`, the final AN must:

1. Name the unavailable paper-level component.
2. State that no corresponding reduced 2012 CMS Open Data file or suitable
   substitute was used in this analysis.
3. Explain the expected limitation or impact on the reduced-sample result.
4. Make clear that the missing component did not block the current reduced
   analysis because it was documented and not silently substituted.

This obligation applies especially to embedded Z to tau tau, separate Z to
mumu/ee fake components, QCD/multijet simulation, diboson WW/WZ/ZZ, single top,
WH/ZH/ttH, H to WW, W4 or inclusive W+jets, and additional DY categories.

The final AN must also describe the sensitivity categories used by the reduced
analysis and compare them to the CMS paper categories. At minimum it must state
whether VBF, boosted or 1-jet, and 0-jet or non-VBF baseline categories were
retained, merged, or downscoped, and must explain the category variables used:
jet multiplicity, `m_jj`, `|Delta eta_jj|`, `pT_tautau` or a documented
available proxy, and b-tag/top-control handles.
