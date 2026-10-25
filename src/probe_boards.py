"""Find which public job boards belong to agencies you name.

Give it agency names or domains. It guesses board tokens and asks each
board API; a missing board is a 404 and costs nothing. Hits go to
config/boards_candidates.csv with the evidence. Nothing is written to
config/boards.csv: a human approves each candidate by copying it there.
"""
import csv
import re
import time
from datetime import date
from pathlib import Path

import source_boards as sb
from dedupe import normalise_company, normalise_domain

ROOT = Path(__file__).resolve().parent.parent
CANDIDATES = ROOT / "config" / "boards_candidates.csv"
COLUMNS = ["ats", "token", "board_name", "probed_for", "name_match",
           "open_jobs", "sample_job", "sample_url", "checked_on", "status"]


def tokens_for(value):
    """Plausible board tokens for one agency name or domain."""
    value = value.strip()
    out = []
    if "." in value and " " not in value:
        stem = normalise_domain(value).split(".")[0]
        out += [stem, stem.replace("-", "")]
    else:
        words = re.sub(r"[^a-z0-9 ]", " ", value.lower()).split()
        out += ["".join(words), "-".join(words), normalise_company(value)]
    seen, uniq = set(), []
    for t in out:
        if t and t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq


def _board_name(ats, raw, jobs):
    if ats == "workable":
        return raw.get("name") or ""
    if ats == "greenhouse" and raw.get("jobs"):
        return raw["jobs"][0].get("company_name") or ""
    if ats == "recruitee" and raw.get("offers"):
        return raw["offers"][0].get("company_name") or ""
    return ""


def probe(values, pause=sb.PAUSE):
    """Return candidate rows for every board that exists."""
    found = []
    for value in values:
        for token in tokens_for(value):
            for ats, (_, parse) in sb.ATS.items():
                try:
                    raw = sb.fetch(ats, token)
                except sb.BoardNotFound:
                    continue
                except sb.BoardError as e:
                    print("  skipped {0}:{1}: {2}".format(ats, token, e))
                    continue
                finally:
                    time.sleep(pause)
                jobs = parse(raw)
                name = _board_name(ats, raw, jobs)
                fresh = max((j for j in jobs if j["date"]), key=lambda j: j["date"], default=None)
                found.append({
                    "ats": ats, "token": token, "board_name": name or "Not found",
                    "probed_for": value,
                    "name_match": "yes" if name and normalise_company(name) ==
                    normalise_company(value.split(".")[0]) else "check",
                    "open_jobs": len(jobs),
                    "sample_job": fresh["title"] if fresh else "",
                    "sample_url": fresh["url"] if fresh else "",
                    "checked_on": date.today().isoformat(), "status": "pending",
                })
    return found


def write(rows, path=CANDIDATES):
    """Append new candidates, skipping any ats:token already listed."""
    p = Path(path)
    existing = set()
    if p.exists():
        with p.open(newline="", encoding="utf-8-sig") as fh:
            existing = {(r["ats"], r["token"]) for r in csv.DictReader(fh)}
    new = [r for r in rows if (r["ats"], r["token"]) not in existing]
    with p.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        if not existing and (not p.exists() or p.stat().st_size == 0):
            w.writeheader()
        w.writerows(new)
    return new
