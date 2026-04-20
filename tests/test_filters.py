from scraper.filters import is_match, location_ok, seniority_ok, title_matches


def test_title_matches_ai_engineer():
    assert title_matches("AI Engineer, RAG")
    assert title_matches("Machine Learning Engineer")
    assert title_matches("ML Engineer, Search")


def test_title_rejects_non_engineering():
    assert not title_matches("Product Designer")
    assert not title_matches("Account Executive")


def test_seniority_rejects_senior_staff_principal():
    assert not seniority_ok("Senior AI Engineer")
    assert not seniority_ok("Staff ML Engineer")
    assert not seniority_ok("Principal Machine Learning Engineer")


def test_seniority_keeps_intern_and_ic():
    assert seniority_ok("AI Engineer Intern")
    assert seniority_ok("Machine Learning Engineer")


def test_location_accepts_sf_and_us_remote():
    assert location_ok("San Francisco, CA", remote=False)
    assert location_ok("Remote - US", remote=True)
    assert location_ok("", remote=True)
    assert location_ok("United States", remote=False)


def test_location_rejects_eu_and_apac():
    assert not location_ok("London, UK", remote=False)
    assert not location_ok("Remote - Europe", remote=True)
    assert not location_ok("Tokyo", remote=False)


def test_is_match_end_to_end():
    good = {"title": "AI Engineer", "location": "San Francisco", "remote": False}
    bad_senior = {"title": "Senior AI Engineer", "location": "San Francisco", "remote": False}
    bad_loc = {"title": "AI Engineer", "location": "London", "remote": False}
    bad_title = {"title": "Sales Engineer", "location": "San Francisco", "remote": False}
    assert is_match(good)
    assert not is_match(bad_senior)
    assert not is_match(bad_loc)
    assert not is_match(bad_title)
