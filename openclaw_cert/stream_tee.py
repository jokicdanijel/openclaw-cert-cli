"""
StreamTee — paralleles Schreiben in Terminal, Raw-Text und JSONL.

Jeder Streaming-Chunk wird Thread-safe in drei Kanäle geschrieben:
  1. Interner Puffer  (für Live-Panel + save_markdown)
  2. Raw-Textdatei    (.txt, jeder Chunk sofort geflusht)
  3. JSON-Lines-Log   (.jsonl, Timestamp + Chunk pro Zeile)
"""
from __future__ import annotations

import datetime
import json
import threading
from pathlib import Path

from openclaw_cert import config


class StreamTee:
    """Thread-safe Streaming-Tee für gleichzeitiges Schreiben in mehrere Kanäle."""

    def __init__(
        self,
        task_num: int,
        task_title: str,
        *,
        save_raw: bool,
        save_jsonl: bool,
    ) -> None:
        self.task_num = task_num
        self.task_title = task_title
        self.chunks: list[str] = []
        self.start_time = datetime.datetime.now()

        ts = self.start_time.strftime("%Y%m%d_%H%M%S")
        safe = task_title.replace(" ", "_").replace("/", "-").replace(":", "")[:30]

        self._raw_fh = None
        self._jsonl_fh = None
        self._lock = threading.Lock()
        self.raw_path: Path | None = None
        self.jsonl_path: Path | None = None

        if save_raw:
            self.raw_path = config.STREAM_DIR / f"stream_{task_num}_{safe}_{ts}.txt"
            self._raw_fh = open(self.raw_path, "w", encoding="utf-8", buffering=1)
            self._raw_fh.write(
                f"# OpenClaw Stream · Aufgabe {task_num}: {task_title}\n"
                f"# Gestartet: {self.start_time.isoformat()}\n"
                f"# {config.PRODUCT} · {config.DEVELOPER}\n"
                f"{'─' * 70}\n\n"
            )

        if save_jsonl:
            self.jsonl_path = config.STREAM_DIR / f"stream_{task_num}_{safe}_{ts}.jsonl"
            self._jsonl_fh = open(self.jsonl_path, "w", encoding="utf-8", buffering=1)

    # ── Streaming ────────────────────────────────────────────────────────────

    def write(self, chunk: str) -> None:
        """Nimmt einen Streaming-Chunk entgegen und schreibt ihn in alle Kanäle."""
        if not chunk:
            return
        with self._lock:
            self.chunks.append(chunk)
            ts = datetime.datetime.now().isoformat()

            if self._raw_fh:
                self._raw_fh.write(chunk)

            if self._jsonl_fh:
                record = {"ts": ts, "chunk": chunk, "task": self.task_num}
                self._jsonl_fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def full_text(self) -> str:
        """Gibt den gesamten bisher gesammelten Text zurück."""
        return "".join(self.chunks)

    # ── Persistenz ───────────────────────────────────────────────────────────

    def save_markdown(self, report_dir: Path) -> Path:
        """Speichert den vollständigen Markdown-Report."""
        from openclaw_cert.tasks import TASKS

        result_text = self.full_text()
        timestamp = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        safe = self.task_title.replace(" ", "_").replace("/", "-").replace(":", "")[:35]
        report_path = report_dir / f"task_{self.task_num}_{safe}.md"
        icon = TASKS.get(self.task_num, {}).get("icon", "📄")

        content = (
            f"# {icon} Aufgabe {self.task_num}: {self.task_title}\n\n"
            f"> **Firefly Copilot · OpenClaw Master-Zertifizierung**  \n"
            f"> **{config.PRODUCT}** · Entwickelt von {config.DEVELOPER}  \n"
            f"> Erstellt: {timestamp}\n\n"
            f"---\n\n"
            f"{result_text}\n\n"
            f"---\n\n"
            f"*OpenClaw Master-Zertifizierungs-CLI · {config.PRODUCT} · {config.DEVELOPER}*\n"
        )
        report_path.write_text(content, encoding="utf-8")
        return report_path

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def close(self) -> None:
        """Schließt alle offenen Datei-Handles."""
        elapsed = (datetime.datetime.now() - self.start_time).total_seconds()
        if self._raw_fh:
            self._raw_fh.write(
                f"\n\n{'─' * 70}\n"
                f"# Stream beendet · Dauer: {elapsed:.1f}s · "
                f"{len(self.full_text())} Zeichen\n"
            )
            self._raw_fh.close()
        if self._jsonl_fh:
            self._jsonl_fh.close()

    def summary(self) -> list[tuple[str, str]]:
        """Gibt eine Liste gespeicherter Dateien zurück (Label, Pfad)."""
        files: list[tuple[str, str]] = []
        if self.raw_path:
            files.append(("Raw-Stream (.txt)", str(self.raw_path)))
        if self.jsonl_path:
            files.append(("JSON-Lines-Log (.jsonl)", str(self.jsonl_path)))
        return files
