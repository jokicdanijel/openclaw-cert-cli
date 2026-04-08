#!/usr/bin/env python3
"""
OpenClaw Live-Listener — zeigt Streams und Logs in Echtzeit.
Startet mit: python3 listener.py
"""

import os
import sys
import time
import threading
from pathlib import Path

BASE_DIR = Path(__file__).parent
STREAMS_DIR = BASE_DIR / "streams"
LOGS_DIR = BASE_DIR / "logs"

# ANSI-Farben
RESET  = "\033[0m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
GREY   = "\033[90m"
BOLD   = "\033[1m"

def header(title: str, color: str = CYAN) -> str:
    bar = "─" * 60
    return f"\n{color}{BOLD}{bar}\n  {title}\n{bar}{RESET}"

def tail_file(path: Path, label: str, color: str) -> None:
    """Liest eine Datei ab und folgt ihr bei neuen Zeilen."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            f.seek(0, 2)  # ans Ende springen (nur neue Inhalte)
            while True:
                line = f.readline()
                if line:
                    ts = time.strftime("%H:%M:%S")
                    print(f"{GREY}[{ts}]{RESET} {color}{label}{RESET}  {line}", end="")
                    sys.stdout.flush()
                else:
                    time.sleep(0.15)
    except Exception:
        pass

def watch_directory(directory: Path, ext: str, label_prefix: str, color: str) -> None:
    """Beobachtet ein Verzeichnis auf neue Dateien und startet tail pro Datei."""
    seen: set = set()
    directory.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            current = {p for p in directory.glob(f"*{ext}") if p.is_file()}
            new_files = current - seen
            for f in sorted(new_files, key=lambda x: x.stat().st_mtime):
                label = f"{label_prefix}: {f.name[:40]}"
                print(header(f"NEU → {label}", color))
                t = threading.Thread(target=tail_file, args=(f, label, color), daemon=True)
                t.start()
                seen.add(f)
        except Exception:
            pass
        time.sleep(1)

def main() -> None:
    print(header("OpenClaw Live-Listener gestartet", GREEN))
    print(f"{GREY}Beobachte: {STREAMS_DIR}  |  {LOGS_DIR}{RESET}")
    print(f"{GREY}Abbrechen mit Ctrl+C{RESET}\n")

    # Streams (txt) — Hauptausgabe der API-Antworten
    t_streams = threading.Thread(
        target=watch_directory,
        args=(STREAMS_DIR, ".txt", "STREAM", CYAN),
        daemon=True,
    )
    # Debug-Logs
    t_logs = threading.Thread(
        target=watch_directory,
        args=(LOGS_DIR, ".log", "LOG", YELLOW),
        daemon=True,
    )

    t_streams.start()
    t_logs.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print(f"\n{GREY}Listener gestoppt.{RESET}\n")

if __name__ == "__main__":
    main()
