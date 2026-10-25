import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dedupe import normalise_domain, normalise_company, dedupe, company_key


def test_www_and_path_variants_collapse():
    assert normalise_domain("https://WWW.Acme.example/careers") == "acme.example"
    assert normalise_domain("acme.example") == "acme.example"


def test_legal_suffixes_dropped():
    assert normalise_company("Acme Agency Ltd") == normalise_company("Acme")


def test_duplicate_domain_is_rejected_with_reason():
    rows = [
        {"account_id": "A1", "domain": "acme.example", "company": "Acme"},
        {"account_id": "A2", "domain": "www.acme.example/jobs", "company": "Acme"},
    ]
    kept, rejected = dedupe(rows, company_key)
    assert len(kept) == 1
    assert len(rejected) == 1
    assert rejected[0]["reason"] == "duplicate_of:A1"


def test_renamed_company_caught_by_name_fallback():
    rows = [
        {"account_id": "B1", "domain": "", "company": "Bolt Media LLC"},
        {"account_id": "B2", "domain": "", "company": "Bolt"},
    ]
    kept, rejected = dedupe(rows, company_key)
    assert len(kept) == 1
    assert rejected[0]["reason"] == "duplicate_of:B1"
