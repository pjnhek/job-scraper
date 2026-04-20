# job-scraper

Scheduled GitHub Actions workflow that scrapes target company job boards and pushes a notification when a matching role is posted.

## Targets

| Company | ATS | Slug |
|---|---|---|
| Perplexity | Ashby | `perplexity` |
| Glean | Greenhouse | `gleanwork` |
| Notion | Ashby | `notion` |
| Dropbox | Greenhouse | `dropbox` |

## Filters

- **Title**: `AI Engineer`, `Machine Learning Engineer`, `ML Engineer` (case-insensitive substring).
- **Seniority reject**: Senior, Sr., Staff, Principal, Lead, Director, Manager, Head of, VP, Vice President. (Intern is kept.)
- **Location**: SF Bay Area or US-remote.

## Schedule

4x/day on US weekdays at 8am, 11am, 2pm, 5pm Pacific. Plus a weekly Sunday keepalive commit to prevent GitHub auto-disabling the scheduled workflow, and a daily ntfy heartbeat.

## Secrets

Set via `gh secret set`:

- `NTFY_TOPIC` — ntfy.sh topic (acts as access credential; keep private)
- `GMAIL_ADDRESS` — sender + recipient email
- `GMAIL_APP_PASSWORD` — 16-char Gmail app password (requires 2FA)

## Local dev

```
uv sync
uv run pytest -v
uv run python -m scraper.main
```
