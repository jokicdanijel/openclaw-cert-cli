#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         OPENCLAW MASTER-ZERTIFIZIERUNGS-CLI                                 ║
║         Firefly Copilot Edition  ·  HyperDashboard-ONE.DE                   ║
║         Entwickelt von Danijel Jokic                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import datetime
from pathlib import Path
from openai import OpenAI

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv optional; start.sh lädt .env via export

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.prompt import Prompt, Confirm
    from rich.markdown import Markdown
    from rich import box
    from rich.rule import Rule
    from rich.live import Live
    from rich.text import Text
except ImportError:
    print("Fehler: 'rich' nicht installiert. Bitte: pip install rich")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# KONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

REPORT_DIR = Path("./reports")
REPORT_DIR.mkdir(exist_ok=True)

console = Console()

DEVELOPER = "Danijel Jokic"
PRODUCT   = "HyperDashboard-ONE.DE"

SYSTEM_PROMPT = """Du bist Firefly Copilot, ein zertifizierter Master-Experte für OpenClaw –
das autonome AI-Agenten-Framework. Du verfügst über tiefgreifendes technisches Wissen über:
- OpenClaw Gateway-Architektur und Agenten-Struktur
- Docker-Sandboxing und Sicherheitsarchitektur
- openclaw.json Konfiguration und alle Parameter
- Telegram Bot Integration
- GuardrailProvider und Fail-Closed Prinzip
- Docker Compose Orchestrierung
- ChromeOS/Linux-Umgebungen

Deine Antworten sind:
✓ Technisch präzise und vollständig
✓ Strukturiert mit Markdown-Überschriften, Tabellen und Code-Blöcken
✓ Sicherheitsbewusst – du weist aktiv auf Risiken hin
✓ Praxisorientiert mit konkreten Beispielen und Konfigurationen
✓ Auf Deutsch verfasst

Du gibst IMMER vollständige, produktionsreife Antworten – niemals unvollständige Fragmente."""

