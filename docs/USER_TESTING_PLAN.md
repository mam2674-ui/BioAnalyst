# User Testing Plan (not yet conducted)

**Status: planned, not run.** No interviews have happened. Do not cite
results, quotes, or completion times from this document until the test
has actually been conducted — this file is the plan, not the findings.

## Participants

3-5 students interested in research, consulting, or biotech investing.
Recruit from a relevant student group or class, not friends who already
know the project (to avoid biased feedback).

## Setup

- Each participant uses their own laptop, with the app already running
  locally (`streamlit run Home.py`) or screen-shared if setup is a
  blocker.
- Record screen + think-aloud audio with consent (see script below).
- No AI API key configured for this test, so every participant sees the
  same experience (keyword-retrieval-only AI assistant).

## Consent-friendly introduction (read aloud or adapt)

> "Thanks for helping test this. This is a student project — a research
> dashboard for exploring biotech companies in one disease area. I'm going
> to give you a couple of tasks and ask you to think out loud while you
> work through them. There's no wrong answer and you're not being tested —
> I'm testing the app. I'll record the screen and audio just for my own
> notes afterward; let me know if you'd rather I didn't. Stop any time."

## Tasks

1. **"Compare two companies' trial designs and identify one important
   limitation of comparing them directly."** (Tests: Clinical Trial
   Comparison page, whether the "not directly comparable" framing lands.)
2. **"Find out whether Clene's drug is FDA-approved yet, and what
   evidence that status is based on."** (Tests: whether the accelerated-
   approval-vs-approval distinction is clear without being told to look
   for it.)
3. **"Using the cash-runway calculator, tell me which company looks most
   financially at risk and why."** (Tests: Financial Analysis page,
   whether the editable-assumptions framing is understood.)
4. **Open-ended: "Ask the AI assistant anything you're curious about."**
   (Tests: discoverability of the assistant, whether declines/refusals
   read as broken or as intentional.)

## What to measure

- Time to complete each task.
- Accuracy: did they reach the right answer, and did they correctly cite
  where they got it?
- Important facts missed (e.g., did they notice the going-concern flag
  without prompting?).
- Corrections required (did you have to intervene or clarify?).
- Usability feedback: confusing labels, unclear navigation, anything they
  tried to click that didn't work.

## Results template (fill in only after actually running this)

| Participant | Background | Task 1 time | Task 2 time | Task 3 time | Notable quotes | Facts missed | Usability issues |
|---|---|---|---|---|---|---|---|
| P1 | | | | | | | |
| P2 | | | | | | | |
| P3 | | | | | | | |

## Limitations of this test, to state upfront in any writeup

A 3-5 person convenience-sample test is not statistically representative
and cannot support claims like "X% of users understood Y." It's useful for
catching obvious usability problems and confusing framing, not for
validating product-market fit or measuring real-world time savings.
