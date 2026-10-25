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


def test_open_role_claims_need_a_field_proving_it():
    for line in ["Your SDR role has been open since 14 October.",
                 "Your SDR role posted on 14 October is still open.",
                 "Acme has an open SDR role, posted 14 October.",
                 "Acme is still hiring an SDR, posted 14 October."]:
        assert first_line.check(line, ROW) == "claims role is still open", line
    proven = dict(ROW, role_open_checked_on="2026-10-24")
    assert first_line.check("Your SDR role posted 14 October is still open.", proven) is None
    assert first_line.check("Outbound team posted an SDR role on 14 October.", ROW) is None


def test_present_tense_live_claims_need_a_field_proving_it():
    lines = ["Acme is hiring an SDR, posted 14 October.",
             "You are hiring an SDR, posted 14 October.",
             "You're hiring an SDR, posted 14 October.",
             "You" + chr(0x2019) + "re hiring an SDR, posted 14 October.",
             "Acme has an opening for an SDR, posted 14 October.",
             "Acme posted SDR openings on 14 October.",
             "Acme is currently recruiting an SDR, posted 14 October.",
             "Acme is looking for an SDR, posted 14 October."]
    for line in lines:
        assert first_line.check(line, ROW) == "claims role is still open", line
    proven = dict(ROW, role_open_checked_on="2026-10-24")
    for line in lines:
        assert first_line.check(line, proven) is None, line


def test_line_may_only_use_fields_the_skill_receives():
    for line in ["You posted an SDR role on 14 October and your site runs Smartlead.",
                 "Your Instantly team posted an SDR role on 14 October.",
                 "Your team of 12 people posted an SDR role on 14 October."]:
        assert first_line.check(line, ROW) == "uses a field the skill does not receive", line


def test_skill_good_examples_pass_the_checker():
    text, _ = first_line.skill()
    good = text.split("## Good", 1)[1].split("## Bad", 1)[0]
    examples = [l.strip() for l in good.splitlines() if l.strip()]
    assert examples
    for line in examples:
        d = [m for m in first_line.MONTHS if m in line][0]
        day = line.split(" " + d)[0].split()[-1]
        row = {"signal_date": "2026-{0:02d}-{1:02d}".format(first_line.MONTHS.index(d) + 1, int(day))}
        assert first_line.check(line, row) is None, line


def test_skill_version_is_read_from_the_skill_file():
    _, version = first_line.skill()
    assert version == "first-line-v3"


def _committed(name):
    import csv
    lines = (ROOT / "copy" / name).read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("# "), name
    return list(csv.DictReader(lines[1:]))


def test_committed_first_lines_match_the_checker():
    """Every verdict in both files is the checker's; a fix row says what it fixes."""
    for name, accounts in (("first_lines_full.csv", 25), ("first_lines.csv", 10)):
        rows = _committed(name)
        assert len({r["account_id"] for r in rows}) == accounts, name
        for r in rows:
            why = first_line.check(r["first_line"],
                                   {"signal_date": r["signal_fact_used"].split(" | ")[1]})
            assert (why is None) == (r["approved"] == "yes"), r
            if why:
                assert r["rejection_reason"] == why, r
            else:
                assert r["rejection_reason"] in ("",) or r["rejection_reason"].startswith("fix:"), r
            assert r["generated_by"].startswith("claude-code-opus-5.5"), r
            assert r["prompt_version"] == first_line.skill()[1], r


def test_best_ten_come_from_the_full_run():
    full = {(r["account_id"], r["first_line"]) for r in _committed("first_lines_full.csv")}
    best = {(r["account_id"], r["first_line"]) for r in _committed("first_lines.csv")}
    assert best <= full
