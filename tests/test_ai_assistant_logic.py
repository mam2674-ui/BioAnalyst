"""
AI output validation tests: the deterministic guards that run before any
retrieval or LLM call. Includes a regression test for a real bug found in
manual QA -- "Which company is the best investment?" did not match any of
the original exact-phrase triggers and was answered from retrieval as if
it were a legitimate question.
"""
from bioanalyst.ai.assistant_logic import is_out_of_scope, try_numeric_intent, try_whats_changed
from bioanalyst.retrieval.search import load_claims, search


# ---- is_out_of_scope ----

def test_rejects_best_investment_phrasing_regression():
    assert is_out_of_scope("Which company is the best investment?") is not None


def test_rejects_various_investment_advice_phrasings():
    for q in ["Should I invest in Clene?", "What's the best stock to buy?",
              "Is this a good trade?", "Should I buy BrainStorm shares?"]:
        assert is_out_of_scope(q) is not None, q


def test_rejects_outcome_prediction_phrasings():
    for q in ["Will the FDA approve Clene's NDA?", "Will the COMBAT-ALS trial succeed?"]:
        assert is_out_of_scope(q) is not None, q


def test_rejects_forecast_phrasings():
    assert is_out_of_scope("What is the market size for ALS treatments in 2030?") is not None


def test_rejects_ranking_phrasings():
    assert is_out_of_scope("Rank the companies by quality") is not None
    assert is_out_of_scope("Which company is best?") is not None


def test_allows_legitimate_research_questions():
    legitimate = [
        "What human evidence supports Clene's CNM-Au8 program?",
        "How do the companies' trial designs differ?",
        "What changed since the last source update?",
        "How many trials have reported negative results?",
        "What is BrainStorm's cash position?",
    ]
    for q in legitimate:
        assert is_out_of_scope(q) is None, q


# ---- try_numeric_intent (against the real seeded DB) ----

def test_numeric_intent_counts_companies_correctly(db_conn):
    answer = try_numeric_intent("How many companies are in this dataset?", db_conn)
    total = db_conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    assert f"**{total}**" in answer


def test_numeric_intent_counts_negative_trials_correctly(db_conn):
    answer = try_numeric_intent("How many trials have reported negative results?", db_conn)
    expected = db_conn.execute(
        "SELECT COUNT(*) FROM trials WHERE results_status='reported_negative'"
    ).fetchone()[0]
    assert f"**{expected}**" in answer
    assert expected > 0  # sanity: PHOENIX and the original NurOwn trial should both count


def test_numeric_intent_returns_none_for_non_countable_question(db_conn):
    assert try_numeric_intent("What does Clene's device do?", db_conn) is None


# ---- try_whats_changed ----

def test_whats_changed_reports_no_changes_when_snapshots_table_is_empty(db_conn):
    answer = try_whats_changed("What changed since the last update?", db_conn)
    assert "No changes have been logged" in answer


def test_whats_changed_returns_none_for_unrelated_question(db_conn):
    assert try_whats_changed("What human evidence supports Clene?", db_conn) is None


# ---- retrieval never fabricates a citation ----

def test_every_retrieved_claim_has_a_real_source_or_is_explicitly_inference(db_conn):
    claims = load_claims(db_conn)
    results, _ = search(claims, "Clene CNM-Au8 HEALEY trial evidence")
    assert results
    for c in results:
        if c.claim_type == "analyst-inference":
            assert c.source_url == "(analyst inference, not an external source)"
        else:
            assert c.source_url.startswith("http"), f"non-inference claim must cite a real URL: {c.field_label}"


def test_nonsense_question_returns_no_results_not_a_fabricated_answer(db_conn):
    claims = load_claims(db_conn)
    results, best_score = search(claims, "xyzzy qwerty asdf zzzzz")
    assert results == []
    assert best_score == 0


# ---- sector scoping (unification-specific) ----

def test_numeric_intent_scopes_to_sector_by_default(db_conn):
    biotech_answer = try_numeric_intent("How many companies are there?", db_conn, sector_id="biotech_als")
    neurotech_answer = try_numeric_intent("How many companies are there?", db_conn, sector_id="neurotech_bci")
    biotech_total = db_conn.execute(
        "SELECT COUNT(*) FROM companies WHERE sector_id='biotech_als'"
    ).fetchone()[0]
    neurotech_total = db_conn.execute(
        "SELECT COUNT(*) FROM companies WHERE sector_id='neurotech_bci'"
    ).fetchone()[0]
    assert biotech_total != neurotech_total, "test fixture should have different counts per sector"
    assert f"**{biotech_total}**" in biotech_answer
    assert f"**{neurotech_total}**" in neurotech_answer


def test_numeric_intent_cross_sector_when_sector_id_is_none(db_conn):
    answer = try_numeric_intent("How many companies are there?", db_conn, sector_id=None)
    total = db_conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    assert f"**{total}**" in answer


def test_retrieval_scoped_to_sector_excludes_other_sector_claims(db_conn):
    biotech_claims = load_claims(db_conn, sector_id="biotech_als")
    assert all(c.sector_id == "biotech_als" for c in biotech_claims)
    assert any("clene" == c.company_id for c in biotech_claims) or any(
        c.company_name == "Clene Inc." for c in biotech_claims
    )
    assert not any(c.company_id == "neuralink" for c in biotech_claims)


def test_retrieval_unscoped_includes_both_sectors(db_conn):
    all_claims = load_claims(db_conn, sector_id=None)
    sector_ids = {c.sector_id for c in all_claims}
    assert sector_ids == {"biotech_als", "neurotech_bci"}


def test_numeric_intent_filters_by_invasiveness_via_program_modality(db_conn):
    """Regression test: an earlier version answered 'how many companies are
    non-invasive?' with the total company count, ignoring the invasiveness
    filter entirely, because invasiveness lives only as free text inside
    programs.modality in the unified schema, not its own column."""
    answer = try_numeric_intent(
        "How many companies are non-invasive?", db_conn, sector_id="neurotech_bci"
    )
    expected = db_conn.execute(
        "SELECT COUNT(DISTINCT c.company_id) FROM companies c "
        "JOIN programs p ON p.company_id = c.company_id "
        "WHERE c.sector_id='neurotech_bci' AND p.modality LIKE 'Non-invasive%'"
    ).fetchone()[0]
    total = db_conn.execute(
        "SELECT COUNT(*) FROM companies WHERE sector_id='neurotech_bci'"
    ).fetchone()[0]
    assert expected < total, "test fixture should have a real mix of invasive/non-invasive companies"
    assert f"**{expected}**" in answer
    assert f"of {total}" in answer
