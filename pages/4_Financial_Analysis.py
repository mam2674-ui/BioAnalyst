"""
Financial Analysis.

Branches by company type, because the two sectors have genuinely
different financial realities:
- Publicly traded, SEC-filing companies (biotech sector): sourced
  quarterly figures + an editable cash-runway scenario calculator.
- Privately held companies (neurotech sector, mostly): funding-round
  history instead -- there is no quarterly filing to source a runway
  calculator from, and funding raised is not revenue or a burn rate.
"""
import streamlit as st

from bioanalyst.db.queries import get_companies, get_financial_periods, get_funding_rounds, in_sector, related
from bioanalyst.finance.calculations import compute_cash_runway, quarterly_burn_from_operating_cash_flow
from bioanalyst.ui_common import fmt_money, fmt_number, fmt_value, md_safe, render_disclaimer_footer, render_header

sector_id = render_header("Financial Analysis")
st.title("Financial Analysis")

companies = in_sector(get_companies(), sector_id)
financials = get_financial_periods()
funding_rounds = get_funding_rounds()

selected_name = st.selectbox("Choose a company", sorted(companies["name"].tolist()))
row = companies.loc[companies["name"] == selected_name].iloc[0]
cid = row["company_id"]

is_sec_filer = bool(row["is_publicly_traded"]) and fmt_value(row["cik"], None) is not None

if not is_sec_filer:
    st.info(
        f"**{row['name']} is privately held** (or, if publicly listed, not an SEC filer -- see "
        f"its Company Profile for details), so there are no quarterly financial statements to "
        f"source a runway calculator from. Showing funding-round history instead.",
        icon="ℹ️",
    )
    company_funding = related(funding_rounds, cid)
    if company_funding.empty:
        st.warning("No funding data logged for this company.")
        st.stop()

    st.subheader("Disclosed funding rounds")
    for _, fr in company_funding.iterrows():
        with st.container(border=True):
            st.markdown(f"**{fr['round_name']}** -- {md_safe(fr['raw_amount_text'])}")
            st.write(f"Announced: {fr['announced_date']}")
            st.caption(md_safe(fr["note"]))
            if fr["source_url"]:
                st.caption(f"Source: [{fr['source_url']}]({fr['source_url']})")
    st.caption(
        "**Funding raised is not revenue, is not a quarterly financial statement, and says "
        "nothing on its own about burn rate or runway** -- none of those can be computed from a "
        "funding announcement, which is why no calculator is shown here for this company."
    )
    render_disclaimer_footer()
    st.stop()

company_fin = related(financials, cid).sort_values("period_end_date", ascending=False)

if company_fin.empty:
    st.info("No financial data logged for this company.")
    st.stop()

f = company_fin.iloc[0]
if f["going_concern_flag"]:
    st.error("⚠️ This filing discloses **substantial doubt about the company's ability to "
             "continue as a going concern.**", icon="🚨")

st.subheader(f"Sourced figures as of {f['period_end_date']} ({f['period_type']})")
c1, c2, c3 = st.columns(3)
c1.metric("Cash & equivalents", fmt_money(f['cash_and_equivalents']))
c1.metric("Marketable securities", fmt_money(f['marketable_securities'], missing_label="not disclosed"))
c2.metric("R&D expense (quarter)", fmt_money(f['rd_expense']))
c2.metric("Operating cash flow (quarter)", fmt_money(f['operating_cash_flow']))
c3.metric("Revenue (quarter)", fmt_money(f['revenue'], missing_label="not disclosed"))
c3.metric("Shares outstanding", fmt_number(f['shares_outstanding']))
st.caption(
    f"Historical, as-filed figures. Units: {f['currency_units']}. Filed {f['filing_date']}. "
    + (f"[Source filing]({f['source_url']})" if f['source_url'] else "")
)

st.divider()
st.subheader("Cash runway scenario calculator")
st.caption(
    "This calculator uses the formula `quarters_of_runway = liquidity / quarterly_burn`, computed "
    "in code -- never estimated or guessed. Burn-rate assumptions below are editable and NOT a "
    "forecast; they default to this quarter's historical operating cash outflow only as a "
    "starting point, which may include one-time items that won't recur."
)

include_securities = st.checkbox(
    "Include marketable securities in liquidity (not always as immediately liquid as cash)",
    value=True,
)

suggested_burn = quarterly_burn_from_operating_cash_flow(f["operating_cash_flow"])
if suggested_burn is None:
    st.warning("No operating cash flow figure on file for this period -- enter burn-rate assumptions manually below.")
    suggested_burn = 5.0

bc1, bc2, bc3 = st.columns(3)
conservative = bc1.number_input("Conservative (higher) quarterly burn, $M", min_value=0.0,
                                  value=round(suggested_burn * 1.25, 2), step=0.5)
base = bc2.number_input("Base case quarterly burn, $M", min_value=0.0, value=round(suggested_burn, 2), step=0.5)
optimistic = bc3.number_input("Optimistic (lower) quarterly burn, $M", min_value=0.0,
                                value=round(suggested_burn * 0.75, 2), step=0.5)

result = compute_cash_runway(
    company_id=cid,
    cash_and_equivalents=f["cash_and_equivalents"],
    marketable_securities=f["marketable_securities"],
    include_marketable_securities=include_securities,
    conservative_burn=conservative, base_burn=base, optimistic_burn=optimistic,
)

st.markdown(f"**Liquidity used:** ${result.liquidity_used:.2f}M ({result.liquidity_components})")
st.code(result.formula, language="text")

rc = st.columns(3)
for col, scenario in zip(rc, result.scenarios):
    with col:
        st.metric(scenario.label, f"{scenario.quarters_of_runway} quarters" if scenario.quarters_of_runway is not None else "n/a")
        if scenario.runway_exhausted_note:
            st.caption(scenario.runway_exhausted_note)

if result.missing_inputs:
    for m in result.missing_inputs:
        st.warning(m, icon="⚠️")

st.caption(
    "Distinguish: this is an *estimated* runway from a single quarter's historical cash flow and "
    "editable assumptions -- not company guidance, not a projection the company has made, and not "
    "a measure of solvency on its own. A company can raise additional capital, change spending, or "
    "generate unexpected revenue/milestone payments that this simple calculation cannot anticipate."
)

render_disclaimer_footer()
