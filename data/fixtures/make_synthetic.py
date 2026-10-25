"""Build the hybrid dry-run fixture: 2 live board rows + 98 synthetic rows.

    python data/fixtures/make_synthetic.py

Deterministic (seeded), so rerunning gives identical files. Writes:
  companies.json              the 100 input rows
  companies_jobchangers.json  15 rows for config/icp_jobchangers.yaml
  suppression_synthetic.csv   made-up customers and opt-outs, offline only
  verify.json                 recorded verifier answers for synthetic emails

Every synthetic row is labelled data_source = synthetic_dry_run. Synthetic
companies and URLs use the reserved .example domain (RFC 2606), so none
can belong to a real company. Surnames are invented syllable pairs.
"""
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
AS_OF = date(2026, 10, 25)
SEED = 20261025

# Captured from the live run on 25 Oct 2026 (python run.py run --live --record)
# with the current title_keywords. Fields boards do not publish: Not found.
LIVE_ROWS = [
    {"account_id": "lever:belkins", "company": "Belkins", "domain": "belkins.io",
     "employee_count": "Not found", "techstack": "Not found", "signal_type": "job_post",
     "signal_date": "2026-10-09",
     "signal_url": "https://jobs.lever.co/belkins/bdec3922-de2c-44dd-a1c5-17a3f4acb9a6",
     "signal_text": "Business Development Representative (BDR) | US Market | Remote",
     "first_name": "", "last_name": "", "title": "Not found", "linkedin_url": "Not found",
     "email": "Not found", "source": "lever", "data_source": "live_board"},
    {"account_id": "greenhouse:memoryblue", "company": "memoryBlue", "domain": "memoryblue.com",
     "employee_count": "Not found", "techstack": "Not found", "signal_type": "job_post",
     "signal_date": "2026-10-20",
     "signal_url": "https://memoryblue.com/jobs/4723416006?gh_jid=4723416006",
     "signal_text": "Spanish Speaking Sales Development Representative - Boston (Immediate Start)",
     "first_name": "", "last_name": "", "title": "Not found", "linkedin_url": "Not found",
     "email": "Not found", "source": "greenhouse", "data_source": "live_board"},
]

# How many synthetic rows of each kind. Totals 98.
KINDS = {
    "valid": 39, "catch_all": 8, "invalid": 8, "role": 3, "unknown": 3,
    "stale": 8, "signal_mismatch": 3, "title_excluded": 6, "title_mismatch": 4,
    "customer": 6, "opt_out": 2, "duplicate": 8,
}

STEMS_A = ["Quill", "Bramb", "Thorn", "Vell", "Ost", "Marr", "Kest", "Fenn", "Lark",
           "Rook", "Wend", "Cind", "Brack", "Dorn", "Gald", "Harr", "Ivo", "Juno"]
STEMS_B = ["mere", "wick", "ford", "stead", "holt", "vane", "ridge", "combe"]
KINDS_OF_AGENCY = ["Outbound", "Leads", "Demand", "Pipeline", "Reach", "Growth",
                   "Outreach", "Prospecting"]
FIRST = ["Ana", "Ben", "Cleo", "Dev", "Ema", "Finn", "Gia", "Hugo", "Isla", "Jon",
         "Kai", "Lena", "Milo", "Nora", "Omar", "Pia", "Ravi", "Sara", "Theo", "Uma",
         "Vik", "Wren", "Yara", "Zane"]
SUR_A = ["Zib", "Quov", "Yrr", "Xan", "Vuth", "Pyx", "Glim", "Brev", "Nox", "Trel"]
SUR_B = ["dale", "quist", "worth", "mont", "holm", "ard", "ix", "enko"]

GOOD_TITLES = ["Founder", "Co-founder", "CEO", "Head of Growth", "Head of Outbound",
               "Head of Deliverability", "Operations Lead", "COO"]
EXCLUDED_TITLES = ["SDR Team Lead", "Account Executive", "Recruiter", "Marketing Intern",
                   "Senior Account Executive", "Founding SDR"]
MISMATCH_TITLES = ["Marketing Manager", "Office Manager", "Designer", "Finance Lead"]
SIGNALS = ["SDR", "Sales Development Representative", "Outbound Manager",
           "Cold Email Specialist", "Deliverability Lead", "Lead Generation Associate",
           "Business Development Representative", "Senior SDR"]
