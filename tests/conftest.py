"""
Shared Fixtures für OpenClaw Cert-CLI Tests (modulare Struktur).
"""

import json
import os
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from rich.console import Console


# ─────────────────────────────────────────────────────────────────────────────
# Verzeichnis-Isolation
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def isolated_dirs(tmp_path, monkeypatch):
    """Ersetzt REPORT_DIR, STREAM_DIR, LOG_DIR durch temporäre Verzeichnisse."""
    reports = tmp_path / "reports"
    streams = tmp_path / "streams"
    logs = tmp_path / "logs"
    reports.mkdir()
    streams.mkdir()
    logs.mkdir()

    from openclaw_cert import config
    monkeypatch.setattr(config, "REPORT_DIR", reports)
    monkeypatch.setattr(config, "STREAM_DIR", streams)
    monkeypatch.setattr(config, "LOG_DIR", logs)

    return {"reports": reports, "streams": streams, "logs": logs, "root": tmp_path}


@pytest.fixture
def silent_console(monkeypatch):
    """Ersetzt die globale Console durch eine, die in einen StringIO schreibt."""
    from openclaw_cert import config
    buf = StringIO()
    quiet = Console(file=buf, force_terminal=True, width=120)
    monkeypatch.setattr(config, "console", quiet)
    return buf


# ─────────────────────────────────────────────────────────────────────────────
# Fake-Reports
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def fake_reports(isolated_dirs):
    """Erstellt Dummy-Reports für Tasks 1-6."""
    reports_dir = isolated_dirs["reports"]
    paths = []
    for i in range(1, 7):
        p = reports_dir / f"task_{i}_Test_Aufgabe.md"
        p.write_text(f"# Aufgabe {i}\n\nInhalt für Task {i}.\n", encoding="utf-8")
        paths.append(p)
    return paths


# ─────────────────────────────────────────────────────────────────────────────
# OpenAI Mock — Fake Streaming Response
# ─────────────────────────────────────────────────────────────────────────────

class FakeDelta:
    def __init__(self, content):
        self.content = content


class FakeChoice:
    def __init__(self, content):
        self.delta = FakeDelta(content)


class FakeChunk:
    def __init__(self, text):
        self.choices = [FakeChoice(text)]


class FakeStream:
    """Simuliert einen OpenAI Streaming-Response."""

    def __init__(self, chunks: list[str]):
        self._chunks = [FakeChunk(c) for c in chunks]

    def __iter__(self):
        return iter(self._chunks)


@pytest.fixture
def mock_openai_client():
    """Gibt einen gemockten OpenAI-Client zurück, der FakeStream liefert."""
    client = MagicMock()

    def make_stream(chunks=None):
        if chunks is None:
            chunks = ["Hallo ", "Welt! ", "Das ist ", "ein Test."]
        client.chat.completions.create.return_value = FakeStream(chunks)
        return client

    make_stream()  # Default setzen
    client.make_stream = make_stream
    return client
