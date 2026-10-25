# QA

## 1. What was tested, where, when, by whom

| | |
| --- | --- |
| What | The offline pipeline (both segments), the dash lint, the seven graded rules, determinism, a clean install, and one live run against public job boards |
| Commit | bce1b75 (QA evidence re-run at this commit) |
| Date | 25 Oct 2026 |
| Machine | Windows 11 Home Single Language 10.0.26300, Git Bash |
| Python | 3.14.7, with PyYAML 6.0.3 and pytest 9.1.1, the versions pinned in requirements.txt |
| By | Claude Code (claude-opus-5-5), directed by the repo owner (github.com/whysaurabhsharma) |

## 2. Three commands from a clean checkout

After `git clone https://github.com/whysaurabhsharma/inboxkit-outbound.git`
and `cd inboxkit-outbound`, type exactly:

```
pip install -r requirements.txt
python run.py run
python -m pytest tests -q
```

Expected: the run prints 100 rows in and 39 live; the tests print
`46 passed`. No API keys and no network after the install. Nothing is
sent; the run writes CSVs to `data/out`.

## 3. The seven graded rules

Command: `python run.py run` then `python src/check_rules.py --live`.
The script reports and never fixes. Its exit code is the number of
failing rules. **Exit code at bce1b75: 0, all seven pass.**

| Rule | Result | Proof |
| --- | --- | --- |
| 1 Claims from inboxkit.com, page linked | Pass | 8 IDs used in messages (C01, C04, C07, C08, C09, C10, P02, P03); each resolves to a claims.md row on inboxkit.com and each URL returned HTTP 200. Every figure in a line that cites an ID appears in that claim's text; a seeded wrong figure is caught |
| 2 No em or en dashes | Pass | `python src/lint_copy.py` exit code 0 across copy/ and 01-memo/ |
| 3 One ask per message | Pass | 6 email bodies: 1 question mark and 1 CTA each, ending on the CTA. LinkedIn: connection note 1 question (connect), follow-up 1 none, follow-up 2 one |
| 4 Working opt-out | Pass | All 6 email bodies carry "Reply no to stop." and `{{unsubscribe_link}}`. `suppress --add` is documented in README.md, RULES.md, CLAUDE.md and copy/sequence.md, and on a temp copy of the list it adds an address that is then suppressed |
| 5 No competitor named | Pass | Smartlead and Instantly: 0 mentions in copy/. The 7 competitors in config/suppression.csv: 0 hits |
| 6 Prospect facts sourced or Not found | Pass | leads.csv: no empty cell in 39 rows; techstack and employee_count read "Not found" in 39 of 39. first_lines.csv (10) and first_lines_full.csv (25): every row has a source URL |
| 7 Nothing gets sent | Pass | .env.example has no sequencer key. export.py writes with csv.DictWriter and imports no network module. No smtplib, sendmail or sequencer API in src/ |

Rule 6 failed on the first run (empty first_line and prompt_version
columns; techstack and employee_count values with no source). Both
were fixed by filling first lines from copy/first_lines.csv and
setting the two fields to "Not found". No source was invented.

## 4. Determinism

Offline runs count signal age back from `data/fixtures/as_of.json`
(25 Oct 2026), not from today.

| Demo | Clock faked to 1 Jan 2030 |
| --- | --- |
| `python run.py run` | 5 of 5 output CSVs byte identical |
| `python run.py run --icp config/icp_jobchangers.yaml --limit 20` | 5 of 5 output CSVs byte identical |

`run_log.csv` is the exception by design: it records the real run time.

## 5. Clean install

A fresh venv with no `yaml` module, then
`pip install --no-cache-dir -r requirements.txt` at bce1b75:

| Step | Result |
| --- | --- |
| Install | PyYAML 6.0.3 and pytest 9.1.1, no build step, no error |
| Primary demo | 100 in, 39 live |
| Job-changer demo | 15 in, 6 live |
| Tests | 46 passed |
| Dash lint | Passed |

The venv was deleted afterwards. This was the same machine, not a
second one; see section 9.

## 6. Not tested

- **No second physical machine.** Every result above is from one
  Windows laptop. Section 9 is for that test.
- **make is not installed here.** The Makefile was checked by reading
  its bytes (7 recipe lines, each starting with a tab, LF endings), not
  by running it.
- **Prospeo has never run against the live API.** `src/enrich_prospeo.py`
  follows Prospeo's documented request shapes but no request has been
  sent. No contacts or emails exist for the 2 real accounts.
- **Apify has never been configured.** `--source apify` refuses to run
  because config/apify.yaml names no actor.
- **The first-line API runner has never run.** `python run.py first-lines`
  needs the anthropic package and a key, neither present here. The 25
  lines in copy/ were produced by Claude Code applying the skill.

## 7. Known limits

- **Tier A is unreachable.** No free source gave headcount or
  techstack for these accounts, so the size (15) and techstack (25)
  points never apply. The maximum score is 60 and tier A starts at 70.
  All 39 leads are tier B: 14 at 60, 25 at 45.
- **The tier thresholds were left alone on purpose.** They were not
  re-based to make the output look better. A tier here reflects signal
  and title only until headcount and techstack can be sourced.
- **The sheet is a labelled hybrid dry run:** 2 live_board accounts
  and 98 synthetic_dry_run rows. The live run found 2 qualifying
  agencies from 6 approved boards (config/sourcing_findings.md).
- **The 5 to 50 size band is stated, not applied,** because no source
  gives headcount.
- **check_rules.py limits:** rule 1 verifies lines that cite an ID, so
  an untagged product claim would need a human read (the copy was read;
  the only untagged statement is the offer from config/segment.md).
  Rule 6 treats signal_url and linkedin_url as the sources; it does not
  trace each field to its own URL.
- **The rule 10 field check knows a fixed list of tool names.** A tool
  outside the list would pass the checker.

## 8. Secrets scrub

Scanned the full git history (all commits, diffs and messages) and the
working tree, including gitignored files, on 25 Oct 2026.

| Check | Result |
| --- | --- |
| API keys, tokens, private keys | None in history or in any tracked file |
| .env | Gitignored, never committed. Holds one non-empty value locally (APIFY_TOKEN); stays on this machine |
| Phone numbers | None found |
| Recorded live data (data/fixtures/live) | Gitignored, never committed; contains no email addresses |

Open, waiting on the repo owner's decision (history not rewritten):

- The commit author email on 24 commits is a personal address. It is
  visible to anyone who can read the repo. Removing it means rewriting
  history and force pushing.
- Two early commits (e1993b0, c298597) contain made-up contact emails
  at two real InboxKit customer domains, plus made-up addresses at
  other domains that may be registered. They were removed from the
  working tree in 544ca6a but remain in history.

## 9. Clean machine run (to be filled in on a second computer)

- Date:
- Machine and OS:
- Python version:
- Commit:
- `pip install -r requirements.txt`:
- `python run.py run`:
- `python -m pytest tests -q`:
- Notes:
