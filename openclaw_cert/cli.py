"""
CLI-Dispatch und interaktives Hauptmenü.
"""
from __future__ import annotations

import logging
import sys
import time

from openai import OpenAI
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.rule import Rule

from openclaw_cert import config
from openclaw_cert.api import get_openai_client, stream_with_retry
from openclaw_cert.display import (
    banner,
    list_streams,
    show_report,
    startup_display,
    status_table,
    stream_config_menu,
)
from openclaw_cert.docs import generate_docs
from openclaw_cert.reports import generate_combined_report, generate_finale_readme
from openclaw_cert.tasks import TASKS


# ─────────────────────────────────────────────────────────────────────────────
#  Einzelne Aufgabe ausführen
# ─────────────────────────────────────────────────────────────────────────────

def run_task(task_num: int, client: OpenAI) -> str:
    """Führt eine einzelne Zertifizierungsaufgabe aus und gibt den Report-Pfad zurück."""
    task = TASKS[task_num]
    cfg = config.STREAM_CONFIG

    config.console.print()
    config.console.print(Rule(
        f"[bold cyan]{task['icon']} Aufgabe {task_num}: {task['title']}[/bold cyan]"
    ))
    config.console.print()
    config.console.print(Panel(
        f"[bold]Beschreibung:[/bold] {task['description']}\n\n"
        f"[dim]Speichern: "
        f"MD={'✓' if cfg['save_markdown'] else '✗'}  "
        f"RAW={'✓' if cfg['save_raw'] else '✗'}  "
        f"JSONL={'✓' if cfg['save_jsonl'] else '✗'}[/dim]",
        border_style="blue",
        padding=(0, 2),
    ))
    config.console.print()
    config.console.print(
        "[dim cyan]▶ Live-Streaming läuft · Daten werden gleichzeitig gespeichert...[/dim cyan]\n"
    )

    start_time = time.time()
    tee = stream_with_retry(
        client,
        task_num=task_num,
        task_title=task["title"],
        prompt=task["prompt"],
        panel_title=f"{task['icon']} Aufgabe {task_num}",
    )
    elapsed = time.time() - start_time

    config.console.print(
        f"\n[dim]✓ Stream abgeschlossen · {elapsed:.1f}s · "
        f"{len(tee.full_text())} Zeichen[/dim]"
    )
    config.console.print()

    # Markdown-Report speichern
    report_path = ""
    if cfg["save_markdown"] and tee.full_text():
        report_path = str(tee.save_markdown(config.REPORT_DIR))

    # Gespeicherte Dateien anzeigen
    saved_files: list[tuple[str, str]] = []
    if report_path:
        saved_files.append(("Markdown-Report (.md)", report_path))
    saved_files.extend(tee.summary())

    if saved_files:
        rows = "\n".join(
            f"  [green]✓[/green]  [dim]{label}:[/dim]  [cyan]{path}[/cyan]"
            for label, path in saved_files
        )
        config.console.print(Panel(
            f"[bold green]Gespeicherte Dateien:[/bold green]\n\n{rows}",
            border_style="green",
            padding=(1, 2),
        ))

    return report_path


def run_all_tasks(client: OpenAI, completed: set[int]) -> None:
    """Führt alle offenen Aufgaben sequenziell aus."""
    pending = [n for n in TASKS if n not in completed]
    if not pending:
        config.console.print("[bold green]Alle Aufgaben bereits abgeschlossen![/bold green]")
        return

    cfg = config.STREAM_CONFIG
    config.console.print(Panel(
        f"[bold cyan]Vollautomatischer Durchlauf[/bold cyan]\n"
        f"[white]{len(pending)} Aufgabe(n) werden sequenziell bearbeitet.[/white]\n"
        f"[dim]Aufgaben: {', '.join(str(n) for n in pending)}[/dim]\n\n"
        f"[dim]Speichern: "
        f"MD={'✓' if cfg['save_markdown'] else '✗'}  "
        f"RAW={'✓' if cfg['save_raw'] else '✗'}  "
        f"JSONL={'✓' if cfg['save_jsonl'] else '✗'}[/dim]",
        border_style="cyan",
        padding=(1, 2),
    ))

    if not Confirm.ask("\n[yellow]Vollautomatischen Durchlauf starten?[/yellow]"):
        return

    reports: list[str] = []
    for i, task_num in enumerate(pending, 1):
        config.console.print(f"\n[dim]─── Fortschritt: {i}/{len(pending)} ───[/dim]")
        path = run_task(task_num, client)
        if path:
            reports.append(path)
        if i < len(pending):
            time.sleep(1)

    config.console.print()
    config.console.print(Rule("[bold green]🏆 ZERTIFIZIERUNGSDURCHLAUF ABGESCHLOSSEN[/bold green]"))
    config.console.print()
    for path in reports:
        config.console.print(f"  [green]✓[/green]  {path}")
    config.console.print()
    generate_combined_report()


