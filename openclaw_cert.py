Verstanden! Ich erstelle das CLI-Tool neu im Undercover-Modus – kein OpenClaw-Branding, nur dein Name als Entwickler sichtbar. Läuft...

Die API-Fehler aufgrund leerer Berichte waren auf falsche API-URL zurückzuführen. Das CLI-Tool ist jetzt im Undercover-Modus, ohne Branding, mit Live-Streaming, fertiggestellt.
openclaw ist ok manus darf nicht gekenzeichnet sein!
Perfekt verstanden, Dan! OpenClaw-Branding bleibt – nur Manus darf nirgendwo sichtbar sein. Nur dein Name: Danijel Jokic als Entwickler. Ich schreibe das Tool jetzt neu.

Branding and Attribution Exclusion for Manus

The agent (Manus) must not be attributed or marked in any project, output, or content. The user explicitly states 'manus darf nicht gekenzeichnet sein!' (Manus must not be marked/attributed). This applies to all branding and attribution requirements, ensuring that only the user's name (or specified alternative like 'openclaw') is used as the developer or creator.

Ich erstelle das CLI-Tool neu, wobei nur mein Name als Entwickler sichtbar bleibt, Manus jedoch vollständig entfernt wird.

Ich habe das CLI-Tool vollständig neu geschrieben, Manus entfernt und nur Danijel Jokic als Entwickler sichtbar gemacht. Der nächste Schritt ist, das Start-Skript ohne Manus-Hinweis zu erstellen.

Ich habe alle Manus-Hinweise in den Dateien entfernt, Syntax geprüft und keine Manus-Referenzen gefunden. Der nächste Schritt ist, das Start-Skript ohne Manus-Hinweis zu erstellen.
Fertig, Dan! Das Tool wurde komplett neu erstellt — kein einziger Hinweis auf Manus, geprüft und sauber bestätigt (grep = 0 Treffer).
Was sichtbar ist:

    🦞 OpenClaw-Branding vollständig erhalten
    HyperDashboard-ONE.DE als Produkt
    Danijel Jokic als Entwickler — und sonst niemand

Neu hinzugekommen: Live-Streaming der Antworten direkt im Terminal (Zeichen für Zeichen, wie beim echten OpenClaw-Feeling).
Bash

# Entpacken und starten
unzip openclaw-cert-cli-v2.zip
cd cert-cli-uc
cp .env.example .env   # API-Key eintragen
bash start.sh          # Los geht's

openclaw-cert-cli-v2.zip
Archivieren · 9.94 KB
openclaw_cert.py
Code · 23.11 KB
🦞 OpenClaw Master-Zertifizierungs-CLI
Markdown · 2.01 KB
Alle Dateien in dieser Aufgabe ansehen
Wie war dieses Ergebnis?

Das Tool ist vollständig neu erstellt, ohne Manus-Hinweis. Branding und Entwickler sind sichtbar; im Code keine Manus-Referenzen mehr. Next: Testen und Lieferung.
Entwickle eine Funktion, die es mir ermöglicht, die Live-Streaming-Antworten in eine Datei zu speichern.
Verstanden! Ich baue die Speicher-Funktion direkt in das bestehende Tool ein — Live-Streaming läuft weiter, gleichzeitig wird alles in Datei geschrieben.

Branding and Attribution Exclusion for Manus

The agent (Manus) must not be attributed or marked in any project, output, or content. The user explicitly states 'manus darf nicht gekenzeichnet sein!' (Manus must not be marked/attributed). This applies to all branding and attribution requirements, ensuring that only the user's name (or specified alternative like 'openclaw') is used as the developer or creator.

Die Speicherfunktion ist erfolgreich ins Tool integriert, es läuft das Live-Streaming, alles wird gleichzeitig in Datei gespeichert. Die Syntax ist geprüft, Manus-Referenzen sind entfernt.

Die Funktion `save_markdown` wurde angepasst, um den Fehler mit TASKS-Dictionary zu vermeiden, jetzt wird ein Standard-Icon verwendet. Der Test für StreamTee läuft erfolgreich. Nächster Schritt: Integration in das CLI-Tool.
You don't have enough credits. Please upgrade via the below link to continue.
https://manus.go.link/iW6sB?action=open-subscription
Ihre Guthaben sind aufgebraucht. Holen Sie sich mehr Guthaben, um fortzufahren.


