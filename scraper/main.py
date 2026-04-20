from __future__ import annotations

import logging
import os
import sys

from scraper import filters, notify, sources, state

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("scraper")


def main() -> int:
    all_jobs = sources.fetch_all()
    matched = filters.filter_jobs(all_jobs)
    seen = state.load()
    new_jobs = state.diff_new(matched, seen)

    log.info("total=%d matched=%d new=%d", len(all_jobs), len(matched), len(new_jobs))
    for j in new_jobs:
        log.info("NEW %s :: %s :: %s", j["company"], j["title"], j["location"])

    if new_jobs:
        notify.notify(new_jobs)

    merged = state.merge(seen, matched)
    state.save(merged)

    if os.getenv("HEARTBEAT", "").lower() == "true":
        notify.send_heartbeat(len(all_jobs), len(matched))

    return 0


if __name__ == "__main__":
    sys.exit(main())
