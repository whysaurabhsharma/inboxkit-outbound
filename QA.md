# QA

## Reviewer: three commands from a clean checkout

After `git clone` and `cd inboxkit-outbound`:

```
pip install -r requirements.txt
python run.py run
python -m pytest tests -q
```

No API keys, no network after install. Nothing is sent; the run
writes CSVs to `data/out`.

## Dev machine run

- Date: 25 Oct 2026
- Machine: Windows 11 Home Single Language 10.0.26300, Git Bash
- Python 3.14.7, PyYAML 6.0.3, pytest 9.1.1 (the tested versions,
  pinned in requirements.txt)
- make: not installed, so Makefile checked by reading it, not running it

| Check | Result |
| --- | --- |
| `pip install --no-cache-dir -r requirements.txt` into a fresh venv | Installed PyYAML 6.0.3 and pytest 9.1.1; demos and tests below pass inside it |
| `python -m pytest tests -q` | 46 passed |
| `python src/lint_copy.py` | Passed, exit 0 |
| `python run.py run` (hybrid: 2 live_board + 98 synthetic_dry_run) | 100 in, 8 deduped, 8 suppressed, 21 off ICP, 73 accounts, 2 need contact, 14 bad email, 8 held, 39 live |
| `python run.py run --icp config/icp_jobchangers.yaml --limit 20` | 15 in, 1 deduped, 1 suppressed, 3 off ICP, 3 bad email, 1 held, 6 live |
| Both demos rerun with the clock faked to 1 Jan 2030 | leads, rejects, suppressed and held CSVs byte identical |
| `python run.py run --live --record` (6 approved boards, 25 Oct 2026) | 6 boards read, 2 agencies with a fresh matching post (Belkins, memoryBlue), 4 with no open jobs, 0 live rows (no contacts without `--enrich`) |
| Replay of that recording offline | Same counts |
| Makefile | All 7 recipe lines start with a tab (0x09), no BOM, LF endings; every target calls a file that exists |

Offline runs count signal age back from `data/fixtures/as_of.json`
(25 Oct 2026), so the demo output does not drift. `run_log.csv`
still records the real run time and duration.

## Graded rules (RULES.md), checked 25 Oct 2026

Command: `python run.py run` then `python src/check_rules.py --live`.
The script reports and never fixes; its exit code is the number of
failing rules. First run: exit 1, six rules pass, rule 6 fails. After
the fixes below: exit 0, all seven pass.

| Rule | Result | Evidence |
| --- | --- | --- |
| 1 Claims from inboxkit.com, page linked | Pass | 8 IDs used in messages (C01, C04, C07, C08, C09, C10, P02, P03); each resolves to a claims.md row on inboxkit.com, and each URL returned HTTP 200. Every figure in a line that cites an ID appears in that claim's text (a test that seeds a wrong figure is caught). P01, P04, P06 appear only in the note explaining why they are not used |
| 2 No em or en dashes | Pass | `python src/lint_copy.py` exit code 0 across copy/ and 01-memo/ |
| 3 One ask per message | Pass | Each of the 6 email bodies: 1 question mark, 1 CTA, ending on the CTA before the opt-out. LinkedIn: connection note 1 question (connect), 0 CTA; follow-up 1: 0 and 0; follow-up 2: 1 and 1 |
| 4 Working opt-out | Pass | All 6 email bodies carry "Reply no to stop." and `{{unsubscribe_link}}`. `suppress --add` is documented in README.md, RULES.md, CLAUDE.md and copy/sequence.md. `suppress.add` on a temp copy of the list added the address and `suppress.apply` then suppressed it |
| 5 No competitor named | Pass | Smartlead and Instantly: 0 mentions in copy/. The 7 competitor names from config/suppression.csv: 0 hits |
| 6 Prospect facts sourced or Not found | Pass after fix | leads.csv: no empty cell in 39 rows; techstack and employee_count read "Not found" in 39 of 39. first_lines.csv (10 rows) and first_lines_full.csv (25 rows): every row has a source URL |
| 7 Nothing gets sent | Pass | .env.example holds APIFY_TOKEN, CLAY_API_KEY, PROSPEO_API_KEY, BOUNCEBAN_API_KEY, ANTHROPIC_API_KEY, no sequencer key. export.py uses csv.DictWriter and imports no network module. No smtplib, sendmail or sequencer API in src/ |

Rule 6 failures found on the first run, and how they were fixed:

1. leads.csv `first_line` and `prompt_version` were empty in 39 of 39
   rows. The pipeline now fills them from approved rows of
   copy/first_lines.csv, matched on account_id: 10 filled, 29 read
   "Not found".
2. leads.csv `techstack` carried a value in 34 of 39 rows and
   `employee_count` in 39 of 39, with no source URL. Every synthetic
   row now reads "Not found" for both, as the 2 live_board rows did. No
   source URL was invented. Scores drop as a result: all 39 leads are
   tier B (14 at 60, 25 at 45), and tier A cannot be reached without
   those two fields. config/scale.md records this as a second
   bottleneck.

Limits of the check: rule 1 verifies lines that cite an ID; a product
claim written without an ID would not be flagged, so the copy was also
read by hand (the only untagged statement is the offer, "size and price
two ways", from config/segment.md). Rule 6 treats signal_url as the
source for signal facts and linkedin_url for person facts; it does not
trace each field to its own URL.

## Clean machine run

- Date:
- Machine and OS:
- Python version:
- Result of the three commands above:
- Notes:
