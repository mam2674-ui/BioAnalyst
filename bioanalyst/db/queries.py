"""
Read-side query helpers shared by every Streamlit page. Keeping all SQL in
one module means the UI pages never hand-write SQL, and a schema change
only needs updating here.

Sector filtering: most getters return ALL sectors' rows (cheap to cache
once); pages filter down to the active sector with `in_sector(df, sector_id)`
or `related(df, company_id)` as needed, rather than re-querying per sector.
"""
import pandas as pd
import streamlit as st

from bioanalyst.db.schema import get_connection


def _query(sql: str) -> pd.DataFrame:
    """Opens a fresh connection per call and closes it immediately rather
    than caching the connection object itself (via st.cache_resource).
    sqlite3.Connection objects are bound to the thread that created them;
    an earlier version of this module cached one connection with
    cache_resource and shared it across threads, which raised 'SQLite
    objects created in a thread can only be used in that same thread' the
    first time a second page touched it. Each @st.cache_data function below
    still caches its *result* (a DataFrame), so this only opens a new
    connection on a genuine cache miss -- cheap for a local SQLite file."""
    conn = get_connection()
    try:
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()


@st.cache_data
def get_meta() -> dict:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT key, value FROM meta").fetchall()
    finally:
        conn.close()
    return {r["key"]: r["value"] for r in rows}


@st.cache_data
def get_sectors() -> pd.DataFrame:
    return _query("SELECT * FROM sectors ORDER BY sector_id")


@st.cache_data
def get_companies() -> pd.DataFrame:
    return _query("SELECT * FROM companies ORDER BY name")


@st.cache_data
def get_programs() -> pd.DataFrame:
    return _query("SELECT * FROM programs")


@st.cache_data
def get_trials() -> pd.DataFrame:
    return _query("""
        SELECT t.*, c.name as company_name, c.sector_id, sd.url as source_url, sd.publisher as source_publisher
        FROM trials t
        LEFT JOIN companies c ON c.company_id = t.company_id
        LEFT JOIN source_documents sd ON sd.id = t.source_document_id
        ORDER BY t.company_id, t.trial_name
    """)


@st.cache_data
def get_financial_periods() -> pd.DataFrame:
    return _query("""
        SELECT f.*, c.name as company_name, c.ticker, c.sector_id, sd.url as source_url
        FROM financial_periods f
        LEFT JOIN companies c ON c.company_id = f.company_id
        LEFT JOIN source_documents sd ON sd.id = f.source_document_id
        ORDER BY f.company_id, f.period_end_date DESC
    """)


@st.cache_data
def get_latest_financial_periods() -> pd.DataFrame:
    df = get_financial_periods()
    if df.empty:
        return df
    return df.sort_values("period_end_date").groupby("company_id").tail(1).reset_index(drop=True)


@st.cache_data
def get_funding_rounds() -> pd.DataFrame:
    return _query("""
        SELECT fr.*, c.name as company_name, c.sector_id, sd.url as source_url
        FROM funding_rounds fr
        LEFT JOIN companies c ON c.company_id = fr.company_id
        LEFT JOIN source_documents sd ON sd.id = fr.source_document_id
        ORDER BY fr.company_id
    """)


@st.cache_data
def get_uncertainties() -> pd.DataFrame:
    return _query("SELECT u.*, c.sector_id FROM uncertainties u "
                  "LEFT JOIN companies c ON c.company_id = u.company_id")


@st.cache_data
def get_refresh_log() -> pd.DataFrame:
    return _query("SELECT * FROM refresh_log ORDER BY started_at DESC")


@st.cache_data
def get_snapshots() -> pd.DataFrame:
    return _query("SELECT * FROM snapshots ORDER BY changed_at DESC")


@st.cache_data
def get_source_documents() -> pd.DataFrame:
    return _query("SELECT * FROM source_documents")


def related(df: pd.DataFrame, company_id: str) -> pd.DataFrame:
    return df.loc[df["company_id"] == company_id]


def in_sector(df: pd.DataFrame, sector_id: str) -> pd.DataFrame:
    """Filters any companies-joined DataFrame (it must have a `sector_id`
    column) down to one sector. Every getter above that joins to
    `companies` carries `sector_id` through for exactly this purpose."""
    return df.loc[df["sector_id"] == sector_id]


def clear_all_caches():
    """Called after a live refresh so the UI reflects it without a restart."""
    get_meta.clear()
    get_sectors.clear()
    get_companies.clear()
    get_programs.clear()
    get_trials.clear()
    get_financial_periods.clear()
    get_latest_financial_periods.clear()
    get_funding_rounds.clear()
    get_uncertainties.clear()
    get_refresh_log.clear()
    get_snapshots.clear()
    get_source_documents.clear()
