from __future__ import annotations


TITLE_KEYWORDS = [
    "ai engineer",
    "machine learning engineer",
    "ml engineer",
]

# "intern" intentionally excluded — user wants intern roles kept
SENIORITY_REJECT = [
    "senior",
    "sr.",
    "sr ",
    "staff",
    "principal",
    "lead",
    "director",
    "manager",
    "head of",
    "vp",
    "vice president",
]

LOCATION_ACCEPT = [
    "san francisco",
    "sf",
    "bay area",
    "palo alto",
    "mountain view",
    "menlo park",
    "oakland",
    "berkeley",
    "south san francisco",
    "redwood city",
    "san mateo",
    "sunnyvale",
    "santa clara",
    "san jose",
    "remote - us",
    "us remote",
    "remote, us",
    "remote (us)",
    "united states",
    "usa",
]


def title_matches(title: str) -> bool:
    t = (title or "").lower()
    return any(k in t for k in TITLE_KEYWORDS)


def seniority_ok(title: str) -> bool:
    t = (title or "").lower()
    return not any(s in t for s in SENIORITY_REJECT)


def location_ok(location: str, remote: bool) -> bool:
    loc = (location or "").lower()
    if remote and ("us" in loc or "united states" in loc or "americas" in loc or loc == ""):
        # accept US-remote; reject EU/APAC-only remote
        if any(bad in loc for bad in ["europe", "emea", "apac", "asia", "uk", "london", "berlin", "paris", "dublin"]):
            return False
        return True
    return any(a in loc for a in LOCATION_ACCEPT)


def is_match(job: dict) -> bool:
    return (
        title_matches(job.get("title", ""))
        and seniority_ok(job.get("title", ""))
        and location_ok(job.get("location", ""), bool(job.get("remote")))
    )


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return [j for j in jobs if is_match(j)]
