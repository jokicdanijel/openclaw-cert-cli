"""
Report-Generierung: Gesamtreport und Finale Zusammenfassung.
"""
from __future__ import annotations

import datetime
import logging
from pathlib import Path

from openclaw_cert import config
from openclaw_cert.tasks import TASKS


def generate_combined_report() -> None:
    """Fasst alle Task-Reports zu einem Gesamt-Dokument zusammen."""
    reports = sorted(config.REPORT_DIR.glob("task_*.md"))
    if not reports:
        config.console.print("[yellow]Keine Reports gefunden.[/yellow]")
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    combined_path = config.REPORT_DIR / "OPENCLAW_MASTER_ZERTIFIZIERUNG_KOMPLETT.md"

    with open(combined_path, "w", encoding="utf-8") as out:
        out.write(
            f"# 🦞 OpenClaw Master-Zertifizierung — Vollständiger Report\n\n"
            f"> **Firefly Copilot · Zertifiziert als OpenClaw Systemexperte**  \n"
            f"> **{config.PRODUCT}** · Entwickelt von {config.DEVELOPER}  \n"
            f"> Abschlussdatum: {timestamp}\n\n"
            f"---\n\n## Inhaltsverzeichnis\n\n"
        )
        for i, task in TASKS.items():
            out.write(f"{i}. {task['icon']} {task['title']}\n")
        out.write("\n---\n\n")

        for rp in reports:
            out.write(rp.read_text(encoding="utf-8"))
            out.write("\n\n---\n\n")

        out.write(
            f"## 🏆 Zertifizierungsbestätigung\n\n"
            f"Hiermit wird bestätigt, dass **Firefly Copilot** alle 6 Aufgaben der  \n"
            f"**OpenClaw Master-Zertifizierung** erfolgreich abgeschlossen hat.\n\n"
            f"**Zertifiziert für:** {config.PRODUCT}  \n"
            f"**Ausgestellt von:** {config.DEVELOPER}  \n"
            f"**Datum:** {timestamp}  \n"
            f"**Status:** ✅ ZERTIFIZIERT\n\n"
            f"---\n"
            f"*OpenClaw Master-Zertifizierungs-CLI · {config.PRODUCT} · {config.DEVELOPER}*\n"
        )

    from rich.panel import Panel
    config.console.print(Panel(
        f"[bold green]📄 Gesamtreport erstellt:[/bold green]\n[cyan]{combined_path}[/cyan]",
        border_style="green",
        padding=(1, 2),
    ))


def generate_finale_readme() -> str:
    """Erstellt FINALE_ZUSAMMENFASSUNG mit Status aller Tasks."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_slug = datetime.datetime.now().strftime("%Y-%m-%d")
    reports = list(config.REPORT_DIR.glob("task_*.md"))
    completed = {int(r.stem.split("_")[1]) for r in reports}
    out_path = config.REPORT_DIR / f"FINALE_ZUSAMMENFASSUNG_{date_slug}.md"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(
            f"# 🦞 OpenClaw Cert-CLI — Finale Zusammenfassung\n\n"
            f"> **{config.PRODUCT}** · Entwickelt von {config.DEVELOPER}  \n"
            f"> Erstellt: {timestamp}\n\n"
            f"---\n\n"
            f"## Status aller Aufgaben\n\n"
            f"| # | Aufgabe | Status | Report |\n"
            f"|---|---------|--------|--------|\n"
        )
        for num, task in TASKS.items():
            status = "✅ Abgeschlossen" if num in completed else "⏳ Offen"
            rfiles = list(config.REPORT_DIR.glob(f"task_{num}_*.md"))
            link = f"[{rfiles[0].name}](./{rfiles[0].name})" if rfiles else "—"
            f.write(f"| {num} | {task['icon']} {task['title']} | {status} | {link} |\n")

        log_files = sorted(config.LOG_DIR.glob("debug_*.log")) if config.LOG_DIR.exists() else []
        f.write(
            f"\n---\n\n"
            f"## Systemzustand\n\n"
            f"- **Abgeschlossen:** {len(completed)}/{len(TASKS)} Aufgaben\n"
            f"- **Modell:** `{config.OPENCLAW_MODEL}`\n"
            f"- **Debug-Modus:** `{'AN' if config.DEBUG else 'AUS'}`\n"
            f"- **Report-Verzeichnis:** `{config.REPORT_DIR.resolve()}`\n"
            f"- **Stream-Verzeichnis:** `{config.STREAM_DIR.resolve()}`\n"
        )
        if log_files:
            f.write(f"- **Letzte Log-Datei:** `{log_files[-1]}`\n")

        if len(completed) == len(TASKS):
            f.write(
                f"\n---\n\n"
                f"## 🏆 Zertifizierungsbestätigung\n\n"
                f"**Firefly Copilot** hat alle 6 Aufgaben erfolgreich abgeschlossen.\n\n"
                f"**Status:** ✅ ZERTIFIZIERT  \n"
                f"**Datum:** {timestamp}  \n"
                f"**Ausgestellt von:** {config.DEVELOPER}  \n"
            )
        f.write(
            f"\n---\n"
            f"*OpenClaw Master-Zertifizierungs-CLI · {config.PRODUCT} · {config.DEVELOPER}*\n"
        )

    logging.info("Finale Zusammenfassung erstellt: %s", out_path)
    from rich.panel import Panel
    config.console.print(Panel(
        f"[bold green]✅ Finale Zusammenfassung erstellt:[/bold green]\n[cyan]{out_path}[/cyan]",
        border_style="green",
        padding=(1, 2),
    ))
    return str(out_path)
