"""Optional second source: an Apify actor. Off until configured.

No actor ships configured. Most job scraping actors target sites whose
terms forbid scraping (LinkedIn, Indeed, Glassdoor), so choosing one is
a deliberate decision recorded in config/apify.yaml, not a default.
"""
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import env

CONFIG = Path(__file__).resolve().parent.parent / "config" / "apify.yaml"
NF = "Not found"
FIELDS = ["company", "domain", "employee_count", "techstack", "signal_date",
          "signal_url", "signal_text", "first_name", "last_name", "title",
          "linkedin_url", "email"]


def load_config(path=CONFIG):
    import yaml
    p = Path(path)
    cfg = yaml.safe_load(p.read_text(encoding="utf-8-sig")) if p.exists() else {}
    cfg = cfg or {}
    if not cfg.get("actor"):
        raise SystemExit(
            "Apify source is off: no actor set in config/apify.yaml. Pick an "
            "actor whose target site allows automated access, set actor, "
            "input, field_map and max_charge_usd, then rerun. The default "
            "live source is --source boards.")
    for need in ("field_map", "max_charge_usd"):
        if not cfg.get(need):
            raise SystemExit("config/apify.yaml needs {0}.".format(need))
    return cfg


def source(icp, record_dir=None, config_path=CONFIG):
    cfg = load_config(config_path)
    token = env.require("APIFY_TOKEN", "Add it to .env or use --source boards.")
    actor = cfg["actor"].replace("/", "~")
    query = urllib.parse.urlencode({
        "maxItems": int(cfg.get("max_items", 100)),
        "maxTotalChargeUsd": float(cfg["max_charge_usd"]),
    })
    url = "https://api.apify.com/v2/acts/{0}/run-sync-get-dataset-items?{1}".format(actor, query)
    req = urllib.request.Request(
        url, data=json.dumps(cfg.get("input") or {}).encode("utf-8"), method="POST",
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            items = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SystemExit("Apify actor {0} returned HTTP {1}. Nothing was "
                         "written.".format(cfg["actor"], e.code))
    except (urllib.error.URLError, ValueError) as e:
        raise SystemExit("Apify actor {0} failed: {1}".format(cfg["actor"], e))
    if not isinstance(items, list):
        raise SystemExit("Apify returned {0}, expected a list of items.".format(type(items).__name__))
    if record_dir:
        Path(record_dir).mkdir(parents=True, exist_ok=True)
        (Path(record_dir) / "apify_raw.json").write_text(json.dumps(items), encoding="utf-8")
    fmap = cfg["field_map"]
    rows = []
    for i, item in enumerate(items):
        row = {f: item.get(fmap[f]) if fmap.get(f) else None for f in FIELDS}
        row = {k: (v if v not in (None, "") else NF) for k, v in row.items()}
        row.update({"account_id": "apify:{0}".format(i), "signal_type": "job_post",
                    "source": "apify:" + cfg["actor"]})
        rows.append(row)
    return rows
