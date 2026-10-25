"""Read .env into os.environ. No dependency, never overrides the shell."""
import os
from pathlib import Path

ENV = Path(__file__).resolve().parent.parent / ".env"


def load(path=ENV):
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if value and key not in os.environ:
            os.environ[key] = value


def require(key, what_to_do):
    """Return the key's value or stop with a message saying how to fix it."""
    load()
    value = os.environ.get(key)
    if not value:
        raise SystemExit("{0} is not set. {1}".format(key, what_to_do))
    return value
