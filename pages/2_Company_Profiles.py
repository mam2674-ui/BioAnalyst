"""Company Profiles: plain-language tech, programs, trial evidence, financials/funding, uncertainties."""
import streamlit as st

from bioanalyst.db.queries import (
    get_companies, get_financial_periods, get_funding_rounds, get_programs, get_trials,
    get_uncertainties, in_sector, related,
)
from bioanalyst.ui_common import claim_badge, fmt_money, fmt_number, fmt_value, md_safe, render_disclaimer_footer, render_header

sector_id = render_header("Company Profiles")
st.title("Company Profiles")

companies = in_sector(get_companies(), sector_id)
programs = get_programs()
trials = get_trials()
financials = get_financial_periods()
funding_rounds = get_funding_rounds()
uncertainties = get_uncertainties()

selected_name = st.selectbox("Choose a company", sorted(companies["name"].tolist()))
row = companies.loc[companies["name"] == selected_name].iloc[0]
cid = row["company_id"]

st.caption("🔷 Direct competitor" if row["relationship_to_use_case"] == "direct" else "🟨 Adjacent company")
ticker_bit = f" ({row['ticker']})" if fmt_value(row["ticker"], None) else ""
st.header(f"{row['name']}{ticker_bit}")
st.caption("Publicly traded" if row["is_publicly_traded"] else "Privately held")
if fmt_value(row["website"], None):
    st.markdown(f"[{row['website']}]({row['website']})")
if row["company_notes"]:
    st.warning(md_safe(row["company_notes"]), icon="ℹ️")

st.subheader("Programs")
for _, p in related(programs, cid).iterrows():
    with st.container(border=True):
        st.markdown(f"**{p['program_name']}** -- {p['modality']}")
        st.write(f"Mechanism: {p['mechanism']}")
        st.write(f"Target indication: {p['target_indication']}")

st.subheader("Clinical trials / studies and evidence")
company_trials = related(trials, cid)
if company_trials.empty:
    st.info("No trials/studies logged for this company in this dataset.")
for _, t in company_trials.iterrows():
    status_color = {"reported_positive": "green", "reported_negative": "red",
                     "reported_mixed": "orange", "not_yet_started": "gray",
                     "planned_not_reported": "blue"}.get(t["results_status"], "gray")
    with st.container(border=True):
        st.markdown(f"**{t['trial_name']}** ({t['phase']}) -- :{status_color}[{t['results_status']}]")
        st.markdown(
            f"- NCT ID: {t['nct_id']}\n"
            f"- Status: {t['status']}\n"
            f"- Design: {t['study_design']}\n"
            f"- Population: {t['population']}\n"
            f"- Comparator: {t['comparator']}\n"
            f"- Enrollment: {fmt_value(t['enrollment'], 'not disclosed')}\n"
            f"- Primary endpoint (planned): {t['primary_endpoint']}\n"
            f"- Key secondary endpoints (planned): {t['key_secondary_endpoints']}\n"
            f"- Outcome timing: {t['outcome_timing']}"
        )
        st.markdown(f"**Reported outcome** ({claim_badge(t['claim_type'])}):")
        st.write(md_safe(t["reported_outcome"]))
        if t["source_url"]:
            st.caption(f"Source: [{t['source_publisher']}]({t['source_url']})")

if row["is_publicly_traded"] and fmt_value(row["cik"], None):
    st.subheader("Financial condition (most recent filed period)")
    company_fin = related(financials, cid).sort_values("period_end_date", ascending=False)
    if company_fin.empty:
        st.info("No financial data logged for this company.")
    else:
        f = company_fin.iloc[0]
        if f["going_concern_flag"]:
            st.error("⚠️ This filing discloses **substantial doubt about the company's ability to "
                     "continue as a going concern.**", icon="🚨")
        fc1, fc2, fc3, fc4 = st.columns(4)
        fc1.metric("Cash & equivalents", fmt_money(f['cash_and_equivalents']))
        fc2.metric("R&D expense (qtr)", fmt_money(f['rd_expense']))
        fc3.metric("Revenue (qtr)", fmt_money(f['revenue'], missing_label="not disclosed"))
        fc4.metric("Shares outstanding", fmt_number(f['shares_outstanding']))
        st.caption(f"As of {f['period_end_date']} ({f['period_type']}, filed {f['filing_date']}). "
                   f"Units: {f['currency_units']}. [Source filing]({f['source_url']})" if f['source_url'] else "")
else:
    st.subheader("Funding history")
    st.caption(
        "This company is privately held (or, if publicly listed, not an SEC filer), so there are "
        "no quarterly financial statements -- venture/growth funding disclosures are shown instead. "
        "**Funding raised is not revenue and does not indicate profitability or burn rate.**"
    )
    company_funding = related(funding_rounds, cid)
    if company_funding.empty:
        st.info("No funding data logged for this company.")
    for _, fr in company_funding.iterrows():
        with st.container(border=True):
            st.markdown(f"**{fr['round_name']}** -- {md_safe(fr['raw_amount_text'])}")
            st.write(f"Announced: {fr['announced_date']}")
            st.caption(md_safe(fr["note"]))
            if fr["source_url"]:
                st.caption(f"Source: [{fr['source_url']}]({fr['source_url']})")

st.subheader("Key uncertainties")
company_unc = related(uncertainties, cid)
for category in ["scientific", "operational", "commercial"]:
    cat_rows = company_unc[company_unc["category"] == category]
    if not cat_rows.empty:
        st.markdown(f"**{category.capitalize()}**")
        for _, u in cat_rows.iterrows():
            st.markdown(f"- {md_safe(u['description'])}")

render_disclaimer_footer()
