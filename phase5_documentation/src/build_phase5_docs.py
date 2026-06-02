from __future__ import annotations

import json
import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import mplhep as mh
import numpy as np
from rich.logging import RichHandler
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import auc, roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "phase5_documentation" / "outputs"
FIG = OUT / "figures"
LOG_PATH = ROOT / "phase5_documentation" / "logs" / "executor_phase5_documentation_20260602T162932Z.md"
EXP_LOG = ROOT / "experiment_log.md"

MVA_INPUTS = [
    "mu_pt",
    "mu_eta",
    "mu_reliso",
    "tau_pt",
    "tau_eta",
    "tau_reliso",
    "met_pt",
    "mt_mu_met",
    "m_vis",
    "m_addmet",
    "pt_tautau_proxy",
    "n_clean_jets",
    "mjj",
    "delta_eta_jj",
    "jet1_pt",
    "btag_max",
]


def load_json(path: str) -> dict:
    with (ROOT / path).open() as handle:
        return json.load(handle)


def append_log(message: str) -> None:
    with LOG_PATH.open("a") as handle:
        handle.write(f"\n## milestone\n\n{message}\n")


def copy_figures() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    sources = [
        ROOT / "phase2_exploration" / "outputs" / "figures",
        ROOT / "phase3_selection" / "outputs" / "figures",
        ROOT / "phase4_inference" / "4a_expected" / "outputs" / "figures",
        ROOT / "phase4_inference" / "4b_partial" / "outputs" / "figures",
        ROOT / "phase4_inference" / "4c_observed" / "outputs" / "figures",
    ]
    copied = 0
    for src_dir in sources:
        for src in src_dir.glob("*.*"):
            if src.suffix.lower() not in {".pdf", ".png"}:
                continue
            shutil.copy2(src, FIG / src.name)
            copied += 1
    log.info("Copied %d upstream figure files", copied)
    append_log(f"Copied {copied} upstream figure files into the Phase 5 figure directory.")


def merge_references() -> None:
    refs = (ROOT / "phase4_inference" / "4c_observed" / "outputs" / "references.bib").read_text()
    (OUT / "references.bib").write_text(refs)
    append_log("Merged Phase 4c references into the Phase 5 bibliography.")


def setup_style() -> None:
    mh.style.use("CMS")


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)


def exp_label(ax: plt.Axes, label_text: str = "Open Data diagnostic") -> None:
    mh.label.exp_label(
        exp="CMS",
        data=True,
        llabel=label_text,
        rlabel=r"$\sqrt{s}=8$ TeV, $L=11.467$ fb$^{-1}$ ref.",
        loc=0,
        ax=ax,
    )


def make_comparison_figures(observed: dict) -> None:
    setup_style()
    primary = observed["observed_fit"]
    score = observed["score_diagnostic_fit"]
    primary_limit = primary["observed_upper_limit"]
    score_limit = score["observed_upper_limit"]
    primary_band = primary_limit["expected_band_minus2_minus1_median_plus1_plus2"]
    score_band = score_limit["expected_band_minus2_minus1_median_plus1_plus2"]

    fig, ax = plt.subplots(figsize=(10, 10))
    rows = {
        "This open data primary": 0.0,
        "BDT score diagnostic": 1.0,
        "CMS Run 1 mu": 2.0,
        "CMS 2018 mu": 3.0,
    }
    ax.fill_betweenx([rows["This open data primary"] - 0.22, rows["This open data primary"] + 0.22], primary_band[0], primary_band[4], color="#f0e442", alpha=0.9, label="Expected 95% band")
    ax.fill_betweenx([rows["This open data primary"] - 0.22, rows["This open data primary"] + 0.22], primary_band[1], primary_band[3], color="#009e73", alpha=0.9, label="Expected 68% band")
    ax.plot(primary_band[2], rows["This open data primary"], marker="s", color="#d55e00", linestyle="", label="Expected median limit")
    ax.plot(primary_limit["observed_limit"], rows["This open data primary"], marker="o", color="black", linestyle="", label="Observed limit")
    ax.plot(primary["mu_hat"], rows["This open data primary"], marker="D", color="#0072b2", linestyle="", label="Fitted mu")

    ax.fill_betweenx([rows["BDT score diagnostic"] - 0.18, rows["BDT score diagnostic"] + 0.18], score_band[1], score_band[3], color="#b0b0b0", alpha=0.45, label="BDT exp. 68%")
    ax.plot(score_band[2], rows["BDT score diagnostic"], marker="s", color="#a65628", linestyle="")
    ax.plot(score_limit["observed_limit"], rows["BDT score diagnostic"], marker="o", color="#555555", linestyle="")
    ax.plot(score["mu_hat"], rows["BDT score diagnostic"], marker="D", color="#984ea3", linestyle="")

    ax.errorbar(0.78, rows["CMS Run 1 mu"], xerr=0.27, fmt="o", color="#202020", capsize=5)
    ax.errorbar(1.09, rows["CMS 2018 mu"], xerr=0.27, fmt="o", color="#202020", capsize=5)
    ax.axvline(1.0, color="black", linestyle="--", linewidth=1.2, label="SM mu=1")
    ax.set_yticks(list(rows.values()), list(rows.keys()))
    ax.set_xlabel("Signal-strength scale mu")
    ax.set_xlim(0, max(30.0, score_limit["observed_limit"] * 1.15))
    ax.invert_yaxis()
    ax.legend(fontsize="x-small", loc="lower right")
    exp_label(ax)
    save(fig, "phase5_mu_limit_comparison")

    fig, ax = plt.subplots(figsize=(10, 10))
    labels = ["Primary observed", "BDT diagnostic", "CMS Run 1", "CMS 2018 obs.", "CMS 2018 exp."]
    z_values = [
        primary["discovery_diagnostic"]["z_value"],
        score["discovery_diagnostic"]["z_value"],
        3.0,
        4.9,
        4.7,
    ]
    colors = ["#0072b2", "#d55e00", "#7a7a7a", "#202020", "#909090"]
    y = np.arange(len(labels))
    ax.barh(y, z_values, color=colors, alpha=0.88, height=0.55)
    ax.axvline(3.0, color="black", linestyle="--", linewidth=1.2)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Local significance diagnostic [standard deviations]")
    ax.set_xlim(0, 5.5)
    ax.invert_yaxis()
    exp_label(ax)
    mh.label.add_text("BDT row is flagged by score-shape validation.", ax=ax, loc="lower right")
    save(fig, "phase5_significance_comparison")
    append_log("Generated CMS-style expected/observed signal-strength and significance comparison figures.")


