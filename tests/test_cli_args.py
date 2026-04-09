"""
Tests für CLI-Argument-Dispatch (Entry Point).

7 Tests: report, streams, ende (ohne API), Einzeltask, all, docs (mit Mock), unbekanntes Arg
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tests.conftest import FakeStream

CERT_PY = str(Path(__file__).parent.parent / "openclaw_cert.py")
VENV_PYTHON = "/home/danijel-jd/.openclaw/.venv/bin/python3"


# ─────────────────────────────────────────────────────────────────────────────
# Nicht-API-Pfade: können direkt als Subprocess laufen
# ─────────────────────────────────────────────────────────────────────────────

def test_cli_report(isolated_dirs, tmp_path):
    """'report' Argument: erstellt Gesamtreport (oder meldet 'keine Reports')."""
    result = subprocess.run(
        [VENV_PYTHON, CERT_PY, "report"],
        capture_output=True, text=True, timeout=10,
        env={"HOME": str(tmp_path), "PATH": "/usr/bin:/bin"},
        cwd=str(isolated_dirs["root"]),
    )
    # Kein Crash — entweder "Keine Reports" oder Erfolg
    assert result.returncode == 0
    assert "Traceback" not in result.stderr


def test_cli_streams(isolated_dirs, tmp_path):
    """'streams' Argument: listet Stream-Dateien (oder meldet 'keine')."""
    result = subprocess.run(
        [VENV_PYTHON, CERT_PY, "streams"],
        capture_output=True, text=True, timeout=10,
        env={"HOME": str(tmp_path), "PATH": "/usr/bin:/bin"},
        cwd=str(isolated_dirs["root"]),
    )
    assert result.returncode == 0
    assert "Traceback" not in result.stderr


def test_cli_ende(isolated_dirs, tmp_path):
    """'ende' Argument: erstellt Finale Zusammenfassung."""
    result = subprocess.run(
        [VENV_PYTHON, CERT_PY, "ende"],
        capture_output=True, text=True, timeout=10,
        env={"HOME": str(tmp_path), "PATH": "/usr/bin:/bin"},
        cwd=str(isolated_dirs["root"]),
    )
    assert result.returncode == 0
    assert "Traceback" not in result.stderr


def test_cli_unknown_arg(tmp_path):
    """Unbekanntes Argument: Fehlermeldung + Usage-Hinweis."""
    result = subprocess.run(
        [VENV_PYTHON, CERT_PY, "quatsch123"],
        capture_output=True, text=True, timeout=10,
        env={"HOME": str(tmp_path), "PATH": "/usr/bin:/bin"},
    )
    assert result.returncode == 0
    output = result.stdout
    assert "Unbekanntes Argument" in output or "Verwendung" in output


# ─────────────────────────────────────────────────────────────────────────────
# API-pflichtige Pfade: mit gemocktem Client testen
# ─────────────────────────────────────────────────────────────────────────────

def test_cli_single_task(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    """CLI-Arg '2': ruft run_task(2, client) auf."""
    import openclaw_cert

    monkeypatch.setattr(openclaw_cert, "get_openai_client", lambda: mock_openai_client)
    monkeypatch.setattr(sys, "argv", ["openclaw_cert.py", "2"])

    # Entry-Point-Logik direkt ausführen
    arg = "2"
    openclaw_cert.banner()
    result = openclaw_cert.run_task(int(arg), mock_openai_client)

    assert result != ""
    mock_openai_client.chat.completions.create.assert_called_once()


def test_cli_all_tasks(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    """CLI-Arg 'all': ruft run_all_tasks auf."""
    import openclaw_cert

    monkeypatch.setattr(openclaw_cert.time, "sleep", lambda _: None)
    monkeypatch.setattr(openclaw_cert.Confirm, "ask", lambda *a, **kw: True)

    mock_openai_client.chat.completions.create.return_value = FakeStream(["Test"])

    openclaw_cert.banner()
    completed = openclaw_cert.status_table()
    openclaw_cert.run_all_tasks(mock_openai_client, completed)

    # 6 offene Tasks → 6 API-Calls
    assert mock_openai_client.chat.completions.create.call_count == 6


def test_cli_docs(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    """CLI-Arg 'docs': ruft generate_docs auf."""
    import openclaw_cert

    mock_openai_client.chat.completions.create.return_value = FakeStream(["Doku-Inhalt"])

    openclaw_cert.generate_docs(mock_openai_client)

    mock_openai_client.chat.completions.create.assert_called_once()

    # Dokumentations-Datei wurde erstellt
    doc_path = isolated_dirs["reports"] / "OPENCLAW_CERT_CLI_DOKUMENTATION.md"
    assert doc_path.exists()
    content = doc_path.read_text(encoding="utf-8")
    assert "Doku-Inhalt" in content
