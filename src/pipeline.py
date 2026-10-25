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


def load_fixture(icp):
    """Return fixture rows and the date they were recorded, if stored.

    A fixture is a list of rows, or {"as_of": ..., "rows": [...]} when it
    was recorded from a live run with --record.
    """
    p = FIXTURES / icp.get("fixtures", "companies.json")
    data = json.loads(p.read_text(encoding="utf-8-sig"))
    if isinstance(data, dict):
        return data["rows"], date.fromisoformat(data["as_of"])
    return data, None


def source(icp, offline=True, source_name="boards", record_dir=None):
    """Offline reads fixtures. Live asks the public job boards, or Apify."""
    if offline:
        return load_fixture(icp)[0]
    if source_name == "boards":
        import source_boards
        return source_boards.source(icp, record_dir=record_dir)
    if source_name == "apify":
        import source_apify
        return source_apify.source(icp, record_dir=record_dir)
    raise SystemExit("Unknown source {0!r}. Use boards or apify.".format(source_name))


def as_of(offline=True, icp=None):
    """The date signal age counts back from. Frozen offline."""
    if offline:
        recorded = load_fixture(icp)[1] if icp else None
        if recorded:
            return recorded
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
    ).strip() or row.get("name") or "Not found"
    out["signal"] = build_signal_cell(row)
    out["score"] = pts
    out["tier"] = scoring.tier(pts)
    out["score_reasons"] = reasons
    return out


def _status(row, offline):
    """Provider status first (Prospeo), BounceBan only for catch-alls."""
    status = row.get("verification_status")
    if not status:
        status = verify.verify(row.get("email"), offline=True) if offline else "unknown"
    if status == "catch_all" and not offline:
        status = verify.verify(row.get("email"), offline=False)
    return status


def run(icp_path, limit=None, offline=True, source_name="boards",
        record=False, enrich=False):
    """Source, dedupe, suppress, filter, enrich, verify, score, export."""
    started = time.time()
    icp = load_icp(icp_path)
    today = as_of(offline, icp)
    record_dir = None
    if record and not offline:
        record_dir = FIXTURES / "live" / today.isoformat()
    raw = source(icp, offline=offline, source_name=source_name,
                 record_dir=record_dir)
    rows_in = len(raw)
    if record_dir:
        record_dir.mkdir(parents=True, exist_ok=True)
        (record_dir / "companies.json").write_text(json.dumps(
            {"as_of": today.isoformat(), "rows": raw}, indent=1), encoding="utf-8")

    kept, dupes = dedupe.dedupe(raw, dedupe.company_key)
    kept, person_dupes = dedupe.dedupe(kept, dedupe.person_key)
    dupes = dupes + person_dupes

    supp_path = str(ROOT / "config" / "suppression.csv")
    kept, suppressed = suppress.apply(kept, supp_path)
    kept, off_signal = icp_filter.apply(kept, icp, today, stage="signal")
    accounts = len(kept)

    if enrich:
        if offline:
            raise SystemExit("--enrich spends Prospeo credits and needs --live.")
        import enrich_prospeo
        enrich_prospeo.enrich(kept, icp)
        kept, late_suppressed = suppress.apply(kept, supp_path)
        suppressed = suppressed + late_suppressed

    kept, off_contact = icp_filter.apply(kept, icp, today, stage="contact")
    off_icp = off_signal + off_contact

    live, held, bad = [], [], []
    for row in (shape(r, icp, today) for r in kept):
        status = _status(row, offline)
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
        "mode": "offline" if offline else "live:" + source_name,
        "rows_in": rows_in,
        "deduped": len(dupes),
        "suppressed": len(suppressed),
        "off_icp": len(off_icp),
        "accounts": accounts,
        "invalid": len(bad),
        "catch_all": len(held),
        "live": len(live),
        "credits_spent": 0 if offline or not enrich else "",
        "seconds": round(time.time() - started, 2),
    }
    run_log.append(**stats)
    return stats, rejects
