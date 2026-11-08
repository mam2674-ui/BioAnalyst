"""
Pure-Python/SQL logic for the AI Research Assistant, kept separate from
the Streamlit page so it can be unit tested without a running Streamlit
session.

Three deterministic guards run before any retrieval or LLM call:
1. is_out_of_scope() -- declines investment advice, stock price predictions,
   "best company" rankings, and invented market-size/forecast questions,
   since this app explicitly must not produce those (see project brief,
   sections 1 and 6).
2. try_numeric_intent() -- countable questions ("how many trials have
   reported negative results") are answered with a direct SQL COUNT, never
   left to retrieval or an LLM to estimate.
3. try_whats_changed() -- "what changed" questions are answered from the
   `snapshots` table (the versioned change log), not guessed.
"""
import sqlite3

# Word-stem / substring triggers grouped by category, rather than a list of
# exact multi-word phrases. An exact-phrase list is exactly what caused a
# real bug found in manual QA: "Which company is the best investment?" did
# not contain any of the original phrases verbatim ("best company",
# "is it a good investment", etc.) and sailed straight through to
# retrieval, which answered with unrelated financial data as if it were
# investment guidance. Matching on word stems anywhere in the question is
# far more robust than trying to anticipate every phrasing.
INVESTMENT_TRIGGERS = ("invest", "stock price", "share price", "price target",
                        "buy or sell", "good trade", "should i buy", "should i sell")
OUTCOME_PREDICTION_TRIGGERS = ("will the trial succeed", "will it get approved",
                               "will the fda approve", "will it be approved",
                               "guaranteed", "is it going to work", "will it work")
RANKING_TRIGGERS = ("best company", "best investment", "which company is best",
                    "which is the best", "rank the companies", "which stock",
                    "which company should i", "top company", "which one is best")
FORECAST_TRIGGERS = ("market size", "total addressable market", "tam ", "forecast",
                     "market cap in", "projected revenue", "revenue projection")


def is_out_of_scope(question: str) -> str | None:
    """Returns a reason string if the question asks for something this app
    must not produce (investment advice, invented forecasts, clinical
    outcome predictions, an opaque 'best company' ranking), else None.
    Checks RANKING and INVESTMENT triggers first since a question can
    contain words from more than one category (e.g. "best investment")."""
    q = question.lower()

    if any(t in q for t in RANKING_TRIGGERS) or (
        "best" in q and ("compan" in q or "invest" in q or "stock" in q)
    ):
        return ("This app deliberately does not produce an opaque 'best company' or 'best investment' "
                "ranking across programs with different mechanisms, trial designs, and evidence "
                "maturity. Use the Competitive Landscape or Clinical Trial Comparison pages to compare "
                "specific dimensions side by side instead.")

    if any(t in q for t in INVESTMENT_TRIGGERS):
        return ("This is a research tool, not investment advice. It will not predict a stock price, "
                "recommend buying or selling, or judge whether something is a good trade or investment.")

    outcome_verb = any(v in q for v in ("succeed", "get approved", "be approved", "pass", "work"))
    if any(t in q for t in OUTCOME_PREDICTION_TRIGGERS) or (
        "will" in q and (outcome_verb or "approve" in q or "fda" in q)
    ) or "guaranteed" in q:
        return ("This app does not predict clinical trial outcomes or regulatory decisions. It can "
                "show you the trial's design, status, and any reported results -- not a prediction of "
                "what the FDA or a future readout will show.")

    if any(t in q for t in FORECAST_TRIGGERS):
        return ("This dataset does not contain market-size, TAM, or revenue forecast figures, and "
                "this tool will not invent one.")

    return None


