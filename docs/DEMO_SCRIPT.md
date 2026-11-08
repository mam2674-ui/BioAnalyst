# BioAnalyst — Two-Minute Demo Script

**Setup beforehand:** `streamlit run Home.py` already running, browser
open to the Home page. No API key configured (so the demo shows the
"works without AI" story, which is itself a selling point).

---

**[0:00-0:15] Home page**
"This is BioAnalyst — a research platform covering two sectors through
one shared database and AI assistant." [Click the sector picker in the
sidebar, switch from Biotech to Neurotech and back.] "That's not two apps
bolted together — one schema, one retrieval engine, one set of pages,
filtered by whichever sector you pick. Let's start in biotech: five public
companies in one disease area, ALS. I picked ALS because it spans almost
every evidence stage at once: an approved drug, a drug that got approved
*and then pulled from the market*, a rejected application, and two
companies still waiting on trial results."

**[0:15-0:40] Company Profiles — Amylyx**
Navigate to Company Profiles, select Amylyx.
"Here's the withdrawal case. Original Phase 2 trial was positive — that's
what got it approved in 2022. But the required confirmatory Phase 3,
PHOENIX, missed its primary endpoint *and* every secondary endpoint in
2024, and the company pulled the drug. Every claim here is tagged —
green for independently supported, yellow for company-reported — and
cited to a real source."

**[0:40-1:05] Financial Analysis — BrainStorm**
Navigate to Financial Analysis, select BrainStorm Cell Therapeutics.
"This is where it gets real. BrainStorm disclosed $22,000 in cash as of
June 30th — that number came from a live call to SEC EDGAR's API, built
into this app, not typed in by hand. The runway calculator — formula's
right here, `liquidity / burn rate`, computed in code — says under a
quarter of runway left at this burn rate."

**[1:05-1:30] AI Research Assistant**
Navigate to AI Research Assistant, type: "Which company is the best
investment?"
"Watch — it refuses. This tool explicitly won't rank companies or give
investment advice, and that's enforced in code, not just a disclaimer."
Then ask: "What human evidence supports Clene's CNM-Au8 program?"
"Now it retrieves the actual claim — note it specifically flags that the
primary endpoint *wasn't* statistically significant, and that the survival
benefit cited in their pending FDA filing is a post-hoc comparison to
historical controls, not a randomized one. That distinction is the whole
point of this project."

**[1:30-1:50] Research Brief**
Navigate to Research Brief.
"Last feature — generates an editable draft brief from this data, clearly
marked for human review, downloadable as Markdown."

**[1:50-2:00] Close**
"Everything here is real, sourced data — SEC filings, ClinicalTrials.gov,
company press releases — not synthetic. 43 automated tests, two live data
adapters, and a documented list of real bugs I found and fixed building
it, which I'm happy to walk through."
