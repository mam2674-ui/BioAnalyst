"""Shared UI chrome: header, sector picker, disclaimer, staleness banner, claim badges."""
import math

import streamlit as st

from bioanalyst.db.queries import get_meta, get_refresh_log, get_sectors
from bioanalyst.db.schema import DB_PATH


def _ensure_db() -> None:
    """Builds the SQLite DB from seed data on first run. The DB file is
    gitignored (checked-in binary data is an anti-pattern), so a fresh
    deploy -- e.g. Streamlit Community Cloud cloning the repo -- starts
    with no data/bioanalyst.db at all. Every page calls render_header()
    before querying anything, and Streamlit's multipage model runs each
    page's script independently (Home.py's module-level code does not run
    when a user deep-links straight to another page), so this has to live
    here rather than in Home.py alone."""
    if not DB_PATH.exists():
        from bioanalyst.db.load_seed import load
        load()


def is_missing(value) -> bool:
    """True for both None and NaN. A value read from a SQL NULL via pandas
    comes back as NaN for numeric (REAL/INTEGER) columns but as None for
    text columns -- `value is None` alone silently misses the numeric case
    and ends up displaying the literal string 'nan' to the user instead of
    'not found'/'not disclosed'. This is the single check to use instead."""
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False


def fmt_money(value, decimals: int = 2, missing_label: str = "not found") -> str:
    return f"${value:.{decimals}f}M" if not is_missing(value) else missing_label


def fmt_number(value, decimals: int = 1, suffix: str = "M", missing_label: str = "not found") -> str:
    return f"{value:.{decimals}f}{suffix}" if not is_missing(value) else missing_label


def fmt_value(value, missing_label: str = "not found"):
    return value if not is_missing(value) else missing_label


def md_safe(text) -> str:
    """Escapes a dollar sign in free-text DATA (claim text, filing notes,
    company notes) before it goes through st.markdown/st.write/st.warning/
    etc. Streamlit's markdown renderer treats a pair of '$' as inline LaTeX
    math -- real bug found during manual QA: a financial note like '...
    ($25.4M + $40.0M = $65.4M total liquidity)' rendered as garbled unicode
    math notation instead of plain text, because it has multiple '$' pairs.
    Apply this to any data-sourced string before display; it is not needed
    for UI strings you write yourself (headers, labels) unless they also
    contain a literal '$'."""
    if text is None:
        return text
    return str(text).replace("$", "\\$")


CLAIM_TYPE_LABELS = {
    "independently-supported": "Independently supported",
    "company-reported": "Company-reported",
    "registry-entry": "Registry entry",
    "analyst-inference": "Analyst inference",
}
CLAIM_TYPE_ICONS = {
    "Independently supported": "🟢",
    "Company-reported": "🟡",
    "Registry entry": "🔷",
    "Analyst inference": "🔵",
}

SECTOR_ICONS = {"biotech_als": "🧬", "neurotech_bci": "🧠"}


