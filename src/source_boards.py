"""Live sourcing from public job board APIs. Free, no keys.

Reads config/boards.csv (human approved), asks each board for its open
jobs, and returns one row per board in the fixture shape: the freshest
job whose title matches signal.title_keywords. A board with no matching
job still returns a row, with the signal fields "Not found", so every
board in the seed file is accounted for in the output.

Never invents a field. Anything a board does not publish is "Not found".
"""
import csv
import html
import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from icp_filter import matches

ROOT = Path(__file__).resolve().parent.parent
BOARDS = ROOT / "config" / "boards.csv"
NF = "Not found"
USER_AGENT = "inboxkit-outbound (+https://github.com/whysaurabhsharma/inboxkit-outbound)"
PAUSE = 0.3


class BoardNotFound(Exception):
    pass


class BoardError(Exception):
    pass


def _date(value):
    """Return YYYY-MM-DD from an ISO string or epoch milliseconds."""
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)) or str(value).isdigit():
        return datetime.fromtimestamp(int(value) / 1000, timezone.utc).date().isoformat()
    try:
        return datetime.fromisoformat(str(value).replace(" UTC", "+00:00")
                                      .replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return None


def _text(value):
    return re.sub(r"<[^>]+>", " ", html.unescape(value or ""))


def parse_greenhouse(data):
    # first_published, not updated_at: an edit must not look like a new post.
    return [{"title": j.get("title"), "date": _date(j.get("first_published")),
             "url": j.get("absolute_url"), "text": _text(j.get("content"))}
            for j in data.get("jobs", [])]


def parse_lever(data):
    return [{"title": j.get("text"), "date": _date(j.get("createdAt")),
             "url": j.get("hostedUrl"),
             "text": (j.get("descriptionPlain") or "") + " " + (j.get("additionalPlain") or "")}
            for j in data]


def parse_ashby(data):
    # publishedAt is the last publish, so a repost can look fresher.
    return [{"title": j.get("title"), "date": _date(j.get("publishedAt")),
             "url": j.get("jobUrl"), "text": j.get("descriptionPlain") or ""}
            for j in data.get("jobs", []) if j.get("isListed", True)]


def parse_workable(data):
    return [{"title": j.get("title"),
             "date": _date(j.get("published_on") or j.get("created_at")),
             "url": j.get("url") or j.get("shortlink"), "text": _text(j.get("description"))}
            for j in data.get("jobs", [])]


def parse_recruitee(data):
    return [{"title": j.get("title"), "date": _date(j.get("published_at")),
             "url": j.get("careers_url"),
             "text": _text(j.get("description")) + " " + _text(j.get("requirements"))}
            for j in data.get("offers", [])]


ATS = {
    "greenhouse": ("https://boards-api.greenhouse.io/v1/boards/{0}/jobs?content=true", parse_greenhouse),
    "lever": ("https://api.lever.co/v0/postings/{0}?mode=json", parse_lever),
    "ashby": ("https://api.ashbyhq.com/posting-api/job-board/{0}", parse_ashby),
    "workable": ("https://www.workable.com/api/accounts/{0}?details=true", parse_workable),
    "recruitee": ("https://{0}.recruitee.com/api/offers/", parse_recruitee),
}


def fetch(ats, token):
    """Return the raw JSON for one board. 404 raises BoardNotFound."""
    if ats not in ATS:
        raise BoardError("Unknown board type {0!r}. Use one of: {1}".format(
            ats, ", ".join(ATS)))
    url = ATS[ats][0].format(token)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                               "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise BoardNotFound(url)
        raise BoardError("{0} returned HTTP {1}".format(url, e.code))
    except urllib.error.URLError as e:
        if ats == "recruitee" and "getaddrinfo" in str(e.reason):
            raise BoardNotFound(url)
        raise BoardError("{0} failed: {1}".format(url, e.reason))
    except ValueError:
        raise BoardError("{0} did not return JSON".format(url))


def load_boards(path=BOARDS):
    p = Path(path)
    if not p.exists():
        raise SystemExit("No {0}. Add approved boards to it, or run "
                         "python run.py probe to find candidates.".format(p))
    with p.open(newline="", encoding="utf-8-sig") as fh:
        rows = [r for r in csv.DictReader(fh) if (r.get("token") or "").strip()]
    if not rows:
        raise SystemExit("{0} has no boards. Approve rows from "
                         "config/boards_candidates.csv first.".format(p))
    return rows


def to_row(board, jobs, icp):
    """One fixture-shaped row: the freshest job matching the signal."""
    keywords = icp.get("signal", {}).get("title_keywords") or []
    hits = [j for j in jobs if j["date"] and matches(j["title"], keywords)]
    best = max(hits, key=lambda j: j["date"]) if hits else None
    stack = [s for s in icp.get("techstack", {}).get("any_of", [])
             if best and matches(best["text"], [s])]
    ats, token = board["ats"].strip().lower(), board["token"].strip()
    return {
        "account_id": "{0}:{1}".format(ats, token),
        "company": board.get("company") or NF,
        "domain": board.get("domain") or NF,
        "employee_count": NF,
        "techstack": ", ".join(stack) or NF,
        "signal_type": "job_post",
        "signal_date": best["date"] if best else NF,
        "signal_url": best["url"] if best else NF,
        "signal_text": best["title"] if best else NF,
        "first_name": "", "last_name": "", "title": NF,
        "linkedin_url": NF, "email": NF,
        "source": ats,
        "open_jobs": len(jobs),
    }


def source(icp, record_dir=None, boards_path=BOARDS):
    """Fetch every approved board. Any failure stops the run."""
    rows = []
    for board in load_boards(boards_path):
        ats, token = board["ats"].strip().lower(), board["token"].strip()
        try:
            raw = fetch(ats, token)
        except BoardNotFound as e:
            raise SystemExit("Board {0}:{1} no longer exists ({2}). Remove it "
                             "from config/boards.csv.".format(ats, token, e))
        except BoardError as e:
            raise SystemExit("Live sourcing failed: {0}. Nothing was written. "
                             "Rerun without --live for the offline demo.".format(e))
        if record_dir:
            raw_dir = Path(record_dir) / "raw"
            raw_dir.mkdir(parents=True, exist_ok=True)
            (raw_dir / "{0}_{1}.json".format(ats, token)).write_text(
                json.dumps(raw), encoding="utf-8")
        rows.append(to_row(board, ATS[ats][1](raw), icp))
        time.sleep(PAUSE)
    return rows
