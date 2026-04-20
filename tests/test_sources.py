import json
from pathlib import Path

from scraper.sources import _parse_ashby, _parse_greenhouse

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
