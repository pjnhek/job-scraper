from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage

import requests

log = logging.getLogger(__name__)


def _email_enabled() -> bool:
    return bool(os.getenv("GMAIL_ADDRESS") and os.getenv("GMAIL_APP_PASSWORD"))


def _ntfy_enabled() -> bool:
    return bool(os.getenv("NTFY_TOPIC"))


def _format_jobs_text(jobs: list[dict]) -> str:
    lines = []
    for j in jobs:
        lines.append(
            f"- [{j['company']}] {j['title']} ({j.get('location','')})\n  {j.get('url','')}"
        )
    return "\n".join(lines)


def send_email(jobs: list[dict]) -> bool:
    if not _email_enabled():
        log.info("email disabled (no GMAIL_ADDRESS / GMAIL_APP_PASSWORD)")
        return False
    addr = os.environ["GMAIL_ADDRESS"]
    pw = os.environ["GMAIL_APP_PASSWORD"]
    subject = f"[job-scraper] {len(jobs)} new role{'s' if len(jobs) != 1 else ''}"
    body = _format_jobs_text(jobs)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = addr
    msg["To"] = addr
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as s:
            s.login(addr, pw)
            s.send_message(msg)
        log.info("email sent to %s", addr)
        return True
    except Exception as e:
        log.exception("email send failed: %s", e)
        return False


def send_ntfy(jobs: list[dict]) -> bool:
    if not _ntfy_enabled():
        log.info("ntfy disabled (no NTFY_TOPIC)")
        return False
    topic = os.environ["NTFY_TOPIC"]
    body = _format_jobs_text(jobs)[:500]
    priority = "high" if len(jobs) >= 3 else "default"
    headers = {
        "Title": f"{len(jobs)} new job{'s' if len(jobs) != 1 else ''}",
        "Priority": priority,
        "Tags": "briefcase",
    }
    if jobs and jobs[0].get("url"):
        headers["Click"] = jobs[0]["url"]
    try:
        r = requests.post(
            f"https://ntfy.sh/{topic}",
            data=body.encode("utf-8"),
            headers=headers,
            timeout=30,
        )
        r.raise_for_status()
        log.info("ntfy sent to %s", topic)
        return True
    except Exception as e:
        log.exception("ntfy send failed: %s", e)
        return False


def send_heartbeat(total_jobs: int, matched_jobs: int) -> bool:
    if not _ntfy_enabled():
        return False
    topic = os.environ["NTFY_TOPIC"]
    body = f"Scraper ran OK. Scanned {total_jobs} postings, {matched_jobs} matched filters."
    try:
        r = requests.post(
            f"https://ntfy.sh/{topic}",
            data=body.encode("utf-8"),
            headers={"Title": "Heartbeat", "Priority": "min", "Tags": "heartbeat"},
            timeout=30,
        )
        r.raise_for_status()
        return True
    except Exception as e:
        log.exception("heartbeat failed: %s", e)
        return False


def notify(jobs: list[dict]) -> dict[str, bool]:
    if not jobs:
        return {"email": False, "ntfy": False}
    return {"email": send_email(jobs), "ntfy": send_ntfy(jobs)}
