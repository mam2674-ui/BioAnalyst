"""
Deterministic financial calculations. Every number here is arithmetic on
stored, sourced values -- nothing is estimated by an LLM, and every function
documents its own formula and what happens when an input is missing.
"""
import math
from dataclasses import dataclass
from typing import Optional


def _is_missing(value) -> bool:
    """True for both None and NaN. Callers here receive raw values straight
    out of a pandas Series (one row of financial_periods), where a SQL NULL
    in a numeric column comes back as float NaN, not None -- a plain
    `value is None` check silently misses that case and lets NaN propagate
    into arithmetic (quarters_of_runway = NaN), which Streamlit would then
    render as the literal string 'nan' instead of an honest 'not found'."""
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False


@dataclass
class RunwayScenario:
    label: str
    quarterly_burn: float          # USD millions, positive number = cash outflow per quarter
    quarters_of_runway: Optional[float]
    runway_exhausted_note: Optional[str] = None


@dataclass
class RunwayResult:
    company_id: str
    liquidity_used: float          # USD millions: cash (+ marketable securities if included)
    liquidity_components: str      # human-readable description of what was summed
    scenarios: list
    missing_inputs: list           # list of strings describing what's missing and why it matters
    formula: str


def compute_cash_runway(
    *,
    company_id: str,
    cash_and_equivalents: Optional[float],
    marketable_securities: Optional[float],
    include_marketable_securities: bool,
    conservative_burn: Optional[float],
    base_burn: Optional[float],
    optimistic_burn: Optional[float],
) -> RunwayResult:
    """
    Formula: quarters_of_runway = liquidity / quarterly_burn, where
    liquidity = cash_and_equivalents (+ marketable_securities, if the caller
    chooses to include them -- they are not always as liquid as cash, which
    is exactly why this is a user choice, not a hardcoded assumption).

    Burn rates are NOT inferred from one quarter's operating cash flow by
    this function -- they are explicit, editable inputs the caller (the UI)
    collects from the user, who may seed them from a historical quarterly
    operating cash flow figure but can and should adjust for known one-time
    items, planned trial costs, or headcount changes. This function never
    guesses a burn rate on its own.
    """
    missing_inputs = []
    if _is_missing(cash_and_equivalents):
        missing_inputs.append(
            "cash_and_equivalents is not available for this company/period -- "
            "runway cannot be computed without it."
        )
        return RunwayResult(
            company_id=company_id, liquidity_used=0.0,
            liquidity_components="unavailable", scenarios=[],
            missing_inputs=missing_inputs,
            formula="quarters_of_runway = liquidity / quarterly_burn",
        )

    liquidity = cash_and_equivalents
    components = "cash and cash equivalents"
    if include_marketable_securities:
        if not _is_missing(marketable_securities):
            liquidity += marketable_securities
            components += " + marketable securities"
        else:
            missing_inputs.append(
                "marketable_securities was requested but is not available for this "
                "company/period -- only cash and cash equivalents were used."
            )

    scenarios = []
    for label, burn in [("Conservative (higher burn)", conservative_burn),
                         ("Base case", base_burn),
                         ("Optimistic (lower burn)", optimistic_burn)]:
        if burn is None or burn <= 0:
            missing_inputs.append(f"{label} burn rate is missing or not positive -- scenario skipped.")
            scenarios.append(RunwayScenario(label=label, quarterly_burn=burn or 0.0, quarters_of_runway=None,
                                             runway_exhausted_note="Cannot compute: missing or invalid burn rate."))
            continue
        quarters = liquidity / burn
        scenarios.append(RunwayScenario(
            label=label, quarterly_burn=burn, quarters_of_runway=round(quarters, 2),
            runway_exhausted_note=f"Liquidity exhausted in ~{quarters:.1f} quarters at this burn rate "
                                   f"if nothing else changes (no new financing, no revenue change, no cost change)."
        ))

    return RunwayResult(
        company_id=company_id, liquidity_used=round(liquidity, 3),
        liquidity_components=components, scenarios=scenarios,
        missing_inputs=missing_inputs,
        formula="quarters_of_runway = liquidity / quarterly_burn, liquidity = " + components,
    )


def quarterly_burn_from_operating_cash_flow(operating_cash_flow: Optional[float]) -> Optional[float]:
    """Convenience only: converts a negative operating cash flow (outflow)
    into a positive burn-rate number to seed the UI's editable input. This
    is a starting suggestion, not a forecast -- the UI must let the user
    override it, since a single quarter's cash flow can include one-time
    items (financings, milestone payments) that don't recur."""
    if _is_missing(operating_cash_flow):
        return None
    return max(0.0, -operating_cash_flow)
