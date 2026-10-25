# CLAUDE.md

How to work in this repo.

## What it does

One YAML segment file in, five CSVs out (plus run_log.csv). Deterministic apart from
two judgment steps that call Claude: qualify-account and
first-line. Everything else is plain Python so it runs identically
on any machine.

## Never

- Never send an email. This repo writes CSVs. There is no send path
  and no sequencer credential in .env.example.
- Never invent a fact about a prospect. If a field cannot be
  sourced, write "Not found".
- Never write a product claim that is not a row in
  config/claims.md with a live inboxkit.com URL.
- Never use an em dash or en dash in anything under copy/ or
  01-memo/. The lint will fail the build.
- Never put more than one ask in a message.
- Never name a competitor in copy.

## Commands

| Command | What it does |
| --- | --- |
| python run.py run | Offline demo on fixtures |
| python run.py run --live --record | Live from public job boards, free |
| python run.py run --live --enrich | Adds Prospeo contacts, spends credits |
| python run.py probe --names "A,b.com" | Find boards, writes candidates only |
| python run.py suppress --add X --reason opt_out | Honour an opt-out |
| python run.py report | Monday review |
| python -m pytest tests -q | Tests |
| python src/lint_copy.py | Dash lint |

## Layout

- config/ icp.yaml, suppression.csv, claims.md, segment.md,
  boards.csv (approved boards), boards_candidates.csv, apify.yaml
- src/ one module per pipeline stage
- skills/ the two Claude prompts, in readable markdown
- data/fixtures/ recorded responses so demo runs offline; companies.json
  is the hybrid dry run (2 live_board + 98 synthetic_dry_run rows),
  rebuilt by make_synthetic.py
- data/out/ generated, gitignored
- copy/ the sequence and LinkedIn messages
- tests/ thirty-nine tests covering dedupe, suppression, verification,
  ICP filters, the frozen demo date, the live sources (offline) and
  the data_source labelling

## Adding a segment

Copy config/icp.yaml, change the signal and title keywords, run
with --icp pointing at the new file. Do not add code for a new
segment.

## Reading CSVs

Always open with encoding="utf-8-sig". Files written on Windows
carry a BOM and the first column header will not match otherwise.
