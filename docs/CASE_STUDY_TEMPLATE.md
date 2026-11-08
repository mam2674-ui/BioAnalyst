# Portfolio Case Study: BioAnalyst

*Fill in the bracketed sections in your own words before using this
anywhere. The structure and the factual record (bugs found, decisions
made) are accurate as of this project's build; the reflective framing
should be yours.*

## The problem

[1-2 sentences: why does cross-referencing ClinicalTrials.gov, SEC
filings, and press releases by hand for biotech research matter to you —
tie to your own interest in biotech/consulting/AI PM.]

## What I built

BioAnalyst — a Streamlit research tool comparing five public ALS
biotechnology companies across clinical evidence, financials, and
commercial uncertainty, backed by a SQLite database with full source
attribution and two live data adapters (SEC EDGAR, ClinicalTrials.gov).

## Decisions I made (and why)

- **Chose ALS as the disease area** because it has enough public
  companies to compare *and* spans nearly every evidence-maturity state
  at once — an approval, a withdrawal, a rejection, a pending filing, and
  an awaited readout. [Add: what you learned about the disease/field in
  the process of choosing this.]
- **SQLite over a simpler flat-file format** because the data has real
  relational structure (companies → programs → trials, a time-series of
  financial periods, and a citation ledger joining everything together).
- **A separate `claims` table, not just annotated columns**, so every
  fact the UI or AI assistant shows can be traced to one citation record —
  this is what makes "cite at the claim level" a real guarantee rather
  than a hope.
- **Built two genuinely live API adapters** (not stubs) because building
  the real thing is what surfaced real bugs (see below) — a mocked
  "pretend" adapter would have hidden exactly the failure modes worth
  learning from.

## Bugs I found and fixed (this is the part worth discussing in an
## interview — it's evidence of real engineering, not just prompting)

1. A classic Streamlit+SQLite threading bug (`@st.cache_resource` sharing
   one SQLite connection across worker threads).
2. An XBRL tag-switching bug in the SEC adapter: Biogen changed which XBRL
   tag it reports cash under partway through its filing history, and an
   early version of the adapter silently returned a stale 2019 value
   instead of the 2026 one.
3. A genuine data discrepancy resolved by going to a primary source: two
   secondary financial-data aggregators disagreed on BrainStorm's cash
   balance; querying SEC EDGAR directly resolved it to a third, more
   severe number neither aggregator had right.
4. A NaN-vs-None bug that displayed the literal string "nan" to users
   instead of "not disclosed" wherever a financial figure was missing.
5. A markdown-rendering bug where dollar signs in plain text got
   interpreted as LaTeX math delimiters.
6. Two rounds of a real guard-logic bug in the AI assistant: an
   exact-phrase block-list for "decline investment advice" missed
   "Which company is the best investment?" and "Will the trial succeed?"
   entirely, because neither matched any listed phrase verbatim.
7. A real evaluation-driven fix: running the 30-question eval set the
   first time scored 14/30, which led to discovering that company- and
   program-level facts (and trial design fields) were never added to the
   AI assistant's searchable corpus at all. Fixing that raised the score
   to 27/30 against the *same* unchanged question set.

[Add: which of these you'd consider the most interesting to walk through
in an interview, and why.]

## What AI assisted with vs. what I decided

[Be specific and honest here — e.g.: "Claude wrote the initial SQL schema
and adapter code; I reviewed and decided the schema should separate
`claims` from the entity tables after thinking about how the AI assistant
needed to cite facts. I chose ALS as the disease area and verified the
company shortlist made sense. I did not personally write the XBRL
tag-pooling fix, but I understood why it was necessary and could explain
it." Fill in what's actually true for your involvement.]

## What's not done yet, honestly

The formal user test (3-5 participants) has not been conducted. The
LLM-synthesis half of the evaluation has not been run (no API key in this
environment). [Note here if either has changed by the time you share this.]

## What I'd do differently or next

[Your own reflection — e.g., multi-entity-aware retrieval, more disease
areas, a scheduled refresh once the pipeline's been stable for longer.]
