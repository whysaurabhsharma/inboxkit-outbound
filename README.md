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
no network and no keys, and finishes in under a second. Run it
twice: the second run adds zero rows.

## What you get

Five files land in `data/out`:

| File | What is in it |
| --- | --- |
| leads.csv | Verified-valid rows only, brief columns first |
| rejects.csv | Duplicates, off-ICP rows and bad emails, each with a reason |
| suppressed.csv | Customers and competitors, with the rule matched |
| held.csv | Catch-all addresses, held back from live |
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

## Live mode

Copy `.env.example` to `.env` and fill in keys, then add `--live`.
Without keys the verifier returns unknown rather than guessing, so
nothing unverified reaches leads.csv.

## Rules

See RULES.md. The dash rule is a lint, not a promise:
`python src/lint_copy.py` exits non-zero on any em or en dash in
`copy/` or `01-memo/`.
