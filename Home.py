"""BioAnalyst entry point. Run with: streamlit run Home.py"""
import streamlit as st

from bioanalyst.db.queries import get_companies, get_programs, get_sectors, get_trials, in_sector
from bioanalyst.ui_common import render_disclaimer_footer, render_header

sector_id = render_header("Home")

st.markdown(
    "<style>.block-container{max-width:920px;}</style>",
    unsafe_allow_html=True,
)

sectors = get_sectors()
sector_row = sectors.loc[sectors["sector_id"] == sector_id].iloc[0]

with st.container(key="hero"):
    st.title("BioAnalyst")
    st.caption("Market Intelligence Platform")
    lead_col, support_col = st.columns([3, 2], gap="large")
    with lead_col:
        st.markdown(f"### {sector_row['name']}")
    with support_col:
        st.markdown(f"**Central question**  \n{sector_row['central_question']}")

st.markdown(
    """
BioAnalyst helps a student analyst research a market by connecting, for each company
in a chosen sector: what the technology/therapy does, what evidence supports it, who
would use and pay for it, and what commercial/scientific questions remain unresolved.
"""
)

st.markdown(
    """
Switch sectors any time with the picker in the left sidebar -- it's the same
underlying platform (one database, one set of pages, one AI assistant) applied to
two genuinely different markets, which is itself part of the point: a biotech
sector of public companies with SEC-filed quarterly financials behaves very
differently from a neurotech sector of mostly-private companies with venture
funding disclosures, and this platform is built to keep those two kinds of
financial fact in clearly separate, never-conflated tables.
"""
)

st.divider()

st.markdown(
    """
Use the pages in the left sidebar:
- **Market Overview** — companies, programs, and trial/study-status distribution.
- **Company Profiles** — a deep dive on one company at a time.
- **Clinical Trial Comparison** — compare trial/study design, population, and results status.
- **Financial Analysis** — SEC-sourced figures + runway calculator (biotech), or
  funding-round history (neurotech, where quarterly financials don't exist).
- **Competitive Landscape** — 2-3 companies side by side.
- **Research Brief** — an editable, sourced intelligence brief draft.
- **AI Research Assistant** — ask questions answered only from this curated dataset.
"""
)

st.divider()

st.info(
    "**This is a research aid for preliminary analysis, not clinical guidance, investment "
    "advice, or an automated trading signal.** It never recommends buying/selling a security, "
    "never predicts a trial or regulatory outcome, and never produces an opaque \"best "
    "company\" score.",
    icon="⚠️",
)

companies = in_sector(get_companies(), sector_id)
programs = get_programs()[get_programs()["company_id"].isin(companies["company_id"])]
trials = in_sector(get_trials(), sector_id)

with st.container(border=True):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Companies (this sector)", len(companies))
    col2.metric("Programs", len(programs))
    col3.metric("Trials/studies tracked", len(trials))
    status_counts = trials["results_status"].value_counts()
    col4.metric("With reported results", int(status_counts.get("reported_positive", 0)
                                              + status_counts.get("reported_negative", 0)
                                              + status_counts.get("reported_mixed", 0)))

all_companies = get_companies()
st.caption(
    f"Across both sectors in this platform: {len(all_companies)} companies total "
    f"({len(sectors)} sectors). This project started as two separate student projects "
    f"(NeuroScope for neurotech, BioSignal for biotech) and was unified into one "
    f"platform with a shared schema, retrieval engine, and AI assistant."
)

render_disclaimer_footer()
