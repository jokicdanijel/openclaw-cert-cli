"""
Tests für run_task() und run_all_tasks() mit gemockter OpenAI-API.

8 Tests: Erfolg, Retry-RateLimit, Retry-Timeout, 3x-Fail, unerwarteter Fehler,
         save_markdown=off, run_all_tasks (mit/ohne offene Tasks)
"""

import openai
import pytest
from unittest.mock import MagicMock, patch, call

from tests.conftest import FakeStream, FakeChunk


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Erfolgreicher Stream → Report gespeichert
# ─────────────────────────────────────────────────────────────────────────────

def test_run_task_success(isolated_dirs, silent_console, mock_openai_client):
    """Erfolgreicher API-Call: Report wird gespeichert, Pfad zurückgegeben."""
    from openclaw_cert import run_task

    result = run_task(1, mock_openai_client)

    # Report-Pfad zurückgegeben
    assert result != ""
    assert "task_1_" in result
    assert result.endswith(".md")

    # Report-Datei existiert und enthält gestreamten Text
    from pathlib import Path
    content = Path(result).read_text(encoding="utf-8")
    assert "Hallo " in content
    assert "ein Test." in content

    # API wurde genau einmal aufgerufen
    mock_openai_client.chat.completions.create.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: RateLimitError → Retry → Erfolg beim 2. Versuch
# ─────────────────────────────────────────────────────────────────────────────

def test_run_task_retry_rate_limit(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    """RateLimitError beim 1. Versuch, Erfolg beim 2. → Report gespeichert."""
    import openclaw_cert
    monkeypatch.setattr(openclaw_cert.time, "sleep", lambda _: None)  # sleep skippen

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {}

    error = openai.RateLimitError(
        message="Rate limit exceeded",
        response=mock_response,
        body=None,
    )

    # 1. Call → RateLimitError, 2. Call → Erfolg
    mock_openai_client.chat.completions.create.side_effect = [
        error,
        FakeStream(["Retry ", "erfolgreich!"]),
    ]

    from openclaw_cert import run_task
    result = run_task(2, mock_openai_client)

    assert result != ""
    assert mock_openai_client.chat.completions.create.call_count == 2

    from pathlib import Path
    content = Path(result).read_text(encoding="utf-8")
    assert "Retry erfolgreich!" in content


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: APITimeoutError → Retry → Erfolg beim 3. Versuch
# ─────────────────────────────────────────────────────────────────────────────

def test_run_task_retry_timeout(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    """2x APITimeoutError, dann Erfolg beim 3. Versuch."""
    import openclaw_cert
    monkeypatch.setattr(openclaw_cert.time, "sleep", lambda _: None)

    error = openai.APITimeoutError(request=MagicMock())

    mock_openai_client.chat.completions.create.side_effect = [
        error,
        error,
        FakeStream(["Dritter ", "Versuch!"]),
    ]

    from openclaw_cert import run_task
    result = run_task(3, mock_openai_client)

    assert result != ""
    assert mock_openai_client.chat.completions.create.call_count == 3


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: 3x RateLimitError → alle fehlgeschlagen → leerer String
# ─────────────────────────────────────────────────────────────────────────────

def test_run_task_all_retries_fail(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    """3x RateLimitError → Funktion gibt '' zurück."""
    import openclaw_cert
    monkeypatch.setattr(openclaw_cert.time, "sleep", lambda _: None)

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {}

    error = openai.RateLimitError(
        message="Rate limit exceeded",
        response=mock_response,
        body=None,
    )

    mock_openai_client.chat.completions.create.side_effect = [error, error, error]

    from openclaw_cert import run_task
    result = run_task(1, mock_openai_client)

    assert result == ""
    assert mock_openai_client.chat.completions.create.call_count == 3

    output = silent_console.getvalue()
    assert "fehlgeschlagen" in output


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Unerwarteter Fehler → sofortiger Abbruch (kein Retry)
# ─────────────────────────────────────────────────────────────────────────────

def test_run_task_unexpected_error(isolated_dirs, silent_console, mock_openai_client):
    """ValueError (nicht-retriable) → sofort leerer String, nur 1 Aufruf."""
    mock_openai_client.chat.completions.create.side_effect = ValueError("Unerwarteter Fehler")

    from openclaw_cert import run_task
    result = run_task(4, mock_openai_client)

    assert result == ""
    mock_openai_client.chat.completions.create.assert_called_once()

    output = silent_console.getvalue()
    assert "Fehler" in output


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: STREAM_CONFIG save_markdown=False → kein Report, aber Stream ok
# ─────────────────────────────────────────────────────────────────────────────

def test_run_task_no_markdown(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    """Mit save_markdown=False: kein .md-Report, aber Funktion läuft durch."""
    import openclaw_cert
    monkeypatch.setattr(openclaw_cert, "STREAM_CONFIG", {
        "save_markdown": False,
        "save_raw": False,
        "save_jsonl": False,
        "flush_interval": 1,
    })

    from openclaw_cert import run_task
    result = run_task(5, mock_openai_client)

    # Leerer Pfad, weil kein Markdown gespeichert
    assert result == ""

    # Kein Report in reports/
    reports = list(isolated_dirs["reports"].glob("task_5_*.md"))
    assert len(reports) == 0


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: run_all_tasks → offene Tasks werden sequenziell abgearbeitet
# ─────────────────────────────────────────────────────────────────────────────

def test_run_all_tasks_with_pending(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    """run_all_tasks mit 4 offenen Tasks: alle werden bearbeitet."""
    import openclaw_cert
    monkeypatch.setattr(openclaw_cert.time, "sleep", lambda _: None)

    # Tasks 1 und 3 sind schon fertig
    reports_dir = isolated_dirs["reports"]
    (reports_dir / "task_1_Test.md").write_text("done", encoding="utf-8")
    (reports_dir / "task_3_Test.md").write_text("done", encoding="utf-8")
    completed = {1, 3}

    # Confirm.ask immer True
    monkeypatch.setattr(openclaw_cert.Confirm, "ask", lambda *a, **kw: True)

    # Jeder run_task-Call gibt neuen FakeStream
    mock_openai_client.chat.completions.create.return_value = FakeStream(["OK"])

    from openclaw_cert import run_all_tasks
    run_all_tasks(mock_openai_client, completed)

    # 4 offene Tasks (2, 4, 5, 6) → 4 API-Calls
    assert mock_openai_client.chat.completions.create.call_count == 4


# ─────────────────────────────────────────────────────────────────────────────
# Test 8: run_all_tasks → keine offenen Tasks → Skip
# ─────────────────────────────────────────────────────────────────────────────

def test_run_all_tasks_none_pending(fake_reports, isolated_dirs, silent_console, mock_openai_client):
    """Alle Tasks fertig → 'Alle Aufgaben bereits abgeschlossen', kein API-Call."""
    from openclaw_cert import run_all_tasks

    completed = {1, 2, 3, 4, 5, 6}
    run_all_tasks(mock_openai_client, completed)

    # Kein API-Call
    mock_openai_client.chat.completions.create.assert_not_called()

    output = silent_console.getvalue()
    assert "bereits abgeschlossen" in output
