"""Run the first-line skill against rows of leads.csv. Never hand-written.

    python run.py first-lines --limit 10

Sends skills/first-line/SKILL.md as the system prompt and one contact
record per request, then checks each returned line against the skill's
own rules. A line that breaks one is kept with approved=no and the
reason, so a human sees what the model wrote. Writes copy/first_lines.csv.

Needs the anthropic package and ANTHROPIC_API_KEY. Stops if either is
missing rather than writing anything by other means.
"""
import csv
import re
from datetime import date
from pathlib import Path

import env

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "first-line" / "SKILL.md"
LEADS = ROOT / "data" / "out" / "leads.csv"
OUT = ROOT / "copy" / "first_lines.csv"
MODEL = "claude-opus-5-5"
COLUMNS = ["account_id", "first_line", "signal_fact_used", "source_url",
           "prompt_version", "approved", "rejection_reason"]
FLATTERY = ("i noticed", "i saw", "congrats", "love what", "hope this finds")
ADJECTIVES = ("impressive", "exciting", "great", "amazing", "incredible")
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def skill():
    text = SKILL.read_text(encoding="utf-8-sig")
    version = text.split("## Version", 1)[1].strip().splitlines()[0].strip()
    return text, version


def record(row):
    first = (row.get("name") or "").split(" ")[0]
    return "\n".join("{0}: {1}".format(k, v) for k, v in [
        ("first_name", first), ("company", row.get("company")),
        ("signal_type", row.get("signal_type")), ("signal_date", row.get("signal_date")),
        ("signal_url", row.get("signal_url")), ("signal_text", row.get("signal_text"))])


def check(line, row):
    """Return the first skill rule the line breaks, or None."""
    low = line.lower()
    if line == "Not found":
        return "no signal_url"
    if len(line.split()) >= 25:
        return "25 words or more"
    if "—" in line or "–" in line:
        return "em or en dash"
    if "?" in line:
        return "question"
    if low.startswith(FLATTERY):
        return "flattery opener"
    if any(re.search(r"\b" + a + r"\b", low) for a in ADJECTIVES):
        return "adjective"
    if "inboxkit" in low or "mailbox" in low:
        return "product claim"
    d = date.fromisoformat(row["signal_date"][:10])
    forms = ["{0} {1}".format(d.day, MONTHS[d.month - 1]),
             "{0} {1}".format(MONTHS[d.month - 1], d.day), d.isoformat()]
    if not any(f.lower() in low for f in forms):
        return "signal date missing"
    return None


def generate(row, client, system):
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=system,
        messages=[{"role": "user", "content": record(row)}],
    )
    if response.stop_reason == "refusal":
        return None, "model refused"
    text = next((b.text for b in response.content if b.type == "text"), "").strip()
    return text, None


def run(limit=10, leads=LEADS, out=OUT):
    env.load()
    try:
        import anthropic
    except ImportError:
        raise SystemExit("The anthropic package is not installed: pip install anthropic. "
                         "Nothing was written.")
    env.require("ANTHROPIC_API_KEY", "Add it to .env to run the first-line skill. "
                "Nothing was written.")
    if not Path(leads).exists():
        raise SystemExit("No {0}. Run python run.py run first.".format(leads))
    with open(leads, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))[:limit]
    system, version = skill()
    client = anthropic.Anthropic()
    results = []
    for row in rows:
        if not row.get("signal_url") or row["signal_url"] == "Not found":
            line, why = "Not found", "no signal_url"
        else:
            line, why = generate(row, client, system)
            why = why or check(line, row)
        results.append({
            "account_id": row.get("account_id"), "first_line": line or "",
            "signal_fact_used": "{0} | {1}".format(row.get("signal_text"), row.get("signal_date")),
            "source_url": row.get("signal_url"), "prompt_version": version,
            "approved": "no" if why else "yes", "rejection_reason": why or "",
        })
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(results)
    return results
