"""The pipeline. One YAML in, four CSVs out."""
import json
import time
from datetime import date
from pathlib import Path

import dedupe
import icp_filter
import suppress
import verify
import score as scoring
import export
import run_log

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "data" / "fixtures"


def load_icp(path):
    """Minimal YAML reader. No dependency needed for this shape."""
    import yaml
    return yaml.safe_load(Path(path).read_text(encoding="utf-8-sig"))


def source(icp, offline=True):
    """Offline reads fixtures. Live would call Apify here."""
    if offline:
        p = FIXTURES / icp.get("fixtures", "companies.json")
        return json.loads(p.read_text(encoding="utf-8-sig"))
    raise SystemExit("Live sourcing needs APIFY_TOKEN. Use make demo.")


def as_of(offline=True):
    """The date signal age counts back from. Frozen offline."""
    if offline:
        p = FIXTURES / "as_of.json"
        data = json.loads(p.read_text(encoding="utf-8-sig"))
        return date.fromisoformat(data["as_of"])
    return date.today()


def build_signal_cell(row):
    bits = [row.get("signal_type") or "", row.get("signal_date") or "",
            row.get("signal_url") or ""]
    return " | ".join(b for b in bits if b)


def shape(row, icp, today=None):
    """Map a raw record onto the brief column names."""
    pts, reasons = scoring.score_row(row, icp, today)
    out = dict(row)
    out["name"] = " ".join(
        [row.get("first_name") or "", row.get("last_name") or ""]
    ).strip()
    out["signal"] = build_signal_cell(row)
    out["score"] = pts
    out["tier"] = scoring.tier(pts)
    out["score_reasons"] = reasons
    return out


def run(icp_path, limit=None, offline=True):
    """Source, dedupe, suppress, filter, verify, score, export."""
    started = time.time()
    icp = load_icp(icp_path)
    raw = source(icp, offline=offline)
    rows_in = len(raw)
    today = as_of(offline)

    shaped = [shape(r, icp, today) for r in raw]

    kept, dupes = dedupe.dedupe(shaped, dedupe.company_key)
    kept, person_dupes = dedupe.dedupe(kept, dedupe.person_key)
    dupes = dupes + person_dupes

    supp_path = str(ROOT / "config" / "suppression.csv")
    kept, suppressed = suppress.apply(kept, supp_path)
    kept, off_icp = icp_filter.apply(kept, icp, today)

    live, held, bad = [], [], []
    for row in kept:
        status = verify.verify(row.get("email"), offline=offline)
        row["verification_status"] = status
        if status == "valid":
            live.append(row)
        elif status == "catch_all":
            row["note"] = "second verifier or sacrificial mailbox first"
            held.append(row)
        else:
            row["reason"] = "bad_email"
            bad.append(row)

    live.sort(key=lambda r: r.get("score", 0), reverse=True)
    cap = limit or icp.get("output", {}).get("limit")
    if cap:
        live = live[:int(cap)]

    rejects = dupes + off_icp + bad
    export.write_leads(live)
    export.write_rejects(rejects)
    export.write_suppressed(suppressed)
    export.write_held(held)

    stats = {
        "icp": Path(icp_path).name,
        "mode": "offline" if offline else "live",
        "rows_in": rows_in,
        "deduped": len(dupes),
        "suppressed": len(suppressed),
        "off_icp": len(off_icp),
        "invalid": len(bad),
        "catch_all": len(held),
        "live": len(live),
        "credits_spent": 0 if offline else "",
        "seconds": round(time.time() - started, 2),
    }
    run_log.append(**stats)
    return stats
