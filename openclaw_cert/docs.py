"""
KI-Dokumentation: Generiert technische Doku via OpenAI-Stream.
"""
from __future__ import annotations

import datetime
import logging

from openai import OpenAI

from openclaw_cert import config
from openclaw_cert.api import stream_with_retry

_DOCS_PROMPT = """Erstelle eine vollständige technische Dokumentation für das OpenClaw Master-Zertifizierungs-CLI.

## Zu dokumentierende Komponenten

### Klasse: StreamTee
- `__init__`, `write`, `full_text`, `save_markdown`, `close`, `summary`

### Funktionen
- `run_task(task_num, client)` — Einzelaufgabe mit Live-Streaming + Retry-Logik (3 Versuche, exponentielles Backoff: 1s→2s→4s)
- `run_all_tasks(client, completed)` — Batch-Durchlauf
- `generate_combined_report()` — Alle Reports zusammenfassen
- `generate_finale_readme()` — Finale Zusammenfassung mit Task-Status
- `generate_docs(client)` — Diese Dokumentation (selbstreferenziell)
- `startup_display()` — README beim Start  (Gedächtnis-Aktivierung)
- `stream_config_menu()` — Speicher-Konfiguration
- `status_table()` — Aufgaben-Übersicht
- `list_streams()` — Stream-Dateien anzeigen
- `show_report(task_num)` — Report anzeigen
- `main_menu()` — Hauptmenü-Loop

### CLI-Argumente
`1`–`6`, `all`, `report`, `streams`, `docs`, `ende`, `--debug`

### Konfiguration
`STREAM_CONFIG`, `OPENCLAW_MODEL`, `LOG_DIR`, `DEBUG`

## Maschinelles Lernen
Erläutere, wie das Tool KI-gestütztes Lernen nutzt: Chain-of-Thought, Streaming-Inference, Zertifizierungsmethodik, Retry-Resilienz.

Für jede Funktion: Zweck, Parameter, Rückgabewert, Besonderheiten. Auf Deutsch verfassen."""


def generate_docs(client: OpenAI) -> None:
    """Generiert die CLI-Dokumentation als KI-gestreamtes Markdown."""
    from rich.rule import Rule

    config.console.print()
    config.console.print(Rule("[bold cyan]📚 KI-Funktionsdokumentation wird generiert[/bold cyan]"))
    config.console.print()
    config.console.print("[dim cyan]▶ Generiere Dokumentation via KI...[/dim cyan]\n")

    tee = stream_with_retry(
        client,
        task_num=0,
        task_title="CLI_Dokumentation",
        prompt=_DOCS_PROMPT,
        panel_title="📚 CLI-Dokumentation",
    )

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out_path = config.REPORT_DIR / "OPENCLAW_CERT_CLI_DOKUMENTATION.md"

    out_path.write_text(
        f"# 📚 OpenClaw Cert-CLI — Technische Dokumentation\n\n"
        f"> **{config.PRODUCT}** · Entwickelt von {config.DEVELOPER}  \n"
        f"> Erstellt: {timestamp}\n\n"
        f"---\n\n"
        f"{tee.full_text()}\n\n"
        f"---\n\n"
        f"*OpenClaw Master-Zertifizierungs-CLI · {config.PRODUCT} · {config.DEVELOPER}*\n",
        encoding="utf-8",
    )

    logging.info("Dokumentation gespeichert: %s", out_path)
    from rich.panel import Panel
    config.console.print(Panel(
        f"[bold green]📚 Dokumentation gespeichert:[/bold green]\n[cyan]{out_path}[/cyan]\n"
        f"[dim]{len(tee.full_text())} Zeichen[/dim]",
        border_style="green",
        padding=(1, 2),
    ))
