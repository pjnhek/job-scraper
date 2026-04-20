from unittest.mock import MagicMock, patch

from scraper import notify


JOB = {
    "id": "ashby:1",
    "company": "TestCo",
    "title": "AI Engineer",
    "department": "Eng",
    "location": "San Francisco",
    "remote": False,
    "url": "https://example.com/job/1",
    "posted_at": "2026-04-20T00:00:00+00:00",
}


def test_email_disabled_without_env(monkeypatch):
    monkeypatch.delenv("GMAIL_ADDRESS", raising=False)
    monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)
    assert notify.send_email([JOB]) is False


def test_ntfy_disabled_without_env(monkeypatch):
    monkeypatch.delenv("NTFY_TOPIC", raising=False)
    assert notify.send_ntfy([JOB]) is False


def test_ntfy_posts_with_headers(monkeypatch):
    monkeypatch.setenv("NTFY_TOPIC", "test-topic")
    with patch("scraper.notify.requests.post") as post:
        post.return_value = MagicMock(status_code=200, raise_for_status=lambda: None)
        assert notify.send_ntfy([JOB]) is True
        args, kwargs = post.call_args
        assert args[0] == "https://ntfy.sh/test-topic"
        assert kwargs["headers"]["Title"].startswith("1 new job")
        assert kwargs["headers"]["Click"] == JOB["url"]


def test_ntfy_high_priority_when_three_or_more(monkeypatch):
    monkeypatch.setenv("NTFY_TOPIC", "test-topic")
    with patch("scraper.notify.requests.post") as post:
        post.return_value = MagicMock(status_code=200, raise_for_status=lambda: None)
        notify.send_ntfy([JOB, JOB, JOB])
        assert post.call_args.kwargs["headers"]["Priority"] == "high"


def test_email_sends_via_smtp_ssl(monkeypatch):
    monkeypatch.setenv("GMAIL_ADDRESS", "a@b.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "pw")
    with patch("scraper.notify.smtplib.SMTP_SSL") as smtp:
        inst = smtp.return_value.__enter__.return_value
        inst.login.return_value = None
        inst.send_message.return_value = None
        assert notify.send_email([JOB]) is True
        inst.login.assert_called_once_with("a@b.com", "pw")
        inst.send_message.assert_called_once()


def test_one_channel_failure_does_not_block_other(monkeypatch):
    monkeypatch.setenv("GMAIL_ADDRESS", "a@b.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "pw")
    monkeypatch.setenv("NTFY_TOPIC", "test-topic")
    with patch("scraper.notify.smtplib.SMTP_SSL", side_effect=RuntimeError("boom")), \
         patch("scraper.notify.requests.post") as post:
        post.return_value = MagicMock(status_code=200, raise_for_status=lambda: None)
        result = notify.notify([JOB])
        assert result == {"email": False, "ntfy": True}


def test_notify_empty_list_is_noop(monkeypatch):
    monkeypatch.setenv("NTFY_TOPIC", "test-topic")
    with patch("scraper.notify.requests.post") as post:
        notify.notify([])
        post.assert_not_called()