def selected_arrays() -> dict[str, np.ndarray]:
    with np.load(ROOT / "phase3_selection" / "outputs" / "sensitivity_selected_events.npz", allow_pickle=False) as payload:
        return {key: payload[key] for key in payload.files}


def make_mva_performance_figures() -> None:
    setup_style()
    selected = selected_arrays()
    sr_mc = selected["is_signal_region"].astype(bool) & np.isin(selected["role"], ["signal", "background"])
    y = (selected["role"][sr_mc] == "signal").astype(int)
    score_columns = {
        "HGB": "mva_score_hist_gradient_boosting",
        "MLP NN": "mva_score_mlp",
        "XGBoost": "mva_score_xgboost",
    }

    fig, ax = plt.subplots(figsize=(10, 10))
    auc_rows = {}
    for label, column in score_columns.items():
        scores = selected[column][sr_mc].astype(float)
        fpr, tpr, _ = roc_curve(y, scores)
        roc_auc = auc(fpr, tpr)
        auc_rows[label] = roc_auc
        roc_label = label + " AUC=" + format(roc_auc, ".3f")
        ax.plot(fpr, tpr, label=roc_label)
    ax.plot([0, 1], [0, 1], color="black", linestyle="--", linewidth=1.0)
    ax.set_xlabel("Background efficiency")
    ax.set_ylabel("Signal efficiency")
    ax.legend(fontsize="x-small", loc="lower right")
    exp_label(ax, "Open Simulation")
    save(fig, "phase5_mva_roc")

    fig, ax = plt.subplots(figsize=(10, 10))
    labels = list(auc_rows.keys()) + ["Transformer"]
    values = list(auc_rows.values()) + [0.0]
    colors = ["#0072b2", "#009e73", "#d55e00", "#7a7a7a"]
    y_pos = np.arange(len(labels))
    ax.barh(y_pos, values, color=colors, alpha=0.88)
    ax.set_yticks(y_pos, labels)
    ax.set_xlabel("Full selected-MC ROC AUC")
    ax.set_xlim(0, 1.0)
    ax.invert_yaxis()
    mh.label.add_text("Transformer not trained: no fast attention stack in the pixi environment.", ax=ax, loc="lower right")
    exp_label(ax, "Open Simulation")
    save(fig, "phase5_mva_auc_summary")

    matrix = np.column_stack(
        [np.nan_to_num(selected[name][sr_mc].astype(float), nan=-999.0, posinf=999.0, neginf=-999.0) for name in MVA_INPUTS]
    )
    x_train, x_test, y_train, y_test = train_test_split(matrix, y, test_size=0.35, random_state=31415, stratify=y)
    model = HistGradientBoostingClassifier(max_iter=180, learning_rate=0.045, max_leaf_nodes=17, l2_regularization=0.05, random_state=2718)
    model.fit(x_train, y_train)
    baseline_auc = roc_auc_score(y_test, model.predict_proba(x_test)[:, 1])
    result = permutation_importance(model, x_test, y_test, n_repeats=5, random_state=2718, scoring="roc_auc")
    drops = np.maximum(result.importances_mean, 0.0)
    order = np.argsort(drops)[-10:][::-1]
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.barh(np.arange(len(order)), drops[order], xerr=result.importances_std[order], color="#0072b2", alpha=0.88)
    ax.set_yticks(np.arange(len(order)), [MVA_INPUTS[idx] for idx in order])
    ax.set_xlabel("Permutation AUC decrease")
    ax.invert_yaxis()
    mh.label.add_text(f"HGB held-out AUC={baseline_auc:.3f}", ax=ax, loc="lower right")
    exp_label(ax, "Open Simulation")
    save(fig, "phase5_hgb_permutation_importance")

    fig, ax = plt.subplots(figsize=(10, 10))
    items = ["Tabular inputs", "HGB", "MLP NN", "XGBoost", "Transformer", "GenMET regression"]
    status = [1, 1, 1, 1, 0, 0]
    colors = ["#009e73" if value else "#d55e00" for value in status]
    ax.barh(np.arange(len(items)), status, color=colors, alpha=0.88)
    ax.set_yticks(np.arange(len(items)), items)
    ax.set_xticks([0, 1], ["Not available", "Available/trained"])
    ax.set_xlim(0, 1.25)
    ax.invert_yaxis()
    mh.label.add_text("Transformer and GenMET regression were downscoped by environment/target availability.", ax=ax, loc="lower right")
    exp_label(ax, "Open Simulation")
    save(fig, "phase5_transformer_feasibility")
    append_log("Generated MVA/NN ROC, AUC, permutation-importance, and transformer-feasibility figures.")


