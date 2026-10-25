import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import icp_filter

TODAY = date(2026, 10, 25)

ICP = {
    "signal": {"type": "job_post", "lookback_days": 90,
               "title_keywords": ["SDR", "outbound"]},
    "contacts": {"title_include": ["founder", "head of growth", "coo"],
                 "title_exclude": ["sdr", "intern"]},
}


def _row(**over):
    row = {"signal_type": "job_post", "signal_date": "2026-10-10",
           "signal_text": "SDR, outbound", "title": "Founder"}
    row.update(over)
    return row


def test_fresh_matching_row_is_kept():
    kept, rejected = icp_filter.apply([_row()], ICP, today=TODAY)
    assert len(kept) == 1
    assert rejected == []


def test_signal_older_than_lookback_is_stale():
    rows = [_row(signal_date="2026-07-26"), _row(signal_date="2026-07-27")]
    kept, rejected = icp_filter.apply(rows, ICP, today=TODAY)
    assert [r["signal_date"] for r in kept] == ["2026-07-27"]
    assert rejected[0]["reason"] == "signal_stale"


def test_missing_signal_date_is_stale():
    assert icp_filter.reason_for(_row(signal_date=""), ICP, TODAY) == "signal_stale"


def test_excluded_title_is_rejected():
    row = _row(title="Founder and SDR Lead")
    kept, rejected = icp_filter.apply([row], ICP, today=TODAY)
    assert kept == []
    assert rejected[0]["reason"] == "title_excluded"


def test_title_matching_nothing_is_mismatch():
    row = _row(title="Marketing Manager")
    kept, rejected = icp_filter.apply([row], ICP, today=TODAY)
    assert kept == []
    assert rejected[0]["reason"] == "title_mismatch"


def test_title_match_is_whole_word():
    assert icp_filter.reason_for(_row(title="Coordinator"), ICP, TODAY) == "title_mismatch"
    assert icp_filter.reason_for(_row(title="International Founder"), ICP, TODAY) is None