OFF_SIGNALS = ["Office Manager", "Graphic Designer", "Bookkeeper"]
STACKS = ["Smartlead", "Instantly", "Smartlead, Instantly", "Not found"]


def build():
    rng = random.Random(SEED)
    companies = rng.sample([a + b for a in STEMS_A for b in STEMS_B], 120)
    people = rng.sample([(f, a + b) for f in FIRST for a in SUR_A for b in SUR_B], 120)
    rows, verify, suppression = [], {}, []
    n = 0

    def base(kind):
        nonlocal n
        stem, agency = companies[n], rng.choice(KINDS_OF_AGENCY)
        first, last = people[n]
        n += 1
        domain = "{0}{1}.example".format(stem.lower(), agency.lower())
        slug = "{0}{1}".format(first, last).lower()
        fresh = kind != "stale"
        age = rng.randint(1, 85) if fresh else rng.randint(100, 200)
        # Drawn and discarded so the rest of the seeded sequence stays put:
        # no free source gives headcount or techstack, so both read Not found.
        rng.randint(5, 50) if rng.random() > 0.1 else rng.choice([3, 64, 90, 120])
        rng.choice(STACKS)
        return {
            "account_id": "S{0:03d}".format(n),
            "company": "{0} {1}".format(stem, agency),
            "domain": domain,
            "employee_count": "Not found",
            "techstack": "Not found",
            "signal_type": "job_post",
            "signal_date": (AS_OF - timedelta(days=age)).isoformat(),
            "signal_url": "https://jobs.example/{0}/{1}".format(domain.split(".")[0], 1000 + n),
            "signal_text": rng.choice(OFF_SIGNALS if kind == "signal_mismatch" else SIGNALS),
            "first_name": first, "last_name": last,
            "title": rng.choice(EXCLUDED_TITLES if kind == "title_excluded" else
                                MISMATCH_TITLES if kind == "title_mismatch" else GOOD_TITLES),
            "linkedin_url": "https://linkedin.example/in/{0}".format(slug),
            "email": "{0}@{1}".format(first.lower(), domain),
            "source": "synthetic",
            "data_source": "synthetic_dry_run",
        }

    for kind, count in KINDS.items():
        if kind == "duplicate":
            continue
        for _ in range(count):
            row = base(kind)
            if kind == "role":
                row["email"] = rng.choice(["info", "hello", "team"]) + "@" + row["domain"]
            elif kind == "customer":
                suppression.append({"domain": row["domain"], "email": "", "reason": "customer",
                                    "note": "synthetic dry-run customer"})
            elif kind == "opt_out":
                suppression.append({"domain": "", "email": row["email"], "reason": "opt_out",
                                    "note": "synthetic dry-run opt-out"})
            if kind in ("catch_all", "invalid"):
                verify[row["email"]] = kind
            elif kind not in ("role", "unknown"):
                verify[row["email"]] = "valid"
            row["_kind"] = kind
            rows.append(row)

    rng.shuffle(rows)
    originals = [r for r in rows if r["_kind"] == "valid"]
    for i, orig in enumerate(rng.sample(originals, KINDS["duplicate"])):
        dup = dict(orig)
        dup["account_id"] = "S{0:03d}".format(n + i + 1)
        if i % 2:
            dup["domain"] = "https://www.{0}/careers".format(orig["domain"])
        else:
            dup["company"] = orig["company"] + " LLC"
        at = rows.index(orig)
        rows.insert(rng.randint(at + 1, len(rows)), dup)

    for r in rows:
        r.pop("_kind", None)
    # Names the 100-row set never used, so the two fixtures cannot collide.
    return LIVE_ROWS + rows, verify, suppression, companies[n:], people[n:]


