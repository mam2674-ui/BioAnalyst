"""
AI Research Assistant.

Grounding chain, in order:
1. is_out_of_scope() -- declines investment advice / outcome predictions / "best company" / invented forecasts.
2. try_numeric_intent() -- countable questions computed by direct SQL, scoped to the active sector.
3. try_whats_changed() -- answered from the snapshots change log (platform-wide).
4. Otherwise: keyword retrieval over `claims` (scoped to the active sector by default), shown
   directly (claim type + citation) whether or not an LLM is configured; LLM synthesis (if
   configured) is strictly additive on top of those claims.
"""
import streamlit as st

from bioanalyst.ai.assistant_logic import is_out_of_scope, try_numeric_intent, try_whats_changed
from bioanalyst.ai.client import is_configured, synthesize
from bioanalyst.db.schema import get_connection
from bioanalyst.retrieval.search import load_claims, search
from bioanalyst.ui_common import claim_badge, md_safe, render_disclaimer_footer, render_header

sector_id = render_header("AI Research Assistant")
st.title("AI Research Assistant")

search_all_sectors = st.checkbox(
    "Search across all sectors (not just the sidebar's current selection)", value=False,
)
effective_sector = None if search_all_sectors else sector_id

conn = get_connection()
claims = load_claims(conn, sector_id=effective_sector)

if is_configured():
    st.success("AI synthesis is configured (ANTHROPIC_API_KEY detected). Answers are grounded strictly in the claims shown below.")
else:
    st.info(
        "AI synthesis is not configured (no ANTHROPIC_API_KEY). The assistant still works: it "
        "retrieves and shows the exact labeled claims that answer your question, with citations.",
        icon="ℹ️",
    )

st.subheader("Ask a question")
if sector_id == "biotech_als":
    examples = [
        "How do the companies' trial designs differ?",
        "What human evidence supports Clene's CNM-Au8 program?",
        "What changed since the last source update?",
        "What are the strongest arguments against Clene's NDA filing?",
        "How many trials have reported negative results?",
        "Which company is the best investment?",
    ]
else:
    examples = [
        "How do the companies' trial designs differ?",
        "What human evidence supports Synchron's Stentrode?",
        "What changed since the last source update?",
        "What could make adoption difficult for Precision Neuroscience?",
        "How many companies are non-invasive?",
        "Which company is the best investment?",
    ]
cols = st.columns(2)
clicked = None
for i, ex in enumerate(examples):
    if cols[i % 2].button(ex, width="stretch", key=f"ex_{i}"):
        clicked = ex

question = st.text_input("Or type your own question", value=clicked or "")

if question:
    scope_decline = is_out_of_scope(question)
    if scope_decline:
        st.warning(scope_decline, icon="🚫")
    else:
        numeric_answer = try_numeric_intent(question, conn, sector_id=effective_sector)
        change_answer = try_whats_changed(question, conn)
        if numeric_answer:
            st.markdown(numeric_answer)
        elif change_answer:
            st.markdown(change_answer)
        else:
            results, best_score = search(claims, question)
            if not results or best_score == 0:
                st.warning(
                    "I don't have enough information in the curated dataset to answer that "
                    "confidently. Try asking about a specific company, trial, or financial period, "
                    "checking 'search across all sectors', or rephrasing your question.",
                    icon="🤷",
                )
            else:
                context_lines = [
                    f"[{i}] ({c.claim_type}) {c.company_name} -- {c.field_label}: {c.value_text} "
                    f"(source: {c.source_url}, as of {c.as_of_date})"
                    for i, c in enumerate(results, 1)
                ]
                context_block = "Claim snippets:\n" + "\n".join(context_lines)

                if is_configured():
                    with st.spinner("Synthesizing grounded answer..."):
                        answer, error = synthesize(question, context_block)
                    if answer:
                        st.markdown("**AI-synthesized answer** (grounded in claims below -- verify before reuse):")
                        st.write(answer)
                    elif error:
                        st.caption(f"⚠️ {error}")

                st.markdown("**Retrieved claims** (what the answer above, or this fallback, is grounded in):")
                for i, c in enumerate(results, 1):
                    with st.container(border=True):
                        sector_tag = f" [{c.sector_id}]" if search_all_sectors else ""
                        st.markdown(f"**[{i}] {c.company_name}**{sector_tag} -- {c.field_label} · {claim_badge(c.claim_type)}")
                        st.write(md_safe(c.value_text))
                        st.caption(f"Source: {c.source_publisher} -- {c.source_url} · as of {c.as_of_date}")

render_disclaimer_footer()
