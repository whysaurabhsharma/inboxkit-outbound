"""Write the output CSVs. This repo never sends anything."""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "out"

# The nine columns the brief asks for, first and in its order.
BRIEF_COLUMNS = [
    "name", "title", "company", "domain", "linkedin_url",
    "email", "verification_status", "signal", "source",
]

# My additions, after the nine.
EXTRA_COLUMNS = [
    "account_id", "score", "tier", "first_line", "prompt_version",
    "signal_date", "signal_url", "techstack", "employee_count",
]


def _write(path, rows, columns):
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / path
    with target.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)
    return target


def write_leads(rows):
    cols = BRIEF_COLUMNS + EXTRA_COLUMNS
    return _write("leads.csv", rows, cols)


def write_rejects(rows):
    cols = ["account_id", "company", "domain", "email",
            "reason", "verification_status", "source"]
    return _write("rejects.csv", rows, cols)


def write_suppressed(rows):
    cols = ["account_id", "company", "domain", "email",
            "suppressed_on", "matched_value", "reason", "note"]
    return _write("suppressed.csv", rows, cols)


def write_held(rows):
    cols = BRIEF_COLUMNS + ["account_id", "note"]
    return _write("held.csv", rows, cols)
