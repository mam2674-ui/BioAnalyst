# BioAnalyst — Product Requirements Document

**Status:** v2 -- unified platform, implemented and manually verified.
Originally two separate v1 projects (NeuroScope for neurotech, BioSignal
for biotech), merged on request into one shared schema/AI-assistant/UI
covering both sectors via a sidebar sector picker. Author: Marcelo
Moraruiz (Columbia '2x), built with AI pair-programming assistance
(Claude). See `docs/CASE_STUDY_TEMPLATE.md` for what was personally
designed/decided vs. AI-assisted, and `docs/DATA_DICTIONARY.md` §7 for
exactly what the unification changed and what it broke along the way.

## 1. Problem

A student analyst, biotech researcher, consultant, or investor doing
preliminary research on a disease area has to manually cross-reference
ClinicalTrials.gov, SEC filings, company press releases, and news coverage
to answer one question: **how do companies pursuing treatments in a given
disease area compare scientifically and commercially, and what could
change that assessment?** Doing this by hand is slow, and it's easy to
accidentally conflate a registered trial with a proven result, or a
regulatory designation with an approval.

## 2. Users and jobs-to-be-done

- **Student analyst** (primary user, this project's actual tester):
  "Give me a structured starting point for a disease area I don't know
  yet, with sources I can verify myself."
- **Biotech researcher / consultant**: "Let me quickly compare 2-3
  companies' trial designs and financial runway without reading five 10-Qs."
- **Investor (preliminary research only)**: "Surface disclosed facts and
  flag what's uncertain — this tool explicitly does not give investment
  advice or a buy/sell signal."

## 3. Scope: v1 (shipped)

- **One disease area**: amyotrophic lateral sclerosis (ALS).
- **Five public companies**: Biogen, Amylyx, BrainStorm Cell Therapeutics,
  Clene, MediciNova — chosen because together they span nearly every
  evidence-maturity state (approved, approved-then-withdrawn, rejected,
  pending-accelerated-approval, fully-enrolled-awaiting-readout).
- **Ten tracked clinical trials** across those five companies.
- **Seven features**, each a Streamlit page: Market Overview, Company
  Profiles, Clinical Trial Comparison, Financial Analysis (with an
  editable cash-runway scenario calculator), Competitive Landscape,
  Research Brief generator, and an optional AI Research Assistant.
- **Two live, public, no-API-key data adapters**: SEC EDGAR's XBRL
  company-facts API and ClinicalTrials.gov's API v2, with a manual refresh
  command (`scripts/refresh_live_data.py`) that never silently overwrites
  historical data.

## 4. Explicit non-goals (v1)

- No multi-disease-area support.
- No complex valuation models (DCF, comps multiples).
- No live news or earnings-event tracking.
- No IPO/financing-intelligence module.
- No scheduled/automatic refresh (manual command only, per the brief's
  own instruction to add scheduling "only after the data pipeline is stable").
- No investment recommendation, trade signal, or "best company" score — ever.
- No market-size/TAM figures — the dataset and the AI assistant both
  explicitly refuse to produce one rather than invent it.

## 5. Functional requirements (what "done" means per feature)

| Feature | Done when |
|---|---|
| Market Overview | Denominators are always shown; filters never silently drop rows without saying so |
| Company Profiles | Every trial/financial fact shows its claim type and source |
| Clinical Trial Comparison | The page explicitly states why 2+ selected trials' results may not be comparable |
| Financial Analysis | Runway is computed in code from editable assumptions, never estimated by the AI |
| Competitive Landscape | No single numeric "score" is computed across companies |
| Research Brief | Output is clearly marked draft/for-human-review, every section is editable |
| AI Research Assistant | Works with zero API key configured; refuses investment/outcome-prediction/ranking questions; every answer traces to a cited claim |

## 6. Known limitations (honest, not aspirational)

- Several fields are marked "not confirmed in this search pass" — see
  `docs/DATA_DICTIONARY.md` §4 for the full checklist.
- The live SEC adapter's generic XBRL-tag matching can lag a company's
  most recent quarter (documented, Biogen case) — it is not guaranteed to
  always be the most current source; the app surfaces this rather than
  hiding it.
- The formal 30-question evaluation (`docs/EVALUATION.md`) and the 3-5
  person user test (`docs/USER_TESTING_PLAN.md`) are both **planned, not
  yet run** as of this PRD's writing. Do not cite results from either
  until they've actually happened.
- Retrieval is plain keyword search, not embeddings — adequate for ~60
  claims, not validated at larger scale.

## 7. Success criteria for this portfolio project

Not "has this made money" or "has this helped real users" — those claims
require actually running the user test and eval first. Success for v1 is:
the app runs standalone, the data is real and traceable to primary
sources, the tests pass, and the author can explain every architectural
decision and every bug found during development in an interview.