TASKS = {
    1: {
        "title": "Kernkonzepte des OpenClaw Systems",
        "icon": "🏗️",
        "description": "Agenten-Architektur, Gateway-Rolle, Tools & Plugins, Task-Flows, OpenAI-API",
        "prompt": """Erstelle eine vollständige technische Dokumentation zu den Kernkonzepten des OpenClaw Systems.

Behandle folgende Punkte erschöpfend:

## 1. Agenten-Architektur
- Wie sind Agenten strukturiert? (Komponenten, Lebenszyklus, Zustandsverwaltung)
- Die zentrale Rolle des Gateways als Hub-and-Spoke Control Plane
- Wie kommunizieren Agenten untereinander und mit dem Gateway?
- Unterschied zwischen nativen Plugins (in-process) und externen Tool-Agenten

## 2. Tools & Plugins
- Kategorien: shell, browser, file, http, code-interpreter
- Plugin-Architektur: Native vs. Sandbox-Plugins
- Wie registriert und aktiviert man Tools in der Konfiguration?
- Sicherheitsgrenzen bei Tool-Ausführung (Trust Boundary)

## 3. Task-Flows
- Wie werden komplexe Aufgaben sequenziert? (Chain-of-Thought → Tool-Call → Observation)
- Retry-Logik und Fehlerbehandlung in Task-Flows
- Parallelisierung vs. sequenzielle Ausführung

## 4. OpenAI-kompatible API
- Bedeutung und Funktion der /v1/chat/completions Schnittstelle
- Integration mit Open WebUI als Frontend
- Authentifizierung und API-Key-Management

Füge konkrete JSON-Konfigurationsbeispiele und Architektur-Diagramme (als ASCII-Art) ein.""",
    },
    2: {
        "title": "Telegram Bot Integration",
        "icon": "📱",
        "description": "BotFather-Setup, Kommunikationsfluss, Sicherheitsaspekte, Webhook vs. Polling",
        "prompt": """Erstelle eine vollständige technische Anleitung zur Telegram Bot Integration mit OpenClaw.

## 1. Zweck und Anwendungsfälle
- Warum Telegram als Kommunikationskanal?
- Use Cases: Benachrichtigungen, Befehlseingabe, Statusabfragen, Agenten-Steuerung
- Multi-User vs. Single-User Bot-Konfiguration

## 2. Schritt-für-Schritt Einrichtung
- BotFather: Token-Generierung, Bot-Konfiguration, Webhook-URL setzen
- openclaw.json: channels.telegram Konfigurationsblock (vollständiges Beispiel)
- Webhook-Endpunkt vs. Long-Polling: Wann was verwenden?
- SSL/TLS-Anforderungen für Webhooks

## 3. Kommunikationsfluss (mit Sequenzdiagramm als ASCII-Art)
- Eingehende Nachricht: Telegram → Webhook → Gateway → Agent → Tool → Response
- Ausgehende Nachricht: Agent → Telegram Bot API → Nutzer
- Message-Queue und Rate-Limiting

## 4. Sicherheitsaspekte
- Bot-Token-Schutz (niemals im Code, immer in Umgebungsvariablen)
- Allowed-Users-Liste: Nur autorisierte Telegram-IDs akzeptieren
- Command-Injection-Prävention bei Shell-Tool-Aufrufen via Telegram
- Audit-Logging aller Telegram-Befehle

Füge vollständige, produktionsreife openclaw.json Konfigurationsbeispiele ein.""",
    },
    3: {
        "title": "openclaw.json Konfiguration: Master-Verständnis",
        "icon": "⚙️",
        "description": "Alle Parameter, Sandbox-Modi, Docker-Backend, Guardrails, Sicherheitsrelevanz",
        "prompt": """Erstelle eine vollständige Referenzdokumentation für die openclaw.json Konfigurationsdatei.

## 1. agents.defaults.sandbox

### sandbox.mode
- "all": Alle Agenten laufen in Sandbox → maximale Sicherheit
- "non-main": Nur Sub-Agenten sandboxed → Kompromiss, Risiken?
- "off": Keine Sandbox → NUR für Entwicklung, niemals Produktion!
- Entscheidungsmatrix: Wann welcher Modus?

### sandbox.backend
- "docker": Bevorzugt für lokale Sandboxen
- "ssh": Remote-Ausführung
- "openshell": Direkter Shell-Zugriff
- Vergleichstabelle aller drei Backends

### sandbox.scope
- "agent" / "session" / "shared" – Isolation vs. Performance

### sandbox.workspaceAccess
- "ro" (read-only) vs. "rw" (read-write)

## 2. agents.defaults.sandbox.docker
- image, network, binds: Bedeutung, Risiken, Host-Schutz
- Gefährliche Bind-Mounts: Was NIEMALS mounten?

## 3. agents.defaults.guardrails
- provider.use: "local" – Vorteile
- provider.config.path, entrypoint, runtime
- Vollständiges Beispiel eines Guardrail-Skripts

## 4. gateway.http.endpoints
- chatCompletions.enabled: Warum notwendig für Open WebUI?

Füge eine vollständige, kommentierte openclaw.json ein.""",
    },
    4: {
        "title": "Sicherheitsarchitektur und Verifizierbarkeit",
        "icon": "🔐",
        "description": "GuardrailProvider, Docker-Sandboxing, Geolocation-Enforcement, Fail-Closed",
        "prompt": """Erstelle eine vollständige Sicherheitsarchitektur-Dokumentation für OpenClaw-Systeme.

## 1. GuardrailProvider als zentrale Sicherheitsinstanz
- Rolle als "Türsteher" vor JEDER Tool-Ausführung
- Vollständiges Guardrail-Skript (Node.js) mit allen Prüfungen
- Fail-Closed Implementierung: Bei Fehler → Ausführung verweigert

## 2. Docker Sandboxing
- Container-Isolation: Wie schützt Docker das Host-System?
- ChromeOS/Linux-spezifische Besonderheiten (Crostini/LXC-Kontext)
- Sicherheitsrelevante Docker-Flags: --no-new-privileges, --read-only, --cap-drop ALL
- Netzwerk-Isolation: openclaw-net

## 3. Standortprüfung (Geolocation-Enforcement)
- Implementierung via Umgebungsvariablen (ALLOWED_COUNTRY, ALLOWED_REGION)
- Node Location API Integration in Guardrail-Skript
- Docker Compose: Übergabe von Standortdaten an Container

## 4. Fehlervermeidung und Verifizierbarkeit
- Statische Analyse, Simulations-Checks, Zustands-Verifizierung
- Idempotenz-Garantien für kritische Operationen

## 5. Sicherheits-Checkliste für OpenClaw-Deployments (20+ Punkte)

Füge konkrete Code-Beispiele für alle Sicherheitsmechanismen ein.""",
    },
    5: {
        "title": "Docker Compose Orchestrierung",
        "icon": "🐳",
        "description": "docker-compose.yml Struktur, Services, Volumes, Netzwerke, Umgebungsvariablen",
        "prompt": """Erstelle eine vollständige Dokumentation zur Docker Compose Orchestrierung für OpenClaw.

## 1. Vollständige docker-compose.yml für OpenClaw
Erstelle eine produktionsreife docker-compose.yml mit:
- openclaw-gateway Service (mit allen Umgebungsvariablen)
- openclaw-sandbox Service (mit Sicherheits-Flags)
- open-webui Service (Frontend)
- Volumes, Netzwerke, Health Checks, Restart-Policies

## 2. Service-Konfiguration im Detail
- Gateway, Sandbox, Netzwerk-Topologie

## 3. Umgebungsvariablen-Management
- .env Datei: Struktur und alle relevanten Variablen
- Standortdaten: LOCATION_COUNTRY, LOCATION_CITY
- Secrets-Management

## 4. Betriebsbefehle und Workflows
- Starten, Logs, Update-Workflow, Backup, Troubleshooting

## 5. ChromeOS/Linux-spezifische Besonderheiten
- Crostini-Container, Ressourcenlimits, Persistenz

Füge vollständige, kommentierte Konfigurationsdateien ein.""",
    },
    6: {
        "title": "Master-Zertifizierungs-Anforderungen",
        "icon": "🏆",
        "description": "Sicherheits-Audit, Guardrail-Skript, Best Practices, Zertifizierungsbestätigung",
        "prompt": """Erstelle das finale Master-Zertifizierungsdokument für Firefly Copilot als OpenClaw-Systemexperte.

## 1. Praxis-Szenario: Vollständige OpenClaw-Installation für HyperDashboard-ONE.DE
- Hardware-Anforderungen, Software-Voraussetzungen
- Installations-Prozess, Sicherheits-Hardening, Monitoring-Setup

## 2. Sicherheits-Audit: Finde die Lücken
Analysiere diese FEHLERHAFTE openclaw.json und identifiziere ALLE Sicherheitsprobleme:
```json
{
  "agents": {
    "defaults": {
      "sandbox": { "mode": "off", "backend": "openshell", "workspaceAccess": "rw" }
    }
  },
  "gateway": {
    "http": {
      "endpoints": { "chatCompletions": { "enabled": true } },
      "auth": { "enabled": false }
    }
  }
}
```
Erkläre jeden Fehler und liefere die korrigierte Version.

## 3. Maßgeschneidertes Guardrail-Skript für HyperDashboard-ONE.DE
Vollständiges, produktionsreifes Node.js Guardrail-Skript mit:
- Whitelist für Shell-Befehle und Netzwerk-Zugriffe
- Geolocation-Check (nur Deutschland)
- Rate-Limiting, Audit-Log (JSON), Fail-Closed

## 4. Troubleshooting-Guide: 10 häufigste OpenClaw-Probleme

## 5. Best Practices Manifest (20 Punkte) für HyperDashboard-ONE.DE

## 6. Formelle Zertifizierungsbestätigung für Firefly Copilot""",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# HILFSFUNKTIONEN
# ─────────────────────────────────────────────────────────────────────────────

def clear():
    os.system("clear" if os.name == "posix" else "cls")


def banner():
    clear()
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]🦞  OPENCLAW MASTER-ZERTIFIZIERUNGS-CLI[/bold cyan]\n"
        f"[white]Firefly Copilot Edition  ·  {PRODUCT}[/white]\n"
        f"[dim]Entwickelt von {DEVELOPER}[/dim]",
        border_style="cyan",
        padding=(1, 4),
    ))
    console.print()


