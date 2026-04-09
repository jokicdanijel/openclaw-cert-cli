"""
Tests für status_table(), list_streams() und show_report().

5 Tests: status (alle fertig, keine fertig, teilweise), list_streams, show_report
"""

import datetime
from pathlib import Path

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# status_table()
# ─────────────────────────────────────────────────────────────────────────────

def test_status_table_all_complete(fake_reports, isolated_dirs, silent_console):
    """Bei 6/6 Reports: Set {1..6} zurückgegeben, Erfolgsmeldung angezeigt."""
    from openclaw_cert import status_table

    completed = status_table()

    assert completed == {1, 2, 3, 4, 5, 6}

    output = silent_console.getvalue()
    assert "ALLE AUFGABEN ABGESCHLOSSEN" in output


def test_status_table_none_complete(isolated_dirs, silent_console):
    """Ohne Reports: leeres Set, keine Erfolgsmeldung."""
    from openclaw_cert import status_table

    completed = status_table()

    assert completed == set()

    output = silent_console.getvalue()
    assert "ALLE AUFGABEN ABGESCHLOSSEN" not in output


def test_status_table_partial(isolated_dirs, silent_console):
    """Bei 2 von 6 Reports: nur diese im Set."""
    from openclaw_cert import status_table

    reports_dir = isolated_dirs["reports"]
    (reports_dir / "task_2_Telegram.md").write_text("# Task 2\n", encoding="utf-8")
    (reports_dir / "task_5_Docker.md").write_text("# Task 5\n", encoding="utf-8")

    completed = status_table()

    assert completed == {2, 5}

    output = silent_console.getvalue()
    assert "ALLE AUFGABEN ABGESCHLOSSEN" not in output


# ─────────────────────────────────────────────────────────────────────────────
# list_streams()
# ─────────────────────────────────────────────────────────────────────────────

def test_list_streams_with_files(isolated_dirs, silent_console):
    """list_streams() zeigt vorhandene Dateien tabellarisch an."""
    from openclaw_cert import list_streams

    streams_dir = isolated_dirs["streams"]
    (streams_dir / "stream_1_test.txt").write_text("Hello Stream", encoding="utf-8")
    (streams_dir / "stream_1_test.jsonl").write_text('{"ts":"now"}\n', encoding="utf-8")

    list_streams()

    output = silent_console.getvalue()
    assert "stream_1_test.txt" in output
    assert "stream_1_test.jsonl" in output


def test_list_streams_empty(isolated_dirs, silent_console):
    """Ohne Stream-Dateien: Warnung angezeigt."""
    from openclaw_cert import list_streams

    list_streams()

    output = silent_console.getvalue()
    assert "Keine Stream-Dateien" in output
