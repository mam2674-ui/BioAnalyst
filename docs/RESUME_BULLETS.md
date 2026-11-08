# Resume Bullet Templates

Fill in bracketed placeholders only with verified, true numbers (e.g.,
from an actual user test you've run, or a metric you've personally
confirmed). Do not fill in a number you haven't verified — an interviewer
asking "how did you measure that" and getting "I'm not sure" is worse than
a bullet with no number.

1. **Technical build:** "Built BioAnalyst, a biotech market-intelligence
   research tool analyzing [5] public ALS companies across clinical trial
   evidence and SEC-sourced financials, using Python, Streamlit, and
   SQLite, with two live API integrations (SEC EDGAR XBRL, ClinicalTrials.gov)
   and [43] automated tests."

2. **Debugging / rigor:** "Identified and fixed [6] distinct bugs during
   development — including a thread-safety issue in SQLite connection
   caching, an XBRL tag-switching bug that silently returned stale
   financial data, and a keyword-matching gap in an AI safety guard —
   each covered by a regression test."

3. **Evaluation-driven improvement:** "Built a [30]-question evaluation
   harness for an AI research assistant's retrieval accuracy; used it to
   find that [2 categories of] source data were missing from the
   assistant's searchable index entirely, fixed the gap, and improved the
   measured pass rate from [14/30] to [27/30] on the same unchanged
   question set."

(A fourth bullet about user testing or measured time savings should only
be written after `docs/USER_TESTING_PLAN.md` has actually been run — do
not draft one in advance of real data.)