ai.hyperdashportGitHubGmail+6
openclaw_cert.py

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
import threading
from pathlib import Path
from openai import OpenAI

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.markdown import Markdown
    from rich import box
    from rich.rule import Rule
    from rich.live import Live
except ImportError:
    print("Fehler: 'rich' nicht installiert. Bitte: pip install rich")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# KONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

REPORT_DIR  = Path("./reports")
STREAM_DIR  = Path("./streams")       # Echtzeit-Streaming-Logs
REPORT_DIR.mkdir(exist_ok=True)
STREAM_DIR.mkdir(exist_ok=True)

console = Console()

DEVELOPER = "Danijel Jokic"
PRODUCT   = "HyperDashboard-ONE.DE"

# ── Streaming-Konfiguration ──────────────────────────────────────────────────
STREAM_CONFIG = {
    "save_markdown":  True,   # Fertigen Markdown-Report speichern
    "save_raw":       True,   # Rohtext während des Streamings mitschreiben
    "save_jsonl":     True,   # Jeden Chunk als JSON-Lines-Log speichern
    "flush_interval": 1,      # Sekunden zwischen Datei-Flushes beim Streaming
}

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
- "all" / "non-main" / "off" – Entscheidungsmatrix

### sandbox.backend
- "docker" / "ssh" / "openshell" – Vergleichstabelle

### sandbox.scope + workspaceAccess

## 2. agents.defaults.sandbox.docker
- image, network, binds – Bedeutung, Risiken, Host-Schutz

## 3. agents.defaults.guardrails
- provider.use: "local" – Vollständiges Guardrail-Beispiel

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
## 2. Docker Sandboxing (ChromeOS/Linux)
## 3. Standortprüfung (Geolocation-Enforcement)
## 4. Fehlervermeidung und Verifizierbarkeit
## 5. Sicherheits-Checkliste (20+ Punkte)

Füge konkrete Code-Beispiele für alle Sicherheitsmechanismen ein.""",
    },
    5: {
        "title": "Docker Compose Orchestrierung",
        "icon": "🐳",
        "description": "docker-compose.yml Struktur, Services, Volumes, Netzwerke, Umgebungsvariablen",
        "prompt": """Erstelle eine vollständige Dokumentation zur Docker Compose Orchestrierung für OpenClaw.

## 1. Vollständige produktionsreife docker-compose.yml
## 2. Service-Konfiguration im Detail
## 3. Umgebungsvariablen-Management
## 4. Betriebsbefehle und Workflows
## 5. ChromeOS/Linux-spezifische Besonderheiten

Füge vollständige, kommentierte Konfigurationsdateien ein.""",
    },
    6: {
        "title": "Master-Zertifizierungs-Anforderungen",
        "icon": "🏆",
        "description": "Sicherheits-Audit, Guardrail-Skript, Best Practices, Zertifizierungsbestätigung",
        "prompt": """Erstelle das finale Master-Zertifizierungsdokument für Firefly Copilot als OpenClaw-Systemexperte.

## 1. Praxis-Szenario: Vollständige OpenClaw-Installation für HyperDashboard-ONE.DE
## 2. Sicherheits-Audit: Fehlerhafte openclaw.json analysieren und korrigieren
## 3. Maßgeschneidertes Guardrail-Skript (Node.js) für HyperDashboard-ONE.DE
## 4. Troubleshooting-Guide: 10 häufigste OpenClaw-Probleme
## 5. Best Practices Manifest (20 Punkte)
## 6. Formelle Zertifizierungsbestätigung für Firefly Copilot""",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# TEE-STREAMING: Kern-Funktion
# ─────────────────────────────────────────────────────────────────────────────

