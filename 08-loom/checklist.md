# Loom checklist

## Close first

- `.env`. It holds a live APIFY_TOKEN. Do not open it on screen.
- The folder holding `inboxkit-outbound-pre-rewrite-2026-10-25.bundle`
  and any terminal showing `git log` on the backup branch. Both carry
  the old history.
- Email, Slack and calendar. Turn on Do Not Disturb.
- Browser tabs not in this list, especially HubSpot, Clay, Google
  Drive and anything logged in with a personal account.
- Any VS Code tab not in the list below.

## Check before recording

Run these once, off camera, in the repo root:

```
git status
python -m pytest tests -q
python run.py run
python run.py sheet
```

- `git status` shows a clean tree. config/icp.yaml must read
  `lookback_days: 90`.
- Tests pass (48).
- The run prints 100 in and 39 live.
- `python run.py sheet` writes data/out/inboxkit-leads.xlsx.

## Open, in this order

1. **01-memo/strategy-memo.md** in markdown preview, scrolled to the top.
   (0:00, then 0:20 for the math table.)
2. **Terminal** in the repo root, font size raised, cleared with `cls`
   or `clear`. (1:00)
3. **VS Code tabs**, left to right, with line numbers on:
   - data/out/rejects.csv (lines 2 and 33)
   - data/out/suppressed.csv (line 2)
   - config/suppression.csv (line 2)
   - config/icp.yaml, cursor on `lookback_days: 90` (2:30)
4. **The workbook**, data/out/inboxkit-leads.xlsx in Excel, or the
   committed 02-lead-list/inboxkit-leads.xlsx imported into Google
   Sheets. Open on the Needs contact tab. (3:15)
5. **QA.md** in markdown preview, scrolled to section 3. (3:45)
6. **copy/sequence.md** in markdown preview, scrolled to "Email 3: the
   money". (4:00)
7. **The workbook again**, switched to the Read me tab. (4:45)
8. **config/scale.md** in markdown preview, scrolled to "First change
   with a budget". (4:50)

## After recording

- `git checkout config/icp.yaml` if the 2:30 edit was not reverted on
  camera, then `git status` to confirm a clean tree.
- `python run.py run` so data/out is back to the 39-lead run.
