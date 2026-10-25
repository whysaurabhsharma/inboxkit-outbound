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
| `python -m pytest tests -q` | 20 passed |
| `python src/lint_copy.py` | Passed, exit 0 |
| `python run.py run` | 10 in, 2 deduped, 1 suppressed, 0 off ICP, 2 bad email, 1 held, 4 live |
| `python run.py run --icp config/icp_jobchangers.yaml --limit 20` | 15 in, 1 deduped, 1 suppressed, 3 off ICP, 3 bad email, 1 held, 6 live |
| Both demos rerun with the clock faked to 1 Jan 2030 | leads, rejects, suppressed and held CSVs byte identical |
| Makefile | All 7 recipe lines start with a tab (0x09), no BOM, LF endings; every target calls a file that exists |

Offline runs count signal age back from `data/fixtures/as_of.json`
(25 Oct 2026), so the demo output does not drift. `run_log.csv`
still records the real run time and duration.

## Clean machine run

- Date:
- Machine and OS:
- Python version:
- Result of the three commands above:
- Notes:
