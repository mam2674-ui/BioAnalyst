"""
SQLite schema for BioAnalyst -- a unified market-intelligence platform
covering more than one sector (currently: neurotechnology/BCI and
biotechnology/ALS).

Design: a `sectors` table scopes everything else -- each company belongs
to exactly one sector, and most UI pages filter by the sector the user has
selected. Below that, normalized entity tables (companies/programs/trials)
plus TWO parallel financial tables, because the two sectors have
genuinely different financial realities:
  - `financial_periods`: quarterly SEC-filed figures for publicly traded
    companies (biotech sector, currently). Not applicable to a private company.
  - `funding_rounds`: venture funding disclosures for privately held
    companies (neurotech sector, currently). Not the same thing as revenue
    or a quarterly filing, and explicitly not comparable to `financial_periods`.
A `claims` ledger is the single place every claim-level citation lives,
regardless of sector. `snapshots` records a diff whenever a refresh
changes a previously-stored value, so history is never silently overwritten.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "bioanalyst.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS sectors (
    sector_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    central_question TEXT NOT NULL,
    scope_note TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    publisher TEXT NOT NULL,
    document_type TEXT NOT NULL CHECK (document_type IN
        ('sec_10q','sec_10k','sec_8k','sec_xbrl_api','press_release',
         'registry','registry_api','ir_page','news','scientific_publication',
         'funding_tracker','company_site')),
    published_date TEXT,
    retrieved_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS companies (
    company_id TEXT PRIMARY KEY,
    sector_id TEXT NOT NULL REFERENCES sectors(sector_id),
    name TEXT NOT NULL,
    ticker TEXT,
    cik TEXT,
    is_publicly_traded INTEGER NOT NULL DEFAULT 0,
    website TEXT,
    relationship_to_use_case TEXT NOT NULL CHECK (relationship_to_use_case IN ('direct','adjacent')),
    company_notes TEXT
);

CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL REFERENCES companies(company_id),
    program_name TEXT NOT NULL,
    mechanism TEXT NOT NULL,
    modality TEXT NOT NULL,
    target_indication TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL REFERENCES companies(company_id),
    program_name TEXT NOT NULL,
    nct_id TEXT,
    trial_name TEXT NOT NULL,
    phase TEXT NOT NULL,
    status TEXT NOT NULL,
    study_design TEXT,
    population TEXT,
    comparator TEXT,
    enrollment INTEGER,
    primary_endpoint TEXT,
    key_secondary_endpoints TEXT,
    outcome_timing TEXT,
    results_status TEXT NOT NULL CHECK (results_status IN
        ('not_yet_started','planned_not_reported','reported_positive',
         'reported_negative','reported_mixed')),
    reported_outcome TEXT,
    source_document_id INTEGER REFERENCES source_documents(id),
    claim_type TEXT NOT NULL CHECK (claim_type IN
        ('independently-supported','company-reported','analyst-inference','registry-entry')),
    last_registry_check_date TEXT
);

CREATE TABLE IF NOT EXISTS financial_periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL REFERENCES companies(company_id),
    period_end_date TEXT NOT NULL,
    filing_date TEXT,
    period_type TEXT NOT NULL CHECK (period_type IN ('10-Q','10-K')),
    currency_units TEXT NOT NULL DEFAULT 'USD',
    cash_and_equivalents REAL,
    marketable_securities REAL,
    total_debt REAL,
    revenue REAL,
    rd_expense REAL,
    operating_cash_flow REAL,
    shares_outstanding REAL,
    going_concern_flag INTEGER NOT NULL DEFAULT 0,
    source_document_id INTEGER REFERENCES source_documents(id),
    UNIQUE(company_id, period_end_date, period_type)
);

CREATE TABLE IF NOT EXISTS funding_rounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL REFERENCES companies(company_id),
    amount_usd REAL,
    raw_amount_text TEXT NOT NULL,
    round_name TEXT NOT NULL,
    announced_date TEXT,
    source_document_id INTEGER REFERENCES source_documents(id),
    note TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT REFERENCES companies(company_id),
    subject_type TEXT NOT NULL CHECK (subject_type IN
        ('company','program','trial','financial_period','funding_round','uncertainty')),
    subject_ref TEXT NOT NULL,
    field_label TEXT NOT NULL,
    value_text TEXT NOT NULL,
    claim_type TEXT NOT NULL CHECK (claim_type IN
        ('independently-supported','company-reported','analyst-inference','registry-entry')),
    source_document_id INTEGER REFERENCES source_documents(id),
    excerpt TEXT,
    as_of_date TEXT
);

CREATE TABLE IF NOT EXISTS uncertainties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL REFERENCES companies(company_id),
    category TEXT NOT NULL CHECK (category IN ('scientific','operational','commercial')),
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_key TEXT NOT NULL,
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_at TEXT NOT NULL,
    source_document_id INTEGER REFERENCES source_documents(id)
);

CREATE TABLE IF NOT EXISTS refresh_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adapter_name TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL CHECK (status IN ('success','partial','failed')),
    detail TEXT
);

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection):
    conn.executescript(SCHEMA)
    conn.commit()
