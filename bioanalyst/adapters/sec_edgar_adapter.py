"""
Live adapter for the SEC EDGAR XBRL "company facts" API
(https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json).

Per SEC's documented access policy (sec.gov/os/accessing-edgar-data), all
requests must carry a descriptive User-Agent identifying the requester;
there is no API key, but there is a rate limit (SEC asks for a reasonable
request rate, informally understood as <=10 req/sec). Verified reachable
2026-10-27 with a plain User-Agent header.

XBRL filers don't all use identical tags for the same concept (a known,
real limitation of this API, not specific to this project) -- this adapter
tries an ordered list of candidate tags per field and uses the first that
resolves, so a company using a non-standard tag just falls through to
"not found" rather than crashing.
"""
from dataclasses import dataclass, field
from typing import Optional

import requests

USER_AGENT = "BioSignal-StudentProject marceloaruizcorujo@gmail.com"
BASE_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
TIMEOUT_SECONDS = 15

INSTANT_CONCEPTS = {
    "cash_and_equivalents": ["CashAndCashEquivalentsAtCarryingValue", "Cash",
                              "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"],
    "marketable_securities": ["MarketableSecuritiesCurrent", "ShortTermInvestments",
                                "AvailableForSaleSecuritiesCurrent"],
    "total_debt": ["LongTermDebtNoncurrent", "LongTermDebt", "DebtInstrumentCarryingAmount"],
}
DURATION_CONCEPTS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                 "RevenueFromContractWithCustomerIncludingAssessedTax"],
    "rd_expense": ["ResearchAndDevelopmentExpense"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
}


@dataclass
class FinancialSnapshot:
    cik: str
    entity_name: Optional[str] = None
    period_end_date: Optional[str] = None
    filed_date: Optional[str] = None
    form: Optional[str] = None
    values: dict = field(default_factory=dict)   # field_name -> float or None
    shares_outstanding: Optional[float] = None
    fetch_succeeded: bool = False
    error: Optional[str] = None


def fetch_company_facts(cik: str) -> dict:
    """Raw fetch, isolated so tests can mock requests.get."""
    padded = str(cik).zfill(10)
    resp = requests.get(
        BASE_URL.format(cik=padded),
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    return resp.json()


def _latest_instant(us_gaap: dict, candidate_tags: list) -> Optional[dict]:
    """Instant (point-in-time) concepts like cash: pick the most recent
    'end' date entry from a 10-Q or 10-K filing, in USD.

    Filers switch XBRL tags over time (e.g. Biogen reported cash under
    CashAndCashEquivalentsAtCarryingValue through 2019, then switched to
    CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents) -- an
    earlier version of this function picked the first candidate tag with
    ANY data, which silently returned a stale 2019 value while a newer tag
    had 2026 data sitting right next to it. Fixed by pooling every
    candidate tag's entries together and taking the single most recent
    'end' date across all of them, so a filer switching tags doesn't look
    like missing data."""
    pooled = []
    for tag in candidate_tags:
        entries = us_gaap.get(tag, {}).get("units", {}).get("USD", [])
        pooled.extend(e for e in entries if e.get("form") in ("10-Q", "10-K"))
    if not pooled:
        return None
    return max(pooled, key=lambda e: e.get("end", ""))


def _latest_quarterly_duration(us_gaap: dict, candidate_tags: list) -> Optional[dict]:
    """Duration concepts like R&D expense: pick the most recent single
    fiscal quarter (~80-100 day span) entry from a 10-Q, in USD. Pools
    across all candidate tags first (see _latest_instant docstring for why:
    the same filer can switch XBRL tags for the same concept over time)."""
    from datetime import date
    quarterly = []
    for tag in candidate_tags:
        entries = us_gaap.get(tag, {}).get("units", {}).get("USD", [])
        for e in entries:
            if e.get("form") != "10-Q" or "start" not in e or "end" not in e:
                continue
            try:
                start = date.fromisoformat(e["start"])
                end = date.fromisoformat(e["end"])
            except ValueError:
                continue
            if 80 <= (end - start).days <= 100:
                quarterly.append(e)
    if not quarterly:
        return None
    return max(quarterly, key=lambda e: e["end"])


def _shares_outstanding(raw: dict) -> Optional[float]:
    dei = raw.get("facts", {}).get("dei", {})
    entries = dei.get("EntityCommonStockSharesOutstanding", {}).get("units", {}).get("shares", [])
    filed = [e for e in entries if e.get("form") in ("10-Q", "10-K")]
    if not filed:
        return None
    best = max(filed, key=lambda e: e.get("end", ""))
    return best.get("val")


def normalize(raw: dict, cik: str) -> FinancialSnapshot:
    us_gaap = raw.get("facts", {}).get("us-gaap", {})
    snap = FinancialSnapshot(cik=cik, entity_name=raw.get("entityName"), fetch_succeeded=True)

    anchor = _latest_instant(us_gaap, INSTANT_CONCEPTS["cash_and_equivalents"])
    if anchor:
        snap.period_end_date = anchor.get("end")
        snap.filed_date = anchor.get("filed")
        snap.form = anchor.get("form")

    for field_name, tags in INSTANT_CONCEPTS.items():
        entry = _latest_instant(us_gaap, tags)
        snap.values[field_name] = entry["val"] if entry else None

    for field_name, tags in DURATION_CONCEPTS.items():
        entry = _latest_quarterly_duration(us_gaap, tags)
        snap.values[field_name] = entry["val"] if entry else None

    snap.shares_outstanding = _shares_outstanding(raw)
    return snap


def get_financial_snapshot(cik: str) -> FinancialSnapshot:
    """Top-level entry point: fetch + normalize, with graceful failure."""
    try:
        raw = fetch_company_facts(cik)
        return normalize(raw, cik)
    except requests.RequestException as exc:
        return FinancialSnapshot(cik=cik, fetch_succeeded=False,
                                  error=f"{exc.__class__.__name__}: {exc}")
    except (KeyError, ValueError, TypeError) as exc:
        return FinancialSnapshot(cik=cik, fetch_succeeded=False,
                                  error=f"Unexpected SEC response shape: {exc}")
