"""Competitive Landscape: 2-3 companies side by side. No opaque 'best company' score."""
import streamlit as st

from bioanalyst.db.queries import (
    get_companies, get_financial_periods, get_funding_rounds, get_trials, get_uncertainties,
    in_sector, related,
)
from bioanalyst.ui_common import fmt_money, md_safe, render_disclaimer_footer, render_header

sector_id = render_header("Competitive Landscape")
st.title("Competitive Landscape")
st.caption(
    "This page deliberately does not compute a single 'best company' score. Programs here differ "
    "in mechanism, population, and evidence maturity in ways a single number would hide."
)

companies = in_sector(get_companies(), sector_id)
trials = get_trials()
financials = get_financial_periods()
funding_rounds = get_funding_rounds()
uncertainties = get_uncertainties()

options = sorted(companies["name"].tolist())
selected = st.multiselect("Choose 2-3 companies", options, default=options[:2], max_selections=3)

if len(selected) < 2:
    st.warning("Select at least 2 companies to compare.")
else:
    rows = [companies.loc[companies["name"] == name].iloc[0] for name in selected]
    cols = st.columns(len(rows))
    for col, row in zip(cols, rows):
        with col:
            st.subheader(row["name"])
            st.markdown(f"**Relationship:** {row['relationship_to_use_case']}")
            st.markdown("**Notes:**")
            st.write(md_safe(row["company_notes"]))

            company_trials = related(trials, row["company_id"])
            st.markdown(f"**Trials/studies ({len(company_trials)}):**")
            for _, t in company_trials.iterrows():
                st.markdown(f"- *{t['trial_name']}* ({t['phase']}): {t['results_status']}")

            company_fin = related(financials, row["company_id"]).sort_values("period_end_date", ascending=False)
            if not company_fin.empty:
                f = company_fin.iloc[0]
                going_concern = " ⚠️ going-concern doubt disclosed" if f["going_concern_flag"] else ""
                st.markdown(
                    f"**Financials ({f['period_end_date']}):** cash "
                    f"{fmt_money(f['cash_and_equivalents'])}{going_concern}"
                )
            else:
                company_fund = related(funding_rounds, row["company_id"])
                if not company_fund.empty:
                    latest = company_fund.iloc[0]
                    st.markdown(
                        f"**Funding:** {md_safe(latest['raw_amount_text'])} ({latest['round_name']}) "
                        f"-- not revenue, not comparable to a quarterly filing"
                    )

            company_unc = related(uncertainties, row["company_id"])
            st.markdown("**Key barriers:**")
            for _, u in company_unc[company_unc["category"] == "commercial"].iterrows():
                st.markdown(f"- {md_safe(u['description'])}")

    st.subheader("Standard of care and alternatives")
    if sector_id == "biotech_als":
        st.write(
            "None of these companies' programs compete only against each other -- all ALS patients "
            "in the US also have access to riluzole (approved 1995) and edaravone (Radicava, approved "
            "2017), both modest-benefit standard-of-care therapies. Any adoption assessment for a new "
            "program needs to ask how much it improves on that existing baseline, not just whether its "
            "own trial looked positive in isolation. (This is analyst framing, not a sourced claim about "
            "a specific head-to-head trial -- no such trial was found in this research pass.)"
        )
    else:
        st.write(
            "None of these companies' programs compete only against each other -- people with severe "
            "speech/motor impairment already have access to non-BCI assistive technology, most notably "
            "eye-tracking speech-generating devices (AAC). Any adoption assessment for a new BCI needs "
            "to ask how much it improves on that existing baseline for a given patient (especially once "
            "eye-tracking performance declines, e.g. late-stage ALS), not just whether its own feasibility "
            "study looked promising in isolation. (This is analyst framing, not a sourced claim about a "
            "specific head-to-head comparison -- Cognixion's own study is explicitly designed around this "
            "comparison, but results were not found in this research pass.)"
        )

render_disclaimer_footer()