# Job-changer scenarios: (kind, start date, new title, techstack, headcount).
JOBCHANGERS = [
    ("valid", "2026-10-06", "Head of Growth", "Smartlead", 14),
    ("duplicate", None, None, None, None),
    ("valid", "2026-09-15", "Head of Outbound", "Instantly", 23),
    ("customer", "2026-10-01", "Head of Growth", "Instantly", 16),
    ("valid", "2026-10-19", "Founder", "Smartlead", 8),
    ("valid", "2026-08-22", "Co-founder", "Instantly", 31),
    ("role", "2026-10-12", "Head of Outbound", "Smartlead", 11),
    ("catch_all", "2026-09-03", "Head of Growth", "Instantly", 19),
    ("invalid", "2026-10-23", "Founder", "Smartlead", 6),
    ("stale", "2026-06-30", "Head of Growth", "Smartlead", 42),
    ("valid", "2026-09-29", "Head of Outbound", "Not found", 27),
    ("valid", "2026-10-08", "Co-founder", "Instantly", 64),
    ("unknown", "2026-10-15", "Head of Growth", "Instantly", 13),
    ("title_excluded", "2026-10-04", "Co-founder and Head of SDR", "Smartlead", 17),
    ("title_mismatch", "2026-10-04", "Growth Marketing Manager", "Smartlead", 17),
]


def build_jobchangers(companies, people):
    rows, verify, suppression = [], {}, []
    for i, (kind, start, title, stack, size) in enumerate(JOBCHANGERS):
        aid = "J{0:02d}".format(i + 1)
        if kind == "duplicate":
            prev = rows[-1]
            rows.append(dict(prev, account_id=aid, company=prev["company"] + " Ltd",
                             domain="https://www.{0}/team".format(prev["domain"])))
            continue
        stem, (first, last) = companies[i], people[i]
        agency = KINDS_OF_AGENCY[i % len(KINDS_OF_AGENCY)]
        domain = "{0}{1}.example".format(stem.lower(), agency.lower())
        profile = "https://linkedin.example/in/{0}{1}".format(first, last).lower()
        # J14 and J15: the contact found is not who the start signal names.
        signal_title = {"title_excluded": "Co-founder",
                        "title_mismatch": "Head of Outbound"}.get(kind, title)
        row = {
            "account_id": aid, "company": "{0} {1}".format(stem, agency), "domain": domain,
            "employee_count": "Not found", "techstack": "Not found", "signal_type": "job_change",
            "signal_date": start, "signal_url": profile,
            "signal_text": "Started as " + signal_title,
            "first_name": first, "last_name": last, "title": title,
            "linkedin_url": profile, "email": "{0}@{1}".format(first.lower(), domain),
            "source": "synthetic", "data_source": "synthetic_dry_run",
        }
        if kind == "role":
            row["email"] = "hello@" + domain
        elif kind == "customer":
            suppression.append({"domain": domain, "email": "", "reason": "customer",
                                "note": "synthetic dry-run customer"})
        if kind in ("catch_all", "invalid"):
            verify[row["email"]] = kind
        elif kind not in ("role", "unknown"):
            verify[row["email"]] = "valid"
        rows.append(row)
    return rows, verify, suppression


def _write_rows(path, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("[\n" + ",\n".join("  " + json.dumps(r, separators=(",", ":"))
                                    for r in rows) + "\n]\n")


def main():
    rows, synthetic_verify, suppression, spare_co, spare_people = build()
    assert len(rows) == 100, len(rows)
    jc_rows, jc_verify, jc_supp = build_jobchangers(spare_co, spare_people)
    synthetic_verify.update(jc_verify)
    suppression += jc_supp
    _write_rows(HERE / "companies.json", rows)
    _write_rows(HERE / "companies_jobchangers.json", jc_rows)
    with open(HERE / "suppression_synthetic.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["domain", "email", "reason", "note"])
        w.writeheader()
        w.writerows(suppression)
    vpath = HERE / "verify.json"
    verify = json.loads(vpath.read_text(encoding="utf-8-sig")) if vpath.exists() else {}
    # Keep answers for other fixtures, replace the synthetic ones.
    verify = {k: v for k, v in verify.items() if not k.endswith(".example")}
    verify.update(synthetic_verify)
    vpath.write_text(json.dumps(verify, indent=2) + "\n", encoding="utf-8")
    print("Wrote {0} + {1} rows, {2} synthetic suppressions, {3} verifier answers.".format(
        len(rows), len(jc_rows), len(suppression), len(synthetic_verify)))


if __name__ == "__main__":
    main()
