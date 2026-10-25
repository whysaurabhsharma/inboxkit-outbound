"""Check every graded rule in RULES.md against the files. Reports, never fixes.

    python src/check_rules.py            # offline checks
    python src/check_rules.py --live     # also fetch each cited claim URL

Run python run.py run first so data/out/leads.csv exists. Exit code is
the number of rules that failed.
"""
import csv
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
COPY = ROOT / "copy"
NF = "Not found"
CTA = "Worth 30 minutes to size and price the mailboxes?"
OPT_OUT = "Reply no to stop."
TAG = "{{unsubscribe_link}}"
ID = re.compile(r"\b[CP]\d{2}\b")


def claims_register():
    """ID -> (claim text, URL) from config/claims.md."""
    out = {}
    for line in (ROOT / "config" / "claims.md").read_text(encoding="utf-8-sig").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and ID.fullmatch(cells[0]):
            out[cells[0]] = (cells[1], cells[2])
    return out


def emails():
    """(title, body) for every email in copy/sequence.md; body is after Subject."""
    text = (COPY / "sequence.md").read_text(encoding="utf-8")
    out = []
    for block in re.split(r"\n#{2,3} ", text):
        m = re.search(r"^Subject: .+$", block, re.M)
        if m:
            body = block[m.end():].split("\n## ")[0].strip()
            out.append((block.splitlines()[0].strip(), body))
    return out


def linkedin_messages():
    text = (COPY / "linkedin.md").read_text(encoding="utf-8")
    out = []
    for block in re.split(r"\n## ", text)[1:]:
        title = block.splitlines()[0].strip()
        if title.startswith(("Connection", "Follow-up")):
            # The message is every line after the one line description.
            lines = [l for l in block.splitlines()[1:] if l.strip()]
            out.append((title, "\n".join(lines[1:])))
    return out


def rule1(live):
    reg = claims_register()
    # Claims are what a prospect reads: email bodies and LinkedIn messages.
    used = {}
    for title, body in emails() + linkedin_messages():
        for cid in ID.findall(body):
            used.setdefault(cid, []).append(title)
    noted = set()
    for p in sorted(COPY.glob("*.md")):
        noted |= set(ID.findall(p.read_text(encoding="utf-8")))
    noted -= set(used)
    problems = []
    rows = []
    for cid in sorted(used):
        if cid not in reg:
            problems.append("{0} used in {1} but not in claims.md".format(cid, used[cid]))
            continue
        url = reg[cid][1]
        status = "not fetched"
        if not url.startswith("https://www.inboxkit.com"):
            problems.append("{0} source is not inboxkit.com: {1}".format(cid, url))
        if live:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    status = str(r.status)
            except Exception as e:
                status = "failed: {0}".format(getattr(e, "code", e))
                problems.append("{0} URL {1} {2}".format(cid, url, status))
        rows.append("{0} -> {1} [{2}] used at {3}".format(cid, url, status, ", ".join(used[cid])))
    if noted:
        rows.append("IDs named only in notes or source tables, not in any message: " + ", ".join(sorted(noted)))
    # Numbers in a line that cites IDs must appear in those claims' text.
    for title, body in emails():
        for line in body.split("\n\n"):
            ids = ID.findall(line)
            if not ids:
                continue
            claim_text = " ".join(reg.get(i, ("", ""))[0] for i in ids).lower()
            for num in re.findall(r"\$?\d+(?:[.,]\d+)?k?", ID.sub("", line).lower()):
                if num.strip("$") not in claim_text.replace("$", ""):
                    problems.append("{0}: '{1}' not in {2}".format(title, num, ids))
    return problems, rows


def rule2():
    r = subprocess.run([sys.executable, str(ROOT / "src" / "lint_copy.py")],
                       capture_output=True, text=True)
    out = r.stdout.strip().splitlines()
    return ([] if r.returncode == 0 else out), ["exit code {0}: {1}".format(r.returncode, out[0])]


def rule3():
    problems, rows = [], []
    for kind, msgs in (("email", emails()), ("linkedin", linkedin_messages())):
        for title, body in msgs:
            q, cta = body.count("?"), body.count(CTA)
            rows.append("{0} | {1}: {2} question mark(s), {3} CTA".format(kind, title, q, cta))
            if q > 1 or cta > 1:
                problems.append("{0} has {1} questions, {2} CTAs".format(title, q, cta))
            if kind == "email" and (q != 1 or cta != 1 or not body.split(OPT_OUT)[0].rstrip().endswith(CTA)):
                problems.append("{0} does not end with the single CTA before the opt-out".format(title))
    return problems, rows


