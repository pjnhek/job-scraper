from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Iterable

import requests

log = logging.getLogger(__name__)

TIMEOUT = 30


COMPANIES: list[dict[str, str]] = [
    {"name": "Perplexity", "ats": "ashby", "slug": "perplexity"},
    {"name": "Glean", "ats": "greenhouse", "slug": "gleanwork"},
    {"name": "Notion", "ats": "ashby", "slug": "notion"},
    {"name": "Dropbox", "ats": "greenhouse", "slug": "dropbox"},
]


def _ms_epoch_to_iso(ms: int | str | None) -> str:
    if ms is None:
        return ""
    try:
        return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).isoformat()
    except (ValueError, TypeError):
        return ""


def _parse_ashby(raw: dict, company: str) -> list[dict]:
    out = []
    for j in raw.get("jobs", []):
        if not j.get("isListed", True):
            continue
        loc = j.get("location") or ""
        out.append({
            "id": f"ashby:{j['id']}",
            "company": company,
            "title": j.get("title", ""),
            "department": j.get("department", "") or "",
            "location": loc,
            "remote": bool(j.get("isRemote")) or "remote" in loc.lower(),
            "url": j.get("jobUrl") or j.get("applyUrl") or "",
            "posted_at": j.get("publishedAt", ""),
        })
    return out


def _parse_greenhouse(raw: dict, company: str) -> list[dict]:
    out = []
    for j in raw.get("jobs", []):
        depts = j.get("departments") or []
        loc_name = (j.get("location") or {}).get("name", "") or ""
        out.append({
            "id": f"greenhouse:{j['id']}",
            "company": company,
            "title": j.get("title", ""),
            "department": depts[0]["name"] if depts else "",
            "location": loc_name,
            "remote": "remote" in loc_name.lower(),
            "url": j.get("absolute_url", ""),
            "posted_at": j.get("updated_at", ""),
        })
    return out


def _parse_lever(raw: list, company: str) -> list[dict]:
    # kept for completeness; not currently used
    out = []
    for j in raw:
        cats = j.get("categories") or {}
        out.append({
            "id": f"lever:{j['id']}",
            "company": company,
            "title": j.get("text", ""),
            "department": cats.get("department", "") or "",
            "location": cats.get("location", "") or "",
            "remote": (j.get("workplaceType") == "remote"),
            "url": j.get("hostedUrl", ""),
            "posted_at": _ms_epoch_to_iso(j.get("createdAt")),
        })
    return out


def _parse_smartrecruiters(raw: dict, company: str) -> list[dict]:
    out = []
    for j in raw.get("content", []):
        loc = j.get("location") or {}
        parts = [loc.get("city") or "", loc.get("region") or ""]
        out.append({
            "id": f"smartrecruiters:{j['id']}",
            "company": company,
            "title": j.get("name", ""),
            "department": (j.get("department") or {}).get("label", "") or "",
            "location": ", ".join(p for p in parts if p),
            "remote": bool(loc.get("remote")),
            "url": j.get("ref", ""),
            "posted_at": j.get("releasedDate", ""),
        })
    return out


PARSERS = {
    "ashby": _parse_ashby,
    "greenhouse": _parse_greenhouse,
    "lever": _parse_lever,
    "smartrecruiters": _parse_smartrecruiters,
}

URL_TEMPLATES = {
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "lever": "https://api.lever.co/v0/postings/{slug}?mode=json",
    "smartrecruiters": "https://api.smartrecruiters.com/v1/companies/{slug}/postings",
}


def fetch_company(company: dict, session: requests.Session | None = None) -> list[dict]:
    ats = company["ats"]
    slug = company["slug"]
    name = company["name"]
    url = URL_TEMPLATES[ats].format(slug=slug)
    s = session or requests
    resp = s.get(url, timeout=TIMEOUT, headers={"User-Agent": "job-scraper/0.1"})
    resp.raise_for_status()
    return PARSERS[ats](resp.json(), name)


def fetch_all(companies: Iterable[dict] | None = None) -> list[dict]:
    companies = list(companies) if companies is not None else COMPANIES
    jobs: list[dict] = []
    with requests.Session() as s:
        for c in companies:
            try:
                batch = fetch_company(c, s)
                log.info("fetched %d jobs from %s", len(batch), c["name"])
                jobs.extend(batch)
            except Exception as e:
                log.exception("failed to fetch %s: %s", c["name"], e)
    return jobs
