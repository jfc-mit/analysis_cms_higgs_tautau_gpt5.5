# Analysis Title: H→ττ Analysis with CMS Open Data

You are performing a Higgs boson search in the τ +τ − decay channel using CMS Open Data from 2012 at √s = 8 TeV. The final state is one muon and one hadronically decaying tau lepton (μτh). Your goal is to produce distributions of key observables — particularly the visible di-tau mass — showing the Higgs signal contribution on top of Standard Model backgrounds. This loosely follows the official CMS publication (Phys. Lett. B 779 (2018) 283 and JHEP 05 (2014) 104).

To optimize the Higgs signal selection, do some categorization, in particular add a VBF category, and be sure to fit all categories simultaneously. Our dataset is missing the full trigger and tau efficiency scale factors, so loosen the tau efficiency selection to 10–15% to allow for good agreement of the Drell-Yan peak. In addition to a baseline analysis, perform three more approaches that focus on fitting a different final observable:

(a) fit an NN discriminator to find the Higgs, propagating the systematic uncertainties in the fit; 
(b) train an NN to regress the direction of the genMET and genMET ϕ in the final state and use this to construct a combined mass with the visible objects as the final observable;
(c) fit the mass after adding the missing energy to the mass distribution.

Also, make sure to apply a tight anti-muon veto, and to normalize the W+jets sample from data using the high mT region. Make sure you put a tight anti-muon veto on the hadronic tau ID. Make sure your Z normalization uncertainty is larger than the MC prediction, at a level of 10–15%, to reflect missing trigger turn-on scale factors and a larger tau efficiency scale factor

Data: /sandbox/work/jfc/analyses/higgs_tautau/data
MC: /sandbox/work/jfc/analyses/higgs_tautau/mc
The datasets include:

File Process Role GluGluToHToTauTau.root gg→H→ττ (mH=125 GeV) Signal VBF_HToTauTau.root VBF H→ττ Signal (subdominant) DYJetsToLL.root Z/gamma*→ll (Drell-Yan) Dominant irreducible background TTbar.root tt̄Background W1JetsToLNu.root, W2JetsToLNu.root, W3JetsToLNu.rootW+jets (1,2,3 jet bins) Background (fake τ_h) Run2012B_SingleMu.root, Run2012C_SingleMu.rootData (SingleMu trigger) Collision data

Any additional CMS Open Data you need is available. All files are available from the CERN Open Data record or the GitHub repo's file listing. Instructions for CMS opendata access: cern-opendata-access.md

- In the final analysis note, compare the final results with publisded results as comprehensively as the available ntuples and this analysis scope allow. Cover every result from that paper that is meaningfully comparable.
- In those comparison tables and figures, include previous-study results and PDG/world-average (if aviable) results where the paper or public references provide them.
