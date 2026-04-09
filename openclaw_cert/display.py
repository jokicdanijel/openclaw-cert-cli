"""
Display-Funktionen: Banner, Status-Tabelle, Stream-Listing, Report-Anzeige.
"""
from __future__ import annotations

import datetime
import logging
from pathlib import Path

from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from openclaw_cert import config
from openclaw_cert.tasks import TASKS


def banner() -> None:
    """Bildschirm leeren und Banner anzeigen."""
    config.console.clear()
    config.console.print()
    config.console.print(Panel.fit(
        f"[bold cyan]🦞  OPENCLAW MASTER-ZERTIFIZIERUNGS-CLI[/bold cyan]\n"
        f"[white]Firefly Copilot Edition  ·  {config.PRODUCT}[/white]\n"
        f"[dim]Entwickelt von {config.DEVELOPER}[/dim]",
        border_style="cyan",
        padding=(1, 4),
    ))
    config.console.print()


def status_table() -> set[int]:
    """Zeigt Task-Übersicht und gibt das Set der abgeschlossenen Task-Nummern zurück."""
    reports = list(config.REPORT_DIR.glob("task_*.md"))
    completed: set[int] = set()
    for r in reports:
        try:
            completed.add(int(r.stem.split("_")[1]))
        except (ValueError, IndexError):
            logging.warning("status_table: unerwarteter Dateiname ignoriert: %s", r.name)

    table = Table(
        title="[bold]Zertifizierungs-Aufgaben Übersicht[/bold]",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("#", style="bold", width=3, justify="center")
    table.add_column("", width=4, justify="center")
    table.add_column("Aufgabe", style="bold white")
    table.add_column("Beschreibung", style="dim")
    table.add_column("Status", width=12, justify="center")

    for num, task in TASKS.items():
        status = "[bold green]✓ Fertig[/bold green]" if num in completed else "[yellow]○ Offen[/yellow]"
        table.add_row(
            str(num), task["icon"], task["title"],
            task["description"][:52] + "…", status,
        )

    config.console.print(table)
    config.console.print()

    if len(completed) == len(TASKS):
        config.console.print(Panel(
            "[bold green]🏆 ALLE AUFGABEN ABGESCHLOSSEN![/bold green]\n"
            "[green]Firefly Copilot ist als OpenClaw Master-Experte zertifiziert.[/green]",
            border_style="green",
        ))
        config.console.print()

    return completed


def list_streams() -> None:
    """Zeigt alle gespeicherten Stream-Dateien."""
    files = sorted(config.STREAM_DIR.iterdir()) if config.STREAM_DIR.exists() else []
    if not files:
        config.console.print("[yellow]Keine Stream-Dateien vorhanden.[/yellow]")
        return

    table = Table(
        title="[bold]Gespeicherte Stream-Dateien[/bold]",
        box=box.SIMPLE,
        border_style="cyan",
        header_style="bold cyan",
    )
    table.add_column("Datei", style="cyan")
    table.add_column("Größe", justify="right", style="white")
    table.add_column("Erstellt", style="dim")

    for f in files:
        stat = f.stat()
        size = f"{stat.st_size / 1024:.1f} KB"
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        table.add_row(f.name, size, mtime)

    config.console.print(table)


def show_report(task_num: int) -> None:
    """Zeigt den Report einer einzelnen Aufgabe an."""
    reports = list(config.REPORT_DIR.glob(f"task_{task_num}_*.md"))
    if not reports:
        config.console.print(f"[yellow]Kein Report für Aufgabe {task_num} gefunden.[/yellow]")
        return
    content = reports[0].read_text(encoding="utf-8")
    config.console.print(Markdown(content))


def startup_display() -> None:
    """Zeigt README beim Start — Gedächtnis-Aktivierung."""
    readme_candidates = [
        Path(__file__).parent.parent / "cert-cli-uc" / "README.md",
        Path(__file__).parent.parent / "🦞 OpenClaw Master-Zertifizierungs-CLI",
    ]
    for path in readme_candidates:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            config.console.print(Panel(
                Markdown(content),
                title="[bold cyan]🧠 Gedächtnis aktiviert — System-Zustand bekannt[/bold cyan]",
                border_style="cyan",
                padding=(1, 2),
            ))
            config.console.print()
            logging.info("startup_display: README geladen: %s", path)
            return
    config.console.print(Panel(
        "[dim]README nicht gefunden — starte ohne Gedächtnis-Aktivierung[/dim]",
        border_style="dim",
        padding=(0, 2),
    ))
    config.console.print()


def stream_config_menu() -> None:
    """Interaktives Menü zum Anpassen der Speicher-Optionen."""
    from rich.prompt import Prompt

    cfg = config.STREAM_CONFIG

    config.console.print()
    config.console.print(Panel(
        "[bold cyan]Streaming-Speicher-Konfiguration[/bold cyan]\n\n"
        f"  [cyan]\\[1][/cyan]  Markdown-Report speichern:  "
        f"{'[green]AN[/green]' if cfg['save_markdown'] else '[red]AUS[/red]'}\n"
        f"  [cyan]\\[2][/cyan]  Raw-Stream (.txt) speichern: "
        f"{'[green]AN[/green]' if cfg['save_raw'] else '[red]AUS[/red]'}\n"
        f"  [cyan]\\[3][/cyan]  JSON-Lines-Log speichern:    "
        f"{'[green]AN[/green]' if cfg['save_jsonl'] else '[red]AUS[/red]'}\n"
        f"  [cyan]\\[b][/cyan]  Zurück",
        border_style="cyan",
        padding=(1, 2),
    ))

    choice = Prompt.ask(
        "[bold cyan]Auswahl[/bold cyan]",
        choices=["1", "2", "3", "b"],
        show_choices=False,
    )
    toggle_map = {"1": "save_markdown", "2": "save_raw", "3": "save_jsonl"}
    if choice in toggle_map:
        key = toggle_map[choice]
        cfg[key] = not cfg[key]
