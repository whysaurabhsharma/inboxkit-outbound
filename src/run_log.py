"""One row per run. This is the audit trail."""
import csv
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "out"
LOG = OUT / "run_log.csv"

COLUMNS = [
    "run_at", "icp", "mode", "rows_in", "deduped",
    "suppressed", "off_icp", "invalid", "catch_all", "live",
    "credits_spent", "seconds", "note",
]


def _migrate():
    """Rewrite a log with an older header so columns stay aligned."""
    if not LOG.exists():
        return
    with LOG.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames == COLUMNS:
            return
        rows = list(reader)
    with LOG.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def append(**fields):
    OUT.mkdir(parents=True, exist_ok=True)
    row = {c: "" for c in COLUMNS}
    row["run_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    row.update({k: v for k, v in fields.items() if k in COLUMNS})
    _migrate()
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
