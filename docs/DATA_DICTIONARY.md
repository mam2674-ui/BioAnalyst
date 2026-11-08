# BioAnalyst Data Dictionary and Methodology

## 1. What this dataset is

Every company, program, trial, and financial figure in this dataset is
real — sourced via live web search and, for financial figures and two
trial registry statuses, direct API/filing reads, all retrieved on
**2026-10-27**. This is not synthetic placeholder data.

That said, it is a **student research project's first verification pass**,
not a maintained feed:

- Some fields are explicitly marked "not confirmed in this search pass" or
  "not captured in this pass" where a single research session did not
  turn up a confident answer.
- A regulatory designation (FDA Breakthrough Device, accelerated approval
  basis, 510(k) clearance) is never the same as full marketing approval.
  A registered or ongoing trial is never evidence of efficacy. Funding
  raised is never revenue.
- Company-wide financials (especially Biogen's) are not ALS-program-specific.

## 2. Claim types

| Claim type | Meaning |
|---|---|
| `independently-supported` | Confirmed by a regulator, a direct SEC filing read, or a live registry/API call |
| `company-reported` | From the company's own press release, site, or guidance, not independently re-verified |
| `registry-entry` | A ClinicalTrials.gov record — a plan/status, not a result |
| `analyst-inference` | This project's own interpretation, not sourced to an external document |

## 3. Schema reference

See `bioanalyst/db/schema.py` for exact DDL. Summary:

- **`companies`**: one row per company, including `cik` (used by the live
  SEC adapter) and `relationship_to_use_case` (`direct`/`adjacent`).
- **`programs`**: one row per named drug/therapy program.
- **`trials`**: one row per trial, including `results_status` (an enum:
  `not_yet_started`, `planned_not_reported`, `reported_positive`,
  `reported_negative`, `reported_mixed`) and `last_registry_check_date`
  (set by the live refresh, not the original research pass).
- **`financial_periods`**: one row per filed quarter, all currently in a
  single consistent unit (`USD millions`) — enforced by
  `tests/test_data_integrity.py::test_currency_units_are_consistent...`.
- **`claims`**: the citation ledger. Every claim-level citation shown in
  the UI or the AI assistant comes from this table, not from reading
  `trials`/`financial_periods` columns directly.
- **`uncertainties`**: scientific/operational/commercial, one set per company.
- **`snapshots`**: a diff log (`old_value` → `new_value`) written whenever
  a live refresh detects a change. Never overwritten or deleted.
- **`refresh_log`**: one row per adapter call per refresh run, with status
  (`success`/`partial`/`failed`) and a human-readable detail string.
- **`source_documents`**: every citation's URL, publisher, type, and dates.

## 4. Verification checklist (do this before citing externally)

- [ ] **Biogen** — the live SEC XBRL feed currently resolves cash only
  through Q1 2026 (3/31/2026), one quarter behind the Q2 2026 10-Q this
  project read manually ($1,285.0M). Likely a dimensional/member-qualified
  XBRL fact the API's flat fact list doesn't surface for this specific
  concept at this specific company; not root-caused further. Don't assume
  the live feed is always more current than a manually-read filing.
- [ ] **Biogen** — marketable securities dropped from ~$1,239M (combined
  current+non-current, 12/31/2025) to $0 (6/30/2026) per the manually-read
  10-Q. This is a large move worth directly confirming rather than assuming
  a data error (e.g., reclassification into a different balance-sheet line).
- [ ] **Amylyx** — revenue and operating cash flow for the 6/30/2026
  period came from the live XBRL feed, not independently cross-read from
  the 10-Q text in this pass.
- [ ] **Clene** — `total_debt` differs between two legitimate reads:
  $47.8M (total liabilities, from the balance sheet text) vs. $17.6M
  (specifically the `LongTermDebtNoncurrent` XBRL tag). These are
  different concepts, not a conflict — don't casually substitute one for
  the other in a brief.
- [ ] **All five companies** — NCT (ClinicalTrials.gov) registry IDs were
  only confirmed for Clene's HEALEY trial (NCT04297683) and MediciNova's
  COMBAT-ALS (NCT04057898). Other trials' NCT IDs were not captured in
  this pass; search clinicaltrials.gov directly by company/drug name.
- [ ] **Every trial's planned primary/secondary endpoints** marked "not
  confirmed in this search pass" should be checked against the trial's own
  ClinicalTrials.gov record or publication before citing specifics.

## 5. Real bugs found and fixed while building this (not hypothetical)

These are documented here, not just in commit history, because they are
exactly the failure modes this project exists to prevent — and finding
them required actually building live adapters and a real retrieval
pipeline rather than stubbing them out.

1. **SEC EDGAR tag-switching bug.** Biogen reported cash under
   `CashAndCashEquivalentsAtCarryingValue` through 2019, then switched to
   `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents`. The
   first version of `sec_edgar_adapter._latest_instant` picked the first
   candidate tag with *any* data and silently returned a stale 2019 value
   while the correct tag had 2026 data sitting right next to it. Fixed by
   pooling every candidate tag's entries and taking the single most recent
   date across all of them. Regression test:
   `tests/test_adapters_mocked.py::test_sec_edgar_adapter_pools_across_tags_for_the_latest_value`.
2. **BrainStorm cash discrepancy, resolved by going to the primary
   source.** Two secondary aggregators disagreed on BrainStorm's 6/30/2026
   cash balance (~$209,000 vs. ~$29,000). Querying SEC EDGAR's XBRL API
   directly resolved it: **$22,000** — neither aggregator was right. This
   is a genuinely severe liquidity position (current liabilities were
   separately reported around $12.4M), not a units error.
3. **NaN-vs-None bug in financial formatting and the runway calculator.**
   A SQL `NULL` in a numeric column comes back from pandas as `float('nan')`,
   not `None`. Code that checked `value is None` silently let NaN through,
   which Streamlit then rendered as the literal string `"nan"` (e.g.,
   "Revenue (quarter): $nanM") instead of "not disclosed." Fixed with a
   shared `is_missing()`/`fmt_money()`/`fmt_number()` helper
   (`bioanalyst/ui_common.py`) used everywhere a financial figure is
   displayed, and a parallel fix inside `finance/calculations.py` itself.
   Regression tests: `tests/test_finance_calculations.py::test_nan_*`.
4. **Markdown `$...$` rendered as LaTeX.** Streamlit's markdown renderer
   treats a pair of `$` as inline math. A financial note like "cash from
   $5.2M to $9.7M" rendered as garbled unicode math notation instead of
   plain text anywhere it went through `st.write`/`st.markdown`. Fixed with
   `md_safe()` (escapes `$` before display) applied at every render site
   showing free-text data.
5. **Out-of-scope guard missed real phrasings, twice.** An initial
   exact-phrase trigger list for "decline investment advice / outcome
   predictions / best-company rankings" missed "Which company is the best
   investment?" and "Will the COMBAT-ALS trial succeed?" — neither matched
   any listed phrase verbatim, so both were answered as if legitimate
   research questions. Fixed by switching from exact-phrase lists to
   word-stem/category-combination matching. Regression tests:
   `tests/test_ai_assistant_logic.py::test_rejects_best_investment_phrasing_regression`
   and `test_rejects_outcome_prediction_phrasings`.
6. **Streamlit + SQLite thread-safety bug.** An earlier version of
   `bioanalyst/db/queries.py` cached a single `sqlite3.Connection` with
   `@st.cache_resource` and shared it across Streamlit's worker threads,
   which SQLite forbids (`sqlite3.ProgrammingError: SQLite objects created
   in a thread can only be used in that same thread`). Fixed by opening a
   fresh connection per query function call and relying on `@st.cache_data`
   to cache the resulting DataFrame instead of the connection object.

## 6. How to add a company or trial

1. Add rows to the relevant lists in `bioanalyst/adapters/seed_facts.py`
   (`COMPANIES`, `PROGRAMS`, `TRIALS`, `FINANCIAL_PERIODS`, `UNCERTAINTIES`),
   with a `source_key` pointing at a `SOURCE_DOCUMENTS` entry.
2. Run `python3 -m bioanalyst.db.load_seed` to rebuild the database.
3. Run `pytest tests/` — `test_data_integrity.py` will catch a missing
   source, an invalid claim type, a broken foreign key, or an inconsistent
   currency unit.
4. If the company has a CIK or the trial has an NCT ID, run
   `python3 scripts/refresh_live_data.py` to pull a live snapshot and
   cross-check it against what you entered.

## 7. Unification: merging the neurotech sector in (BioAnalyst)

This project started as two separate student projects -- **NeuroScope**
(brain-computer interfaces, 7 companies) and **BioSignal** (ALS biotech, 5
companies) -- and was merged, on request, into one platform called
**BioAnalyst** with a shared schema, retrieval engine, and AI assistant.

### Schema changes made for the merge

- Added a `sectors` table (`biotech_als`, `neurotech_bci`), with every
  company now carrying a `sector_id` foreign key.
- Added `companies.is_publicly_traded` and made `companies.ticker`/`cik`
  nullable, since most neurotech companies are privately held.
- Added a new `funding_rounds` table, structurally separate from
  `financial_periods`, for venture funding disclosures (private companies)
  as opposed to SEC-filed quarterly figures (public companies). A company
  has rows in at most one of the two tables -- enforced by
  `tests/test_data_integrity.py::test_every_sec_filer_has_financial_periods_and_no_funding_rounds`.
- `claims.subject_type` gained a `funding_round` option.
- Ported NeuroScope's companies/programs/trials/funding/uncertainties data
  into the new schema's shape, backfilling four real NCT IDs for neurotech
  studies that the original NeuroScope research pass had marked "not
  found" (Neuralink's PRIME study, Synchron's COMMAND study, Paradromics'
  Connect-One study, Cognixion's comparison study) by directly querying
  ClinicalTrials.gov's API during the merge.

### Real bugs found and fixed during the merge (in addition to §5's list)

7. **ONWARD Medical edge case.** This company is publicly traded (Euronext)
   but not an SEC filer, so `is_publicly_traded=1` with `cik=NULL`. An
   early version of the Financial Analysis / Company Profiles branching
   logic checked only `is_publicly_traded` to decide whether to show SEC
   financials or funding-round history, which would have tried to show an
   empty SEC panel for this company. Fixed by requiring both
   `is_publicly_traded` AND a non-null `cik` before showing the SEC path.
8. **AI assistant numeric-intent gap for invasiveness.** NeuroScope's
   original assistant could answer "how many companies are non-invasive?"
   because `invasiveness` was its own column. In the unified schema that
   detail only exists as free text inside `programs.modality` (e.g.
   "Non-invasive -- scalp EEG plus AR display"). The merged numeric-intent
   handler initially just returned the total company count for this
   question -- not wrong, but not an answer to what was actually asked,
   and this was one of the AI assistant's own example-question buttons.
   Fixed by adding a `LIKE 'Non-invasive%'`/`LIKE 'Invasive%'` filter
   joined through `programs`, with the answer's own text disclosing that
   this is a text match on `modality`, not a dedicated column, since that
   is a real, acknowledged precision limitation rather than something to
   present as more exact than it is.
9. **Sector picker persistence across page navigation.** Found during
   manual QA, not fully resolved with certainty: switching the sidebar
   sector picker and then navigating to a different page via a sidebar
   link reset the selection back to the first sector, even with the
   textbook-correct Streamlit pattern (seed `session_state` once, rely on
   the widget's `key=` thereafter). Persisting the choice via
   `st.query_params` was also tried, but Streamlit's native sidebar
   page-navigation links drop the URL's query string on click regardless.
   The current implementation does both (session_state as primary,
   query-param seeding for direct links) and is believed correct per
   Streamlit's documented behavior, but the reset was still observed
   inside this project's own preview/testing tool specifically -- which
   may indicate that tool creates a fresh server-side session per page
   path rather than reusing one WebSocket session (not standard
   `streamlit run` behavior), though this was not confirmed with
   certainty from inside that same tool. If this reset is also observed
   running the app directly in an ordinary browser tab (not through a
   preview/sharing proxy), that would indicate a real, currently-unfixed
   bug -- please verify and report with those exact conditions.

### Evaluation after unification

Re-running `docs/eval_questions.csv` (all 30 questions were originally
written for the biotech sector) with retrieval scoped to `biotech_als`
(matching the AI assistant page's actual default behavior) still scores
27/30 -- unchanged by the merge. Running the same questions unscoped
across both sectors drops one question's score because the larger,
mixed-sector corpus pushed a relevant claim out of the top-6 results; see
`docs/EVALUATION.md`'s "Update: after unifying" section for that finding
in full, including why the scoped number is the one that reflects real
default behavior.
