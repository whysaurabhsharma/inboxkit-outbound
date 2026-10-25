import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import suppress
import verify

SUPP = str(ROOT / "config" / "suppression.csv")


def test_seeded_list_loads():
    domains, _ = suppress.load(SUPP)
    assert len(domains) > 20


def test_customer_domain_suppressed():
    rows = [{"domain": "vectify.io", "email": "a@vectify.io"}]
    kept, supp = suppress.apply(rows, SUPP)
    assert kept == []
    assert supp[0]["reason"] == "customer"


def test_competitor_domain_suppressed():
    rows = [{"domain": "www.zapmail.ai", "email": "b@zapmail.ai"}]
    kept, supp = suppress.apply(rows, SUPP)
    assert kept == []
    assert supp[0]["reason"] == "competitor"


def test_unrelated_domain_survives():
    rows = [{"domain": "someagency.com", "email": "c@someagency.example"}]
    kept, supp = suppress.apply(rows, SUPP)
    assert len(kept) == 1
    assert supp == []


def test_role_addresses_never_go_live():
    assert verify.verify("info@acme.example") == "role"
    assert verify.verify("sales@acme.example") == "role"


def test_malformed_address_is_invalid():
    assert verify.verify("not-an-email") == "invalid"
    assert verify.verify("") == "invalid"


def test_unseen_address_is_unknown_not_valid():
    assert verify.verify("someone@unseen-domain.com") == "unknown"