def rule4():
    problems, rows = [], []
    for title, body in emails():
        ok = OPT_OUT in body and TAG in body
        rows.append("{0}: opt-out line {1}, merge tag {2}".format(
            title, "yes" if OPT_OUT in body else "NO", "yes" if TAG in body else "NO"))
        if not ok:
            problems.append(title + " lacks the opt-out line or merge tag")
    docs = [p for p in ("README.md", "RULES.md", "CLAUDE.md", "copy/sequence.md")
            if "suppress --add" in (ROOT / p).read_text(encoding="utf-8-sig")]
    rows.append("suppress --add documented in: " + ", ".join(docs))
    if not docs:
        problems.append("suppress --add is not documented")
    # Prove the command path works on a copy of the list, not the real one.
    import suppress
    tmp = Path(tempfile.mkdtemp()) / "suppression.csv"
    shutil.copy(ROOT / "config" / "suppression.csv", tmp)
    added = suppress.add("someone@agency.example", "opt_out", str(tmp))
    kept, supp = suppress.apply([{"domain": "agency.example", "email": "someone@agency.example"}], str(tmp))
    rows.append("suppress.add on a temp copy: added={0}, then apply suppressed {1} of 1".format(added, len(supp)))
    if not (added and len(supp) == 1):
        problems.append("suppress --add did not suppress the address")
    return problems, rows


def rule5():
    problems, rows = [], []
    competitors = []
    with open(ROOT / "config" / "suppression.csv", newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            if r["reason"] == "competitor":
                competitors.append(r["domain"].split(".")[0])
    for p in sorted(COPY.glob("*")):
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for name in ("smartlead", "instantly"):
                if name in line.lower():
                    rows.append("{0}:{1} mentions {2}: {3}".format(p.name, n, name, line.strip()[:100]))
            for c in competitors:
                if c in line.lower():
                    problems.append("{0}:{1} names competitor {2}".format(p.name, n, c))
    if not any("mentions" in r for r in rows):
        rows.append("Smartlead and Instantly: 0 mentions in copy/")
    rows.append("competitors checked: " + ", ".join(competitors) + "; hits: " +
                str(sum("competitor" in x for x in problems)))
    return problems, rows


def rule6():
    problems, rows = [], []
    leads = ROOT / "data" / "out" / "leads.csv"
    with open(leads, newline="", encoding="utf-8-sig") as fh:
        data = list(csv.DictReader(fh))
    empty = {}
    for r in data:
        for k, v in r.items():
            if not v.strip():
                empty[k] = empty.get(k, 0) + 1
        if not r.get("signal_url", "").startswith("https://"):
            problems.append("{0} has no signal source URL".format(r["account_id"]))
    for k, n in empty.items():
        problems.append("leads.csv column {0}: {1} of {2} cells empty, neither a value nor Not found".format(k, n, len(data)))
    for col in ("techstack", "employee_count"):
        valued = sum(1 for r in data if r[col].strip() and r[col] != NF)
        if valued:
            problems.append("leads.csv column {0}: {1} of {2} rows carry a value with no source URL for it".format(
                col, valued, len(data)))
    rows.append("leads.csv: {0} rows checked".format(len(data)))
    for name in ("first_lines.csv", "first_lines_full.csv"):
        lines = (COPY / name).read_text(encoding="utf-8").splitlines()
        fl = list(csv.DictReader(lines[1:]))
        bad = [r["account_id"] for r in fl if not r["source_url"].startswith("https://")
               and r["first_line"] != NF]
        rows.append("{0}: {1} rows, {2} without a source URL".format(name, len(fl), len(bad)))
        problems += ["{0} {1} has no source URL".format(name, a) for a in bad]
    return problems, rows


def rule7():
    problems, rows = [], []
    env = (ROOT / ".env.example").read_text(encoding="utf-8-sig")
    keys = re.findall(r"^([A-Z_]+)=", env, re.M)
    rows.append(".env.example keys: " + ", ".join(keys))
    seq = [k for k in keys if any(s in k for s in ("SMARTLEAD", "INSTANTLY", "LEMLIST", "SEQUENC", "SMTP", "GMAIL"))]
    if seq:
        problems.append("sequencer credential in .env.example: " + ", ".join(seq))
    export = (ROOT / "src" / "export.py").read_text(encoding="utf-8-sig")
    net = [w for w in ("urllib", "requests", "smtplib", "socket", "http") if w in export]
    rows.append("export.py: writes via csv.DictWriter only; network modules referenced: " + (", ".join(net) or "none"))
    if net:
        problems.append("export.py references " + ", ".join(net))
    hits = []
    for p in sorted((ROOT / "src").glob("*.py")):
        if p.name == "check_rules.py":
            continue  # this file lists the search terms
        t = p.read_text(encoding="utf-8-sig").lower()
        for w in ("smtplib", "sendmail", "smartlead.ai", "instantly.ai", "/campaigns"):
            if w in t:
                hits.append("{0}: {1}".format(p.name, w))
    rows.append("send paths in src/ (smtplib, sendmail, sequencer APIs): " + (", ".join(hits) or "none"))
    if hits:
        problems += hits
    return problems, rows


def main():
    live = "--live" in sys.argv
    rules = [("1 Claims from inboxkit.com, page linked", lambda: rule1(live)),
             ("2 No em or en dashes", rule2), ("3 One ask per message", rule3),
             ("4 Working opt-out", rule4), ("5 No competitor named", rule5),
             ("6 Prospect facts sourced or Not found", rule6), ("7 Nothing gets sent", rule7)]
    failed = 0
    for name, fn in rules:
        problems, rows = fn()
        print("Rule {0}: {1}".format(name, "PASS" if not problems else "FAIL"))
        for r in rows:
            print("  " + r)
        for p in problems:
            print("  FAIL: " + p)
        failed += bool(problems)
    return failed


if __name__ == "__main__":
    sys.exit(main())
