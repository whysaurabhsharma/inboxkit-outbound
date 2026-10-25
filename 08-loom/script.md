# Loom script, under 5 minutes

Three pauses are marked **[PAUSE]**: stop talking and let the screen
carry it for two to three seconds. Elapsed time is cumulative. Counts
below come from the committed fixtures and do not change between runs.

## 0:00 to 0:20 · The bet

**On screen:** 01-memo/strategy-memo.md, top of the page, "The bet".

**Say:**
> InboxKit should go after outbound agencies of 5 to 50 people that
> posted an SDR or outbound role in the last 90 days. A hiring post is
> the most public, dated proof that their sending volume is about to
> change, and infrastructure gets bought when volume changes.

**Elapsed:** 0:20

## 0:20 to 1:00 · The memo

**On screen:** scroll to "The math, in your unit". Cursor on the EPP
row (227 and 425), then on the line under the table.

**Say:**
> Fifteen qualified demos need thirty positive replies, if half of them
> book. At a 1.5 percent positive rate that is 2,000 contacts and 6,800
> emails: 227 emails per demo. At the conservative 0.8 percent it is
> 3,750 contacts and 425 per demo. Both are under your 500.
>
> The number I trust least is that half of positive replies book. It is
> a clean number with nothing behind it, so it is the first one I would
> measure.

**Elapsed:** 1:00

## 1:00 to 2:30 · The repo running live

**On screen:** a cleared terminal in the repo root. Type:

```
python run.py run
```

**Say:**
> One command, no keys, no network. A hundred rows in: two real agencies
> from public job boards and ninety eight synthetic ones, labelled.

**[PAUSE]** on the printed counts: 100 in, 8 deduped, 8 suppressed,
21 off ICP, 39 live, and the line of reject reasons.

**On screen:** open data/out/rejects.csv. Point at line 2:
`S098, Quillcombe Leads, https://www.quillcombeleads.example/careers,
duplicate_of:S028`.

**Say:**
> This is a duplicate. Same company, entered as a www address with a
> careers path. It normalises to the same domain, so it is rejected and
> points at the row it duplicates.

**On screen:** scroll to line 33: `S057, team@ivoholtprospecting.example,
bad_email`, verification_status `role`.

**Say:**
> A role address. team@ never reaches the lead list, whatever the
> verifier says.

**On screen:** open data/out/suppressed.csv, line 2: `S087, customer,
synthetic dry-run customer`. Then open config/suppression.csv, line 2:
`vectify.io, customer, named on inboxkit.com homepage`.

**Say:**
> This run suppresses synthetic customers. The real list sits here: your
> customers, each with where it came from, this one off your homepage,
> plus the competitors from your compare pages.

**On screen:** back to the terminal. Type `python run.py run` again.

**Say:**
> Run it again. Identical output: same 39, same counts, same rows. Each
> run rewrites the files from the same inputs; it does not compare
> against the last run.

**Elapsed:** 2:30

## 2:30 to 3:15 · A new segment is a file

**On screen:** open config/icp.yaml. Change `lookback_days: 90` to
`lookback_days: 30`. Save. In the terminal:

```
python run.py run
git diff --stat
```

**Say:**
> One field: the signal window, 90 days down to 30. Same command.

**[PAUSE]** on the new counts: live 39 becomes 14, and signal_stale
goes from 8 to 58.

**Say:**
> Thirty nine leads become fourteen, and fifty eight rows are now
> rejected as stale, each with its reason. git diff shows one line
> changed and no code. A new segment is this file.

**On screen:** `git checkout config/icp.yaml`, then `python run.py run`
to restore 39.

**Elapsed:** 3:15

## 3:15 to 4:00 · The sheet

**On screen:** the workbook from `python run.py sheet`, open on the
Needs contact tab: Belkins and memoryBlue, real job URLs, every person
field "Not found", data_source `live_board`.

**Say:**
> The two real agencies. Their job posts are real and dated. Job boards
> do not name a contact, so every person field says Not found rather
> than a guess.

**[PAUSE]** on the Needs contact tab.

**On screen:** the Leads tab, data_source column (`synthetic_dry_run`)
and tier column (all B). Then QA.md, section 3, the paragraph starting
"Rule 6 failed on the first run".

**Say:**
> Every synthetic row says so. And here is what I got wrong. My own rule
> checker failed my first sheet: the synthetic rows carried headcount
> and techstack with no source. I set them to Not found instead of
> inventing one. That removed the size and techstack points, so tier A
> is now unreachable, and I left the thresholds where they were.

**Elapsed:** 4:00

## 4:00 to 4:45 · The copy

**On screen:** copy/sequence.md, "Email 3: the money". Then scroll to
"Claims used, with sources", rows C01 and C04.

**Say:**
> One email. Line one is their dated post. Line three is the Azure
> price, tagged C04 against C01. Every tag resolves to a row in the
> claims register with an inboxkit.com page. No links in the body, one
> question, the opt-out line.

**On screen:** terminal:

```
python src/lint_copy.py
```

**Say:**
> And the dash rule is a check, not a promise. It passes.

**Elapsed:** 4:45

## 4:45 to 4:50 · What I did not do

**On screen:** the workbook's Read me tab, rows "What this is" (sends
nothing), "Rows by source" (98 synthetic_dry_run) and "Spend" ($0).

**Say:**
> Nothing was sent. No credits spent. The 98 synthetic rows are
> labelled.

**Elapsed:** 4:50

## 4:50 to 4:58 · With a budget

**On screen:** config/scale.md, "First change with a budget".

**Say:**
> With a budget, I'd test a headcount-filtered company search on 100
> accounts before email credits: accounts are the bottleneck.

**Elapsed:** 4:58
