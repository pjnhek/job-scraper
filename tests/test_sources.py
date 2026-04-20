import json
from pathlib import Path

from scraper.sources import COMPANIES, PARSERS, URL_TEMPLATES, _parse_ashby, _parse_greenhouse

FIX = Path(__file__).parent / "fixtures"


def test_ashby_parses_normalized_shape():
    raw = json.loads((FIX / "ashby_sample.json").read_text())
    jobs = _parse_ashby(raw, "Perplexity")
    assert len(jobs) >= 1
    j = jobs[0]
    assert j["id"].startswith("ashby:")
    assert j["company"] == "Perplexity"
    assert {"title", "department", "location", "remote", "url", "posted_at"} <= j.keys()
    assert isinstance(j["remote"], bool)


def test_greenhouse_parses_normalized_shape():
    raw = json.loads((FIX / "greenhouse_sample.json").read_text())
    jobs = _parse_greenhouse(raw, "Glean")
    assert len(jobs) >= 1
    j = jobs[0]
    assert j["id"].startswith("greenhouse:")
    assert j["company"] == "Glean"
    assert {"title", "department", "location", "remote", "url", "posted_at"} <= j.keys()


def test_greenhouse_infers_remote_from_location_string():
    raw = {
        "jobs": [
            {
                "id": 1,
                "title": "X",
                "departments": [{"name": "Eng"}],
                "location": {"name": "Remote - United States"},
                "absolute_url": "https://example.com/1",
                "updated_at": "2026-01-01T00:00:00Z",
            }
        ]
    }
    jobs = _parse_greenhouse(raw, "Co")
    assert jobs[0]["remote"] is True


def test_companies_have_required_fields_and_supported_ats():
    for company in COMPANIES:
        assert {"name", "ats", "slug"} <= company.keys()
        assert company["name"]
        assert company["slug"]
        assert company["ats"] in PARSERS
        assert company["ats"] in URL_TEMPLATES


def test_companies_are_unique_by_name_and_ats_slug_pair():
    names = [company["name"] for company in COMPANIES]
    ats_slug_pairs = [(company["ats"], company["slug"]) for company in COMPANIES]

    assert len(names) == len(set(names))
    assert len(ats_slug_pairs) == len(set(ats_slug_pairs))
