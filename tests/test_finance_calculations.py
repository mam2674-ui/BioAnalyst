"""
Financial calculation tests, including the exact NaN-vs-None bug found
during manual QA: a pandas Series value read from a SQL NULL comes back
as float('nan'), not None, and an earlier version of this module only
checked `is None`, silently propagating NaN into the runway result.
"""
import math

from bioanalyst.finance.calculations import compute_cash_runway, quarterly_burn_from_operating_cash_flow


def test_runway_formula_is_liquidity_over_burn():
    result = compute_cash_runway(
        company_id="test", cash_and_equivalents=100.0, marketable_securities=None,
        include_marketable_securities=False,
        conservative_burn=25.0, base_burn=20.0, optimistic_burn=10.0,
    )
    base = next(s for s in result.scenarios if s.label == "Base case")
    assert base.quarters_of_runway == 5.0  # 100 / 20


def test_runway_includes_marketable_securities_only_when_requested():
    with_securities = compute_cash_runway(
        company_id="t", cash_and_equivalents=50.0, marketable_securities=50.0,
        include_marketable_securities=True, conservative_burn=10.0, base_burn=10.0, optimistic_burn=10.0,
    )
    without_securities = compute_cash_runway(
        company_id="t", cash_and_equivalents=50.0, marketable_securities=50.0,
        include_marketable_securities=False, conservative_burn=10.0, base_burn=10.0, optimistic_burn=10.0,
    )
    assert with_securities.liquidity_used == 100.0
    assert without_securities.liquidity_used == 50.0


def test_missing_cash_returns_empty_scenarios_not_a_crash():
    result = compute_cash_runway(
        company_id="t", cash_and_equivalents=None, marketable_securities=100.0,
        include_marketable_securities=True, conservative_burn=10.0, base_burn=10.0, optimistic_burn=10.0,
    )
    assert result.scenarios == []
    assert any("cash_and_equivalents is not available" in m for m in result.missing_inputs)


def test_nan_cash_is_treated_as_missing_not_as_a_number():
    """Regression test: a pandas NaN (from a SQL NULL numeric column) must
    be treated the same as None, not propagate into a NaN runway result."""
    result = compute_cash_runway(
        company_id="t", cash_and_equivalents=float("nan"), marketable_securities=None,
        include_marketable_securities=False, conservative_burn=10.0, base_burn=10.0, optimistic_burn=10.0,
    )
    assert result.scenarios == []
    assert any("not available" in m for m in result.missing_inputs)


def test_nan_marketable_securities_falls_back_to_cash_only():
    result = compute_cash_runway(
        company_id="t", cash_and_equivalents=100.0, marketable_securities=float("nan"),
        include_marketable_securities=True, conservative_burn=10.0, base_burn=10.0, optimistic_burn=10.0,
    )
    assert result.liquidity_used == 100.0
    assert any("marketable_securities" in m for m in result.missing_inputs)


def test_missing_or_zero_burn_rate_skips_that_scenario_without_crashing():
    result = compute_cash_runway(
        company_id="t", cash_and_equivalents=100.0, marketable_securities=None,
        include_marketable_securities=False, conservative_burn=None, base_burn=0.0, optimistic_burn=10.0,
    )
    conservative = next(s for s in result.scenarios if s.label == "Conservative (higher burn)")
    base = next(s for s in result.scenarios if s.label == "Base case")
    optimistic = next(s for s in result.scenarios if s.label == "Optimistic (lower burn)")
    assert conservative.quarters_of_runway is None
    assert base.quarters_of_runway is None
    assert optimistic.quarters_of_runway == 10.0


def test_quarterly_burn_from_operating_cash_flow_converts_outflow_to_positive_burn():
    assert quarterly_burn_from_operating_cash_flow(-5.0) == 5.0


def test_quarterly_burn_from_operating_cash_flow_handles_none_and_nan():
    assert quarterly_burn_from_operating_cash_flow(None) is None
    assert quarterly_burn_from_operating_cash_flow(float("nan")) is None


def test_quarterly_burn_from_positive_operating_cash_flow_is_zero_not_negative():
    # A company with positive operating cash flow has no "burn" to speak of;
    # the function should not return a negative burn rate.
    assert quarterly_burn_from_operating_cash_flow(5.0) == 0.0
