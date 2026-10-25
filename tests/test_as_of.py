import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pipeline
import score

FROZEN = date.fromisoformat(json.loads(
    (ROOT / "data" / "fixtures" / "as_of.json").read_text(encoding="utf-8-sig")
)["as_of"])


def test_offline_counts_back_from_fixture_date():
    assert pipeline.as_of(offline=True) == FROZEN


def test_live_counts_back_from_today():
    assert pipeline.as_of(offline=False) == date.today()


def test_score_uses_the_date_it_is_given():
    icp = {"techstack": {"any_of": []}, "company": {}, "contacts": {}}
    row = {"signal_url": "https://x", "signal_date": "2026-10-01"}
    _, fresh = score.score_row(row, icp, today=date(2026, 10, 25))
    _, aged = score.score_row(row, icp, today=date(2027, 10, 25))
    assert "signal_under_30_days" in fresh
    assert "signal_under_30_days" not in aged