def status_table():
    reports = list(REPORT_DIR.glob("task_*.md"))
    completed = {int(r.stem.split("_")[1]) for r in reports}

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
            str(num),
            task["icon"],
            task["title"],
            task["description"][:52] + "…",
            status,
        )

    console.print(table)
    console.print()

    if len(completed) == len(TASKS):
        console.print(Panel(
            "[bold green]🏆 ALLE AUFGABEN ABGESCHLOSSEN![/bold green]\n"
            "[green]Firefly Copilot ist als OpenClaw Master-Experte zertifiziert.[/green]",
            border_style="green",
        ))
        console.print()

    return completed


def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        console.print("[bold red]Fehler:[/bold red] OPENAI_API_KEY nicht gesetzt.")
        sys.exit(1)
    # Immer offiziellen HTTPS-Endpunkt verwenden
    return OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")


def run_task(task_num: int, client: OpenAI) -> str:
    task = TASKS[task_num]
    console.print()
    console.print(Rule(
        f"[bold cyan]{task['icon']} Aufgabe {task_num}: {task['title']}[/bold cyan]"
    ))
    console.print()
    console.print(Panel(
        f"[bold]Beschreibung:[/bold] {task['description']}\n\n"
        "[dim]Firefly Copilot analysiert und beantwortet diese Aufgabe vollautomatisch...[/dim]",
        border_style="blue",
        padding=(0, 2),
    ))
    console.print()

    # ── Live-Streaming der Antwort ──────────────────────────────────────────
    result_chunks = []
    start_time = time.time()

    console.print(f"[dim cyan]▶ Streaming läuft...[/dim cyan]\n")

    try:
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": task["prompt"]},
            ],
            temperature=0.3,
            max_tokens=4096,
            stream=True,
        )

        with Live(console=console, refresh_per_second=15) as live:
            buffer = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                result_chunks.append(delta)
                buffer += delta
                # Zeige live den akkumulierten Text als Markdown
                live.update(
                    Panel(
                        Markdown(buffer),
                        title=f"[bold cyan]{task['icon']} Aufgabe {task_num} · Live-Ausgabe[/bold cyan]",
                        border_style="cyan",
                        padding=(0, 2),
                    )
                )

    except Exception as e:
        console.print(f"[bold red]API-Fehler:[/bold red] {e}")
        return ""

    result_text = "".join(result_chunks)
    elapsed = time.time() - start_time
    console.print(f"\n[dim]✓ Fertig in {elapsed:.1f}s · {len(result_text)} Zeichen[/dim]")
    console.print()

    # ── Report speichern ────────────────────────────────────────────────────
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_title = task["title"].replace(" ", "_").replace("/", "-").replace(":", "")[:35]
    report_path = REPORT_DIR / f"task_{task_num}_{safe_title}.md"

    report_content = (
        f"# {task['icon']} Aufgabe {task_num}: {task['title']}\n\n"
        f"> **Firefly Copilot · OpenClaw Master-Zertifizierung**  \n"
        f"> **{PRODUCT}** · Entwickelt von {DEVELOPER}  \n"
        f"> Erstellt: {timestamp}\n\n"
        f"---\n\n"
        f"{result_text}\n\n"
        f"---\n\n"
        f"*OpenClaw Master-Zertifizierungs-CLI · {PRODUCT} · {DEVELOPER}*\n"
    )

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    console.print(Panel(
        f"[bold green]✓ Report gespeichert:[/bold green] [cyan]{report_path}[/cyan]",
        border_style="green",
        padding=(0, 2),
    ))

    return str(report_path)


