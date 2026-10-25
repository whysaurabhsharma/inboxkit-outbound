"""The Monday review, straight from the run log."""
import csv
from pathlib import Path

import run_log

OUT = Path(__file__).resolve().parent.parent / "data" / "out"


def _count_leads():
    p = OUT / "leads.csv"
    if not p.exists():
        return 0, {}
    with p.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    tiers = {}
    for r in rows:
        t = r.get("tier") or "?"
        tiers[t] = tiers.get(t, 0) + 1
    return len(rows), tiers


def monday_review():
    runs = run_log.read()
    if not runs:
        return "No runs logged yet. Run: python run.py run"
    last = runs[-1]
    total, tiers = _count_leads()
    tier_line = ", ".join(
        "{0}: {1}".format(k, tiers[k]) for k in sorted(tiers)
    ) or "none"

    lines = []
    lines.append("Monday review")
    lines.append("=" * 40)
    lines.append("")
    lines.append("Numbers, last run " + last.get("run_at", ""))
    lines.append("  sourced      " + last.get("rows_in", "0"))
    lines.append("  deduped out  " + last.get("deduped", "0"))
    lines.append("  suppressed   " + last.get("suppressed", "0"))
    lines.append("  off ICP      " + (last.get("off_icp") or "0"))
    lines.append("  accounts     " + (last.get("accounts") or "0"))
    lines.append("  need contact " + (last.get("needs_contact") or "0"))
    lines.append("  bad email    " + last.get("invalid", "0"))
    lines.append("  held         " + last.get("catch_all", "0"))
    lines.append("  live         " + last.get("live", "0"))
    lines.append("  run time     " + last.get("seconds", "0") + "s")
    lines.append("  tiers        " + tier_line)
    lines.append("")
    lines.append("Top three learnings")
    lines.append("  1. ")
    lines.append("  2. ")
    lines.append("  3. ")
    lines.append("")
    lines.append("Next three launches")
    lines.append("  1. ")
    lines.append("  2. ")
    lines.append("  3. ")
    lines.append("")
    lines.append("Total runs logged: " + str(len(runs)))
    return chr(10).join(lines)