# ─────────────────────────────────────────────────────────────────────────────
#  CLI-Argument-Dispatch
# ─────────────────────────────────────────────────────────────────────────────

def dispatch_cli_args() -> None:
    """Verarbeitet ``sys.argv[1]`` und ruft die passende Funktion auf."""
    arg = sys.argv[1]

    # Befehle ohne API-Key
    if arg == "report":
        generate_combined_report()
    elif arg == "streams":
        list_streams()
    elif arg == "ende":
        generate_finale_readme()
    elif arg in ("all", "docs") or (arg.isdigit() and 1 <= int(arg) <= 6):
        client = get_openai_client()
        if arg == "all":
            banner()
            completed = status_table()
            run_all_tasks(client, completed)
        elif arg == "docs":
            generate_docs(client)
        else:
            banner()
            run_task(int(arg), client)
    else:
        config.console.print(f"[red]Unbekanntes Argument: {arg}[/red]")
        config.console.print(
            "Verwendung: python -m openclaw_cert [--debug] "
            "[1-6 | all | report | streams | docs | ende]"
        )


# ─────────────────────────────────────────────────────────────────────────────
#  Interaktives Menü
# ─────────────────────────────────────────────────────────────────────────────

def main_menu() -> None:
    """Hauptmenü-Loop."""
    client = get_openai_client()
    startup_display()
    Prompt.ask("[dim]Enter drücken um zum Menü zu gelangen...[/dim]")

    while True:
        banner()
        completed = status_table()

        config.console.print("[bold cyan]Optionen:[/bold cyan]")
        config.console.print("  [cyan]\\[1-6][/cyan]  Einzelne Aufgabe ausführen (Live-Streaming + Speichern)")
        config.console.print("  [cyan]\\[a][/cyan]    Alle offenen Aufgaben vollautomatisch ausführen")
        config.console.print("  [cyan]\\[s][/cyan]    Speicher-Konfiguration anpassen")
        config.console.print("  [cyan]\\[l][/cyan]    Gespeicherte Stream-Dateien anzeigen")
        config.console.print("  [cyan]\\[r][/cyan]    Report einer Aufgabe anzeigen")
        config.console.print("  [cyan]\\[g][/cyan]    Gesamtreport generieren")
        config.console.print("  [cyan]\\[d][/cyan]    CLI-Dokumentation per KI generieren")
        config.console.print("  [cyan]\\[e][/cyan]    Finale Zusammenfassung erstellen (Ende)")
        config.console.print("  [cyan]\\[q][/cyan]    Beenden")
        config.console.print()

        choice = Prompt.ask(
            "[bold cyan]Auswahl[/bold cyan]",
            choices=["1", "2", "3", "4", "5", "6", "a", "s", "l", "r", "g", "d", "e", "q"],
            show_choices=False,
        )

        if choice == "q":
            config.console.print(
                f"\n[dim]Auf Wiedersehen! {config.PRODUCT} · {config.DEVELOPER}[/dim]\n"
            )
            break

        elif choice in ("1", "2", "3", "4", "5", "6"):
            task_num = int(choice)
            if task_num in completed and not Confirm.ask(
                f"[yellow]Aufgabe {task_num} bereits ausgeführt. Erneut?[/yellow]"
            ):
                continue
            run_task(task_num, client)
            Prompt.ask("\n[dim]Enter drücken um fortzufahren...[/dim]")

        elif choice == "a":
            run_all_tasks(client, completed)
            Prompt.ask("\n[dim]Enter drücken um fortzufahren...[/dim]")

        elif choice == "s":
            stream_config_menu()

        elif choice == "l":
            list_streams()
            Prompt.ask("\n[dim]Enter drücken um fortzufahren...[/dim]")

        elif choice == "r":
            task_num = int(Prompt.ask(
                "[cyan]Welche Aufgabe anzeigen?[/cyan]",
                choices=["1", "2", "3", "4", "5", "6"],
            ))
            show_report(task_num)
            Prompt.ask("\n[dim]Enter drücken um fortzufahren...[/dim]")

        elif choice == "g":
            generate_combined_report()
            Prompt.ask("\n[dim]Enter drücken um fortzufahren...[/dim]")

        elif choice == "d":
            generate_docs(client)
            Prompt.ask("\n[dim]Enter drücken um fortzufahren...[/dim]")

        elif choice == "e":
            generate_finale_readme()
            Prompt.ask("\n[dim]Enter drücken um fortzufahren...[/dim]")
