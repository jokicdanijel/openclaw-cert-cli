"""Tests für Display-Funktionen (openclaw_cert.display)."""

import pytest


def test_status_table_all_complete(fake_reports, isolated_dirs, silent_console):
    from openclaw_cert.display import status_table
    completed = status_table()
    assert completed == {1, 2, 3, 4, 5, 6}
    assert "ALLE AUFGABEN ABGESCHLOSSEN" in silent_console.getvalue()


def test_status_table_none(isolated_dirs, silent_console):
    from openclaw_cert.display import status_table
    completed = status_table()
    assert completed == set()
    assert "ALLE AUFGABEN ABGESCHLOSSEN" not in silent_console.getvalue()


def test_status_table_partial(isolated_dirs, silent_console):
    reports_dir = isolated_dirs["reports"]
    (reports_dir / "task_2_Test.md").write_text("# 2\n", encoding="utf-8")
    (reports_dir / "task_5_Test.md").write_text("# 5\n", encoding="utf-8")

    from openclaw_cert.display import status_table
    completed = status_table()
    assert completed == {2, 5}


def test_list_streams_with_files(isolated_dirs, silent_console):
    streams_dir = isolated_dirs["streams"]
    (streams_dir / "stream_1.txt").write_text("Hello Stream", encoding="utf-8")
    (streams_dir / "stream_1.jsonl").write_text('{"ts":"now"}\n', encoding="utf-8")

    from openclaw_cert.display import list_streams
    list_streams()
    output = silent_console.getvalue()
    assert "stream_1.txt" in output
    assert "stream_1.jsonl" in output


def test_list_streams_empty(isolated_dirs, silent_console):
    from openclaw_cert.display import list_streams
    list_streams()
    assert "Keine Stream-Dateien" in silent_console.getvalue()
