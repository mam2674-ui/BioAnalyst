# BioAnalyst — Market Intelligence Platform

A unified research tool covering two sectors through one shared schema, one AI
assistant, and one set of pages:

- **Biotechnology — Amyotrophic Lateral Sclerosis (ALS)**: five public companies,
  ten tracked clinical trials, SEC-filed quarterly financials.
- **Neurotechnology — Brain-Computer Interfaces (BCI)**: seven companies (six
  direct, one adjacent) in assistive communication/computer control, mostly
  privately held, with venture funding disclosures instead of quarterly filings.

**This started as two separate student portfolio projects** (NeuroScope for
neurotech, BioSignal for biotech) and was merged into one platform with a
shared database, retrieval engine, and AI assistant — on request, to show a
single, more capable architecture applied across two genuinely different
markets. See `docs/DATA_DICTIONARY.md` §7 for what the unification actually
required and what broke along the way.

**Not investment advice, clinical guidance, or an automated trading signal.**

## Why these two sectors are a good match for one platform — and where they
## genuinely differ

Both sectors answer the same shape of question ("how do companies pursuing
similar goals compare scientifically and commercially, and what could change
the assessment?") and share a research methodology (sourced claims, claim
types, explicit gaps). But they differ in one load-bearing way: the biotech
sector's companies are SEC filers with quarterly financial statements; the
neurotech sector's companies are almost all privately held, with venture
funding disclosures instead. The platform keeps these in two separate tables
(`financial_periods` vs. `funding_rounds`) specifically so they're never
casually conflated — a company's cash runway can be computed from one, never
the other.

## Quickstart

```bash
cd BioAnalyst
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 -m bioanalyst.db.load_seed   # builds data/bioanalyst.db from the curated seed dataset
streamlit run Home.py
```

Then open http://localhost:8501 (or whatever port Streamlit reports), and use
the **Sector** picker in the sidebar to switch between the two sectors.

`data/bioanalyst.db` is a generated build artifact (gitignored) — the
version-controlled source of truth is `bioanalyst/adapters/seed_facts.py`.
Re-run the loader any time you edit that file.

## Refreshing live data

```bash
python3 scripts/refresh_live_data.py
```

Calls two live, public, no-API-key-required sources directly:
- **SEC EDGAR XBRL company-facts API** (`data.sec.gov`) for each company with
  a CIK (biotech sector, currently; the neurotech sector's one publicly
  traded company, ONWARD Medical, is Euronext-listed and outside this API's
  coverage, so it correctly has no CIK and is skipped).
- **ClinicalTrials.gov API v2** for each trial/study with a registered NCT ID
  (six companies across both sectors have a confirmed one).

It never silently overwrites a financial period -- a new one is only
inserted if genuinely newer than what's on file, and every change (or
non-change) is logged to `refresh_log` and `snapshots`.

## Running tests

```bash
source .venv/bin/activate
pytest tests/ -v
```

53 tests covering: identifier mapping (NCT IDs, CIKs) and foreign keys,
sector scoping, currency-unit consistency, financial calculations and
cash-runway scenarios (including a NaN-vs-None regression), source
attribution on every claim, snapshot/change-detection logic, stale-data
handling, and the AI assistant's deterministic guards (investment-advice
refusal, outcome-prediction refusal, numeric-intent correctness including
sector-scoped and invasiveness-filtered counts) -- all against mocked
external services, no real network calls in the test suite itself.

## Enabling AI synthesis (optional)

The AI Research Assistant always works without an API key -- it retrieves
and displays labeled, cited claims using plain keyword search, scoped to
the active sector by default (with a "search across all sectors" option).
To also get an LLM-synthesized paragraph on top of those claims (still
strictly grounded in them):

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
pip install anthropic
streamlit run Home.py
```

The key is read server-side via `os.environ` (`bioanalyst/ai/client.py`)
and never sent to or rendered in the browser. `.gitignore` excludes `.env`
and `.streamlit/secrets.toml`. Each session is capped at 20 AI calls as a
basic cost guard, and repeated identical questions are cached.

## Project structure

```
Home.py                          entry point (run with `streamlit run`)
pages/
  1_Market_Overview.py             Feature A
  2_Company_Profiles.py            Feature B (branches: SEC financials vs. funding rounds)
  3_Clinical_Trial_Comparison.py   Feature C
  4_Financial_Analysis.py          Feature D (SEC + runway calc, or funding history)
  5_Competitive_Landscape.py       Feature E
  6_Research_Brief.py              Feature F (sector-aware template text)
  7_AI_Research_Assistant.py       Feature G (sector-scoped by default, optional AI layer)
bioanalyst/
  adapters/
    seed_facts.py                   curated, cited seed dataset for BOTH sectors (source of truth)
    clinicaltrials_adapter.py        live ClinicalTrials.gov API v2 client
    sec_edgar_adapter.py             live SEC EDGAR XBRL company-facts client
  db/
    schema.py                        SQLite DDL (sectors, companies, programs, trials,
                                      financial_periods, funding_rounds, claims, ...)
    load_seed.py                     loads seed_facts.py into the database
    queries.py                       all read-side SQL, cached per-page, sector-aware
  finance/calculations.py          deterministic cash-runway math
  retrieval/search.py              keyword search over the claims ledger, sector-filterable
  ai/
    assistant_logic.py               numeric-intent / out-of-scope / what-changed guards
    client.py                        optional, gracefully-degrading LLM synthesis
  ui_common.py                     shared header, sector picker, disclaimer, NaN-safe formatters
scripts/refresh_live_data.py      manual refresh command
docs/                             data dictionary, PRD, evaluation, user-testing plan,
                                  case study template, demo script, resume bullets
tests/                            53 tests, mocked external services
```

## Architecture notes

- **A `sectors` table scoping everything else**, rather than two separate
  codebases: every company belongs to exactly one sector, and the sidebar
  sector picker filters almost every page. The alternative (two Streamlit
  apps bolted together) would have meant duplicating the retrieval engine,
  the AI guards, and every page's logic -- unifying the schema instead
  means a bug fix or a new feature only needs to be written once.
- **Two parallel financial tables, not one overloaded one**:
  `financial_periods` (SEC quarterly filings) and `funding_rounds` (venture
  disclosures) are kept structurally separate because they answer
  different questions and must never be silently compared as if equivalent.
  A company has rows in exactly one of the two (enforced by a test).
- **A `claims` ledger, not just annotated tables**: every claim-level
  citation the AI assistant or a company profile page shows comes from one
  table (`claims`), not from reading entity-table columns directly.
- **Two real live adapters, not a mocked "pretend API"**: SEC EDGAR's XBRL
  company-facts endpoint and ClinicalTrials.gov's API v2 are both public,
  unauthenticated, and genuinely called over the network when you run
  `refresh_live_data.py`. Building and debugging these surfaced several
  real bugs during development (see `docs/DATA_DICTIONARY.md` §6).
- **Plain keyword search, not embeddings**: the claims corpus is a little
  over a hundred rows across both sectors. A token-overlap search is
  simple enough to unit test exhaustively; embeddings are a reasonable
  next step only if an evaluation shows this missing relevant claims.
- **Sector choice persisted via `st.query_params`, not session_state
  alone**: found during manual QA that relying purely on a `key=`-based
  widget did not reliably survive sidebar page navigation in this
  project's preview/testing environment. See `bioanalyst/ui_common.py`'s
  `render_sector_picker()` docstring for the full account, including what
  was and wasn't confirmed as the root cause -- flagged honestly rather
  than claimed fixed with certainty, since it could not be fully isolated
  from inside that same environment.
