"""Email verification. Only valid rows go live."""
import json
import os
from pathlib import Path

STATUSES = ("valid", "catch_all", "invalid", "unknown", "role")
ROLE_PREFIXES = {"info", "sales", "support", "admin", "hello",
                 "contact", "team", "help", "billing", "noreply"}

FIXTURES = Path(__file__).resolve().parent.parent / "data" / "fixtures"


def _fixture_path():
    return FIXTURES / "verify.json"


def _load_fixtures():
    p = _fixture_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8-sig"))


def _save_fixtures(data):
    FIXTURES.mkdir(parents=True, exist_ok=True)
    _fixture_path().write_text(json.dumps(data, indent=2), encoding="utf-8")


def _looks_role(email):
    return email.split("@")[0].lower() in ROLE_PREFIXES


def verify(email, offline=True, record=False):
    """Return one of STATUSES. Offline reads recorded fixtures."""
    email = (email or "").strip().lower()
    if not email or "@" not in email:
        return "invalid"
    if _looks_role(email):
        return "role"
    fixtures = _load_fixtures()
    if offline:
        return fixtures.get(email, "unknown")
    status = _call_bounceban(email)
    if record:
        fixtures[email] = status
        _save_fixtures(fixtures)
    return status


def _call_bounceban(email):
    """Live call. Returns unknown without a key rather than guessing."""
    key = os.environ.get("BOUNCEBAN_API_KEY")
    if not key:
        return "unknown"
    import urllib.request
    import urllib.parse
    url = "https://api.bounceban.com/v1/verify/single?"
    url += urllib.parse.urlencode({"email": email})
    req = urllib.request.Request(url, headers={"Authorization": key})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return "unknown"
    raw = str(data.get("result") or data.get("status") or "").lower()
    if raw in ("deliverable", "valid"):
        return "valid"
    if raw in ("undeliverable", "invalid"):
        return "invalid"
    if "catch" in raw or raw == "accept_all":
        return "catch_all"
    if raw == "role":
        return "role"
    return "unknown"