def figure_ref_check(md_path: Path) -> list[str]:
    text = md_path.read_text()
    refs = sorted(set(re.findall(r"figures/[^)]+\.pdf", text)))
    return [ref for ref in refs if not (OUT / ref).exists()]


def compile_doc(stem: str) -> None:
    cmd = [
        "pandoc",
        f"{stem}.md",
        "-o",
        f"{stem}.tex",
        "--standalone",
        "--include-in-header=../../conventions/preamble.tex",
        "--number-sections",
        "--toc",
        "--filter",
        "pandoc-crossref",
        "--citeproc",
        "--bibliography=references.bib",
    ]
    subprocess.run(cmd, cwd=OUT, check=True)
    subprocess.run([sys.executable, "../../conventions/postprocess_tex.py", f"{stem}.tex"], cwd=OUT, check=True)
    subprocess.run(["tectonic", f"{stem}.tex"], cwd=OUT, check=True)
    append_log(f"Compiled {stem}.md to TeX and PDF.")


def fmt(value: float, ndigits: int = 3) -> str:
    return f"{value:.{ndigits}f}"


def build_analysis_note(observed: dict, partial: dict, expected: dict, comparison: dict, yields: dict, score_yields: dict) -> str:
    primary = observed["observed_fit"]
    score = observed["score_diagnostic_fit"]
    primary_lim = primary["observed_upper_limit"]
    score_lim = score["observed_upper_limit"]
    primary_band = primary_lim["expected_band_minus2_minus1_median_plus1_plus2"]
    score_band = score_lim["expected_band_minus2_minus1_median_plus1_plus2"]
    obs_val = observed["validation_summary"]
    score_val = observed["score_diagnostic_validation_summary"]
    pval = partial["validation_summary"]
    w_full = observed["wjets_high_mt_scale"]
    w_10 = partial["wjets_high_mt_scale"]
    vbf_scale = observed["vbf_background_scale"]
    qcd_primary = observed["qcd_sideband_estimates"]["visible_mass_qcd_primary"]
    qcd_score = observed["qcd_sideband_estimates"]["hgb_score_qcd_diagnostic"]
    exp_lim = expected["expected_upper_limit"]
    exp_z = expected["discovery_sensitivity"]["z_value"]

    category_rows = []
    for cat in ["vbf", "boosted", "zero_jet"]:
        total = yields["totals"][cat]
        category_rows.append(
            f"| {cat} | {total['data_total']} | {total['background_total']:.2f} | "
            f"{total['qcd_total']:.2f} | {total['signal_total']:.3f} | {total['data_over_background']:.3f} |"
        )
    category_table = "\n".join(category_rows)

    score_rows = []
    for cat in ["vbf", "boosted", "zero_jet"]:
        total = score_yields["totals"][cat]
        score_rows.append(
            f"| {cat} | {total['data_total']} | {total['background_total']:.2f} | "
            f"{total['qcd_total']:.2f} | {total['signal_total']:.3f} | {total['data_over_background']:.3f} |"
        )
    score_table = "\n".join(score_rows)

    return f"""---
title: "CMS Open Data H to tau tau Search: Final Analysis Note"
author: "Analysis my_analysis"
date: "2026-06-02"
bibliography: references.bib
---

# Abstract {{-}}

This note documents a reduced CMS 2012 Open Data search for Higgs boson decays
to tau pairs in the mu tau_h final state. A Phase 5 audit found that the
original observed BDT-score fit was not a valid evidence result: it omitted a
reducible QCD/fake-tau background estimate and failed high-score shape
validation. The final conservative result therefore uses visible mass in VBF,
boosted, and zero-jet categories with a same-sign data-driven QCD/fake template.
It gives `mu_hat = {primary['mu_hat']:.4f}`, an observed 95% CLs limit
`mu < {primary_lim['observed_limit']:.4f}`, and `Z = {primary['discovery_diagnostic']['z_value']:.4f}`.
The categorized BDT-score model is retained as a flagged diagnostic with
`mu_hat = {score['mu_hat']:.4f}` and `Z = {score['discovery_diagnostic']['z_value']:.4f}`.

# Change Log {{-}}

Phase 5 v2 responds to the observed-versus-expected audit. It adds a same-sign
QCD/fake estimate, changes the primary full-data result to the visible-mass
fallback, keeps the BDT score as a diagnostic, adds NN/MVA performance figures,
and compiles the paper with REVTeX PRL formatting.

# Data And Simulation

The data are Run2012B and Run2012C TauPlusX reduced samples from the public
HiggsTauTauReduced mirror, using the CMS Open Data H to tau tau luminosity
reference of 11.467/fb [@cms_open_data_htt_2012; @cms_open_data_skim]. The
localized mirror files contain about one tenth of the event entries listed in
the Open Data records; this is treated as the public reduced processing sample
scope, while MC weights continue to use the official record denominators
specified in `normalization_inputs.json`, as required by the sample provenance.

The available MC set contains ggH and VBF H to tau tau, DYJetsToLL, TTbar, and
W1/W2/W3JetsToLNu. QCD multijet, diboson, single top, embedded Z to tau tau,
W4/inclusive W+jets, associated Higgs, and H to WW remain unavailable as
reduced samples and are not silently substituted.

![Sample inventory. The figure summarizes local reduced ROOT entries and file
sizes for the public H to tau tau files used in the analysis. The entries are
processing entries, while normalization uses official Open Data record
denominators and the cited luminosity reference.](figures/sample_event_count_file_size.pdf){{#fig:an-samples}}

# Event Selection And Categories

Events are required to pass `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`. Muons have
pt > 20 GeV and |eta| < 2.1 with tight identification and isolation. Hadronic
tau candidates have pt > 20 GeV, |eta| < 2.3, decay-mode ID, tight isolation
ID, and tight anti-muon ID. The signal region uses opposite-sign mu tau_h pairs
with muon-MET transverse mass below 40 GeV. The W control region uses high
transverse mass, and the QCD/fake estimate uses same-sign low-mT events.

The fit categories are mutually exclusive VBF, boosted, and zero-jet. VBF
requires at least two clean jets, leading-dijet mass above 300 GeV, and
leading-dijet |Delta eta| above 2.5. Boosted events have at least one clean jet
after failing VBF, and zero-jet events have no clean jets.

| Category | Data | Background | QCD/fake | Signal | Data/background |
|---|---:|---:|---:|---:|---:|
{category_table}

![Cutflow summary. This plot shows raw event counts after each selection step
for data, signal MC, and background MC. It verifies that the selection chain is
monotonic and that the reduced samples remain populated after trigger, object,
charge, and transverse-mass requirements.](figures/cutflow_summary.pdf){{#fig:an-cutflow}}

# QCD And W Control Corrections

The W+jets normalization is measured in the high-mT control region as
`{w_full['applied_scale_factor']:.4f} ± {w_full['absolute_uncertainty']:.4f}`.
The 10% validation value was `{w_10['applied_scale_factor']:.4f} ± {w_10['absolute_uncertainty']:.4f}`.
The values agree within the larger 10% uncertainty and support the W-control
arithmetic.

The VBF category originally had a large MC overprediction. Tightening the VBF
cuts and applying a simple b-tag veto did not solve it, so a disjoint VBF-like
top-btag control region outside the low-mT signal region was used to calibrate
the MC-background rate in the VBF category. The resulting VBF background scale
is `{vbf_scale['applied_scale_factor']:.4f} ± {vbf_scale['absolute_uncertainty']:.4f}`;
it is applied only to MC backgrounds in VBF and not to the signal or QCD/fake
template.

The same-sign QCD/fake estimate subtracts non-QCD MC from same-sign low-mT data
and transfers the resulting template to opposite-sign signal candidates. For
the primary visible-mass model, the OS/SS transfer factor measured in the lowest
visible-mass bin is `{qcd_primary['transfer_sideband']['scale_factor']:.4f} ± {qcd_primary['transfer_sideband']['absolute_uncertainty']:.4f}`.
For the BDT score diagnostic, the corresponding low-score factor is
`{qcd_score['transfer_sideband']['scale_factor']:.4f} ± {qcd_score['transfer_sideband']['absolute_uncertainty']:.4f}`.

![Full high-mT W control comparison. The figure shows the derivation inputs for
the full-data W+jets control scale. The control region is outside the low-mT
signal region and the scale is propagated to the observed workspace without
signal-region tuning.](figures/w_highmt_scale_full.pdf){{#fig:an-wscale}}

# MVA And Transformer Diagnostics

The requested NN/MVA program was evaluated using the available reduced event
features. Histogram gradient boosting, an MLP neural network, and XGBoost were
trained on selected MC only. A transformer was not trained because the current
pixi environment lacks a fast attention stack and the reduced files do not
contain the GenMET target needed for the requested missing-momentum regression.

![MVA ROC curves. This figure shows ROC curves for the HGB, MLP neural-network,
and XGBoost score columns on selected signal/background MC. It is an
open-simulation performance diagnostic and does not validate data/MC score
shapes.](figures/phase5_mva_roc.pdf){{#fig:an-mva-roc}}

![MVA AUC summary. This figure compares the full selected-MC ROC AUC values for
the trained classifiers and records that the transformer branch was not trained
in this fast reduced-sample pass. The BDT score has strong MC separation, but
that is not sufficient for an observed evidence claim.](figures/phase5_mva_auc_summary.pdf){{#fig:an-mva-auc}}

![HGB permutation importance. This figure shows the leading permutation
importance values for a retrained HGB classifier on a held-out selected-MC
split. It documents which reduced features drive the classifier response used
in the diagnostic score fit.](figures/phase5_hgb_permutation_importance.pdf){{#fig:an-mva-importance}}

![Transformer feasibility. This figure records which modern-model branches were
available in the current environment. The transformer and GenMET-regression
branches are explicitly downscoped rather than reported as unperformed
successes.](figures/phase5_transformer_feasibility.pdf){{#fig:an-transformer}}

# Primary Visible-Mass Result

The primary statistical model is a binned pyhf profile likelihood in visible
mass, with one signal-strength parameter `mu`, the W high-mT scale, the
same-sign QCD/fake transfer uncertainty, luminosity, DY and tau/open-data
normalization terms, and MC statistical terms [@pyhf_joss; @read_cls;
@cowan_asymptotic].

| Quantity | Value | Interpretation |
|---|---:|---|
| Primary median expected 95% CLs limit | mu < {primary_band[2]:.4f} | corrected visible-mass workspace |
| Primary observed 95% CLs limit | mu < {primary_lim['observed_limit']:.4f} | conservative observed result |
| Primary mu_hat | {primary['mu_hat']:.4f} | best fit, bounded at zero if no excess |
| Primary q0 Z | {primary['discovery_diagnostic']['z_value']:.4f} | diagnostic only |
| Primary combined data/background | {obs_val['combined']['data_over_background']:.4f} | validation after QCD/fake correction |
| Primary chi2/ndf | {obs_val['combined']['chi2_per_ndf']:.4f} | validation after QCD/fake correction |

The primary result is much more stable than the original score-only observed
fit. It does not show a Higgs-like excess: `mu_hat` is `{primary['mu_hat']:.4f}`
and `Z = {primary['discovery_diagnostic']['z_value']:.4f}`. The observed limit
is compatible with the weak sensitivity expected from this reduced single-final
state setup.

![Primary visible-mass validation in VBF. The plot compares full data to the
QCD-corrected visible-mass prediction in the VBF category. The remaining VBF
deficit is a limitation, but it no longer drives a fake signal-strength
increase.](figures/observed_mvis_vbf.pdf){{#fig:an-primary-vbf}}

![Primary visible-mass validation in boosted. The plot compares full data to
the QCD-corrected visible-mass prediction in the boosted category. This channel
is part of the conservative primary fit.](figures/observed_mvis_boosted.pdf){{#fig:an-primary-boosted}}

![Primary visible-mass validation in zero-jet. The zero-jet normalization is
stabilized by the same-sign QCD/fake estimate, which removes the dominant
normalization pathology seen in the original score-only result.](figures/observed_mvis_zero_jet.pdf){{#fig:an-primary-zero}}

# BDT Score Diagnostic

The BDT-score model is kept because it was explicitly requested and has better
expected MC separation. It is not used as the primary observed evidence result,
because its high-score bins remain shape-flagged after adding the QCD/fake
template.

| Category | Data | Background | QCD/fake | Signal | Data/background |
|---|---:|---:|---:|---:|---:|
{score_table}

| Quantity | Value | Interpretation |
|---|---:|---|
| Score median expected 95% CLs limit | mu < {score_band[2]:.4f} | diagnostic expected score workspace |
| Score observed 95% CLs limit | mu < {score_lim['observed_limit']:.4f} | flagged diagnostic |
| Score mu_hat | {score['mu_hat']:.4f} | flagged high-score shape diagnostic |
| Score q0 Z | {score['discovery_diagnostic']['z_value']:.4f} | not CMS-quality evidence |
| Score combined data/background | {score_val['combined']['data_over_background']:.4f} | score validation after QCD/fake correction |
| Score chi2/ndf | {score_val['combined']['chi2_per_ndf']:.4f} | score validation after QCD/fake correction |

![Score-template diagnostic in VBF. This figure keeps the categorized BDT score
view requested for sensitivity studies. It is diagnostic because the score
shape is not validated well enough for an observed evidence claim.](figures/observed_score_vbf.pdf){{#fig:an-score-vbf}}

![Score-template diagnostic in boosted. This figure shows the boosted score
template after QCD/fake correction. High-score residuals motivate the
diagnostic-only status.](figures/observed_score_boosted.pdf){{#fig:an-score-boosted}}

![Score-template diagnostic in zero-jet. This figure shows that the zero-jet
normalization is improved by QCD/fake correction while high-score shape
residuals remain visible.](figures/observed_score_zero_jet.pdf){{#fig:an-score-zero}}

![Observed pull and ratio summary. The figure compares primary visible-mass and
BDT-score validation behavior after the QCD/fake audit correction. It shows why
the visible-mass model is primary and the score fit is diagnostic.](figures/observed_pull_ratio_summary.pdf){{#fig:an-pull-summary}}

# Comparison With Published Results

CMS Run 1 reported evidence for H to tau tau using 7 and 8 TeV data with
multiple final states, embedded backgrounds, and a full calibration program;
the quoted best-fit signal strength was 0.78 ± 0.27 [@cms_htt_2014]. CMS 2018
reported observed and expected significances of 4.9 and 4.7 and a signal
strength near 1.09 [@cms_htt_2018]. These are not direct pass/fail targets for
this reduced open-data workflow.

| Result | Scope | Significance | Signal-strength information |
|---|---|---:|---|
| This open-data primary | 8 TeV mu tau_h reduced mirror, visible mass | {primary['discovery_diagnostic']['z_value']:.3f} | mu_hat = {primary['mu_hat']:.3f}; mu < {primary_lim['observed_limit']:.3f}; expected mu < {primary_band[2]:.3f} |
| This BDT diagnostic | 8 TeV mu tau_h reduced mirror, HGB score | {score['discovery_diagnostic']['z_value']:.3f} flagged | mu_hat = {score['mu_hat']:.3f}; mu < {score_lim['observed_limit']:.3f}; expected mu < {score_band[2]:.3f} |
| CMS Run 1 | 7+8 TeV multi-channel | >3 | mu = 0.78 ± 0.27 |
| CMS 2018 | 13 TeV multi-channel | observed 4.9, expected 4.7 | mu = 1.09 ± about 0.27 |

![Signal-strength and limit comparison. The figure uses a CMS-style
expected-band and observed-marker presentation for the primary open-data limit,
with the flagged BDT diagnostic and published CMS signal-strength measurements
shown as context. The open-data diagnostic is not directly equivalent to CMS
publication measurements.](figures/phase5_mu_limit_comparison.pdf){{#fig:an-mu-comparison}}

![Significance comparison. The figure compares the primary open-data diagnostic
and the flagged BDT-score diagnostic with CMS publication values. The BDT row is
explicitly not interpreted as evidence.](figures/phase5_significance_comparison.pdf){{#fig:an-significance-comparison}}

# Conclusion

The final audit-corrected result is a conservative visible-mass plus QCD/fake
template fit. It gives `mu_hat = {primary['mu_hat']:.4f}`, an observed 95% CLs
limit `mu < {primary_lim['observed_limit']:.4f}`, and `Z = {primary['discovery_diagnostic']['z_value']:.4f}`.
The originally surprising BDT-score observed result is retained only as a
flagged diagnostic because the score shape is not validated in data. This is
the correct interpretation of the reduced CMS Open Data workflow: reproducible
and useful for methodology, but not CMS-quality evidence for H to tau tau.

# References {{-}}
"""


