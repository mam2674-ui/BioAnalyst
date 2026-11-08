"""
Tests for the versioned-snapshot / staleness logic in
scripts/refresh_live_data.py, using an in-memory DB and mocked adapters
so no real network call happens and no real data is mutated.
"""
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from bioanalyst.adapters.clinicaltrials_adapter import TrialRegistrySnapshot
from bioanalyst.adapters.sec_edgar_adapter import FinancialSnapshot
import refresh_live_data


def test_refresh_does_not_insert_a_period_no_newer_than_whats_on_file(db_conn):
    before = db_conn.execute(
        "SELECT COUNT(*) FROM financial_periods WHERE company_id='biogen'"
    ).fetchone()[0]

    stale_snapshot = FinancialSnapshot(
        cik="0000875045", entity_name="BIOGEN INC.", period_end_date="2026-03-31",
        filed_date="2026-04-29", form="10-Q", values={}, shares_outstanding=None,
        fetch_succeeded=True,
    )
    with patch("refresh_live_data.get_financial_snapshot", return_value=stale_snapshot):
        refresh_live_data.refresh_financials(db_conn)

    after = db_conn.execute(
        "SELECT COUNT(*) FROM financial_periods WHERE company_id='biogen'"
    ).fetchone()[0]
    assert after == before, "a non-newer period must not be inserted"

    log = db_conn.execute(
        "SELECT detail FROM refresh_log WHERE adapter_name='sec_edgar' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert "not newer" in log[0]


def test_refresh_inserts_a_genuinely_newer_period_and_logs_a_snapshot(db_conn):
    before = db_conn.execute(
        "SELECT COUNT(*) FROM financial_periods WHERE company_id='medicinova'"
    ).fetchone()[0]

    newer_snapshot = FinancialSnapshot(
        cik="0001226616", entity_name="MEDICINOVA INC", period_end_date="2099-12-31",
        filed_date="2100-01-01", form="10-Q",
        values={"cash_and_equivalents": 1.0, "marketable_securities": None, "total_debt": None,
                "revenue": None, "rd_expense": None, "operating_cash_flow": None},
        shares_outstanding=None, fetch_succeeded=True,
    )

    def fake_snapshot(cik):
        # Other companies: succeed but report no newer data than what's on
        # file, so this test doesn't pollute refresh_log with unrelated
        # 'failed' rows that a later test's exact-count assertion would see.
        if cik == "0001226616":
            return newer_snapshot
        return FinancialSnapshot(cik=cik, entity_name="other", period_end_date="2000-01-01",
                                  filed_date="2000-01-02", form="10-Q", values={},
                                  shares_outstanding=None, fetch_succeeded=True)

    with patch("refresh_live_data.get_financial_snapshot", side_effect=fake_snapshot):
        refresh_live_data.refresh_financials(db_conn)

    after = db_conn.execute(
        "SELECT COUNT(*) FROM financial_periods WHERE company_id='medicinova'"
    ).fetchone()[0]
    assert after == before + 1

    snap_row = db_conn.execute(
        "SELECT old_value, new_value FROM snapshots WHERE table_name='financial_periods' "
        "AND record_key='medicinova' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert snap_row is not None
    assert snap_row[1] == "2099-12-31"


def test_refresh_logs_failed_status_when_adapter_fails(db_conn):
    company_count = len(db_conn.execute("SELECT company_id FROM companies WHERE cik IS NOT NULL").fetchall())
    before = db_conn.execute(
        "SELECT COUNT(*) FROM refresh_log WHERE adapter_name='sec_edgar' AND status='failed'"
    ).fetchone()[0]

    with patch("refresh_live_data.get_financial_snapshot",
               return_value=FinancialSnapshot(cik="x", fetch_succeeded=False, error="mocked failure")):
        refresh_live_data.refresh_financials(db_conn)

    after = db_conn.execute(
        "SELECT COUNT(*) FROM refresh_log WHERE adapter_name='sec_edgar' AND status='failed'"
    ).fetchone()[0]
    assert after - before == company_count, "exactly one failed log entry per company with a CIK"


def test_trial_status_change_is_logged_to_snapshots_before_being_applied(db_conn):
    before_status = db_conn.execute(
        "SELECT status FROM trials WHERE nct_id='NCT04057898'"
    ).fetchone()[0]

    changed_snapshot = TrialRegistrySnapshot(
        nct_id="NCT04057898", title="mock", overall_status="Completed", raw_status="COMPLETED",
        enrollment_count=234, enrollment_type="ACTUAL", last_update_posted="2099-01-01",
        fetch_succeeded=True,
    )
    with patch("refresh_live_data.get_trial_snapshot", return_value=changed_snapshot):
        refresh_live_data.refresh_trials(db_conn)

    after_status = db_conn.execute(
        "SELECT status FROM trials WHERE nct_id='NCT04057898'"
    ).fetchone()[0]
    assert after_status == "Completed"
    assert after_status != before_status

    snap_row = db_conn.execute(
        "SELECT old_value, new_value FROM snapshots WHERE table_name='trials' "
        "AND record_key='NCT04057898' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert tuple(snap_row) == (before_status, "Completed")
