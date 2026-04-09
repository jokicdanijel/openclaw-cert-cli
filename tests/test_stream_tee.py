"""
Tests für die StreamTee-Klasse in openclaw_cert.py.

StreamTee ist die zentrale Streaming-Komponente:
  - Schreibt gleichzeitig in Terminal, Raw-Text (.txt) und JSONL (.jsonl)
  - Thread-safe via Lock
  - Verwaltet Datei-Handles mit sauberem close()

8 Tests: init, write, full_text, save_markdown, close, summary, disabled_outputs, thread_safety
"""

import json
import threading
from pathlib import Path

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: __init__ erstellt Dateien und Header korrekt
# ─────────────────────────────────────────────────────────────────────────────

def test_init_creates_files(isolated_dirs):
    """StreamTee.__init__ erstellt Raw- und JSONL-Dateien im STREAM_DIR."""
    from openclaw_cert import StreamTee

    tee = StreamTee(task_num=1, task_title="Test Aufgabe", save_raw=True, save_jsonl=True)

    try:
        # Raw-Datei existiert und hat Header
        assert tee.raw_path is not None
        assert tee.raw_path.exists()
        header = tee.raw_path.read_text(encoding="utf-8")
        assert "Aufgabe 1: Test Aufgabe" in header
        assert "─" * 70 in header

        # JSONL-Datei existiert (noch leer, kein Header)
        assert tee.jsonl_path is not None
        assert tee.jsonl_path.exists()

        # Pfade liegen im STREAM_DIR
        streams_dir = isolated_dirs["streams"]
        assert str(tee.raw_path).startswith(str(streams_dir))
        assert str(tee.jsonl_path).startswith(str(streams_dir))
    finally:
        tee.close()


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: write() speichert Chunks in Raw + JSONL
# ─────────────────────────────────────────────────────────────────────────────

def test_write_stores_chunks(isolated_dirs):
    """write() schreibt Chunks in die internen Puffer und in beide Dateien."""
    from openclaw_cert import StreamTee

    tee = StreamTee(task_num=2, task_title="Write Test", save_raw=True, save_jsonl=True)

    try:
        tee.write("Hallo ")
        tee.write("Welt!")

        # Interner Puffer
        assert tee.chunks == ["Hallo ", "Welt!"]

        # Raw-Datei: line-buffered → flush vor dem Lesen nötig
        tee._raw_fh.flush()
        raw_content = tee.raw_path.read_text(encoding="utf-8")
        assert "Hallo " in raw_content
        assert "Welt!" in raw_content

        # JSONL: Zwei Zeilen, jede mit ts, chunk, task
        jsonl_content = tee.jsonl_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(jsonl_content) == 2

        record1 = json.loads(jsonl_content[0])
        assert record1["chunk"] == "Hallo "
        assert record1["task"] == 2
        assert "ts" in record1

        record2 = json.loads(jsonl_content[1])
        assert record2["chunk"] == "Welt!"
    finally:
        tee.close()


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: write() ignoriert leere Strings
# ─────────────────────────────────────────────────────────────────────────────

def test_write_ignores_empty(isolated_dirs):
    """write('') und write(None-äquivalent) schreibt nichts."""
    from openclaw_cert import StreamTee

    tee = StreamTee(task_num=3, task_title="Empty Test", save_raw=True, save_jsonl=True)

    try:
        tee.write("")
        tee.write("")
        tee.write("ok")

        assert tee.chunks == ["ok"]
        assert len(tee.jsonl_path.read_text(encoding="utf-8").strip().split("\n")) == 1
    finally:
        tee.close()


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: full_text() verbindet alle Chunks
# ─────────────────────────────────────────────────────────────────────────────

def test_full_text(isolated_dirs):
    """full_text() gibt den gesamten Text als einen String zurück."""
    from openclaw_cert import StreamTee

    tee = StreamTee(task_num=4, task_title="FullText", save_raw=False, save_jsonl=False)

    try:
        assert tee.full_text() == ""

        tee.write("A")
        tee.write("B")
        tee.write("C")

        assert tee.full_text() == "ABC"
    finally:
        tee.close()


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: save_markdown() erstellt korrekten Report
# ─────────────────────────────────────────────────────────────────────────────

