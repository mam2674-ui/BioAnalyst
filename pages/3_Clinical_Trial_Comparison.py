"""Clinical Trial Comparison: compare trial design/evidence without ranking efficacy across trials."""
import streamlit as st

from bioanalyst.db.queries import get_trials, in_sector
from bioanalyst.ui_common import claim_badge, fmt_value, md_safe, render_disclaimer_footer, render_header

sector_id = render_header("Clinical Trial Comparison")
st.title("Clinical Trial Comparison")
st.warning(
    "Different trials/studies here have different designs, populations, comparators, and "
    "endpoints. This page deliberately does **not** rank or score them against each other -- a "
    "6-patient safety-focused early feasibility study and a 664-patient confirmatory efficacy "
    "trial are not on the same footing, even when shown side by side.",
    icon="⚖️",
)

trials = in_sector(get_trials(), sector_id)
labels = trials["company_name"] + " -- " + trials["trial_name"]
selected = st.multiselect("Choose 2-4 trials to compare", labels.tolist(), default=labels.tolist()[:3], max_selections=4)

if len(selected) < 2:
    st.info("Select at least 2 trials to compare.")
else:
    rows = [trials.iloc[labels.tolist().index(s)] for s in selected]
    cols = st.columns(len(rows))
    fields = [
        ("Sponsor", "company_name"), ("Intervention", "program_name"), ("Phase", "phase"),
        ("Registry status", "status"), ("Design", "study_design"), ("Population", "population"),
        ("Comparator", "comparator"), ("Enrollment", "enrollment"),
        ("Primary endpoint (planned)", "primary_endpoint"),
        ("Key secondary endpoints (planned)", "key_secondary_endpoints"),
        ("Outcome timing", "outcome_timing"), ("Results status", "results_status"),
    ]
    for col, row in zip(cols, rows):
        with col:
            st.subheader(row["trial_name"])
            for label, field in fields:
                st.markdown(f"**{label}**")
                st.write(fmt_value(row[field]))
                st.markdown("---")
            st.markdown(f"**Reported outcome** ({claim_badge(row['claim_type'])})")
            st.write(md_safe(row["reported_outcome"]))
            if row["source_url"]:
                st.caption(f"[{row['source_publisher']}]({row['source_url']})")

    st.subheader("Why these outcomes may not be directly comparable")
    reasons = []
    if len({r["population"] for r in rows}) > 1:
        reasons.append("Populations differ (e.g., genetically/molecularly restricted vs. broad eligibility, or differing severity criteria).")
    if len({r["comparator"] for r in rows}) > 1:
        reasons.append("Comparators differ (concurrent randomized placebo vs. historical/external controls).")
    if len({r["phase"] for r in rows}) > 1:
        reasons.append("Trial phases differ, so sample sizes and statistical power differ substantially.")
    if len({r["results_status"] for r in rows}) > 1:
        reasons.append("Results maturity differs -- comparing a reported result to a not-yet-reported trial tells you nothing about relative efficacy.")
    if not reasons:
        reasons.append("These trials share similar design parameters in the fields shown, but still "
                        "differ in ways (site selection, era, standard-of-care changes) this table doesn't capture.")
    for r in reasons:
        st.markdown(f"- {r}")

render_disclaimer_footer()
