"""Fails if an em dash or en dash appears in any graded text file."""
import sys
from pathlib import Path

BANNED = {"\u2014": "em dash (U+2014)", "\u2013": "en dash (U+2013)"}
TARGETS = ["copy", "01-memo"]
SUFFIXES = {".md", ".csv", ".txt", ".yaml", ".yml"}

def main() -> int:
    root = Path(__file__).resolve().parent.parent
    failures = []
    for target in TARGETS:
        base = root / target
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for lineno, line in enumerate(text.splitlines(), start=1):
                for char, label in BANNED.items():
                    if char in line:
                        rel = path.relative_to(root)
                        failures.append(f"{rel}:{lineno}: {label}")
    if failures:
        print("Dash lint failed:")
        for failure in failures:
            print("  " + failure)
        return 1
    print("Dash lint passed. No em dashes or en dashes found.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
