"""Market Overview: companies, programs, trial-status distribution, denominators defined."""
import plotly.express as px
import streamlit as st

from bioanalyst.db.queries import get_companies, get_trials, in_sector
from bioanalyst.ui_common import render_disclaimer_footer, render_header

sector_id = render_header("Market Overview")
st.title("Market Overview")

companies = in_sector(get_companies(), sector_id)
trials = in_sector(get_trials(), sector_id)

st.sidebar.header("Filters")
relationship_opts = sorted(companies["relationship_to_use_case"].unique())
relationship_sel = st.sidebar.multiselect("Relationship to use case", relationship_opts, default=relationship_opts)
phase_opts = sorted(trials["phase"].unique())
phase_sel = st.sidebar.multiselect("Trial/study phase", phase_opts, default=phase_opts)
status_opts = sorted(trials["results_status"].unique())
status_sel = st.sidebar.multiselect("Results status", status_opts, default=status_opts)

filtered_companies = companies[companies["relationship_to_use_case"].isin(relationship_sel)]
filtered_trials = trials[trials["phase"].isin(phase_sel) & trials["results_status"].isin(status_sel)
                          & trials["company_id"].isin(filtered_companies["company_id"])]

st.caption(
    f"Showing **{len(filtered_companies)} of {len(companies)}** companies and "
    f"**{len(filtered_trials)} of {len(trials)}** trials/studies (denominator = all companies/trials "
    f"currently in this dataset's scope for this sector, not the full global market)."
)

c1, c2 = st.columns(2)
with c1:
    if not filtered_trials.empty:
        fig = px.bar(
            filtered_trials["results_status"].value_counts().reset_index(),
            x="results_status", y="count",
            labels={"results_status": "Results status", "count": "Number of trials/studies"},
            title=f"Trials/studies by results status (n = {len(filtered_trials)})",
        )
        st.plotly_chart(fig, width="stretch")
    st.caption(
        "'Reported' here only means an outcome has been disclosed somewhere (company release, "
        "conference presentation, or filing) -- it does not mean independently peer-reviewed, "
        "and 'not_yet_started'/'planned_not_reported' both mean no efficacy conclusion is possible yet."
    )
with c2:
    if not filtered_trials.empty:
        fig2 = px.bar(
            filtered_trials["phase"].value_counts().reset_index(),
            x="count", y="phase", orientation="h",
            labels={"phase": "Phase", "count": "Number of trials/studies"},
            title=f"Trials/studies by phase (n = {len(filtered_trials)})",
        )
        st.plotly_chart(fig2, width="stretch")

st.subheader("Companies in scope")
st.dataframe(
    filtered_companies[["name", "ticker", "relationship_to_use_case", "company_notes"]],
    width="stretch", hide_index=True,
)

st.subheader("Trials/studies in scope")
st.dataframe(
    filtered_trials[["company_name", "trial_name", "phase", "status", "results_status", "outcome_timing"]],
    width="stretch", hide_index=True,
)

render_disclaimer_footer()
