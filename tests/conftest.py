import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def db_conn():
    """A fresh in-memory DB loaded from the real seed data for each test session."""
    import sqlite3

    from bioanalyst.db import load_seed
    from bioanalyst.db.schema import SCHEMA

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)

    # Reuse load_seed's insert helpers against this in-memory connection
    # instead of the on-disk DB, so tests never depend on (or mutate)
    # data/bioanalyst.db.
    load_seed._insert_sectors(conn)
    source_ids = load_seed._insert_source_documents(conn)
    load_seed._insert_companies(conn)
    load_seed._insert_programs(conn)
    claims = []
    claims += load_seed._insert_company_and_program_claims(conn, source_ids)
    claims += load_seed._insert_trials(conn, source_ids)
    claims += load_seed._insert_financial_periods(conn, source_ids)
    claims += load_seed._insert_funding_rounds(conn, source_ids)
    claims += load_seed._insert_uncertainties(conn)
    load_seed._insert_claims(conn, claims)
    conn.commit()
    return conn