def run_all_tasks(client: OpenAI, completed: set):
    pending = [n for n in TASKS if n not in completed]
    if not pending:
        console.print("[bold green]Alle Aufgaben bereits abgeschlossen![/bold green]")
        return

    console.print(Panel(
        f"[bold cyan]Vollautomatischer Durchlauf[/bold cyan]\n"
        f"[white]{len(pending)} Aufgabe(n) werden sequenziell bearbeitet.[/white]\n"
        f"[dim]Aufgaben: {', '.join(str(n) for n in pending)}[/dim]",
        border_style="cyan",
        padding=(1, 2),
    ))

    if not Confirm.ask("\n[yellow]Vollautomatischen Durchlauf starten?[/yellow]"):
        return

    reports = []
    for i, task_num in enumerate(pending, 1):
        console.print(f"\n[dim]─── Fortschritt: {i}/{len(pending)} ───[/dim]")
        path = run_task(task_num, client)
        if path:
            reports.append(path)
        if i < len(pending):
            time.sleep(1)

    # Abschluss
    console.print()
    console.print(Rule("[bold green]🏆 ZERTIFIZIERUNGSDURCHLAUF ABGESCHLOSSEN[/bold green]"))
    console.print()

    for path in reports:
        console.print(f"  [green]✓[/green]  {path}")

    console.print()
    generate_combined_report()


