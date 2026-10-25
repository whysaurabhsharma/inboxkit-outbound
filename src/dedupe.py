"""Deduplicate companies and people."""
import re

LEGAL = {"inc", "llc", "ltd", "limited", "corp", "corporation",
         "gmbh", "bv", "pty", "plc", "co", "company", "group",
         "agency", "media", "digital", "labs", "lab"}


def normalise_domain(value):
    if not value:
        return ""
    v = value.strip().lower()
    v = re.sub(r"^https?://", "", v)
    v = re.sub(r"^www\.", "", v)
    v = v.split("/")[0].split("?")[0].split(":")[0]
    return v.strip(".")


def normalise_company(value):
    if not value:
        return ""
    v = re.sub(r"[^a-z0-9 ]", " ", value.lower())
    words = [w for w in v.split() if w and w not in LEGAL]
    return "".join(words)


def company_key(row):
    domain = normalise_domain(row.get("domain"))
    if domain:
        return "d:" + domain
    name = normalise_company(row.get("company"))
    return "c:" + name if name else ""


def person_key(row):
    first = (row.get("first_name") or "").strip().lower()
    last = (row.get("last_name") or "").strip().lower()
    domain = normalise_domain(row.get("domain"))
    return "|".join([first, last, domain])


def dedupe(rows, key_fn):
    """Return kept rows and rejected rows with a reason."""
    seen = {}
    kept = []
    rejected = []
    for row in rows:
        key = key_fn(row)
        if not key:
            kept.append(row)
            continue
        if key in seen:
            out = dict(row)
            out["reason"] = "duplicate_of:" + str(seen[key])
            rejected.append(out)
        else:
            seen[key] = row.get("account_id") or row.get("domain") or key
            kept.append(row)
    return kept, rejected
