# inboxkit-outbound

One YAML file describing a segment goes in. A sequencer-ready CSV
comes out, with every rejected row logged and a reason beside it.

Nothing is ever sent. This repo writes CSVs and has no sequencer
credentials.

## Run it

Five commands, from a clean checkout, no API keys needed.

```
git clone https://github.com/whysaurabhsharma/inboxkit-outbound.git
cd inboxkit-outbound
pip install -r requirements.txt
python run.py run
python -m pytest tests -q
```

With make available, those are `make setup`, `make demo` and
`make test`.

The demo runs on recorded fixtures in `data/fixtures`, so it needs
no network and no keys, and finishes in under a second. Signal age
counts back from the date in `data/fixtures/as_of.json`, not today,
so the output is identical whenever you run it. Run it
twice: the second run adds zero rows.

## What you get

The default demo is a labelled hybrid dry run of 100 rows: 2 real
agencies from the live board run and 98 synthetic ones. The
`data_source` column, straight after the brief's nine, says which
(`live_board` or `synthetic_dry_run`). See config/sourcing_findings.md
for why it is a hybrid. `data/fixtures/make_synthetic.py` rebuilds the
synthetic rows deterministically.

Six files land in `data/out`:

| File | What is in it |
| --- | --- |
| leads.csv | Verified-valid rows only, brief columns first, then data_source |
| rejects.csv | Duplicates, off-ICP rows and bad emails, each with a reason |
| suppressed.csv | Customers and competitors, with the rule matched |
| held.csv | Catch-all addresses, held back from live |
| needs_contact.csv | Accounts that passed every ICP check but have no verified contact yet: the enrichment queue |
| run_log.csv | One row per run: counts, credits, seconds |

## A new segment is one file and one command

```
python run.py run --icp config/icp_jobchangers.yaml --limit 20
```

## Honouring an opt-out

```
python run.py suppress --add someone@agency.example --reason opt_out
```

## The Monday review

```
python run.py report
```

## One sheet for Google Sheets

```
python run.py sheet
```

Writes `data/out/inboxkit-leads.xlsx`: a Read me tab, then Leads, Needs
contact, Held, Rejects, Suppressed and Run log, each with a bold frozen
header. Upload it to Google Sheets with File > Import.

A built copy is committed at `02-lead-list/inboxkit-leads.xlsx`. It is
a snapshot of one run; regenerate it with
`python run.py run && python run.py sheet --out 02-lead-list/inboxkit-leads.xlsx`.

## Live mode

```
python run.py run --live --record
```

Live sourcing reads the public job board APIs (Greenhouse, Lever,
Ashby, Workable, Recruitee) for every agency in `config/boards.csv`.
No keys, no cost, no scraping. Any failed call stops the run; it
never falls back to the demo fixtures. `--record` saves the responses
to `data/fixtures/live/<date>/` (gitignored, since it holds real
data) so the run replays offline.

Boards only list companies and job posts, so live rows have no
contact until `--enrich` finds one with Prospeo (spends credits,
needs `PROSPEO_API_KEY`). Prospeo's verified status is the
verification result; BounceBan is only asked about catch-alls.

To find boards for more agencies:

```
python run.py probe --names "Agency One,agencytwo.com"
```

Hits land in `config/boards_candidates.csv`. Copy the ones you have
checked into `config/boards.csv`; nothing gets there automatically.

`--source apify` exists but is off until `config/apify.yaml` names an
actor.

## First lines

`copy/first_lines_full.csv` holds 25 first lines produced by Claude
Code applying `skills/first-line/SKILL.md` to rows of
`data/out/leads.csv`, each run through the checker in
`src/first_line.py`. All 25 passed, so the file has zero rejections;
none were invented. `copy/first_lines.csv` holds the 10 chosen from
them. The `generated_by` column and each file's first line say how
they were made.

For volume, `python run.py first-lines` runs the same skill through
the Anthropic API (needs `pip install anthropic` and
`ANTHROPIC_API_KEY`) and overwrites the file.

## Rules

See RULES.md. The dash rule is a lint, not a promise:
`python src/lint_copy.py` exits non-zero on any em or en dash in
`copy/` or `01-memo/`.
