"""
Adapter tests using mocked external services (per project brief section 12:
"Use mocked external services in tests"). No real network calls happen here
-- that's what the manual verification in docs/EVALUATION.md's dev notes
covers separately.
"""
from unittest.mock import MagicMock, patch

import requests

from bioanalyst.adapters.clinicaltrials_adapter import get_trial_snapshot
from bioanalyst.adapters.sec_edgar_adapter import _latest_instant, _latest_quarterly_duration, get_financial_snapshot


def _mock_response(json_data, status_ok=True):
    resp = MagicMock()
    resp.json.return_value = json_data
    if status_ok:
        resp.raise_for_status.return_value = None
    else:
        resp.raise_for_status.side_effect = requests.HTTPError("mocked 404")
    return resp


def test_clinicaltrials_adapter_handles_network_failure_gracefully():
    with patch("bioanalyst.adapters.clinicaltrials_adapter.requests.get",
               side_effect=requests.ConnectionError("mocked network failure")):
        snap = get_trial_snapshot("NCT99999999")
    assert snap.fetch_succeeded is False
    assert "ConnectionError" in snap.error
    assert snap.overall_status is None  # must not show stale/fake data as if it were fresh


def test_clinicaltrials_adapter_normalizes_a_successful_response():
    fake_json = {
        "protocolSection": {
            "identificationModule": {"briefTitle": "Mock ALS Trial"},
            "statusModule": {"overallStatus": "RECRUITING",
                              "lastUpdatePostDateStruct": {"date": "2026-01-01"}},
            "designModule": {"enrollmentInfo": {"count": 42, "type": "ESTIMATED"}},
        }
    }
    with patch("bioanalyst.adapters.clinicaltrials_adapter.requests.get",
               return_value=_mock_response(fake_json)):
        snap = get_trial_snapshot("NCT00000000")
    assert snap.fetch_succeeded is True
    assert snap.overall_status == "Recruiting"
    assert snap.enrollment_count == 42


def test_clinicaltrials_adapter_tolerates_missing_fields_in_response():
    with patch("bioanalyst.adapters.clinicaltrials_adapter.requests.get",
               return_value=_mock_response({"protocolSection": {}})):
        snap = get_trial_snapshot("NCT00000001")
    assert snap.fetch_succeeded is True
    assert snap.overall_status is None
    assert snap.enrollment_count is None


def test_sec_edgar_adapter_handles_network_failure_gracefully():
    with patch("bioanalyst.adapters.sec_edgar_adapter.requests.get",
               side_effect=requests.ConnectionError("mocked network failure")):
        snap = get_financial_snapshot("0000000000")
    assert snap.fetch_succeeded is False
    assert "ConnectionError" in snap.error


def test_sec_edgar_adapter_pools_across_tags_for_the_latest_value():
    """Regression test for a real bug: Biogen switched XBRL tags for cash
    over time (CashAndCashEquivalentsAtCarryingValue through 2019, then
    CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents after).
    An earlier version picked the FIRST candidate tag with ANY data and
    silently returned a stale 2019 value while a newer tag had 2026 data.
    This test constructs exactly that shape and asserts the newer value wins."""
    us_gaap = {
        "CashAndCashEquivalentsAtCarryingValue": {
            "units": {"USD": [{"end": "2019-12-31", "val": 111, "form": "10-K"}]}
        },
        "Cash": {"units": {"USD": []}},
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents": {
            "units": {"USD": [{"end": "2026-06-30", "val": 999, "form": "10-Q"}]}
        },
    }
    candidate_tags = ["CashAndCashEquivalentsAtCarryingValue", "Cash",
                      "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"]
    best = _latest_instant(us_gaap, candidate_tags)
    assert best["val"] == 999
    assert best["end"] == "2026-06-30"


def test_sec_edgar_adapter_quarterly_duration_filters_to_single_quarter_spans():
    us_gaap = {
        "ResearchAndDevelopmentExpense": {
            "units": {"USD": [
                {"start": "2026-01-01", "end": "2026-06-30", "val": 999, "form": "10-Q"},  # 6-month, should be excluded
                {"start": "2026-04-01", "end": "2026-06-30", "val": 50, "form": "10-Q"},   # 1 quarter, should win
            ]}
        }
    }
    best = _latest_quarterly_duration(us_gaap, ["ResearchAndDevelopmentExpense"])
    assert best["val"] == 50


def test_sec_edgar_adapter_full_normalize_with_mocked_response():
    fake_json = {
        "entityName": "MOCK BIOTECH INC",
        "facts": {
            "us-gaap": {
                "CashAndCashEquivalentsAtCarryingValue": {
                    "units": {"USD": [{"end": "2026-06-30", "val": 5000000, "form": "10-Q", "filed": "2026-08-01"}]}
                },
                "ResearchAndDevelopmentExpense": {
                    "units": {"USD": [{"start": "2026-04-01", "end": "2026-06-30", "val": 1000000, "form": "10-Q"}]}
                },
            },
            "dei": {
                "EntityCommonStockSharesOutstanding": {
                    "units": {"shares": [{"end": "2026-06-30", "val": 10000000, "form": "10-Q"}]}
                }
            },
        },
    }
    with patch("bioanalyst.adapters.sec_edgar_adapter.requests.get", return_value=_mock_response(fake_json)):
        snap = get_financial_snapshot("0000000000")
    assert snap.fetch_succeeded is True
    assert snap.entity_name == "MOCK BIOTECH INC"
    assert snap.values["cash_and_equivalents"] == 5000000
    assert snap.values["rd_expense"] == 1000000
    assert snap.shares_outstanding == 10000000
