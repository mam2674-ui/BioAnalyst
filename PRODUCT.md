# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Existing codebase: Streamlit (Python), SQLite. Not a greenfield stack choice.

## Users

A Columbia undergraduate (neuroscience/biology background, exploring business,
consulting, and AI-product-management career paths) building this as a
portfolio piece: a market-intelligence research tool that demonstrates the
ability to connect technical/scientific facts to commercial reasoning.
Secondary audience: anyone reviewing that portfolio (interviewers, mentors).

*Inferred from this project's existing README.md, docs/, and build history
rather than a fresh interview — the author and I have already built this
product together across prior sessions, so re-asking would repeat known
answers. Flagging the inference per Impeccable's init rules rather than
presenting it as newly confirmed.*

## Product Purpose

BioAnalyst helps a student analyst research a market by connecting, for each
company in a chosen sector: what the technology/therapy does, what evidence
supports it, who would use and pay for it, and what commercial/scientific
questions remain unresolved. It never recommends a trade, predicts a trial
outcome, or produces an opaque "best company" score — the explicit refusal
rails are a stated product principle, not an incidental limitation.

## Positioning

One shared platform (one database, one set of pages, one AI assistant) applied
to two genuinely different kinds of market: a biotech sector of public
companies with SEC-filed quarterly financials, and a neurotech sector of
mostly-private companies with venture funding disclosures. The product's
mechanism is keeping those two kinds of financial fact in clearly separate,
never-conflated tables while still presenting them through one consistent
interface — most tools pick one sector type or silently blend the two.

## Operating Context

A locally-run Streamlit multipage app (`streamlit run Home.py`), SQLite-backed
(`data/bioanalyst.db`), with live-refresh adapters against SEC EDGAR and
ClinicalTrials.gov (`scripts/refresh_live_data.py`). Used by one analyst at a
time, session-scoped (sector choice persists via `st.session_state` /
`st.query_params` across the 8 pages). No auth, no multi-tenant concerns.

## Capabilities and Constraints

- 8 pages: Home, Market Overview, Company Profiles, Clinical Trial Comparison,
  Financial Analysis, Competitive Landscape, Research Brief, AI Research
  Assistant.
- Every claim shown is tagged with a source type (independently-supported,
  company-reported, registry-entry, analyst-inference) and traceable to a
  `claims` ledger row.
- AI assistant answers only from the curated dataset (deterministic numeric
  intent + keyword retrieval; optional LLM synthesis is strictly additive and
  capped), and explicitly declines investment-advice / outcome-prediction /
  ranking questions.
- Financial Analysis branches structurally by company type: SEC-filed
  quarterly figures + a runway calculator for public companies, funding-round
  history for private ones — these are never shown as comparable numbers.

## Brand Commitments

Name: BioAnalyst. No existing logo, color, or type commitments prior to this
redesign — this is the project's first deliberate visual-identity pass (see
DESIGN.md).

## Evidence on Hand

Real seed dataset (12 companies, 17 trials/studies, 5 financial periods, 7
funding rounds, 36 uncertainties, 44 source documents) documented in
`docs/DATA_DICTIONARY.md`. A 30-question evaluation harness
(`scripts/run_evaluation.py`) with results logged in `docs/EVALUATION.md`. No
synthetic company names or fabricated figures — all seed facts trace to a
real source document.

## Product Principles

1. Never conflate two different kinds of financial fact (public filings vs.
   private funding rounds) even when showing them side by side.
2. Every displayed claim is sourced and typed; "not found" is always shown
   instead of a silently blank or guessed value.
3. The product refuses investment advice, trial-outcome prediction, and
   opaque ranking by design, not by accident — this is a constraint the
   interface should make visible, not hide.
4. One shared system serves two sectors; the interface should read as one
   coherent product, not two apps stapled together.

## Accessibility & Inclusion

No project-specific requirement established beyond ordinary WCAG AA hygiene
(this redesign's contrast and touch-target choices are checked against that
bar; see the audit note in DESIGN.md).