def inject_design_system() -> None:
    """Platform-wide visual system (run once per page via render_header).

    Restrained color strategy: one accent (deep blue, set in
    .streamlit/config.toml) plus neutrals; no full-bleed color on
    data-dense pages. Pill-shaped controls and tightened display-type
    tracking are the two structural cues carried over from auditing
    untillabs.com's marketing site, translated for an Operate-mode
    research tool: the pill language reads as "interactive control"
    rather than "campaign CTA," and the type tightening is reserved for
    headings, never body text at a dense data size."""
    st.markdown(
        """
        <style>
        .stButton > button,
        div[data-baseweb="select"] > div,
        div[data-baseweb="base-input"] {
            border-radius: 999px !important;
        }
        h1 {
            letter-spacing: -0.02em;
            font-weight: 700 !important;
        }
        h2, h3 {
            letter-spacing: -0.01em;
        }
        [data-testid="stMetricValue"] {
            font-weight: 700;
        }
        .st-key-hero {
            background: linear-gradient(135deg, #EEF2FC 0%, #DCE6FA 55%, #FFFFFF 100%);
            border-radius: 24px;
            padding: 2.25rem 2.25rem 1.75rem 2.25rem;
            margin-bottom: 0.5rem;
        }
        .st-key-hero h1 {
            margin-bottom: 0.1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sector_picker() -> str:
    """Renders the sector selector in the sidebar and returns the active
    sector_id.

    Seeded from `st.query_params` only on first load (e.g. a deep link
    like `?sector=neurotech_bci`); every render after that defers entirely
    to `st.session_state["active_sector_id"]` via the widget's `key=`,
    which is the documented Streamlit mechanism for persisting a choice
    across multipage navigation within one session.

    Manual QA note: this is the textbook-correct Streamlit pattern (seed
    session_state once, never pass `index=` afterward, let the widget's
    `key=` carry it across reruns) -- an earlier version broke this by
    recomputing `index=` from `st.query_params` on every render, which
    overrides session_state's persisted value every time (fixed here).
    Separately, testing inside this project's preview/browser-pane tool
    showed the sector STILL reverting to the first option after clicking
    a sidebar page link, even with this corrected pattern -- which,
    combined with the fact that Streamlit's native page-navigation links
    also drop the URL's query string on click, suggests the preview tool's
    proxy may start a fresh server-side session per page path rather than
    reusing one WebSocket session, which is not standard `streamlit run`
    behavior. This could not be confirmed either way from inside that same
    tool. If you see the sector reset when navigating in a real browser
    tab at the app's own URL (not through a preview/sharing proxy), that
    would indicate a genuine bug here; please report it with those exact
    conditions so it can be reproduced and fixed."""
    sectors = get_sectors()
    options = sectors["sector_id"].tolist()
    labels = {row["sector_id"]: f"{SECTOR_ICONS.get(row['sector_id'], '')} {row['name']}"
              for _, row in sectors.iterrows()}

    if "active_sector_id" not in st.session_state:
        query_sector = st.query_params.get("sector")
        st.session_state["active_sector_id"] = query_sector if query_sector in options else options[0]

    selected = st.sidebar.selectbox(
        "Sector", options, format_func=lambda sid: labels.get(sid, sid), key="active_sector_id",
    )
    st.query_params["sector"] = selected  # keeps the current URL shareable/bookmarkable
    return selected


def render_header(page_title: str) -> str:
    """Sets page config, renders the sector picker + data-freshness banner,
    and returns the active sector_id for the calling page to filter by."""
    st.set_page_config(page_title=f"BioAnalyst - {page_title}", layout="wide")
    _ensure_db()
    inject_design_system()
    sector_id = render_sector_picker()
    sectors = get_sectors()
    sector_row = sectors.loc[sectors["sector_id"] == sector_id].iloc[0]
    meta = get_meta()

    st.caption(
        f"{SECTOR_ICONS.get(sector_id, '')} **{sector_row['name']}** · "
        f"Seed data last verified: **{meta.get('data_last_verified', 'unknown')}** · "
        "Research tool only — not investment or medical advice."
    )
    st.caption(f"*{sector_row['scope_note']}*")

    last_refresh = meta.get("last_live_refresh_attempt")
    if last_refresh:
        st.caption(f"🔄 Last live-data refresh attempt: {last_refresh[:19].replace('T', ' ')} UTC")
    else:
        st.caption("🔄 No live-data refresh has been run yet in this environment. "
                   "Run `python3 scripts/refresh_live_data.py` to check SEC EDGAR / ClinicalTrials.gov for updates.")

    failed = get_refresh_log()
    if not failed.empty:
        recent_failures = failed[failed["status"] == "failed"]
        if not recent_failures.empty:
            with st.expander(f"⚠️ {len(recent_failures)} source(s) failed on last refresh attempt(s) -- click to see which"):
                for _, r in recent_failures.iterrows():
                    st.write(f"**{r['adapter_name']}** at {r['started_at'][:19].replace('T',' ')}: {r['detail']}")

    return sector_id


def claim_badge(claim_type_key: str) -> str:
    label = CLAIM_TYPE_LABELS.get(claim_type_key, claim_type_key)
    icon = CLAIM_TYPE_ICONS.get(label, "⚪")
    return f"{icon} {label}"


def render_disclaimer_footer():
    with st.expander("About this data (read before citing anything externally)"):
        st.write(
            "This is a student portfolio research tool, not investment or medical advice. "
            "It does not recommend buying, selling, or holding any security, and does not "
            "predict trial outcomes or regulatory decisions."
        )
        st.write(
            "Claim types used throughout: 🟢 **Independently supported** (regulator, registry, or "
            "primary filing), 🟡 **Company-reported** (the company's own press release/site, not yet "
            "independently re-verified by this project), 🔷 **Registry entry** (ClinicalTrials.gov "
            "record, which is a plan/status, not a result), 🔵 **Analyst inference** (this project's "
            "own interpretation)."
        )
        st.write(
            "A regulatory designation (e.g., FDA Breakthrough Device, accelerated approval basis, "
            "510(k) clearance) is not the same as full marketing approval. A registered or ongoing "
            "trial is not evidence of efficacy. **Funding raised (neurotech sector) is not revenue, "
            "and is not the same kind of fact as a quarterly SEC filing (biotech sector) -- the two "
            "are shown in separate tables and should never be compared directly.** See "
            "`docs/DATA_DICTIONARY.md` for the full sourcing methodology and a checklist of fields "
            "that still need a second verification pass."
        )
