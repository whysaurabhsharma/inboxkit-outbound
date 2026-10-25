"""Find the decision maker and a verified email with Prospeo.

Spends Prospeo credits, so it only runs with --live --enrich. Per
account, at most two credits: one Search Person request (charged only
when it returns someone) and one Enrich Person (charged only when an
email is found). Prospeo's VERIFIED status is the verification result;
BounceBan is only asked about catch-alls, in the pipeline.

Request shapes follow https://prospeo.io/api-docs as read on
25 Oct 2026. Not yet exercised against the live API.
"""
import json
import time
import urllib.error
import urllib.request

import env

BASE = "https://api.prospeo.io"
NF = "Not found"
PAUSE = 0.5


def _post(path, body, key):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"X-KEY": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:200]
        if e.code in (400, 404) and "NO_MATCH" in detail:
            return None
        raise SystemExit("Prospeo {0} returned HTTP {1}: {2}. Nothing was "
                         "written.".format(path, e.code, detail))
    except urllib.error.URLError as e:
        raise SystemExit("Prospeo {0} failed: {1}".format(path, e.reason))
    if data.get("error"):
        if data.get("error_code") == "NO_MATCH":
            return None
        raise SystemExit("Prospeo {0} error: {1}".format(path, data))
    return data


def find_person(domain, icp, key):
    """Return the first person at domain whose title passes the ICP."""
    from icp_filter import matches
    contacts = icp.get("contacts", {})
    body = {"filters": {
        "company": {"websites": {"include": [domain]}},
        "person_job_title": {"include": contacts.get("title_include") or [],
                             "match_mode": "CONTAINS"},
    }}
    data = _post("/search-person", body, key)
    for item in (data or {}).get("results", []):
        person = item.get("person") or {}
        if not matches(person.get("current_job_title"),
                       contacts.get("title_exclude") or []):
            return person
    return None


def enrich_email(person_id, key):
    data = _post("/enrich-person", {"only_verified_email": True,
                                    "data": {"person_id": person_id}}, key)
    email = ((data or {}).get("person") or {}).get("email") or {}
    if email.get("status") == "VERIFIED" and email.get("email"):
        return email["email"]
    return None


def enrich(rows, icp):
    """Fill contact fields in place. Rows with nobody found stay Not found."""
    key = env.require("PROSPEO_API_KEY",
                      "Add it to .env (free plan at prospeo.io) or drop --enrich.")
    for row in rows:
        domain = row.get("domain")
        if not domain or domain == NF:
            continue
        person = find_person(domain, icp, key)
        time.sleep(PAUSE)
        if not person:
            continue
        row["first_name"] = person.get("first_name") or ""
        row["last_name"] = person.get("last_name") or ""
        row["name"] = person.get("full_name") or NF
        row["title"] = person.get("current_job_title") or NF
        row["linkedin_url"] = person.get("linkedin_url") or NF
        email = enrich_email(person.get("person_id"), key)
        time.sleep(PAUSE)
        if email:
            row["email"] = email
            row["verification_status"] = "valid"
            row["verification_source"] = "prospeo"
    return rows
