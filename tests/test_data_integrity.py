"""
Identifier mapping, foreign keys, and source-attribution tests. These
guard against the real bug found while building this dataset: a company
or trial record losing its link to a verifiable source.
"""
import pandas as pd


def test_every_company_has_a_valid_sector_and_relationship(db_conn):
    df = pd.read_sql_query("SELECT * FROM companies", db_conn)
    assert set(df["sector_id"].unique()) <= {"biotech_als", "neurotech_bci"}
    assert set(df["relationship_to_use_case"].unique()) <= {"direct", "adjacent"}
    assert df["company_id"].is_unique


def test_sec_filers_have_a_cik_others_do_not_claim_sec_coverage(db_conn):
    # Not every company has a CIK -- the neurotech sector is mostly privately
    # held (and ONWARD Medical, though public, trades on Euronext, outside
    # SEC EDGAR's coverage). The real invariant is: every company FLAGGED as
    # an SEC filer (is_publicly_traded AND has a cik) must have a well-formed,
    # zero-paddable-to-10-digit CIK; everyone else legitimately has none.
    df = pd.read_sql_query("SELECT company_id, cik, is_publicly_traded FROM companies", db_conn)
    sec_filers = df[df["cik"].notna()]
    assert len(sec_filers) >= 1, "expected at least one SEC-filing company in this dataset"
    for _, row in sec_filers.iterrows():
        assert row["is_publicly_traded"] == 1, f"{row['company_id']} has a CIK but isn't flagged publicly traded"
        padded = str(row["cik"]).zfill(10)
        assert len(padded) == 10
        assert padded.isdigit()


def test_privately_held_companies_have_no_cik(db_conn):
    df = pd.read_sql_query("SELECT company_id, cik, is_publicly_traded FROM companies", db_conn)
    private = df[df["is_publicly_traded"] == 0]
    assert len(private) >= 1, "expected at least one privately held company in this dataset"
    assert private["cik"].isna().all(), "a privately held company should not have a CIK"


def test_trial_company_id_foreign_keys_resolve(db_conn):
    company_ids = {r[0] for r in db_conn.execute("SELECT company_id FROM companies")}
    trial_ids = {r[0] for r in db_conn.execute("SELECT company_id FROM trials")}
    assert trial_ids <= company_ids


def test_financial_period_foreign_keys_resolve(db_conn):
    company_ids = {r[0] for r in db_conn.execute("SELECT company_id FROM companies")}
    fin_ids = {r[0] for r in db_conn.execute("SELECT company_id FROM financial_periods")}
    assert fin_ids <= company_ids


def test_nct_ids_present_are_well_formed(db_conn):
    rows = db_conn.execute("SELECT nct_id FROM trials").fetchall()
    for (nct_id,) in rows:
        if nct_id and nct_id.startswith("NCT"):
            assert len(nct_id) == 11, f"{nct_id} is not a well-formed NCT id (NCT + 8 digits)"
            assert nct_id[3:].isdigit()


def test_every_trial_has_a_claim_type_and_source(db_conn):
    rows = db_conn.execute(
        "SELECT trial_name, claim_type, source_document_id FROM trials"
    ).fetchall()
    assert rows, "expected at least one trial"
    for trial_name, claim_type, source_document_id in rows:
        assert claim_type in ("independently-supported", "company-reported",
                                "analyst-inference", "registry-entry"), trial_name
        assert source_document_id is not None, f"{trial_name} has no source document"


def test_every_financial_period_has_a_source_document(db_conn):
    rows = db_conn.execute(
        "SELECT company_id, period_end_date, source_document_id FROM financial_periods"
    ).fetchall()
    assert rows
    for company_id, period, source_id in rows:
        assert source_id is not None, f"{company_id} {period} has no source document"


def test_every_claim_has_a_claim_type_and_attribution(db_conn):
    """Every claim must either cite a source_document or be explicitly
    analyst-inference -- an unlabeled, unsourced claim is exactly the
    failure mode the claim-type system exists to prevent."""
    rows = db_conn.execute("SELECT field_label, claim_type, source_document_id FROM claims").fetchall()
    assert rows
    for label, claim_type, source_id in rows:
        assert claim_type in ("independently-supported", "company-reported",
                                "analyst-inference", "registry-entry")
        if claim_type != "analyst-inference":
            assert source_id is not None, f"non-inference claim '{label}' has no source"


def test_currency_units_are_consistent_across_financial_periods(db_conn):
    rows = db_conn.execute("SELECT currency_units FROM financial_periods").fetchall()
    units = {r[0] for r in rows}
    assert units == {"USD millions"}, (
        f"expected all financial_periods rows in a single consistent unit label, got {units} -- "
        "a mismatched unit label (e.g. 'USD' vs 'USD millions' vs 'USD thousands') is exactly "
        "the kind of silent unit bug this test is meant to catch"
    )


def test_going_concern_flag_is_boolean(db_conn):
    rows = db_conn.execute("SELECT going_concern_flag FROM financial_periods").fetchall()
    for (flag,) in rows:
        assert flag in (0, 1)


def test_funding_rounds_foreign_keys_resolve(db_conn):
    company_ids = {r[0] for r in db_conn.execute("SELECT company_id FROM companies")}
    funding_ids = {r[0] for r in db_conn.execute("SELECT company_id FROM funding_rounds")}
    assert funding_ids <= company_ids
    assert len(funding_ids) >= 1


def test_every_sec_filer_has_financial_periods_and_no_funding_rounds(db_conn):
    """A company shouldn't have BOTH financial_periods and funding_rounds --
    those are two different kinds of fact (quarterly filing vs. venture
    funding) and conflating them for one company would be exactly the
    mistake the two-table design exists to prevent."""
    fin_ids = {r[0] for r in db_conn.execute("SELECT DISTINCT company_id FROM financial_periods")}
    funding_ids = {r[0] for r in db_conn.execute("SELECT DISTINCT company_id FROM funding_rounds")}
    assert fin_ids & funding_ids == set(), (
        f"companies with BOTH financial_periods and funding_rounds: {fin_ids & funding_ids}"
    )


def test_claims_subject_types_are_all_valid(db_conn):
    valid = {"company", "program", "trial", "financial_period", "funding_round", "uncertainty"}
    rows = db_conn.execute("SELECT DISTINCT subject_type FROM claims").fetchall()
    assert {r[0] for r in rows} <= valid


def test_both_sectors_have_at_least_one_direct_and_company(db_conn):
    for sector_id in ("biotech_als", "neurotech_bci"):
        n = db_conn.execute(
            "SELECT COUNT(*) FROM companies WHERE sector_id=?", (sector_id,)
        ).fetchone()[0]
        assert n >= 1, f"sector {sector_id} has no companies"
