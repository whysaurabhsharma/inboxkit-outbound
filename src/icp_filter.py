"""Drop rows the ICP rules out. Runs before verify, so no credits.

Two stages. "signal" checks the account and runs first. "contact" checks
the person and runs after enrichment, since live sources find accounts
before anyone at them.
"""
import re
from datetime import date, datetime

NF = "Not found"


def matches(text, keywords):
    """Whole-word match, so "coo" never hits "coordinator"."""
    text = (text or "").lower()
    for kw in keywords:
        pattern = r"(?<![a-z0-9])" + re.escape(kw.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, text):
            return True
    return False


def _signal_date(value):
    try:
        return datetime.fromisoformat(str(value)[:10]).date()
    except ValueError:
        return None


def _missing(value):
    return not value or value == NF


def signal_reason(row, icp, today):
    signal = icp.get("signal", {})
    if _missing(row.get("signal_url")):
        return "no_signal"

    lookback = signal.get("lookback_days")
    if lookback is not None:
        d = _signal_date(row.get("signal_date"))
        if d is None or (today - d).days > int(lookback):
            return "signal_stale"

    wanted_type = signal.get("type")
    keywords = signal.get("title_keywords") or []
    if wanted_type and row.get("signal_type") != wanted_type:
        return "signal_mismatch"
    if keywords and not matches(row.get("signal_text"), keywords):
        return "signal_mismatch"
    return None


def contact_reason(row, icp):
    contacts = icp.get("contacts", {})
    title = row.get("title")
    if _missing(title):
        return "no_contact"
    if matches(title, contacts.get("title_exclude") or []):
        return "title_excluded"
    include = contacts.get("title_include") or []
    if include and not matches(title, include):
        return "title_mismatch"
    return None


def reason_for(row, icp, today=None, stage="all"):
    """Return the reject reason for one row, or None to keep it."""
    today = today or date.today()
    if stage in ("all", "signal"):
        why = signal_reason(row, icp, today)
        if why:
            return why
    if stage in ("all", "contact"):
        return contact_reason(row, icp)
    return None


def apply(rows, icp, today=None, stage="all"):
    """Return kept rows and rejected rows with a reason."""
    kept, rejected = [], []
    for row in rows:
        why = reason_for(row, icp, today, stage)
        if why:
            out = dict(row)
            out["reason"] = why
            rejected.append(out)
        else:
            kept.append(row)
    return kept, rejected
