"""
Runs docs/eval_questions.csv against the actual deterministic pipeline
(out-of-scope guard -> numeric intent -> what-changed -> keyword
retrieval) and records real pass/fail/partial results.

This intentionally does NOT call an LLM: no ANTHROPIC_API_KEY is
configured in this development environment, so the "grounded assistant vs.
ungrounded LLM" comparison the project brief asks for cannot be run here.
This script evaluates the retrieval/guard layer only and says so plainly in
its output -- per the brief's own instruction: "If a model API is
unavailable, run the tests that are possible and clearly describe the
remaining evaluation."

Run as: python3 scripts/run_evaluation.py
"""
import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bioanalyst.ai.assistant_logic import is_out_of_scope, try_numeric_intent, try_whats_changed
from bioanalyst.db.schema import get_connection
from bioanalyst.retrieval.search import load_claims, search


def evaluate_row(row: dict, conn, claims: list, sector_id: str | None) -> dict:
    question = row["question"]
    expected = row["expected_behavior"]
    start = time.perf_counter()

    scope_reason = is_out_of_scope(question)
    numeric_answer = try_numeric_intent(question, conn, sector_id=sector_id) if not scope_reason else None
    changed_answer = try_whats_changed(question, conn) if not scope_reason and not numeric_answer else None
    results, best_score = ([], 0)
    if not scope_reason and not numeric_answer and not changed_answer:
        results, best_score = search(claims, question)

    elapsed_ms = (time.perf_counter() - start) * 1000

    # Include field_label alongside value_text: field_label is part of what
    # the UI actually shows the user for each retrieved claim (see
    # pages/7_AI_Research_Assistant.py), so scoring against value_text alone
    # under-counted real answers -- an earlier version of this harness did
    # that and under-reported the pass rate.
    combined_text = " ".join([
        scope_reason or "", numeric_answer or "", changed_answer or "",
        " ".join(f"{c.field_label} {c.value_text}" for c in results),
    ]).lower().replace("-", " ")

    outcome = "FAIL"
    detail = ""

    if expected.startswith("decline_out_of_scope"):
        outcome = "PASS" if scope_reason else "FAIL"
        detail = scope_reason or "(not declined)"
    elif expected.startswith("should_refuse_or_decline"):
        outcome = "PASS" if (scope_reason or not results) else "FAIL"
        detail = scope_reason or (f"best_score={best_score}, no results" if not results else "answered anyway")
    elif expected.startswith("should_refuse_insufficient_info"):
        outcome = "PASS" if not results else "PARTIAL"
        detail = f"best_score={best_score}, {len(results)} result(s) returned"
    elif expected.startswith("should_correct_misleading_premise"):
        # Heuristic: a correction should surface language distinguishing
        # submission/designation from approval, not just any match.
        flagged = any(w in combined_text for w in ("not yet", "clearance", "not approved",
                                                       "accelerated approval", "designation", "pending"))
        outcome = "PASS" if flagged else "PARTIAL"
        detail = "correcting language found" if flagged else "no explicit correction language found -- needs human review"
    elif expected.startswith("numeric_or_retrieval_mentions:"):
        # Normalize the keyword the same way combined_text was normalized
        # (hyphens -> spaces) -- an earlier version only normalized one
        # side, so a keyword like "2026-06-30" could never match text that
        # had already been turned into "2026 06 30".
        keyword = expected.split(":", 1)[1].lower().replace("-", " ")
        outcome = "PASS" if keyword in combined_text else "FAIL"
        detail = f"looked for '{keyword}'"
    elif expected.startswith("retrieval_mentions:"):
        keyword = expected.split(":", 1)[1].lower().replace("-", " ")
        outcome = "PASS" if keyword in combined_text else "FAIL"
        detail = f"looked for '{keyword}', best_score={best_score}, {len(results)} result(s)"
    elif expected.startswith("changed_answer_or_no_changes_logged"):
        outcome = "PASS" if changed_answer else "FAIL"
        detail = changed_answer[:80] if changed_answer else "(no answer)"
    else:
        detail = f"unrecognized expected_behavior: {expected}"

    return dict(
        id=row["id"], category=row["category"], question=question, outcome=outcome,
        detail=detail, elapsed_ms=round(elapsed_ms, 2),
        declined=bool(scope_reason), had_results=bool(results),
    )


def main():
    # All 30 questions in docs/eval_questions.csv were written for the
    # biotech_als sector (before this platform had multiple sectors), and
    # the AI Research Assistant page scopes retrieval to the user's active
    # sector by default -- so this evaluation should too, to match real
    # default behavior. (Unscoping it, which an earlier version of this
    # script did, is a real but different evaluation: it tests cross-sector
    # retrieval precision, not default single-sector behavior, and one
    # biotech-specific question's score changed when unscoped -- see
    # docs/EVALUATION.md for that finding.)
    sector_id = "biotech_als"
    conn = get_connection()
    claims = load_claims(conn, sector_id=sector_id)

    with (ROOT / "docs" / "eval_questions.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = [evaluate_row(r, conn, claims, sector_id) for r in rows]

    pass_count = sum(1 for r in results if r["outcome"] == "PASS")
    partial_count = sum(1 for r in results if r["outcome"] == "PARTIAL")
    fail_count = sum(1 for r in results if r["outcome"] == "FAIL")

    print(f"{'ID':<4}{'Category':<22}{'Outcome':<10}{'Time(ms)':<10}Detail")
    for r in results:
        print(f"{r['id']:<4}{r['category']:<22}{r['outcome']:<10}{r['elapsed_ms']:<10}{r['detail'][:70]}")

    print(f"\n{len(results)} questions evaluated (deterministic pipeline only -- no LLM call).")
    print(f"PASS: {pass_count}  PARTIAL: {partial_count}  FAIL: {fail_count}")
    print(f"Average response time: {sum(r['elapsed_ms'] for r in results)/len(results):.3f} ms "
          f"(no API cost -- this run made zero LLM calls)")

    out_path = ROOT / "docs" / "eval_results.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
