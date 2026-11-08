"""
Live adapter for ClinicalTrials.gov API v2 (https://clinicaltrials.gov/api/v2/).
Public, no API key required. Verified reachable 2026-10-27.

Fetching is isolated in `fetch_study` so tests can mock `requests.get`
without hitting the network (see tests/test_clinicaltrials_adapter.py).
Normalization into our schema's vocabulary is a separate function so a
schema or wording change on the registry side doesn't require touching
fetch logic.
"""
from dataclasses import dataclass
from typing import Optional

import requests

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
TIMEOUT_SECONDS = 10

# ClinicalTrials.gov overallStatus values we might see, normalized to the
# same vocabulary used in trials.status for human-readable consistency.
STATUS_DISPLAY = {
    "ACTIVE_NOT_RECRUITING": "Active, not recruiting",
    "RECRUITING": "Recruiting",
    "COMPLETED": "Completed",
    "TERMINATED": "Terminated",
    "WITHDRAWN": "Withdrawn",
    "NOT_YET_RECRUITING": "Not yet recruiting",
    "SUSPENDED": "Suspended",
    "UNKNOWN": "Unknown (registry status not updated recently)",
}


@dataclass
class TrialRegistrySnapshot:
    nct_id: str
    title: Optional[str]
    overall_status: Optional[str]      # normalized display string
    raw_status: Optional[str]          # the registry's own enum value, for audit
    enrollment_count: Optional[int]
    enrollment_type: Optional[str]     # 'ACTUAL' or 'ESTIMATED'
    last_update_posted: Optional[str]
    fetch_succeeded: bool
    error: Optional[str] = None


def fetch_study(nct_id: str) -> dict:
    """Raw fetch, isolated so tests can mock requests.get. Raises on
    network error -- callers (get_trial_snapshot) catch and wrap it."""
    resp = requests.get(f"{BASE_URL}/{nct_id}", timeout=TIMEOUT_SECONDS)
    resp.raise_for_status()
    return resp.json()


def normalize(raw: dict, nct_id: str) -> TrialRegistrySnapshot:
    """Pulls only the fields BioSignal displays; tolerates missing keys
    (registry schema has changed before and will again)."""
    protocol = raw.get("protocolSection", {})
    ident = protocol.get("identificationModule", {})
    status_module = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})

    raw_status = status_module.get("overallStatus")
    enrollment_info = design.get("enrollmentInfo", {})
    last_update = status_module.get("lastUpdatePostDateStruct", {})

    return TrialRegistrySnapshot(
        nct_id=nct_id,
        title=ident.get("briefTitle"),
        overall_status=STATUS_DISPLAY.get(raw_status, raw_status),
        raw_status=raw_status,
        enrollment_count=enrollment_info.get("count"),
        enrollment_type=enrollment_info.get("type"),
        last_update_posted=last_update.get("date"),
        fetch_succeeded=True,
    )


def get_trial_snapshot(nct_id: str) -> TrialRegistrySnapshot:
    """Top-level entry point: fetch + normalize, with graceful failure.
    Never raises -- a failed fetch returns fetch_succeeded=False so the UI
    can show 'registry check failed, showing last verified data' instead
    of crashing or silently showing stale data as if it were fresh."""
    try:
        raw = fetch_study(nct_id)
        return normalize(raw, nct_id)
    except requests.RequestException as exc:
        return TrialRegistrySnapshot(
            nct_id=nct_id, title=None, overall_status=None, raw_status=None,
            enrollment_count=None, enrollment_type=None, last_update_posted=None,
            fetch_succeeded=False, error=f"{exc.__class__.__name__}: {exc}",
        )
    except (KeyError, ValueError) as exc:
        return TrialRegistrySnapshot(
            nct_id=nct_id, title=None, overall_status=None, raw_status=None,
            enrollment_count=None, enrollment_type=None, last_update_posted=None,
            fetch_succeeded=False, error=f"Unexpected registry response shape: {exc}",
        )
