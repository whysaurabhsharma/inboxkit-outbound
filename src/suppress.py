"""Match rows against the suppression list."""
import csv
from pathlib import Path

from dedupe import normalise_domain


def load(path="config/suppression.csv"):
    domains = {}
    emails = {}
    p = Path(path)
    if not p.exists():
        return domains, emails
    with p.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            reason = (row.get("reason") or "suppressed").strip()
            note = (row.get("note") or "").strip()
            dom = normalise_domain(row.get("domain"))
            mail = (row.get("email") or "").strip().lower()
            if dom:
                domains[dom] = (reason, note)
            if mail:
                emails[mail] = (reason, note)
    return domains, emails


def apply(rows, path="config/suppression.csv"):
    domains, emails = load(path)
    kept = []
    suppressed = []
    for row in rows:
        dom = normalise_domain(row.get("domain"))
        mail = (row.get("email") or "").strip().lower()
        hit = None
        if mail and mail in emails:
            hit = ("email", mail, emails[mail])
        elif dom and dom in domains:
            hit = ("domain", dom, domains[dom])
        if hit:
            field, value, pair = hit
            out = dict(row)
            out["suppressed_on"] = field
            out["matched_value"] = value
            out["reason"] = pair[0]
            out["note"] = pair[1]
            suppressed.append(out)
        else:
            kept.append(row)
    return kept, suppressed


def add(email, reason, path="config/suppression.csv"):
    """Append one address. This is how an opt-out is honoured."""
    email = email.strip().lower()
    _, emails = load(path)
    if email in emails:
        return False
    with Path(path).open("a", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerow(["", email, reason, "added by run.py"])
    return True

