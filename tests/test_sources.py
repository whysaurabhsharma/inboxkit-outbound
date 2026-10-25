import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import env
import pipeline
import probe_boards
import source_apify
import source_boards as sb

ICP = {"signal": {"title_keywords": ["SDR", "business development"]},
       "techstack": {"any_of": ["Smartlead", "Instantly"]}}
BOARD = {"company": "Acme Leads", "domain": "acmeleads.example", "ats": "lever", "token": "acme"}


def test_each_board_parser_reads_title_date_url():
    cases = {
        "greenhouse": {"jobs": [{"title": "SDR", "first_published": "2026-10-01T09:00:00-04:00",
                                 "updated_at": "2026-10-20T09:00:00-04:00",
                                 "absolute_url": "https://g/1", "content": "&lt;p&gt;Smartlead&lt;/p&gt;"}]},
        "lever": [{"text": "SDR", "createdAt": 1790000000000, "hostedUrl": "https://l/1",
                   "descriptionPlain": "x"}],
        "ashby": {"jobs": [{"title": "SDR", "publishedAt": "2026-10-01T10:00:00.000+00:00",
                            "jobUrl": "https://a/1", "descriptionPlain": "x", "isListed": True}]},
        "workable": {"name": "Acme", "jobs": [{"title": "SDR", "published_on": "2026-10-01",
                                               "url": "https://w/1", "description": "x"}]},
        "recruitee": {"offers": [{"title": "SDR", "published_at": "2026-10-01 09:31:36 UTC",
                                  "careers_url": "https://r/1", "description": "x"}]},
    }
    for ats, payload in cases.items():
        job = sb.ATS[ats][1](payload)[0]
        assert job["title"] == "SDR", ats
        assert job["url"].startswith("https://"), ats
        assert len(job["date"]) == 10, ats
    # Greenhouse uses first_published, so an edit does not look like a new post.
    assert sb.parse_greenhouse(cases["greenhouse"])[0]["date"] == "2026-10-01"


def test_row_takes_freshest_matching_job_and_never_invents():
    jobs = [{"title": "SDR", "date": "2026-09-01", "url": "https://l/old", "text": ""},
            {"title": "Business Development Rep", "date": "2026-10-09", "url": "https://l/new",
             "text": "We run Instantly"},
            {"title": "FP&A Analyst", "date": "2026-10-20", "url": "https://l/fpa", "text": ""}]
    row = sb.to_row(BOARD, jobs, ICP)
    assert row["signal_url"] == "https://l/new"
    assert row["techstack"] == "Instantly"
    assert row["employee_count"] == "Not found"
    assert row["email"] == "Not found"
    assert row["title"] == "Not found"
    assert row["data_source"] == "live_board"


def test_board_with_no_matching_job_has_no_signal():
    row = sb.to_row(BOARD, [{"title": "Designer", "date": "2026-10-01", "url": "u", "text": ""}], ICP)
    assert row["signal_url"] == "Not found"
    assert row["techstack"] == "Not found"


def test_empty_boards_file_stops_with_instructions(tmp_path):
    p = tmp_path / "boards.csv"
    p.write_text("company,domain,ats,token\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="boards_candidates"):
        sb.load_boards(p)


def test_apify_refuses_without_an_actor(tmp_path):
    p = tmp_path / "apify.yaml"
    p.write_text("actor:\nmax_charge_usd: 0.5\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="no actor set"):
        source_apify.load_config(p)


def test_enrich_refuses_without_prospeo_key(monkeypatch):
    import enrich_prospeo
    monkeypatch.setattr(env, "load", lambda path=None: None)
    monkeypatch.delenv("PROSPEO_API_KEY", raising=False)
    with pytest.raises(SystemExit, match="PROSPEO_API_KEY"):
        enrich_prospeo.enrich([{"domain": "acmeleads.example"}], {})


def test_enrich_is_refused_offline():
    with pytest.raises(SystemExit, match="needs --live"):
        pipeline.run(str(ROOT / "config" / "icp.yaml"), offline=True, enrich=True)


def test_recorded_fixture_replays_with_its_own_date(tmp_path, monkeypatch):
    rec = {"as_of": "2027-03-01", "rows": [{"account_id": "x"}]}
    (tmp_path / "rec.json").write_text(json.dumps(rec), encoding="utf-8")
    monkeypatch.setattr(pipeline, "FIXTURES", tmp_path)
    rows, as_of = pipeline.load_fixture({"fixtures": "rec.json"})
    assert rows == [{"account_id": "x"}]
    assert pipeline.as_of(True, {"fixtures": "rec.json"}).isoformat() == "2027-03-01"


def test_probe_tokens_from_names_and_domains():
    assert probe_boards.tokens_for("Martal Group") == ["martalgroup", "martal-group", "martal"]
    assert probe_boards.tokens_for("https://www.sales-focus.com/") == ["sales-focus", "salesfocus"]
