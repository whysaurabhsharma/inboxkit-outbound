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