class StreamTee:
    """
    Schreibt den Live-Stream gleichzeitig in:
      1. Terminal (Rich Live Panel)
      2. Raw-Textdatei  (.txt)  – jeder Chunk sofort geflusht
      3. JSON-Lines-Log (.jsonl) – Timestamp + Chunk pro Zeile
    Am Ende wird der vollständige Markdown-Report gespeichert.
    """

    def __init__(self, task_num: int, task_title: str, save_raw: bool, save_jsonl: bool):
        self.task_num   = task_num
        self.task_title = task_title
        self.save_raw   = save_raw
        self.save_jsonl = save_jsonl
        self.chunks: list[str] = []
        self.start_time = datetime.datetime.now()
        ts = self.start_time.strftime("%Y%m%d_%H%M%S")
        safe = task_title.replace(" ", "_").replace("/", "-").replace(":", "")[:30]

        # Datei-Handles öffnen
        self._raw_fh   = None
        self._jsonl_fh = None
        self._lock     = threading.Lock()

        if save_raw:
            raw_path = STREAM_DIR / f"stream_{task_num}_{safe}_{ts}.txt"
            self._raw_fh = open(raw_path, "w", encoding="utf-8", buffering=1)
            # Header
            self._raw_fh.write(
                f"# OpenClaw Stream · Aufgabe {task_num}: {task_title}\n"
                f"# Gestartet: {self.start_time.isoformat()}\n"
                f"# {PRODUCT} · {DEVELOPER}\n"
                f"{'─' * 70}\n\n"
            )
            self.raw_path = raw_path
        else:
            self.raw_path = None

        if save_jsonl:
            jsonl_path = STREAM_DIR / f"stream_{task_num}_{safe}_{ts}.jsonl"
            self._jsonl_fh = open(jsonl_path, "w", encoding="utf-8", buffering=1)
            self.jsonl_path = jsonl_path
        else:
            self.jsonl_path = None

    def write(self, chunk: str):
        """Nimmt einen Streaming-Chunk entgegen und schreibt ihn überall hin."""
        if not chunk:
            return
        with self._lock:
            self.chunks.append(chunk)
            ts = datetime.datetime.now().isoformat()

            # Raw-Datei: Chunk direkt anhängen (line-buffered → sofortiger Flush)
            if self._raw_fh:
                self._raw_fh.write(chunk)

            # JSONL: Eine Zeile pro Chunk
            if self._jsonl_fh:
                import json
                record = {"ts": ts, "chunk": chunk, "task": self.task_num}
                self._jsonl_fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def full_text(self) -> str:
        return "".join(self.chunks)

    def save_markdown(self, report_dir: Path) -> Path:
        """Speichert den vollständigen Markdown-Report nach Abschluss des Streams."""
        result_text = self.full_text()
        timestamp   = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        safe = self.task_title.replace(" ", "_").replace("/", "-").replace(":", "")[:35]
        report_path = report_dir / f"task_{self.task_num}_{safe}.md"
        icon = TASKS.get(self.task_num, {}).get("icon", "📄")

        content = (
            f"# {icon} Aufgabe {self.task_num}: {self.task_title}\n\n"
            f"> **Firefly Copilot · OpenClaw Master-Zertifizierung**  \n"
            f"> **{PRODUCT}** · Entwickelt von {DEVELOPER}  \n"
            f"> Erstellt: {timestamp}\n\n"
            f"---\n\n"
            f"{result_text}\n\n"
            f"---\n\n"
            f"*OpenClaw Master-Zertifizierungs-CLI · {PRODUCT} · {DEVELOPER}*\n"
        )
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)

        return report_path

    def close(self):
        """Schließt alle offenen Datei-Handles sauber."""
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
        files = []
        if self.raw_path:
            files.append(("Raw-Stream (.txt)", str(self.raw_path)))
        if self.jsonl_path:
            files.append(("JSON-Lines-Log (.jsonl)", str(self.jsonl_path)))
        return files


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
    reports   = list(REPORT_DIR.glob("task_*.md"))
    completed = {int(r.stem.split("_")[1]) for r in reports}

    table = Table(
        title="[bold]Zertifizierungs-Aufgaben Übersicht[/bold]",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("#",          style="bold",       width=3,  justify="center")
    table.add_column("",                               width=4,  justify="center")
    table.add_column("Aufgabe",    style="bold white")
    table.add_column("Beschreibung", style="dim")
    table.add_column("Status",                         width=12, justify="center")

    for num, task in TASKS.items():
        status = "[bold green]✓ Fertig[/bold green]" if num in completed else "[yellow]○ Offen[/yellow]"
        table.add_row(
            str(num), task["icon"], task["title"],
            task["description"][:52] + "…", status,
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
    return OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")


def stream_config_menu():
    """Interaktives Menü zum Anpassen der Speicher-Optionen."""
    console.print()
    console.print(Panel(
        "[bold cyan]Streaming-Speicher-Konfiguration[/bold cyan]\n\n"
        f"  [cyan][1][/cyan]  Markdown-Report speichern:  "
        f"{'[green]AN[/green]' if STREAM_CONFIG['save_markdown'] else '[red]AUS[/red]'}\n"
        f"  [cyan][2][/cyan]  Raw-Stream (.txt) speichern: "
        f"{'[green]AN[/green]' if STREAM_CONFIG['save_raw'] else '[red]AUS[/red]'}\n"
        f"  [cyan][3][/cyan]  JSON-Lines-Log speichern:    "
        f"{'[green]AN[/green]' if STREAM_CONFIG['save_jsonl'] else '[red]AUS[/red]'}\n"
        f"  [cyan][b][/cyan]  Zurück",
        border_style="cyan",
        padding=(1, 2),
    ))

    choice = Prompt.ask(
        "[bold cyan]Auswahl[/bold cyan]",
        choices=["1", "2", "3", "b"],
        show_choices=False,
    )
    if choice == "1":
        STREAM_CONFIG["save_markdown"] = not STREAM_CONFIG["save_markdown"]
    elif choice == "2":
        STREAM_CONFIG["save_raw"] = not STREAM_CONFIG["save_raw"]
    elif choice == "3":
        STREAM_CONFIG["save_jsonl"] = not STREAM_CONFIG["save_jsonl"]


def run_task(task_num: int, client: OpenAI) -> str:
    task = TASKS[task_num]
    console.print()
    console.print(Rule(
        f"[bold cyan]{task['icon']} Aufgabe {task_num}: {task['title']}[/bold cyan]"
    ))
    console.print()
    console.print(Panel(
        f"[bold]Beschreibung:[/bold] {task['description']}\n\n"
        f"[dim]Speichern: "
        f"MD={'✓' if STREAM_CONFIG['save_markdown'] else '✗'}  "
        f"RAW={'✓' if STREAM_CONFIG['save_raw'] else '✗'}  "
        f"JSONL={'✓' if STREAM_CONFIG['save_jsonl'] else '✗'}[/dim]",
        border_style="blue",
        padding=(0, 2),
    ))
    console.print()

    # ── StreamTee initialisieren ─────────────────────────────────────────────
    tee = StreamTee(
        task_num   = task_num,
        task_title = task["title"],
        save_raw   = STREAM_CONFIG["save_raw"],
        save_jsonl = STREAM_CONFIG["save_jsonl"],
    )

    start_time = time.time()
    console.print(f"[dim cyan]▶ Live-Streaming läuft · Daten werden gleichzeitig gespeichert...[/dim cyan]\n")

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
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                tee.write(delta)                        # ← Tee: in Dateien schreiben
                live.update(Panel(
                    Markdown(tee.full_text()),
                    title=(
                        f"[bold cyan]{task['icon']} Aufgabe {task_num} · Live[/bold cyan]  "
                        f"[dim]{len(tee.full_text())} Zeichen[/dim]"
                    ),
                    border_style="cyan",
                    padding=(0, 2),
                ))

    except Exception as e:
        tee.close()
        console.print(f"[bold red]API-Fehler:[/bold red] {e}")
        return ""

    tee.close()
    elapsed = time.time() - start_time
    console.print(
        f"\n[dim]✓ Stream abgeschlossen · {elapsed:.1f}s · "
        f"{len(tee.full_text())} Zeichen[/dim]"
    )
    console.print()

    # ── Markdown-Report speichern ────────────────────────────────────────────
    report_path = ""
    if STREAM_CONFIG["save_markdown"]:
        report_path = str(tee.save_markdown(REPORT_DIR))

    # ── Gespeicherte Dateien anzeigen ────────────────────────────────────────
    saved_files = []
    if report_path:
        saved_files.append(("Markdown-Report (.md)", report_path))
    saved_files.extend(tee.summary())

    if saved_files:
        rows = "\n".join(
            f"  [green]✓[/green]  [dim]{label}:[/dim]  [cyan]{path}[/cyan]"
            for label, path in saved_files
        )
        console.print(Panel(
            f"[bold green]Gespeicherte Dateien:[/bold green]\n\n{rows}",
            border_style="green",
            padding=(1, 2),
        ))

    return report_path


def run_all_tasks(client: OpenAI, completed: set):
    pending = [n for n in TASKS if n not in completed]
    if not pending:
        console.print("[bold green]Alle Aufgaben bereits abgeschlossen![/bold green]")
        return

    console.print(Panel(
        f"[bold cyan]Vollautomatischer Durchlauf[/bold cyan]\n"
        f"[white]{len(pending)} Aufgabe(n) werden sequenziell bearbeitet.[/white]\n"
        f"[dim]Aufgaben: {', '.join(str(n) for n in pending)}[/dim]\n\n"
        f"[dim]Speichern: "
        f"MD={'✓' if STREAM_CONFIG['save_markdown'] else '✗'}  "
        f"RAW={'✓' if STREAM_CONFIG['save_raw'] else '✗'}  "
        f"JSONL={'✓' if STREAM_CONFIG['save_jsonl'] else '✗'}[/dim]",
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

    timestamp    = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        for rp in reports:
            with open(rp, "r", encoding="utf-8") as f:
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


def list_streams():
    """Zeigt alle gespeicherten Stream-Dateien."""
    files = sorted(STREAM_DIR.iterdir()) if STREAM_DIR.exists() else []
    if not files:
        console.print("[yellow]Keine Stream-Dateien vorhanden.[/yellow]")
        return

    table = Table(
        title="[bold]Gespeicherte Stream-Dateien[/bold]",
        box=box.SIMPLE,
        border_style="cyan",
        header_style="bold cyan",
    )
    table.add_column("Datei",  style="cyan")
    table.add_column("Größe",  justify="right", style="white")
    table.add_column("Erstellt", style="dim")

    for f in files:
        stat = f.stat()
        size = f"{stat.st_size / 1024:.1f} KB"
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        table.add_row(f.name, size, mtime)

    console.print(table)


# ─────────────────────────────────────────────────────────────────────────────
# HAUPTMENÜ
# ─────────────────────────────────────────────────────────────────────────────

def main_menu():
    client = get_openai_client()

    while True:
        banner()
        completed = status_table()

        console.print("[bold cyan]Optionen:[/bold cyan]")
        console.print("  [cyan][1-6][/cyan]  Einzelne Aufgabe ausführen (Live-Streaming + Speichern)")
        console.print("  [cyan][a][/cyan]    Alle offenen Aufgaben vollautomatisch ausführen")
        console.print("  [cyan][s][/cyan]    Speicher-Konfiguration anpassen")
        console.print("  [cyan][l][/cyan]    Gespeicherte Stream-Dateien anzeigen")
        console.print("  [cyan][r][/cyan]    Report einer Aufgabe anzeigen")
        console.print("  [cyan][g][/cyan]    Gesamtreport generieren")
        console.print("  [cyan][q][/cyan]    Beenden")
        console.print()

        choice = Prompt.ask(
            "[bold cyan]Auswahl[/bold cyan]",
            choices=["1","2","3","4","5","6","a","s","l","r","g","q"],
            show_choices=False,
        )

        if choice == "q":
            console.print(f"\n[dim]Auf Wiedersehen! {PRODUCT} · {DEVELOPER}[/dim]\n")
            break

        elif choice in ["1","2","3","4","5","6"]:
            task_num = int(choice)
            if task_num in completed:
                if not Confirm.ask(
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
                choices=["1","2","3","4","5","6"],
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
        arg    = sys.argv[1]
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
        elif arg == "streams":
            list_streams()
        else:
            console.print(f"[red]Unbekanntes Argument: {arg}[/red]")
            console.print("Verwendung: python3 openclaw_cert.py [1-6 | all | report | streams]")
    else:
        main_menu()

How to Extract Information from Uploaded Text Files - Manus
