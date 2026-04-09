"""
Shared Fixtures für OpenClaw Cert-CLI Tests.
"""

import json
import os
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from rich.console import Console


# ─────────────────────────────────────────────────────────────────────────────
# Verzeichnis-Isolation: Tests schreiben nie ins echte Projektverzeichnis
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

    import openclaw_cert
    monkeypatch.setattr(openclaw_cert, "REPORT_DIR", reports)
    monkeypatch.setattr(openclaw_cert, "STREAM_DIR", streams)
    monkeypatch.setattr(openclaw_cert, "LOG_DIR", logs)

    return {"reports": reports, "streams": streams, "logs": logs, "root": tmp_path}


@pytest.fixture
def silent_console(monkeypatch):
    """Ersetzt die globale Console durch eine, die in einen StringIO schreibt."""
    import openclaw_cert
    buf = StringIO()
    quiet = Console(file=buf, force_terminal=True, width=120)
    monkeypatch.setattr(openclaw_cert, "console", quiet)
    return buf


# ─────────────────────────────────────────────────────────────────────────────
# Fake-Reports für status_table / generate_combined_report
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def fake_reports(isolated_dirs):
    """Erstellt Dummy-Reports für Tasks 1-6 im temp reports-Verzeichnis."""
    reports_dir = isolated_dirs["reports"]
    paths = []
    for i in range(1, 7):
        p = reports_dir / f"task_{i}_Test_Aufgabe.md"
        p.write_text(f"# Aufgabe {i}\n\nInhalt für Task {i}.\n", encoding="utf-8")
        paths.append(p)
    return paths


# ─────────────────────────────────────────────────────────────────────────────
# OpenAI Mock – Fake Streaming Response
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

    # Default: 4 Chunks
    make_stream()
    client._configure_stream = make_stream
    return client
