"""Research Brief: editable, sourced intelligence brief draft. Marked for human review."""
from datetime import date

import streamlit as st

from bioanalyst.db.queries import (
    get_companies, get_financial_periods, get_funding_rounds, get_meta, get_sectors, get_trials,
    get_uncertainties, in_sector, related,
)
from bioanalyst.ui_common import fmt_value, render_disclaimer_footer, render_header

sector_id = render_header("Research Brief")
st.title("Research Brief Generator")
st.warning(
    "**Draft for human review.** Template-assembled from the curated dataset below. Read every "
    "section and correct anything imprecise before using it anywhere.",
    icon="📝",
)

companies = in_sector(get_companies(), sector_id)
trials = get_trials()
financials = get_financial_periods()
funding_rounds = get_funding_rounds()
uncertainties = get_uncertainties()
meta = get_meta()
sector_row = get_sectors().set_index("sector_id").loc[sector_id]

options = sorted(companies["name"].tolist())
selected = st.multiselect("Include companies in this brief", options, default=options)
scope = companies[companies["name"].isin(selected)]
if scope.empty:
    st.info("Select at least one company.")
    st.stop()

today = date.today().isoformat()

scope_text = (
    f"Sector: {sector_row['name']}. Central question: {sector_row['central_question']} "
    f"Scope: {len(scope)} companies, "
    f"{len(trials[trials['company_id'].isin(scope['company_id'])])} tracked trials/studies."
)

if sector_id == "biotech_als":
    background_text = (
        "Amyotrophic lateral sclerosis (ALS) is a progressive neurodegenerative disease affecting "
        "motor neurons, leading to loss of voluntary muscle control; most patients die within "
        "2-5 years of diagnosis, typically from respiratory failure. Two modest-benefit therapies "
        "are current standard of care (riluzole, edaravone/Radicava) -- background context, not an "
        "independently re-verified claim in this research pass."
    )
else:
    background_text = (
        "Brain-computer interfaces (BCI) aim to restore communication or computer/device control "
        "for people with severe motor impairment (e.g., tetraplegia, ALS, spinal cord injury) by "
        "decoding neural signals directly, bypassing damaged motor pathways. Approaches range from "
        "fully invasive intracortical implants to non-invasive scalp EEG, with corresponding "
        "tradeoffs in signal quality, surgical risk, and regulatory pathway -- background context, "
        "not an independently re-verified claim in this research pass."
    )

landscape_lines = []
for _, c in scope.iterrows():
    ticker_bit = f" ({c['ticker']})" if fmt_value(c["ticker"], None) else ""
    landscape_lines.append(f"- **{c['name']}**{ticker_bit}, {c['relationship_to_use_case']}: {c['company_notes']}")
landscape_text = "\n".join(landscape_lines)

evidence_lines = []
for _, c in scope.iterrows():
    company_trials = related(trials, c["company_id"])
    evidence_lines.append(f"**{c['name']}**")
    for _, t in company_trials.iterrows():
        evidence_lines.append(f"- *{t['trial_name']}* ({t['phase']}, {t['results_status']}): {t['reported_outcome']}")
evidence_text = "\n".join(evidence_lines)

financial_lines = []
for _, c in scope.iterrows():
    cf = related(financials, c["company_id"]).sort_values("period_end_date", ascending=False)
    if not cf.empty:
        f = cf.iloc[0]
        gc = " [GOING-CONCERN DOUBT DISCLOSED]" if f["going_concern_flag"] else ""
        financial_lines.append(
            f"- **{c['name']}** (as of {f['period_end_date']}, SEC-filed): cash ${f['cash_and_equivalents']}M, "
            f"R&D ${f['rd_expense']}M/qtr{gc}"
        )
    else:
        cr = related(funding_rounds, c["company_id"])
        if not cr.empty:
            latest = cr.iloc[0]
            financial_lines.append(
                f"- **{c['name']}** (privately held -- funding, not a financial statement): "
                f"{latest['raw_amount_text']} ({latest['round_name']}, {latest['announced_date']})"
            )
financial_text = "\n".join(financial_lines)

if sector_id == "biotech_als":
    opportunities_text = (
        "Each program addresses a real unmet need (no highly effective ALS therapy exists), but "
        "commercial opportunity depends heavily on regulatory outcome, addressable population size "
        "(e.g., Biogen's SOD1-ALS indication is genetically restricted to a small subset of all ALS "
        "patients), and whether any accelerated approval survives its confirmatory trial -- Amylyx's "
        "Relyvrio is the clearest cautionary example of why an approval alone is not a stable commercial outcome."
    )
    milestones_text = (
        "- MediciNova: COMBAT-ALS topline data expected by end of 2026 (fully enrolled, 234 patients).\n"
        "- Clene: accelerated-approval NDA decision pending (filed October 2026); confirmatory "
        "RESTORE-ALS trial targeted to start Q1 2027.\n"
        "- Biogen: ATLAS confirmatory trial for Qalsody's continued accelerated approval -- no "
        "reported readout found in this research pass.\n"
        "- BrainStorm: Phase 3b ENDURANCE trial remains unfunded/unstarted as of this research pass."
    )
    diligence_text = (
        "- What is each company's realistic timeline and probability-weighted path from current "
        "status to a durable (non-withdrawn) approval?\n"
        "- For genetically-restricted indications (Biogen), what is the actual addressable patient count?\n"
        "- How does each company's cash runway compare to its probable time-to-next-catalyst?\n"
        "- Which trial designs used concurrent randomized controls vs. historical/external controls, "
        "and how much should that affect confidence in the reported result?\n"
        "- What would each company's program need to show to outperform existing standard of care "
        "(riluzole, edaravone), not just outperform placebo?"
    )
