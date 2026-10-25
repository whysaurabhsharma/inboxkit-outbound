import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import first_line

ROW = {"signal_date": "2026-10-14"}


def test_clean_line_passes():
    assert first_line.check("You posted an SDR role on 14 October.", ROW) is None


def test_each_skill_rule_is_enforced():
    cases = {
        "I noticed you posted an SDR role on 14 October.": "flattery opener",
        "You posted an exciting SDR role on 14 October.": "adjective",
        "Hiring an SDR since 14 October?": "question",
        "You posted an SDR role on 14 October \u2014 nice.": "em or en dash",
        "You posted an SDR role on 14 October and InboxKit can help.": "product claim",
        "You posted an SDR role recently.": "signal date missing",
        " ".join(["word"] * 25): "25 words or more",
    }
    for line, reason in cases.items():
        assert first_line.check(line, ROW) == reason, line


def test_skill_version_is_read_from_the_skill_file():
    _, version = first_line.skill()
    assert version == "first-line-v1"


def test_committed_first_lines_match_the_checker():
    import csv
    path = ROOT / "copy" / "first_lines.csv"
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("# ")
    rows = list(csv.DictReader(lines[1:]))
    assert len({r["account_id"] for r in rows}) == 10
    for r in rows:
        why = first_line.check(r["first_line"], {"signal_date": r["signal_fact_used"].split(" | ")[1]})
        assert (why is None) == (r["approved"] == "yes"), r
        assert (why or "") == r["rejection_reason"], r
        assert r["generated_by"].startswith("claude-code-opus-5.5")
