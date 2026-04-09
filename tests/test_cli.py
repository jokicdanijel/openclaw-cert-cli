"""Tests für CLI-Dispatch (openclaw_cert.cli)."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tests.conftest import FakeStream

VENV_PYTHON = "/home/danijel-jd/.openclaw/.venv/bin/python3"
SANDBOX_ROOT = str(Path(__file__).resolve().parent.parent)


def test_cli_report(isolated_dirs, tmp_path):
    result = subprocess.run(
        [VENV_PYTHON, "-m", "openclaw_cert", "report"],
        capture_output=True, text=True, timeout=10,
        env={"HOME": str(tmp_path), "PATH": "/usr/bin:/bin", "PYTHONPATH": SANDBOX_ROOT},
        cwd=str(isolated_dirs["root"]),
    )
    assert result.returncode == 0
    assert "Traceback" not in result.stderr


def test_cli_streams(isolated_dirs, tmp_path):
    result = subprocess.run(
        [VENV_PYTHON, "-m", "openclaw_cert", "streams"],
        capture_output=True, text=True, timeout=10,
        env={"HOME": str(tmp_path), "PATH": "/usr/bin:/bin", "PYTHONPATH": SANDBOX_ROOT},
        cwd=str(isolated_dirs["root"]),
    )
    assert result.returncode == 0
    assert "Traceback" not in result.stderr


def test_cli_ende(isolated_dirs, tmp_path):
    result = subprocess.run(
        [VENV_PYTHON, "-m", "openclaw_cert", "ende"],
        capture_output=True, text=True, timeout=10,
        env={"HOME": str(tmp_path), "PATH": "/usr/bin:/bin", "PYTHONPATH": SANDBOX_ROOT},
        cwd=str(isolated_dirs["root"]),
    )
    assert result.returncode == 0
    assert "Traceback" not in result.stderr


def test_cli_unknown_arg(tmp_path):
    result = subprocess.run(
        [VENV_PYTHON, "-m", "openclaw_cert", "quatsch123"],
        capture_output=True, text=True, timeout=10,
        env={"HOME": str(tmp_path), "PATH": "/usr/bin:/bin", "PYTHONPATH": SANDBOX_ROOT},
    )
    assert result.returncode == 0
    assert "Unbekanntes Argument" in result.stdout or "Verwendung" in result.stdout


def test_cli_single_task(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    from openclaw_cert.cli import run_task
    from openclaw_cert.display import banner
    banner()
    result = run_task(2, mock_openai_client)
    assert result != ""
    mock_openai_client.chat.completions.create.assert_called_once()


def test_cli_all_tasks(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    import openclaw_cert.api as api_mod
    import openclaw_cert.cli as cli_mod
    monkeypatch.setattr(api_mod.time, "sleep", lambda _: None)
    monkeypatch.setattr(cli_mod.time, "sleep", lambda _: None)
    monkeypatch.setattr(cli_mod, "Confirm", type("C", (), {"ask": staticmethod(lambda *a, **k: True)}))

    mock_openai_client.chat.completions.create.return_value = FakeStream(["Test"])

    from openclaw_cert.display import banner, status_table
    banner()
    completed = status_table()
    from openclaw_cert.cli import run_all_tasks
    run_all_tasks(mock_openai_client, completed)
    assert mock_openai_client.chat.completions.create.call_count == 6


def test_cli_docs(isolated_dirs, silent_console, mock_openai_client, monkeypatch):
    mock_openai_client.chat.completions.create.return_value = FakeStream(["Doku-Inhalt"])

    from openclaw_cert.docs import generate_docs
    generate_docs(mock_openai_client)

    mock_openai_client.chat.completions.create.assert_called_once()
    doc = isolated_dirs["reports"] / "OPENCLAW_CERT_CLI_DOKUMENTATION.md"
    assert doc.exists()
    assert "Doku-Inhalt" in doc.read_text("utf-8")
