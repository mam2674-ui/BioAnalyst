"""
Manual refresh command (section 7 of the project brief: "For the first
version, use a manual refresh button or command. Add scheduled refresh
only after the data pipeline is stable.")

Run as: python3 scripts/refresh_live_data.py

What it does, per company/trial:
- Calls the live SEC EDGAR adapter for each company with a CIK, and the
  live ClinicalTrials.gov adapter for each trial with a known NCT ID.
- Never silently overwrites existing financial_periods rows: a new period
  is only INSERTED if its period_end_date is strictly newer than what's on
  file for that company. If the live source returns data no newer than
  what's stored (a real case found during development: Biogen's live XBRL
  feed currently lags one quarter behind the 10-Q this project read
  manually), that is logged as "no newer data found," not silently ignored.
- Trial status changes ARE applied in place (status is a mutable field,
  not a period snapshot), but the prior value is written to `snapshots`
  first, so history is never lost.
- Every adapter call is logged to `refresh_log` with a status of success,
  partial, or failed, so the UI can show which source last succeeded and
  when, per section 7's requirement to display "which source failed."
"""
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bioanalyst.adapters.clinicaltrials_adapter import get_trial_snapshot
from bioanalyst.adapters.sec_edgar_adapter import get_financial_snapshot
from bioanalyst.db.schema import get_connection


def refresh_financials(conn):
    companies = conn.execute("SELECT company_id, name, cik FROM companies WHERE cik IS NOT NULL").fetchall()
    for comp in companies:
        started = datetime.now(timezone.utc).isoformat()
        snap = get_financial_snapshot(comp["cik"])
        if not snap.fetch_succeeded:
            conn.execute(
                "INSERT INTO refresh_log (adapter_name, started_at, finished_at, status, detail) "
                "VALUES (?,?,?,?,?)",
                ("sec_edgar", started, datetime.now(timezone.utc).isoformat(), "failed",
                 f"{comp['company_id']}: {snap.error}"),
            )
            print(f"[FAILED] SEC EDGAR refresh for {comp['name']}: {snap.error}")
            continue

        latest = conn.execute(
            "SELECT period_end_date FROM financial_periods WHERE company_id=? "
            "ORDER BY period_end_date DESC LIMIT 1", (comp["company_id"],)
        ).fetchone()
        on_file = latest["period_end_date"] if latest else None

        if on_file and snap.period_end_date and snap.period_end_date <= on_file:
            conn.execute(
                "INSERT INTO refresh_log (adapter_name, started_at, finished_at, status, detail) "
                "VALUES (?,?,?,?,?)",
                ("sec_edgar", started, datetime.now(timezone.utc).isoformat(), "success",
                 f"{comp['company_id']}: live data (period {snap.period_end_date}) is not newer than "
                 f"what's on file ({on_file}) -- no new period inserted."),
            )
            print(f"[OK] {comp['name']}: no newer data than what's on file ({on_file}); "
                  f"live feed's latest is {snap.period_end_date}.")
            continue

        conn.execute(
            """INSERT INTO financial_periods
            (company_id, period_end_date, filing_date, period_type, currency_units,
             cash_and_equivalents, marketable_securities, total_debt, revenue, rd_expense,
             operating_cash_flow, shares_outstanding, going_concern_flag, source_document_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,NULL)""",
            (comp["company_id"], snap.period_end_date, snap.filed_date, snap.form, "USD (raw, not millions)",
             snap.values.get("cash_and_equivalents"), snap.values.get("marketable_securities"),
             snap.values.get("total_debt"), snap.values.get("revenue"), snap.values.get("rd_expense"),
             snap.values.get("operating_cash_flow"), snap.shares_outstanding, 0),
        )
        conn.execute(
            "INSERT INTO snapshots (table_name, record_key, field_name, old_value, new_value, changed_at, source_document_id) "
            "VALUES (?,?,?,?,?,?,NULL)",
            ("financial_periods", comp["company_id"], "period_end_date", on_file, snap.period_end_date,
             datetime.now(timezone.utc).isoformat()),
        )
        conn.execute(
            "INSERT INTO refresh_log (adapter_name, started_at, finished_at, status, detail) VALUES (?,?,?,?,?)",
            ("sec_edgar", started, datetime.now(timezone.utc).isoformat(), "success",
             f"{comp['company_id']}: inserted new period {snap.period_end_date} (previously {on_file})."),
        )
        print(f"[UPDATED] {comp['name']}: new financial period {snap.period_end_date} "
              f"(previously {on_file}). NOTE: raw live values are in original filing units "
              f"(not normalized to millions) -- reconcile before display, see docs/DATA_DICTIONARY.md.")


