"""
Tests für listener.py — Live-Datei-Watcher.

3 Tests: tail_file liest neue Zeilen, watch_directory erkennt neue Dateien, leeres Verzeichnis
"""

import threading
import time
from pathlib import Path

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: tail_file liest neue Zeilen aus einer Datei
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.slow
def test_tail_file_reads_new_lines(tmp_path, capsys):
    """tail_file() liest neue Zeilen, die an eine Datei angehängt werden."""
    from listener import tail_file

    test_file = tmp_path / "test.txt"
    test_file.write_text("initial\n", encoding="utf-8")

    # tail_file startet am Ende → sieht "initial" nicht
    t = threading.Thread(
        target=tail_file,
        args=(test_file, "TEST", "\033[96m"),
        daemon=True,
    )
    t.start()

    # Kurz warten, dann neue Zeile anhängen
    time.sleep(0.3)
    with open(test_file, "a", encoding="utf-8") as f:
        f.write("neue Zeile\n")

    # Warten bis tail_file die Zeile liest
    time.sleep(0.5)

    captured = capsys.readouterr()
    assert "neue Zeile" in captured.out


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: watch_directory erkennt neue Dateien und startet Threads
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.slow
def test_watch_directory_detects_new_file(tmp_path, capsys):
    """watch_directory() erkennt eine neue .txt-Datei und gibt 'NEU' aus."""
    from listener import watch_directory

    watch_dir = tmp_path / "streams"
    watch_dir.mkdir()

    t = threading.Thread(
        target=watch_directory,
        args=(watch_dir, ".txt", "STREAM", "\033[96m"),
        daemon=True,
    )
    t.start()

    # Neue Datei erstellen
    time.sleep(1.5)
    (watch_dir / "stream_new.txt").write_text("Hallo\n", encoding="utf-8")

    time.sleep(1.5)

    captured = capsys.readouterr()
    assert "NEU" in captured.out
    assert "stream_new.txt" in captured.out


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: watch_directory mit leerem Verzeichnis — kein Crash
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.slow
def test_watch_directory_empty(tmp_path):
    """watch_directory() auf leerem Verzeichnis: läuft ohne Fehler."""
    from listener import watch_directory

    watch_dir = tmp_path / "empty"
    # Verzeichnis existiert noch nicht → watch_directory erstellt es

    t = threading.Thread(
        target=watch_directory,
        args=(watch_dir, ".txt", "TEST", "\033[96m"),
        daemon=True,
    )
    t.start()

    time.sleep(1.5)

    # Verzeichnis wurde erstellt (mkdir parents=True in watch_directory)
    assert watch_dir.exists()
    # Thread läuft noch (daemon, kein Crash)
    assert t.is_alive()
