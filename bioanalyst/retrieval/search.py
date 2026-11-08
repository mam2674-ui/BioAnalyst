"""
Simple keyword retrieval over the `claims` table -- the single ledger of
every citable fact in the database. No embeddings: the corpus here is a
few dozen rows, which a plain token-overlap search can handle, and keeping
it simple keeps it debuggable and testable. Upgrade to embeddings only if
docs/EVALUATION.md's eval later shows this missing relevant claims that
embeddings would catch (not measured yet, so not built).

This module is intentionally the direct port of the pattern validated in
the NeuroScope project, including the fix for a real bug found there: a
naive single-token overlap can match an unrelated claim on a coincidental
shared word, so the minimum match threshold is 2 shared tokens, not 1.
"""
import re
from dataclasses import dataclass

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "of", "for", "to", "and",
    "in", "on", "what", "which", "who", "how", "does", "do", "this", "that",
    "with", "by", "as", "it", "its", "be", "been", "has", "have", "had",
    "or", "about", "would", "could", "can", "most", "did", "between",
}


@dataclass
class Claim:
    id: int
    company_id: str
    company_name: str
    sector_id: str
    subject_type: str
    subject_ref: str
    field_label: str
    value_text: str
    claim_type: str
    source_url: str
    source_publisher: str
    as_of_date: str


def _tokenize(text: str) -> set:
    tokens = re.findall(r"[a-z0-9]+", str(text).lower())
    return {t for t in tokens if t not in STOPWORDS and len(t) > 2}


def load_claims(conn, sector_id: str | None = None) -> list:
    """Loads claims, optionally scoped to one sector (via companies.sector_id).
    Pages scope to the user's active sector by default; pass sector_id=None
    for a cross-sector search if that's ever needed."""
    sql = """
        SELECT c.id, c.company_id, co.name as company_name, co.sector_id,
               c.subject_type, c.subject_ref, c.field_label, c.value_text,
               c.claim_type, c.as_of_date, sd.url as source_url, sd.publisher as source_publisher
        FROM claims c
        LEFT JOIN companies co ON co.company_id = c.company_id
        LEFT JOIN source_documents sd ON sd.id = c.source_document_id
    """
    params = ()
    if sector_id is not None:
        sql += " WHERE co.sector_id = ?"
        params = (sector_id,)
    rows = conn.execute(sql, params).fetchall()
    return [Claim(
        id=r["id"], company_id=r["company_id"] or "", company_name=r["company_name"] or r["company_id"] or "",
        sector_id=r["sector_id"] or "", subject_type=r["subject_type"], subject_ref=r["subject_ref"],
        field_label=r["field_label"], value_text=r["value_text"], claim_type=r["claim_type"],
        as_of_date=r["as_of_date"] or "",
        source_url=r["source_url"] or "(analyst inference, not an external source)",
        source_publisher=r["source_publisher"] or "BioAnalyst analysis",
    ) for r in rows]


def search(claims: list, query: str, top_k: int = 6, min_score: int = 2):
    """Rank claims by token-overlap score. Returns (results, best_score)."""
    q_tokens = _tokenize(query)
    scored = []
    for cl in claims:
        c_tokens = _tokenize(cl.value_text) | _tokenize(cl.company_name) | _tokenize(cl.field_label) | _tokenize(cl.subject_ref)
        score = len(q_tokens & c_tokens)
        if score > 0:
            scored.append((score, cl))
    scored.sort(key=lambda x: x[0], reverse=True)
    best_score = scored[0][0] if scored else 0
    results = [cl for score, cl in scored[:top_k] if score >= min_score]
    return results, best_score