def refresh_trials(conn):
    # Positive match on the real NCT format (NCT + 8 digits) rather than a
    # negative match excluding known "not found"/"not registered" phrasings
    # -- the neurotech sector's data also uses phrasings like "multiple (not
    # consolidated in this pass)" that a negative "NOT LIKE 'not %'" filter
    # would have let through, wastefully calling the API with a value that
    # was never a real NCT id.
    trials = conn.execute(
        "SELECT id, company_id, trial_name, nct_id, status FROM trials "
        "WHERE nct_id GLOB 'NCT[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'"
    ).fetchall()
    for t in trials:
        started = datetime.now(timezone.utc).isoformat()
        snap = get_trial_snapshot(t["nct_id"])
        if not snap.fetch_succeeded:
            conn.execute(
                "INSERT INTO refresh_log (adapter_name, started_at, finished_at, status, detail) VALUES (?,?,?,?,?)",
                ("clinicaltrials_gov", started, datetime.now(timezone.utc).isoformat(), "failed",
                 f"{t['trial_name']} ({t['nct_id']}): {snap.error}"),
            )
            print(f"[FAILED] ClinicalTrials.gov refresh for {t['trial_name']}: {snap.error}")
            continue

        if snap.overall_status and snap.overall_status != t["status"]:
            conn.execute(
                "INSERT INTO snapshots (table_name, record_key, field_name, old_value, new_value, changed_at, source_document_id) "
                "VALUES (?,?,?,?,?,?,NULL)",
                ("trials", t["nct_id"], "status", t["status"], snap.overall_status, datetime.now(timezone.utc).isoformat()),
            )
            conn.execute("UPDATE trials SET status=?, last_registry_check_date=? WHERE id=?",
                         (snap.overall_status, date.today().isoformat(), t["id"]))
            print(f"[CHANGED] {t['trial_name']} status: '{t['status']}' -> '{snap.overall_status}'")
        else:
            conn.execute("UPDATE trials SET last_registry_check_date=? WHERE id=?",
                         (date.today().isoformat(), t["id"]))
            print(f"[OK] {t['trial_name']}: registry status unchanged ({t['status']}).")

        conn.execute(
            "INSERT INTO refresh_log (adapter_name, started_at, finished_at, status, detail) VALUES (?,?,?,?,?)",
            ("clinicaltrials_gov", started, datetime.now(timezone.utc).isoformat(), "success",
             f"{t['trial_name']} ({t['nct_id']}): checked, status={snap.overall_status}, "
             f"enrollment={snap.enrollment_count} ({snap.enrollment_type})."),
        )


def main():
    conn = get_connection()
    print("=== Refreshing financial data from SEC EDGAR ===")
    refresh_financials(conn)
    print("\n=== Refreshing trial status from ClinicalTrials.gov ===")
    refresh_trials(conn)
    conn.execute(
        "INSERT INTO meta (key, value) VALUES ('last_live_refresh_attempt', ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (datetime.now(timezone.utc).isoformat(),),
    )
    conn.commit()
    conn.close()
    print("\nDone. See the `refresh_log` and `snapshots` tables for a full record of this run.")


if __name__ == "__main__":
    main()