else:
    opportunities_text = (
        "Each program addresses a real unmet need, but commercial opportunity depends heavily on "
        "regulatory pathway (most are early-feasibility-stage, years from a marketable product), "
        "addressable population size (e.g., invasive-implant candidates are a smaller pool than "
        "non-invasive-device candidates), and whether a product can outperform existing non-BCI "
        "alternatives (e.g., eye-tracking AAC devices) enough to justify surgical risk and cost."
    )
    milestones_text = (
        "- Synchron: preparing a pivotal trial in 2026, aiming to be first to an FDA-approved "
        "implantable communication BCI.\n"
        "- Paradromics: first human implant completed June 2026 (Connect-One); 6-year per-participant "
        "follow-up planned.\n"
        "- Precision Neuroscience: converting its 510(k) temporary-use clearance into a chronic "
        "implantable product is the next regulatory step, not yet filed in sources found.\n"
        "- Cognixion: ongoing comparison trial vs. eye-tracking AAC devices -- results not yet reported."
    )
    diligence_text = (
        "- What is each company's realistic timeline from early feasibility study to a marketable, "
        "FDA-approved (not just breakthrough-designated or temporarily cleared) product?\n"
        "- What reimbursement pathway, if any, exists or is being pursued for this patient population?\n"
        "- How do study populations and designs differ across companies, and does that limit direct "
        "comparison of reported outcomes (e.g., safety-only early feasibility vs. a larger trial)?\n"
        "- What would adoption require from clinicians, caregivers, and patients (surgery, training, "
        "device maintenance, explant risk)?\n"
        "- What would a BCI need to show to outperform existing non-BCI alternatives (e.g., "
        "eye-tracking AAC devices), not just demonstrate feasibility in isolation?"
    )

risks_lines = []
for _, c in scope.iterrows():
    unc = related(uncertainties, c["company_id"])
    for _, u in unc.iterrows():
        risks_lines.append(f"- **{c['name']}** ({u['category']}): {u['description']}")
risks_text = "\n".join(risks_lines)

sources_lines = []
seen = set()
for _, t in trials[trials["company_id"].isin(scope["company_id"])].iterrows():
    if t["source_url"] and t["source_url"] not in seen:
        sources_lines.append(f"- {t['source_url']}")
        seen.add(t["source_url"])
sources_text = "\n".join(sources_lines)

st.subheader("1. Market scope")
scope_text = st.text_area("scope", scope_text, height=100, label_visibility="collapsed")
st.subheader("2. Scientific background")
background_text = st.text_area("background", background_text, height=100, label_visibility="collapsed")
st.subheader("3. Company landscape")
landscape_text = st.text_area("landscape", landscape_text, height=160, label_visibility="collapsed")
st.subheader("4. Evidence")
evidence_text = st.text_area("evidence", evidence_text, height=220, label_visibility="collapsed")
st.subheader("5. Financial / funding considerations")
financial_text = st.text_area("financial", financial_text, height=140, label_visibility="collapsed")
st.subheader("6. Commercial opportunities")
opportunities_text = st.text_area("opportunities", opportunities_text, height=120, label_visibility="collapsed")
st.subheader("7. Risks and counterarguments")
risks_text = st.text_area("risks", risks_text, height=220, label_visibility="collapsed")
st.subheader("8. Key milestones")
milestones_text = st.text_area("milestones", milestones_text, height=140, label_visibility="collapsed")
st.subheader("9. Questions for further diligence")
diligence_text = st.text_area("diligence", diligence_text, height=160, label_visibility="collapsed")
st.subheader("10. Sources and data dates")
sources_text = st.text_area("sources", sources_text, height=140, label_visibility="collapsed")

full_brief = f"""# BioAnalyst Brief (DRAFT -- for human review)
Generated {today} · Sector: {sector_row['name']} · Companies: {", ".join(selected)} · Data last verified: {meta.get('data_last_verified')}

**Template-assembled from a curated dataset; requires human review before use. Not investment advice.**

## 1. Market scope
{scope_text}

## 2. Scientific background
{background_text}

## 3. Company landscape
{landscape_text}

## 4. Evidence
{evidence_text}

## 5. Financial / funding considerations
{financial_text}

## 6. Commercial opportunities
{opportunities_text}

## 7. Risks and counterarguments
{risks_text}

## 8. Key milestones
{milestones_text}

## 9. Questions for further diligence
{diligence_text}

## 10. Sources and data dates
{sources_text}
"""

st.divider()
st.subheader("Full draft")
st.code(full_brief, language="markdown")
st.download_button("Download brief as Markdown", full_brief, file_name=f"bioanalyst_brief_{today}.md", mime="text/markdown")

render_disclaimer_footer()
