"""Tests für die StreamTee-Klasse (openclaw_cert.stream_tee)."""

import json
import threading
from pathlib import Path

import pytest


def test_init_creates_files(isolated_dirs):
    """StreamTee.__init__ erstellt Raw- und JSONL-Dateien im STREAM_DIR."""
    from openclaw_cert.stream_tee import StreamTee

    tee = StreamTee(task_num=1, task_title="Test Aufgabe", save_raw=True, save_jsonl=True)
    try:
        assert tee.raw_path is not None and tee.raw_path.exists()
        header = tee.raw_path.read_text(encoding="utf-8")
        assert "Aufgabe 1: Test Aufgabe" in header
        assert "─" * 70 in header

        assert tee.jsonl_path is not None and tee.jsonl_path.exists()

        streams_dir = isolated_dirs["streams"]
        assert str(tee.raw_path).startswith(str(streams_dir))
        assert str(tee.jsonl_path).startswith(str(streams_dir))
    finally:
        tee.close()


def test_write_stores_chunks(isolated_dirs):
    """write() schreibt in Puffer, Raw und JSONL."""
    from openclaw_cert.stream_tee import StreamTee

    tee = StreamTee(task_num=2, task_title="Write Test", save_raw=True, save_jsonl=True)
    try:
        tee.write("Hallo ")
        tee.write("Welt!")
        assert tee.chunks == ["Hallo ", "Welt!"]

        tee._raw_fh.flush()
        raw = tee.raw_path.read_text(encoding="utf-8")
        assert "Hallo " in raw and "Welt!" in raw

        lines = tee.jsonl_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0])["chunk"] == "Hallo "
        assert json.loads(lines[1])["task"] == 2
    finally:
        tee.close()


def test_write_ignores_empty(isolated_dirs):
    """write('') schreibt nichts."""
    from openclaw_cert.stream_tee import StreamTee

    tee = StreamTee(task_num=3, task_title="Empty", save_raw=True, save_jsonl=True)
    try:
        tee.write("")
        tee.write("")
        tee.write("ok")
        assert tee.chunks == ["ok"]
        assert len(tee.jsonl_path.read_text(encoding="utf-8").strip().split("\n")) == 1
    finally:
        tee.close()


def test_full_text(isolated_dirs):
    """full_text() verbindet alle Chunks."""
    from openclaw_cert.stream_tee import StreamTee

    tee = StreamTee(task_num=4, task_title="FullText", save_raw=False, save_jsonl=False)
    try:
        assert tee.full_text() == ""
        tee.write("A")
        tee.write("B")
        tee.write("C")
        assert tee.full_text() == "ABC"
    finally:
        tee.close()


def test_save_markdown(isolated_dirs):
    """save_markdown() erzeugt korrekte .md-Datei."""
    from openclaw_cert.stream_tee import StreamTee

    tee = StreamTee(task_num=1, task_title="Kernkonzepte", save_raw=False, save_jsonl=False)
    try:
        tee.write("# Kernkonzepte\n\nDies ist der Inhalt.")
        report_path = tee.save_markdown(isolated_dirs["reports"])

        assert report_path.exists()
        content = report_path.read_text(encoding="utf-8")
        assert "Aufgabe 1: Kernkonzepte" in content
        assert "Dies ist der Inhalt." in content
        assert "Firefly Copilot" in content
        assert report_path.name.startswith("task_1_")
    finally:
        tee.close()


def test_close_writes_footer(isolated_dirs):
    """close() schreibt Footer mit Dauer und Zeichenanzahl."""
    from openclaw_cert.stream_tee import StreamTee

    tee = StreamTee(task_num=5, task_title="Close Test", save_raw=True, save_jsonl=True)
    tee.write("Inhalt hier.")
    tee.close()

    raw = tee.raw_path.read_text(encoding="utf-8")
    assert "Stream beendet" in raw
    assert "Dauer:" in raw
    assert tee._raw_fh.closed
    assert tee._jsonl_fh.closed


def test_summary_lists_files(isolated_dirs):
    """summary() gibt korrekte Datei-Labels zurück."""
    from openclaw_cert.stream_tee import StreamTee

    tee = StreamTee(task_num=6, task_title="Summary", save_raw=True, save_jsonl=True)
    try:
        files = tee.summary()
        assert len(files) == 2
        labels = [f[0] for f in files]
        assert "Raw-Stream (.txt)" in labels
        assert "JSON-Lines-Log (.jsonl)" in labels
    finally:
        tee.close()

    tee_none = StreamTee(task_num=6, task_title="Summary2", save_raw=False, save_jsonl=False)
    try:
        assert tee_none.summary() == []
    finally:
        tee_none.close()


@pytest.mark.slow
def test_thread_safety(isolated_dirs):
    """Parallele Writes verlieren keine Daten."""
    from openclaw_cert.stream_tee import StreamTee

    tee = StreamTee(task_num=1, task_title="Concurrency", save_raw=True, save_jsonl=True)
    num_threads, writes_per = 10, 50
    barrier = threading.Barrier(num_threads)

    def writer(tid):
        barrier.wait()
        for i in range(writes_per):
            tee.write(f"T{tid}-{i} ")

    threads = [threading.Thread(target=writer, args=(t,)) for t in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    tee.close()

    assert len(tee.chunks) == num_threads * writes_per
    jsonl = tee.jsonl_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(jsonl) == num_threads * writes_per