def try_numeric_intent(question: str, conn: sqlite3.Connection, sector_id: str | None = None) -> str | None:
    """Returns an answer string for a countable question computed directly
    via SQL, or None if the question doesn't look countable. Scoped to one
    sector by default (matching what the user sees on every other page);
    pass sector_id=None for a platform-wide count across all sectors."""
    q = question.lower()
    if "how many" not in q and "count" not in q:
        return None

    scope_clause = " WHERE c.sector_id = ?" if sector_id else ""
    scope_params = (sector_id,) if sector_id else ()
    scope_note = f" in the {sector_id} sector" if sector_id else " across all sectors"

    if "compan" in q:
        total = conn.execute(
            f"SELECT COUNT(*) FROM companies c{scope_clause}", scope_params
        ).fetchone()[0]
        if "direct" in q:
            n = conn.execute(
                f"SELECT COUNT(*) FROM companies c{scope_clause}"
                f"{' AND' if scope_clause else ' WHERE'} c.relationship_to_use_case='direct'",
                scope_params,
            ).fetchone()[0]
            return f"**{n}** of {total} companies{scope_note} are direct competitors (computed from `companies`, not estimated)."
        if "adjacent" in q:
            n = conn.execute(
                f"SELECT COUNT(*) FROM companies c{scope_clause}"
                f"{' AND' if scope_clause else ' WHERE'} c.relationship_to_use_case='adjacent'",
                scope_params,
            ).fetchone()[0]
            return f"**{n}** of {total} companies{scope_note} are adjacent (computed from `companies`, not estimated)."
        if "non-invasive" in q or "non invasive" in q or "invasive" in q:
            # "invasiveness" isn't its own column in the unified schema --
            # it only exists as free text inside programs.modality (e.g.
            # "Non-invasive -- scalp EEG plus AR display"). Filtering that
            # text directly is still a real SQL COUNT, not a guess, but is
            # necessarily less precise than a clean enum column would be.
            want_non_invasive = "non-invasive" in q or "non invasive" in q
            like_pattern = "Non-invasive%" if want_non_invasive else "Invasive%"
            n = conn.execute(
                f"SELECT COUNT(DISTINCT c.company_id) FROM companies c "
                f"JOIN programs p ON p.company_id = c.company_id{scope_clause}"
                f"{' AND' if scope_clause else ' WHERE'} p.modality LIKE ?",
                (*scope_params, like_pattern),
            ).fetchone()[0]
            label = "non-invasive" if want_non_invasive else "invasive"
            return (f"**{n}** of {total} companies{scope_note} have a {label} program "
                    f"(computed from `programs.modality` text match, not estimated -- "
                    f"invasiveness isn't a dedicated column, so this matches on the modality "
                    f"description starting with '{like_pattern[:-1]}').")
        return f"**{total}** companies are in this dataset{scope_note} (computed from `companies`, not estimated)."

    if "trial" in q or "stud" in q:
        total = conn.execute(
            f"SELECT COUNT(*) FROM trials t JOIN companies c ON c.company_id = t.company_id{scope_clause}",
            scope_params,
        ).fetchone()[0]
        status_map = {
            "negative": "reported_negative", "failed": "reported_negative",
            "positive": "reported_positive", "mixed": "reported_mixed",
            "not yet started": "not_yet_started", "not started": "not_yet_started",
            "pending": "planned_not_reported", "ongoing": "planned_not_reported",
        }
        for phrase, status in status_map.items():
            if phrase in q:
                status_clause = f"{' AND' if scope_clause else ' WHERE'} t.results_status=?"
                n = conn.execute(
                    f"SELECT COUNT(*) FROM trials t JOIN companies c ON c.company_id = t.company_id"
                    f"{scope_clause}{status_clause}",
                    (*scope_params, status),
                ).fetchone()[0]
                return (f"**{n}** of {total} trials/studies{scope_note} have status `{status}` "
                        f"(computed from `trials`, not estimated).")
        return f"**{total}** trials/studies are in this dataset{scope_note} (computed from `trials`, not estimated)."

    return None


def try_whats_changed(question: str, conn: sqlite3.Connection) -> str | None:
    """Returns a summary of the most recent entries in the snapshots table
    if the question asks what changed, else None. Never invents a change
    that wasn't logged."""
    q = question.lower()
    if not any(p in q for p in ("what changed", "what's changed", "whats changed", "recent change", "since the last")):
        return None

    rows = conn.execute(
        "SELECT table_name, record_key, field_name, old_value, new_value, changed_at "
        "FROM snapshots ORDER BY changed_at DESC LIMIT 10"
    ).fetchall()
    if not rows:
        return ("No changes have been logged in the `snapshots` table yet -- this dataset has not had "
                "a live refresh run against it since it was first built, or no live refresh has detected "
                "a difference. Run `python3 scripts/refresh_live_data.py` to check for updates.")
    lines = [f"- `{r['table_name']}` / {r['record_key']} / {r['field_name']}: "
             f"`{r['old_value']}` -> `{r['new_value']}` (detected {r['changed_at']})" for r in rows]
    return "Most recent logged changes (from the `snapshots` table):\n" + "\n".join(lines)