def test_save_markdown(isolated_dirs):
    """save_markdown() erzeugt eine .md-Datei mit Header, Inhalt und Footer."""
    from openclaw_cert import StreamTee

    tee = StreamTee(task_num=1, task_title="Kernkonzepte", save_raw=False, save_jsonl=False)

    try:
        tee.write("# Kernkonzepte\n\nDies ist der Inhalt.")

        report_path = tee.save_markdown(isolated_dirs["reports"])

        assert report_path.exists()
        content = report_path.read_text(encoding="utf-8")

        # Header-Elemente
        assert "Aufgabe 1: Kernkonzepte" in content
        assert "Firefly Copilot" in content
        assert "HyperDashboard-ONE.DE" in content

        # Inhalt
        assert "Dies ist der Inhalt." in content

        # Footer
        assert "Danijel Jokic" in content

        # Dateiname-Format
        assert report_path.name.startswith("task_1_")
        assert report_path.suffix == ".md"
    finally:
        tee.close()


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: close() schließt Handles und schreibt Footer
# ─────────────────────────────────────────────────────────────────────────────

def test_close_writes_footer(isolated_dirs):
    """close() schreibt einen Footer mit Dauer und Zeichenanzahl in die Raw-Datei."""
    from openclaw_cert import StreamTee

    tee = StreamTee(task_num=5, task_title="Close Test", save_raw=True, save_jsonl=True)

    tee.write("Inhalt hier.")
    tee.close()

    raw_content = tee.raw_path.read_text(encoding="utf-8")
    assert "Stream beendet" in raw_content
    assert "Dauer:" in raw_content
    assert "Zeichen" in raw_content

    # Handles sind geschlossen — erneuter write sollte fehlschlagen
    assert tee._raw_fh.closed
    assert tee._jsonl_fh.closed


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: summary() listet gespeicherte Dateien korrekt
# ─────────────────────────────────────────────────────────────────────────────

def test_summary_lists_files(isolated_dirs):
    """summary() gibt Labels und Pfade der gespeicherten Dateien zurück."""
    from openclaw_cert import StreamTee

    # Beide aktiviert
    tee_both = StreamTee(task_num=6, task_title="Summary", save_raw=True, save_jsonl=True)
    try:
        files = tee_both.summary()
        assert len(files) == 2
        labels = [f[0] for f in files]
        assert "Raw-Stream (.txt)" in labels
        assert "JSON-Lines-Log (.jsonl)" in labels
    finally:
        tee_both.close()

    # Beide deaktiviert
    tee_none = StreamTee(task_num=6, task_title="Summary2", save_raw=False, save_jsonl=False)
    try:
        assert tee_none.summary() == []
        assert tee_none.raw_path is None
        assert tee_none.jsonl_path is None
    finally:
        tee_none.close()


# ─────────────────────────────────────────────────────────────────────────────
# Test 8: Thread-Safety — parallele writes verlieren keine Daten
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.slow
def test_thread_safety(isolated_dirs):
    """Mehrere Threads schreiben gleichzeitig — kein Datenverlust."""
    from openclaw_cert import StreamTee

    tee = StreamTee(task_num=1, task_title="Concurrency", save_raw=True, save_jsonl=True)

    num_threads = 10
    writes_per_thread = 50
    barrier = threading.Barrier(num_threads)

    def writer(thread_id):
        barrier.wait()  # Alle Threads starten gleichzeitig
        for i in range(writes_per_thread):
            tee.write(f"T{thread_id}-{i} ")

    threads = [
        threading.Thread(target=writer, args=(t,))
        for t in range(num_threads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    tee.close()

    # Alle Chunks da?
    expected_total = num_threads * writes_per_thread
    assert len(tee.chunks) == expected_total

    # JSONL: gleiche Anzahl Zeilen
    jsonl_lines = tee.jsonl_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(jsonl_lines) == expected_total

    # Jede JSONL-Zeile ist valides JSON
    for line in jsonl_lines:
        record = json.loads(line)
        assert "chunk" in record
        assert "ts" in record
