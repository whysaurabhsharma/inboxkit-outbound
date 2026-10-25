"""One row per run. This is the audit trail."""
import csv
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "out"
LOG = OUT / "run_log.csv"

COLUMNS = [
    "run_at", "icp", "mode", "rows_in", "deduped",
    "suppressed", "invalid", "catch_all", "live",
    "credits_spent", "seconds", "note",
]


def append(**fields):
    OUT.mkdir(parents=True, exist_ok=True)
    row = {c: "" for c in COLUMNS}
    row["run_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    row.update({k: v for k, v in fields.items() if k in COLUMNS})
    new = not LOG.exists()
    with LOG.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        if new:
            w.writeheader()
        w.writerow(row)
    return LOG


def read():
    if not LOG.exists():
        return []
    with LOG.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))