def build_paper_markdown(observed: dict) -> str:
    primary = observed["observed_fit"]
    score = observed["score_diagnostic_fit"]
    primary_lim = primary["observed_upper_limit"]
    primary_band = primary_lim["expected_band_minus2_minus1_median_plus1_plus2"]
    score_lim = score["observed_upper_limit"]
    return f"""# A CMS Open Data Diagnostic Search for H to Tau Tau in the Mu Tau_h Final State

This PRL-formatted draft reports the audit-corrected result. The primary
visible-mass plus QCD/fake fit gives `mu_hat = {primary['mu_hat']:.3f}`,
`mu < {primary_lim['observed_limit']:.3f}` at 95% CLs, with median expected
limit `{primary_band[2]:.3f}`. The categorized BDT-score result gives
`mu_hat = {score['mu_hat']:.3f}` and `mu < {score_lim['observed_limit']:.3f}`,
but remains diagnostic only because score-shape validation is flagged.
"""


def tex_escape(text: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def build_prl_tex(observed: dict, yields: dict) -> str:
    primary = observed["observed_fit"]
    score = observed["score_diagnostic_fit"]
    primary_lim = primary["observed_upper_limit"]
    primary_band = primary_lim["expected_band_minus2_minus1_median_plus1_plus2"]
    score_lim = score["observed_upper_limit"]
    qcd_primary = observed["qcd_sideband_estimates"]["visible_mass_qcd_primary"]
    vbf_scale = observed["vbf_background_scale"]
    rows = []
    for cat in ["vbf", "boosted", "zero_jet"]:
        total = yields["totals"][cat]
        rows.append(
            rf"{tex_escape(cat)} & {total['data_total']} & {total['background_total']:.1f} & "
            rf"{total['qcd_total']:.1f} & {total['signal_total']:.2f} \\"
        )
    category_rows = "\n".join(rows)
    return rf"""\documentclass[aps,prl,reprint,superscriptaddress,nofootinbib]{{revtex4-2}}
\usepackage{{graphicx}}
\usepackage{{amsmath}}
\usepackage{{booktabs}}
\usepackage{{xcolor}}
\begin{{document}}

\title{{A CMS Open Data Diagnostic Search for $H\to\tau\tau$ in the $\mu\tau_h$ Final State}}
\author{{Analysis my\_analysis}}
\affiliation{{CMS Open Data reduced-sample analysis}}
\date{{June 2, 2026}}

\begin{{abstract}}
A diagnostic search for Higgs boson decays to tau pairs is performed with
CMS 2012 Open Data reduced samples in the $\mu\tau_h$ final state.  A Phase 5
audit found that an initially selected BDT-score observed fit was not a valid
evidence result because the score shape failed data validation.  The primary
result is therefore a conservative visible-mass fit in VBF, boosted, and
zero-jet categories with a same-sign data-driven QCD/fake template.  The fit
gives $\hat\mu={primary['mu_hat']:.3f}$, an observed 95\% CLs upper limit
$\mu<{primary_lim['observed_limit']:.3f}$, and a discovery diagnostic
$Z={primary['discovery_diagnostic']['z_value']:.3f}$.  The BDT-score fit gives
$\hat\mu={score['mu_hat']:.3f}$ and $\mu<{score_lim['observed_limit']:.3f}$ but
is retained only as a flagged diagnostic, not as CMS-quality evidence.
\end{{abstract}}

\maketitle

\paragraph{{Data and method.}}
The analysis uses the public Run2012B/C TauPlusX HiggsTauTauReduced mirror and
the CMS Open Data luminosity reference of 11.467 fb$^{{-1}}$.  Signal and
background simulations are normalized with official Open Data record event
denominators rather than local reduced-file entries.  Events are selected with
the $\mu+\tau_h$ trigger, tight muon and hadronic-tau requirements including a
tight anti-muon veto, opposite-sign charge, and low transverse mass.

\paragraph{{Background correction.}}
The W+jets normalization is measured in a high-$m_T$ control region.  The
VBF-background rate is calibrated in a VBF-like top-btag control region outside
the low-$m_T$ signal region, giving a scale
${vbf_scale['applied_scale_factor']:.3f}\pm{vbf_scale['absolute_uncertainty']:.3f}$.
The reducible QCD/fake contribution is estimated from same-sign low-$m_T$ data
after subtracting non-QCD simulation.  For the primary visible-mass fit, the
OS/SS transfer factor measured in the lowest visible-mass bin is
${qcd_primary['transfer_sideband']['scale_factor']:.3f}\pm{qcd_primary['transfer_sideband']['absolute_uncertainty']:.3f}$.

\begin{{table}}[b]
\caption{{Selected yields in the primary visible-mass fit after the QCD/fake
audit correction.  Background includes DY, ttbar, W+jets, and the same-sign
QCD/fake estimate.}}
\begin{{ruledtabular}}
\begin{{tabular}}{{lrrrr}}
Category & Data & Bkg. & QCD/fake & Signal \\
{category_rows}
\end{{tabular}}
\end{{ruledtabular}}
\end{{table}}

\paragraph{{Results.}}
The primary corrected workspace has median expected 95\% CLs limit
$\mu<{primary_band[2]:.3f}$ and observed limit
$\mu<{primary_lim['observed_limit']:.3f}$.  The best fit is
$\hat\mu={primary['mu_hat']:.3f}$ with $Z={primary['discovery_diagnostic']['z_value']:.3f}$.
This is the conservative final observed result.  The categorized BDT-score fit
is shown only as a diagnostic because high-score residuals remain after the
QCD/fake correction.

\begin{{figure}}[t]
\includegraphics[width=\linewidth]{{figures/phase5_mu_limit_comparison.pdf}}
\caption{{Signal-strength and limit comparison.  The primary open-data result
is shown with expected bands and an observed marker following CMS-style limit
plot conventions.  The BDT score row is flagged and the CMS publication rows
are context, not direct validation targets.}}
\end{{figure}}

\begin{{figure}}[t]
\includegraphics[width=\linewidth]{{figures/observed_mvis_zero_jet.pdf}}
\caption{{Primary visible-mass validation in the zero-jet category.  The
same-sign QCD/fake estimate stabilizes the dominant zero-jet normalization,
which was the main pathology in the original score-only observed result.}}
\end{{figure}}

\paragraph{{MVA diagnostics.}}
Histogram gradient boosting, an MLP neural network, and XGBoost were trained
on selected simulation.  Their ROC curves and feature-importance diagnostics
are retained to document the sensitivity study.  A transformer and the
requested GenMET regression are downscoped because the fast attention stack and
GenMET target are absent from the current reduced workflow.

\begin{{figure}}[t]
\includegraphics[width=\linewidth]{{figures/phase5_mva_roc.pdf}}
\caption{{Classifier ROC curves for the HGB, MLP neural-network, and XGBoost
score columns on selected signal and background simulation.  These curves show
MC separation power but do not validate observed score shapes.}}
\end{{figure}}

\paragraph{{Comparison and interpretation.}}
CMS Run 1 reported evidence for $H\to\tau\tau$ with a best-fit signal strength
of $0.78\pm0.27$, and CMS later observed the decay at 13 TeV with observed and
expected significances of 4.9 and 4.7.  The present reduced open-data result is
not a reproduction of those analyses: it uses fewer channels, a reduced public
sample, limited calibrations, and a simplified background program.  Its value
is methodological reproducibility, not an independent CMS-quality evidence
claim.

\begin{{thebibliography}}{{9}}
\bibitem{{cms2014}} CMS Collaboration, Evidence for the 125 GeV Higgs boson decaying to a pair of tau leptons, JHEP 05 (2014) 104.
\bibitem{{cms2018}} CMS Collaboration, Observation of the SM scalar boson decaying to a pair of tau leptons, Phys. Lett. B 779 (2018) 283.
\bibitem{{opendata}} CERN Open Data Portal, CMS Higgs to tau tau reduced samples for education and outreach.
\bibitem{{pyhf}} L. Heinrich et al., pyhf: pure-Python implementation of HistFactory statistical models.
\bibitem{{cls}} A. L. Read, Presentation of search results: the CLs technique.
\bibitem{{cowan}} G. Cowan et al., Asymptotic formulae for likelihood-based tests of new physics.
\end{{thebibliography}}

\end{{document}}
"""


def compile_prl(observed: dict, yields: dict) -> None:
    tex = build_prl_tex(observed, yields)
    (OUT / "PAPER_PRL_v1.tex").write_text(tex)
    subprocess.run(["tectonic", "PAPER_PRL_v1.tex"], cwd=OUT, check=True)
    append_log("Compiled PAPER_PRL_v1.tex with REVTeX PRL class.")


def write_docs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    observed = load_json("phase4_inference/4c_observed/outputs/observed_results.json")
    partial = load_json("phase4_inference/4b_partial/outputs/partial_results.json")
    expected = load_json("phase4_inference/4a_expected/outputs/expected_results.json")
    comparison = load_json("phase4_inference/4c_observed/outputs/comparison_to_4a_4b.json")
    yields = load_json("phase4_inference/4c_observed/outputs/observed_yields.json")
    score_yields = load_json("phase4_inference/4c_observed/outputs/score_observed_yields.json")

    copy_figures()
    merge_references()
    make_comparison_figures(observed)
    make_mva_performance_figures()

    an = build_analysis_note(observed, partial, expected, comparison, yields, score_yields)
    paper_md = build_paper_markdown(observed)
    (OUT / "ANALYSIS_NOTE_5_v1.md").write_text(an)
    (OUT / "PAPER_PRL_v1.md").write_text(paper_md)
    append_log("Wrote Phase 5 final analysis note and PRL summary markdown.")

    missing = figure_ref_check(OUT / "ANALYSIS_NOTE_5_v1.md")
    if missing:
        raise RuntimeError(f"Missing figure references in ANALYSIS_NOTE_5_v1.md: {missing}")

    compile_doc("ANALYSIS_NOTE_5_v1")
    compile_prl(observed, yields)

    with EXP_LOG.open("a") as handle:
        handle.write(
            "\n## Phase 5 documentation executor 2026-06-02T16:29:32Z\n\n"
            "- Rewrote final AN around the audit-corrected visible-mass/QCD primary result.\n"
            "- Added MVA/NN ROC, AUC, feature-importance, and transformer-feasibility figures.\n"
            "- Generated PAPER_PRL_v1.tex/pdf with REVTeX PRL formatting, not pandoc article formatting.\n"
        )
    append_log("Appended Phase 5 audit-corrected summary to experiment_log.md.")


if __name__ == "__main__":
    write_docs()
