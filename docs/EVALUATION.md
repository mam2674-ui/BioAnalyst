# Evaluation

This documents what was **actually run**, including the real bugs it
found and the fixes that followed — not a polished final number presented
without its history. Per the project's own rule (don't invent benchmark
scores), everything below is a real, reproducible result.

## What was run, and what wasn't

**Run:** the 30-question set in `docs/eval_questions.csv` against the
deterministic pipeline only — the out-of-scope guard, the numeric-intent
handler, the "what changed" handler, and keyword retrieval over the
`claims` ledger (`scripts/run_evaluation.py`).

**Not run:** the "grounded assistant vs. ungrounded LLM" comparison the
project brief asks for, and any measurement of LLM answer quality,
citation support in an AI-synthesized answer, or API cost. This
development environment has no `ANTHROPIC_API_KEY` configured. If you add
one, `scripts/run_evaluation.py` can be extended to also call
`bioanalyst.ai.client.synthesize()` per question and compare — that's the
next step, not yet done.

**Not run:** the 3-5 person user test (see `docs/USER_TESTING_PLAN.md`).
No claim of user data appears anywhere in this repo.

## Reproduce this

```bash
python3 -m bioanalyst.db.load_seed
python3 scripts/run_evaluation.py
```

Outputs a per-question table to stdout and `docs/eval_results.csv`.

## Results (current, reproducible)

**27 PASS / 2 PARTIAL / 1 FAIL** out of 30 questions. Average response
time 0.48ms per question (pure Python/SQLite — no network or LLM call, so
no API cost for this run).

| Category | Pass | Partial | Fail |
|---|---|---|---|
| factual_retrieval (6) | 6 | 0 | 0 |
| company_comparison (4) | 3 | 0 | 1 |
| trial_phase_status (4) | 4 | 0 | 0 |
| planned_vs_reported (4) | 4 | 0 | 0 |
| financial_values (4) | 4 | 0 | 0 |
| conflicting_or_outdated (2) | 2 | 0 | 0 |
| unanswerable (3) | 1 | 2 | 0 |
| misleading_premise (3) | 3 | 0 | 0 |

## This evaluation found three real, fixed bugs — not just scored the app

The first run of this evaluation scored **14/30**, not 27/30. Getting from
14 to 27 required fixing real gaps the eval surfaced, each documented in
`docs/DATA_DICTIONARY.md` §5:

1. **Company and program facts were missing from the searchable corpus
   entirely.** All six `factual_retrieval` questions failed on the first
   run (e.g., "What mechanism does Clene's CNM-Au8 use?") because
   `bioanalyst/db/load_seed.py` only ever wrote trial/financial/uncertainty
   facts to the `claims` table — never company or program facts, even
   though those exist in the `companies` and `programs` tables and are
   shown on the Company Profiles page. Fixed by adding
   `_insert_company_and_program_claims()`.
2. **Trial design fields (phase, population, comparator, enrollment,
   planned endpoints, outcome timing) were in the `trials` table but not
   in `claims`.** The assistant could answer "what did this trial show"
   but not "what phase is this trial in" or "when are results expected."
   Fixed by adding a second claim per trial covering design/status,
   tagged `registry-entry` (plan/status information, not a result).
3. **Two bugs in the evaluation harness itself**, found while
   investigating why fixes #1-2 didn't fully close the gap: the harness's
   keyword-match scoring only looked at `value_text`, not `field_label`
   (which the UI also shows the user), and a hyphen-normalization step was
   applied to the retrieved text but not to the search keyword, so
   `"2026-06-30"` could never match `"2026 06 30"`. Both fixed in
   `scripts/run_evaluation.py`.

I also caught my own mistake in *writing* the eval: question 7 originally
expected the keyword "breakthrough," a term that is never used anywhere in
this ALS dataset (it's FDA terminology from an unrelated earlier project).
Fixed by correcting the expected keyword to "accelerated approval," which
the dataset actually contains.

## What's still a known, unfixed limitation

- **Question 7 (company_comparison) still fails.** "How do Biogen and
  Amylyx's regulatory histories differ?" needs claims from *both*
  companies to answer well, but flat top-k keyword retrieval returned only
  one company's claim in the top results. This is a real limitation of
  single-pass keyword search for multi-entity comparison questions, not
  something I patched around. The honest next step, if this mattered at
  production scale, would be detecting multi-entity questions and running
  retrieval once per entity -- not yet built.
- **Questions 26-27 (unanswerable) score PARTIAL, not PASS.** Both ask
  about information genuinely not in this dataset (an independent data
  monitoring committee's assessment; an exact dosing schedule). The
  retriever returns some loosely related claims (best_score 2-3) rather
  than cleanly refusing. The `min_score=2` threshold is deliberately loose
  enough to avoid false refusals on real questions (see the NeuroScope
  project's regression test for the opposite failure mode), which trades
  off against over-eagerly answering genuinely unanswerable ones. This is
  a real precision/recall tradeoff, not a bug — worth knowing about.

## Retrieval vs. generation, evaluated separately

Per the brief's instruction to evaluate these separately: everything
above is a retrieval/guard-layer evaluation. No generation step
(LLM-written prose) was evaluated, because none ran (no API key). If you
configure `ANTHROPIC_API_KEY` and re-run with the synthesis path enabled,
track separately: factual correctness *of the LLM's prose*, whether it
preserves the claim-type distinctions it was given, and whether it cites
snippet numbers correctly -- none of that is implied by the retrieval
layer scoring well, since the retrieval layer's job is only to surface the
right raw material.

## Update: after unifying with the neurotech sector (BioAnalyst)

Running this same 30-question set with retrieval unscoped across both
sectors (rather than scoped to `biotech_als`, which is what all 30
questions were written for) dropped the score from 27/30 to 26/30:
question 10 ("Which company's trial is closest to reporting results?",
expecting MediciNova's "end of 2026" COMBAT-ALS readout) lost its answer
because adding ~50 neurotech claims to the same flat top-6 keyword search
pushed it out of the results. This is a real, honest finding about
cross-sector retrieval precision, not a bug: the production AI Research
Assistant page scopes to the user's active sector by default (with an
explicit "search across all sectors" checkbox for the cross-sector case),
and `scripts/run_evaluation.py` now matches that default by evaluating
with `sector_id="biotech_als"`, which restores 27/30. The unscoped,
26/30 result is left documented here rather than hidden, since it is a
genuine tradeoff of the "search across all sectors" option a user can
still choose.
