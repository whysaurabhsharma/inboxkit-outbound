"""Score accounts 0 to 100 and assign a tier."""
from datetime import datetime, timezone

WEIGHTS = {
    "signal_fresh": 30,
    "signal_present": 15,
    "techstack_match": 25,
    "size_in_band": 15,
    "title_match": 15,
}


def _days_old(iso_date, today=None):
    if not iso_date:
        return None
    try:
        d = datetime.fromisoformat(str(iso_date).replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    if today is None:
        return (datetime.now(timezone.utc) - d).days
    return (today - d.date()).days


def score_row(row, icp, today=None):
    """Return score and the reasons behind it. today defaults to now."""
    points = 0
    reasons = []
    age = _days_old(row.get("signal_date"), today)
    if row.get("signal_url"):
        points += WEIGHTS["signal_present"]
        reasons.append("signal_present")
        if age is not None and age <= 30:
            points += WEIGHTS["signal_fresh"]
            reasons.append("signal_under_30_days")
        elif age is not None and age <= 90:
            points += WEIGHTS["signal_fresh"] // 2
            reasons.append("signal_under_90_days")
    stack = (row.get("techstack") or "").lower()
    wanted = [s.lower() for s in icp.get("techstack", {}).get("any_of", [])]
    if any(w in stack for w in wanted):
        points += WEIGHTS["techstack_match"]
        reasons.append("techstack_match")
    size = row.get("employee_count")
    lo = icp.get("company", {}).get("size_min", 0)
    hi = icp.get("company", {}).get("size_max", 10**6)
    if size and lo <= int(size) <= hi:
        points += WEIGHTS["size_in_band"]
        reasons.append("size_in_band")
    title = (row.get("title") or "").lower()
    includes = icp.get("contacts", {}).get("title_include", [])
    if any(t.lower() in title for t in includes):
        points += WEIGHTS["title_match"]
        reasons.append("title_match")
    return min(points, 100), ",".join(reasons)


def tier(score):
    if score >= 70:
        return "A"
    if score >= 45:
        return "B"
    return "C"
