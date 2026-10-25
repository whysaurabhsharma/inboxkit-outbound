import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import export
from dedupe import normalise_domain

FIXTURES = ROOT / "data" / "fixtures"
LABELS = {"live_board", "live_apify", "synthetic_dry_run"}


def _rows(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8-sig"))


def test_data_source_follows_the_nine_brief_columns():
    cols = export.BRIEF_COLUMNS + export.PROVENANCE + export.EXTRA_COLUMNS
    assert len(export.BRIEF_COLUMNS) == 9
    assert cols[9] == "data_source"


def test_every_fixture_row_is_labelled():
    for name in ("companies.json", "companies_jobchangers.json"):
        for row in _rows(name):
            assert row.get("data_source") in LABELS, (name, row["account_id"])


def test_synthetic_rows_cannot_be_real_companies():
    for row in _rows("companies.json"):
        if row["data_source"] == "synthetic_dry_run":
            assert normalise_domain(row["domain"]).endswith(".example"), row["account_id"]
            assert ".example/" in row["signal_url"]


def test_live_rows_carry_a_real_dated_signal_and_invent_nothing():
    live = [r for r in _rows("companies.json") if r["data_source"] == "live_board"]
    assert {r["company"] for r in live} == {"Belkins", "memoryBlue"}
    for r in live:
        assert r["signal_url"].startswith("https://")
        assert len(r["signal_date"]) == 10
        for field in ("employee_count", "title", "email", "linkedin_url"):
            assert r[field] == "Not found"


def test_live_accounts_go_to_needs_contact_not_rejects(tmp_path, monkeypatch):
    import csv
    import pipeline
    import run_log
    monkeypatch.setattr(export, "OUT", tmp_path)
    monkeypatch.setattr(run_log, "OUT", tmp_path)
    monkeypatch.setattr(run_log, "LOG", tmp_path / "run_log.csv")
    stats, rejects = pipeline.run(str(ROOT / "config" / "icp.yaml"))
    with (tmp_path / "needs_contact.csv").open(encoding="utf-8-sig") as fh:
        needs = list(csv.DictReader(fh))
    assert {r["company"] for r in needs} == {"Belkins", "memoryBlue"}
    assert all(r["data_source"] == "live_board" for r in needs)
    assert stats["needs_contact"] == 2
    assert not [r for r in rejects if r.get("data_source") == "live_board"]