def generate_combined_report():
    reports = sorted(REPORT_DIR.glob("task_*.md"))
    if not reports:
        console.print("[yellow]Keine Reports gefunden.[/yellow]")
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    combined_path = REPORT_DIR / "OPENCLAW_MASTER_ZERTIFIZIERUNG_KOMPLETT.md"

    with open(combined_path, "w", encoding="utf-8") as out:
        out.write(
            f"# 🦞 OpenClaw Master-Zertifizierung — Vollständiger Report\n\n"
            f"> **Firefly Copilot · Zertifiziert als OpenClaw Systemexperte**  \n"
            f"> **{PRODUCT}** · Entwickelt von {DEVELOPER}  \n"
            f"> Abschlussdatum: {timestamp}\n\n"
            f"---\n\n## Inhaltsverzeichnis\n\n"
        )
        for i, task in TASKS.items():
            out.write(f"{i}. {task['icon']} {task['title']}\n")
        out.write("\n---\n\n")

        for report_path in reports:
            with open(report_path, "r", encoding="utf-8") as f:
                out.write(f.read())
            out.write("\n\n---\n\n")

        out.write(
            f"## 🏆 Zertifizierungsbestätigung\n\n"
            f"Hiermit wird bestätigt, dass **Firefly Copilot** alle 6 Aufgaben der  \n"
            f"**OpenClaw Master-Zertifizierung** erfolgreich abgeschlossen hat.\n\n"
            f"**Zertifiziert für:** {PRODUCT}  \n"
            f"**Ausgestellt von:** {DEVELOPER}  \n"
            f"**Datum:** {timestamp}  \n"
            f"**Status:** ✅ ZERTIFIZIERT\n\n"
            f"---\n"
            f"*OpenClaw Master-Zertifizierungs-CLI · {PRODUCT} · {DEVELOPER}*\n"
        )

    console.print(Panel(
        f"[bold green]📄 Gesamtreport erstellt:[/bold green]\n[cyan]{combined_path}[/cyan]",
        border_style="green",
        padding=(1, 2),
    ))


def show_report(task_num: int):
    reports = list(REPORT_DIR.glob(f"task_{task_num}_*.md"))
    if not reports:
        console.print(f"[yellow]Kein Report für Aufgabe {task_num} gefunden.[/yellow]")
        return
    with open(reports[0], "r", encoding="utf-8") as f:
        content = f.read()
    console.print(Markdown(content))


# ─────────────────────────────────────────────────────────────────────────────
# HAUPTMENÜ
# ─────────────────────────────────────────────────────────────────────────────

def main_menu():
    client = get_openai_client()

    while True:
        banner()
        completed = status_table()

        console.print("[bold cyan]Optionen:[/bold cyan]")
        console.print("  [cyan][1-6][/cyan]  Einzelne Aufgabe ausführen (mit Live-Streaming)")
        console.print("  [cyan][a][/cyan]    Alle offenen Aufgaben vollautomatisch ausführen")
        console.print("  [cyan][r][/cyan]    Report einer Aufgabe anzeigen")
        console.print("  [cyan][g][/cyan]    Gesamtreport generieren")
        console.print("  [cyan][q][/cyan]    Beenden")
        console.print()

        choice = Prompt.ask(
            "[bold cyan]Auswahl[/bold cyan]",
            choices=["1", "2", "3", "4", "5", "6", "a", "r", "g", "q"],
            show_choices=False,
        )

        if choice == "q":
            console.print(f"\n[dim]Auf Wiedersehen! {PRODUCT} · {DEVELOPER}[/dim]\n")
            break

        elif choice in ["1", "2", "3", "4", "5", "6"]:
            task_num = int(choice)
            if task_num in completed:
                if not Confirm.ask(
                    f"[yellow]Aufgabe {task_num} wurde bereits ausgeführt. Erneut ausführen?[/yellow]"
                ):
                    continue
            run_task(task_num, client)
            Prompt.ask("\n[dim]Enter drücken um fortzufahren...[/dim]")

        elif choice == "a":
            run_all_tasks(client, completed)
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


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        client = get_openai_client()
        if arg == "all":
            banner()
            completed = status_table()
            run_all_tasks(client, completed)
        elif arg.isdigit() and 1 <= int(arg) <= 6:
            banner()
            run_task(int(arg), client)
        elif arg == "report":
            generate_combined_report()
        else:
            console.print(f"[red]Unbekanntes Argument: {arg}[/red]")
            console.print("Verwendung: python3 openclaw_cert.py [1-6|all|report]")
    else:
        main_menu()
