from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable

DEFAULT_PATH = Path("seen_jobs.json")


def load(path: Path | str = DEFAULT_PATH) -> dict[str, dict]:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text() or "{}")
    except json.JSONDecodeError:
        return {}


def save(seen: dict[str, dict], path: Path | str = DEFAULT_PATH) -> None:
    p = Path(path)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(seen, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, p)


def diff_new(jobs: Iterable[dict], seen: dict[str, dict]) -> list[dict]:
    return [j for j in jobs if j["id"] not in seen]


def merge(seen: dict[str, dict], jobs: Iterable[dict]) -> dict[str, dict]:
    out = dict(seen)
    for j in jobs:
        out[j["id"]] = {
            "company": j.get("company", ""),
            "title": j.get("title", ""),
            "url": j.get("url", ""),
            "posted_at": j.get("posted_at", ""),
        }
    return out
