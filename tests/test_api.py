"""Tests für API-Integration: stream_with_retry + run_task (openclaw_cert.api + cli)."""

import openai
import pytest
from unittest.mock import MagicMock

from tests.conftest import FakeStream


def test_run_task_success(isolated_dirs, silent_console, mock_openai_client):
    from openclaw_cert.cli import run_task
    result = run_task(1, mock_openai_client)

    assert result != ""
    assert "task_1_" in result
    from pathlib import Path
    content = Path(result).read_text("utf-8")
    assert "Hallo " in content
    mock_openai_client.chat.completions.create.assert_called_once()


def test_run_task_retry_rate_limit(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    from openclaw_cert import config
    import openclaw_cert.api as api_mod
    monkeypatch.setattr(api_mod.time, "sleep", lambda _: None)

    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.headers = {}
    error = openai.RateLimitError(message="Rate limit", response=mock_resp, body=None)

    mock_openai_client.chat.completions.create.side_effect = [
        error,
        FakeStream(["Retry ", "erfolgreich!"]),
    ]

    from openclaw_cert.cli import run_task
    result = run_task(2, mock_openai_client)
    assert result != ""
    assert mock_openai_client.chat.completions.create.call_count == 2


def test_run_task_retry_timeout(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    import openclaw_cert.api as api_mod
    monkeypatch.setattr(api_mod.time, "sleep", lambda _: None)

    error = openai.APITimeoutError(request=MagicMock())
    mock_openai_client.chat.completions.create.side_effect = [
        error, error, FakeStream(["Dritter ", "Versuch!"]),
    ]

    from openclaw_cert.cli import run_task
    result = run_task(3, mock_openai_client)
    assert result != ""
    assert mock_openai_client.chat.completions.create.call_count == 3


def test_run_task_all_retries_fail(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    import openclaw_cert.api as api_mod
    monkeypatch.setattr(api_mod.time, "sleep", lambda _: None)

    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.headers = {}
    error = openai.RateLimitError(message="Rate limit", response=mock_resp, body=None)
    mock_openai_client.chat.completions.create.side_effect = [error, error, error]

    from openclaw_cert.cli import run_task
    result = run_task(1, mock_openai_client)
    assert result == ""
    assert mock_openai_client.chat.completions.create.call_count == 3


def test_run_task_unexpected_error(isolated_dirs, silent_console, mock_openai_client):
    mock_openai_client.chat.completions.create.side_effect = ValueError("Unerwartet")

    from openclaw_cert.cli import run_task
    result = run_task(4, mock_openai_client)
    assert result == ""
    mock_openai_client.chat.completions.create.assert_called_once()


def test_run_task_no_markdown(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    from openclaw_cert import config
    monkeypatch.setattr(config, "STREAM_CONFIG", {
        "save_markdown": False, "save_raw": False, "save_jsonl": False, "flush_interval": 1,
    })

    from openclaw_cert.cli import run_task
    result = run_task(5, mock_openai_client)
    assert result == ""
    assert len(list(isolated_dirs["reports"].glob("task_5_*.md"))) == 0


def test_run_all_tasks_with_pending(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    import openclaw_cert.api as api_mod
    from openclaw_cert import config
    from rich.prompt import Confirm
    import openclaw_cert.cli as cli_mod
    monkeypatch.setattr(api_mod.time, "sleep", lambda _: None)
    monkeypatch.setattr(cli_mod.time, "sleep", lambda _: None)
    monkeypatch.setattr(cli_mod, "Confirm", type("C", (), {"ask": staticmethod(lambda *a, **k: True)}))

    reports_dir = isolated_dirs["reports"]
    (reports_dir / "task_1_Test.md").write_text("done", encoding="utf-8")
    (reports_dir / "task_3_Test.md").write_text("done", encoding="utf-8")

    mock_openai_client.chat.completions.create.return_value = FakeStream(["OK"])

    from openclaw_cert.cli import run_all_tasks
    run_all_tasks(mock_openai_client, {1, 3})
    assert mock_openai_client.chat.completions.create.call_count == 4


def test_run_all_tasks_none_pending(isolated_dirs, silent_console, mock_openai_client):
    from openclaw_cert.cli import run_all_tasks
    run_all_tasks(mock_openai_client, {1, 2, 3, 4, 5, 6})
    assert "bereits abgeschlossen" in silent_console.getvalue()
