"""
Loads bioanalyst/adapters/seed_facts.py into the SQLite database, generating
a `claims` row for every citable fact so the UI and AI assistant can cite at
the claim level rather than just at the table-row level.

Run as: python3 -m bioanalyst.db.load_seed

This is idempotent: it wipes and rebuilds all tables from the seed module
each run (appropriate for a curated, versioned seed file -- see
scripts/refresh_live_data.py for the separate live-adapter refresh, which
instead diffs against existing rows and writes to `snapshots`).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from bioanalyst.adapters import seed_facts
from bioanalyst.db.schema import get_connection, init_schema


def _insert_sectors(conn):
    for sector_id, s in seed_facts.SECTORS.items():
        conn.execute(
            "INSERT INTO sectors (sector_id, name, central_question, scope_note) "
            "VALUES (:sector_id, :name, :central_question, :scope_note)",
            dict(sector_id=sector_id, **s),
        )


def _insert_source_documents(conn) -> dict:
    key_to_id = {}
    for key, doc in seed_facts.SOURCE_DOCUMENTS.items():
        cur = conn.execute(
            "INSERT INTO source_documents (title, url, publisher, document_type, published_date, retrieved_date) "
            "VALUES (:title, :url, :publisher, :document_type, :published_date, :retrieved_date)",
            doc,
        )
        key_to_id[key] = cur.lastrowid
    return key_to_id


def _insert_companies(conn):
    for c in seed_facts.COMPANIES:
        conn.execute(
            "INSERT INTO companies (company_id, sector_id, name, ticker, cik, is_publicly_traded, "
            "website, relationship_to_use_case, company_notes) "
            "VALUES (:company_id, :sector_id, :name, :ticker, :cik, :is_publicly_traded, "
            ":website, :relationship_to_use_case, :company_notes)",
            c,
        )


def _insert_programs(conn):
    for p in seed_facts.PROGRAMS:
        conn.execute(
            "INSERT INTO programs (company_id, program_name, mechanism, modality, target_indication) "
            "VALUES (:company_id, :program_name, :mechanism, :modality, :target_indication)",
            p,
        )


def _insert_trials(conn, source_ids: dict):
    claims = []
    for t in seed_facts.TRIALS:
        row = dict(t)
        source_key = row.pop("source_key")
        row["source_document_id"] = source_ids[source_key]
        conn.execute(
            """INSERT INTO trials
            (company_id, program_name, nct_id, trial_name, phase, status, study_design,
             population, comparator, enrollment, primary_endpoint, key_secondary_endpoints,
             outcome_timing, results_status, reported_outcome, source_document_id, claim_type)
            VALUES
            (:company_id, :program_name, :nct_id, :trial_name, :phase, :status, :study_design,
             :population, :comparator, :enrollment, :primary_endpoint, :key_secondary_endpoints,
             :outcome_timing, :results_status, :reported_outcome, :source_document_id, :claim_type)""",
            row,
        )
        claims.append(dict(
            company_id=t["company_id"], subject_type="trial", subject_ref=t["trial_name"],
            field_label=f"{t['trial_name']} ({t['phase']}, {t['status']})",
            value_text=t["reported_outcome"], claim_type=t["claim_type"],
            source_document_id=source_ids[source_key], excerpt=t["reported_outcome"],
            as_of_date=seed_facts.RETRIEVED,
        ))
        # Real gap found via docs/eval_questions.csv: trial design fields
        # (phase, status, population, comparator, enrollment, planned
        # endpoints, outcome timing) were stored in the `trials` table and
        # shown on Company Profiles / Clinical Trial Comparison, but were
        # never added to the `claims` ledger the AI assistant searches --
        # it could answer "what did this trial show" but not "what phase
        # is this trial in" or "when are results expected," because that
        # text simply wasn't in its corpus. This second claim per trial
        # closes that gap with a `registry-entry` claim type, since this
        # is plan/status information, not a result.
        claims.append(dict(
            company_id=t["company_id"], subject_type="trial", subject_ref=t["trial_name"],
            field_label=f"{t['trial_name']} design and status",
            value_text=(
                f"{t['trial_name']} is a {t['phase']} trial, registry status: {t['status']}. "
                f"Design: {t['study_design']}. Population: {t['population']}. "
                f"Comparator: {t['comparator']}. Enrollment: {t['enrollment']}. "
                f"Planned primary endpoint: {t['primary_endpoint']}. "
                f"Planned key secondary endpoints: {t['key_secondary_endpoints']}. "
                f"Outcome timing: {t['outcome_timing']}."
            ),
            claim_type="registry-entry",
            source_document_id=source_ids[source_key],
            excerpt=f"Status: {t['status']}; outcome timing: {t['outcome_timing']}",
            as_of_date=seed_facts.RETRIEVED,
        ))
    return claims


def _insert_financial_periods(conn, source_ids: dict):
    claims = []
    for f in seed_facts.FINANCIAL_PERIODS:
        row = dict(f)
        source_key = row.pop("source_key")
        note = row.pop("note")
        row["source_document_id"] = source_ids[source_key]
        conn.execute(
            """INSERT INTO financial_periods
            (company_id, period_end_date, filing_date, period_type, currency_units,
             cash_and_equivalents, marketable_securities, total_debt, revenue, rd_expense,
             operating_cash_flow, shares_outstanding, going_concern_flag, source_document_id)
            VALUES
            (:company_id, :period_end_date, :filing_date, :period_type, :currency_units,
             :cash_and_equivalents, :marketable_securities, :total_debt, :revenue, :rd_expense,
             :operating_cash_flow, :shares_outstanding, :going_concern_flag, :source_document_id)""",
            row,
        )
        summary = (
            f"Period ended {f['period_end_date']} ({f['period_type']}): "
            f"cash={f['cash_and_equivalents']}, rd_expense={f['rd_expense']}, "
            f"revenue={f['revenue']}, shares_outstanding={f['shares_outstanding']} "
            f"[{f['currency_units']}]. {note}"
        )
        claim_type = "company-reported" if "NOT YET RESOLVED" in note else "independently-supported"
        claims.append(dict(
            company_id=f["company_id"], subject_type="financial_period",
            subject_ref=f["period_end_date"], field_label=f"Financials as of {f['period_end_date']}",
            value_text=summary, claim_type=claim_type,
            source_document_id=source_ids[source_key], excerpt=note,
            as_of_date=seed_facts.RETRIEVED,
        ))
    return claims


def _insert_funding_rounds(conn, source_ids: dict):
    """Venture funding rounds for privately held companies -- a parallel
    track to _insert_financial_periods, since the two are not the same
    kind of fact (a funding round is capital raised, not a quarterly
    financial statement) and should never be casually conflated."""
    claims = []
    for fr in seed_facts.FUNDING_ROUNDS:
        row = dict(fr)
        source_key = row.pop("source_key")
        note = row.pop("note")
        row["source_document_id"] = source_ids[source_key]
        conn.execute(
            """INSERT INTO funding_rounds
            (company_id, amount_usd, raw_amount_text, round_name, announced_date, source_document_id, note)
            VALUES
            (:company_id, :amount_usd, :raw_amount_text, :round_name, :announced_date, :source_document_id, :note)""",
            dict(**row, note=note),
        )
        summary = (
            f"{fr['round_name']} ({fr['raw_amount_text']}), announced {fr['announced_date']}. "
            f"{note} Funding raised is not revenue and is not a quarterly financial statement."
        )
        claims.append(dict(
            company_id=fr["company_id"], subject_type="funding_round",
            subject_ref=fr["round_name"], field_label=f"Funding: {fr['round_name']}",
            value_text=summary, claim_type="company-reported",
            source_document_id=source_ids[source_key], excerpt=note,
            as_of_date=seed_facts.RETRIEVED,
        ))
    return claims


def _insert_company_and_program_claims(conn, source_ids: dict) -> list:
    """
    Real gap found via docs/eval_questions.csv (questions 1, 2, 4, 5 all
    failed): company and program facts -- ticker, mechanism, modality,
    program name -- were only ever written to the `companies`/`programs`
    tables, never to the `claims` ledger the retrieval engine searches.
    The AI assistant could answer "what did Clene's HEALEY trial show" but
    not "what mechanism does Clene's CNM-Au8 use," because that fact
    simply wasn't in its searchable corpus at all. This adds those claims,
    anchored to a source document already cited for that company (a
    financial period, a funding round, or failing that its first trial),
    which is a defensible citation since the underlying program facts were
    gathered in the same research pass as everything else about that company.
    """
    anchor_source = {f["company_id"]: source_ids[f["source_key"]] for f in seed_facts.FINANCIAL_PERIODS}
    for fr in seed_facts.FUNDING_ROUNDS:
        anchor_source.setdefault(fr["company_id"], source_ids[fr["source_key"]])
    for t in seed_facts.TRIALS:
        anchor_source.setdefault(t["company_id"], source_ids[t["source_key"]])

    claims = []
    for c in seed_facts.COMPANIES:
        src = anchor_source.get(c["company_id"])
        ticker_bit = f"ticker {c['ticker']}, " if c["ticker"] else ""
        claims.append(dict(
            company_id=c["company_id"], subject_type="company", subject_ref=c["name"],
            field_label=f"{c['name']} overview",
            value_text=f"{c['name']} ({ticker_bit}{'publicly traded' if c['is_publicly_traded'] else 'privately held'}) "
                       f"is a {c['relationship_to_use_case']} company in this dataset. {c['company_notes']}",
            claim_type="company-reported", source_document_id=src, excerpt=c["company_notes"],
            as_of_date=seed_facts.RETRIEVED,
        ))

    for p in seed_facts.PROGRAMS:
        src = anchor_source.get(p["company_id"])
        claims.append(dict(
            company_id=p["company_id"], subject_type="program", subject_ref=p["program_name"],
            field_label=f"{p['program_name']} program",
            value_text=f"{p['program_name']} is a {p['modality']} with mechanism: {p['mechanism']}. "
                       f"Target indication: {p['target_indication']}.",
            claim_type="company-reported", source_document_id=src,
            excerpt=f"Mechanism: {p['mechanism']}", as_of_date=seed_facts.RETRIEVED,
        ))
    return claims


def _insert_uncertainties(conn):
    claims = []
    for u in seed_facts.UNCERTAINTIES:
        conn.execute(
            "INSERT INTO uncertainties (company_id, category, description) VALUES (:company_id, :category, :description)",
            u,
        )
        claims.append(dict(
            company_id=u["company_id"], subject_type="uncertainty", subject_ref=u["category"],
            field_label=f"{u['category'].capitalize()} uncertainty", value_text=u["description"],
            claim_type="analyst-inference", source_document_id=None, excerpt=None,
            as_of_date=seed_facts.RETRIEVED,
        ))
    return claims


def _insert_claims(conn, claims: list):
    for c in claims:
        conn.execute(
            """INSERT INTO claims
            (company_id, subject_type, subject_ref, field_label, value_text, claim_type,
             source_document_id, excerpt, as_of_date)
            VALUES
            (:company_id, :subject_type, :subject_ref, :field_label, :value_text, :claim_type,
             :source_document_id, :excerpt, :as_of_date)""",
            c,
        )


def load():
    conn = get_connection()
    init_schema(conn)
    tables = ["claims", "snapshots", "refresh_log", "uncertainties", "funding_rounds",
              "financial_periods", "trials", "programs", "companies", "sectors",
              "source_documents", "meta"]
    for t in tables:
        conn.execute(f"DELETE FROM {t}")
    conn.commit()

    _insert_sectors(conn)
    source_ids = _insert_source_documents(conn)
    _insert_companies(conn)
    _insert_programs(conn)
    all_claims = []
    all_claims += _insert_company_and_program_claims(conn, source_ids)
    all_claims += _insert_trials(conn, source_ids)
    all_claims += _insert_financial_periods(conn, source_ids)
    all_claims += _insert_funding_rounds(conn, source_ids)
    all_claims += _insert_uncertainties(conn)
    _insert_claims(conn, all_claims)

    conn.execute("INSERT INTO meta (key, value) VALUES ('data_last_verified', ?)", (seed_facts.RETRIEVED,))
    conn.execute("INSERT INTO meta (key, value) VALUES ('sector_count', ?)", (str(len(seed_facts.SECTORS)),))
    conn.execute("INSERT INTO meta (key, value) VALUES ('company_count', ?)", (str(len(seed_facts.COMPANIES)),))
    conn.execute("INSERT INTO meta (key, value) VALUES ('trial_count', ?)", (str(len(seed_facts.TRIALS)),))
    conn.commit()
    print(f"Loaded {len(seed_facts.SECTORS)} sectors, {len(seed_facts.COMPANIES)} companies, "
          f"{len(seed_facts.PROGRAMS)} programs, {len(seed_facts.TRIALS)} trials, "
          f"{len(seed_facts.FINANCIAL_PERIODS)} financial periods, {len(seed_facts.FUNDING_ROUNDS)} "
          f"funding rounds, {len(seed_facts.UNCERTAINTIES)} uncertainties, {len(all_claims)} claims, "
          f"{len(source_ids)} source documents.")
    conn.close()


if __name__ == "__main__":
    load()
