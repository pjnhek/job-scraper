import json

from scraper import state


def test_roundtrip_save_load(tmp_path):
    p = tmp_path / "seen.json"
    seen = {"ashby:1": {"company": "X", "title": "Y", "url": "", "posted_at": ""}}
    state.save(seen, p)
    assert state.load(p) == seen


def test_diff_new_returns_only_unseen():
    seen = {"ashby:1": {}}
    jobs = [{"id": "ashby:1"}, {"id": "ashby:2"}, {"id": "greenhouse:3"}]
    new = state.diff_new(jobs, seen)
    assert [j["id"] for j in new] == ["ashby:2", "greenhouse:3"]


def test_merge_adds_without_mutating_input():
    seen = {"a": {"company": "A"}}
    jobs = [{"id": "b", "company": "B", "title": "t", "url": "u", "posted_at": "p"}]
    merged = state.merge(seen, jobs)
    assert "a" in merged and "b" in merged
    assert seen == {"a": {"company": "A"}}


def test_load_missing_file_returns_empty(tmp_path):
    assert state.load(tmp_path / "does_not_exist.json") == {}


def test_load_invalid_json_returns_empty(tmp_path):
    p = tmp_path / "seen.json"
    p.write_text("not valid json")
    assert state.load(p) == {}


def test_save_is_atomic_via_tmp_replace(tmp_path):
    p = tmp_path / "seen.json"
    state.save({"a": {}}, p)
    # overwrite works
    state.save({"b": {}}, p)
    assert json.loads(p.read_text()) == {"b": {}}
