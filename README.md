# 🦞 OpenClaw Master-Zertifizierungs-CLI

> **Interaktives CLI-Tool zur vollautomatischen KI-Zertifizierung mit GPT-Streaming**

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)](https://python.org)
[![OpenAI API](https://img.shields.io/badge/OpenAI-API-green?logo=openai)](https://platform.openai.com)
[![Docker](https://img.shields.io/badge/Docker-Sandbox-2496ED?logo=docker)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## Was ist das?

Ein Python-CLI, das einen KI-Agenten vollautomatisch durch **6 Zertifizierungsaufgaben** des [OpenClaw](https://github.com/jokicdanijel)-Systems führt. Jede Aufgabe wird per OpenAI Streaming-API live im Terminal ausgeführt und als Markdown-Report gespeichert.

**Features:**
- 🎯 **6 Prüfungsaufgaben** — Architektur, Telegram, Konfiguration, Sicherheit, Docker, Master-Audit
- 📡 **Live-Streaming** — API-Antworten werden in Echtzeit im Terminal angezeigt
- 📝 **Automatische Reports** — Markdown + JSON-Lines + Raw-Text pro Aufgabe
- 🔄 **Retry-Logik** — 3× Retry mit exponentiellem Backoff (1s → 2s → 4s)
- 🐳 **Docker-Sandbox** — Isolierte Ausführung via Dockerfile + Watchdog
- 🖥️ **Interaktives Menü** — Rich-basiertes TUI mit Farbausgabe

---

## Schnellstart

### 1. Repository klonen

```bash
git clone https://github.com/jokicdanijel/openclaw-cert-cli.git
cd openclaw-cert-cli
```

### 2. Abhängigkeiten installieren

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install rich openai python-dotenv
```

Oder automatisch:

```bash
bash setup.sh
```

### 3. API-Key konfigurieren

```bash
cp .env.example .env
nano .env   # OPENAI_API_KEY eintragen
```

### 4. Starten

```bash
# Interaktives Menü
python3 openclaw_cert.py

# Oder direkt alle Aufgaben
python3 openclaw_cert.py all
```

---

## Verwendung

| Befehl | Beschreibung |
|---|---|
| `python3 openclaw_cert.py` | Interaktives Menü mit allen Optionen |
| `python3 openclaw_cert.py all` | Alle offenen Aufgaben automatisch durchlaufen |
| `python3 openclaw_cert.py 3` | Einzelne Aufgabe ausführen (z.B. Aufgabe 3) |
| `python3 openclaw_cert.py report` | Gesamtreport aus vorhandenen Reports generieren |
| `python3 openclaw_cert.py ende` | Finale Zusammenfassung mit Zertifizierungsstatus |
| `python3 openclaw_cert.py docs` | CLI-Dokumentation per KI generieren |
| `python3 openclaw_cert.py --debug all` | Debug-Modus mit erweitertem Logging |

### Menü-Optionen

```
[1-6]  Einzelne Aufgabe ausführen (Live-Streaming + Speichern)
[a]    Alle offenen Aufgaben vollautomatisch ausführen
[s]    Speicher-Konfiguration anpassen
[l]    Gespeicherte Stream-Dateien anzeigen
[r]    Report einer Aufgabe anzeigen
[g]    Gesamtreport generieren
[d]    CLI-Dokumentation per KI generieren
[e]    Finale Zusammenfassung erstellen
[q]    Beenden
```

---

## Die 6 Zertifizierungsaufgaben

| #  | Aufgabe | Inhalt |
|----|---------|--------|
| 1  | 🏗️ Kernkonzepte | Agenten-Architektur, Gateway-Rolle, Tools & Plugins, Task-Flows |
| 2  | 📱 Telegram Bot | BotFather-Setup, Webhook, Kommunikationsfluss, Sicherheit |
| 3  | ⚙️ openclaw.json | Alle Parameter, Sandbox-Modi, Docker-Backend, Guardrails |
| 4  | 🔐 Sicherheitsarchitektur | GuardrailProvider, Docker-Sandboxing, Fail-Closed-Prinzip |
| 5  | 🐳 Docker Compose | Orchestrierung, Services, Volumes, Netzwerke |
| 6  | 🏆 Master-Zertifizierung | Sicherheits-Audit, Guardrail-Skript, Best Practices |

---

## Konfiguration

Erstelle eine `.env` aus der Vorlage:

```env
OPENAI_API_KEY=sk-proj-...    # Pflicht — dein OpenAI API-Key
OPENCLAW_MODEL=gpt-4o         # Modell (Standard: gpt-4o)
OPENCLAW_DEBUG=false           # true = Debug-Logging in logs/
```

---

## Projektstruktur

```
openclaw-cert-cli/
├── openclaw_cert.py        # Haupt-CLI (Menü, Streaming, Reports)
├── listener.py             # Live-Listener für Streams & Logs
├── watchdog.sh             # Docker-Watchdog (5-Min-Automatisierung)
├── Dockerfile              # Docker-Sandbox für isolierte Ausführung
├── setup.sh                # Automatisches Setup (venv + Pakete + .env)
├── start.sh                # Starter-Skript
├── .env.example            # Konfigurationsvorlage
├── .gitignore
├── cert-cli-uc/            # Use-Case-Verzeichnis
│   ├── openclaw_cert.py
│   ├── README.md
│   └── start.sh
├── reports/                # Generierte Markdown-Reports (nicht in Git)
│   ├── task_1_*.md
│   ├── task_2_*.md
│   ├── ...
│   └── FINALE_ZUSAMMENFASSUNG_*.md
├── streams/                # Live-Stream-Logs (nicht in Git)
│   ├── stream_*_*.txt      # Raw-Chunks
│   └── stream_*_*.jsonl    # JSON-Lines mit Timestamps
└── logs/                   # Debug-Logs (nicht in Git)
```

---

## Architektur

```
openclaw_cert.py
├── StreamTee          — Live-Streaming in Terminal + .txt + .jsonl
├── run_task()         — Einzelaufgabe mit 3× Retry (expon. Backoff)
├── run_all_tasks()    — Vollautomatischer Batch-Durchlauf
├── generate_docs()    — KI-gestützte CLI-Dokumentation
├── generate_finale_readme() — Finale Zusammenfassung
├── startup_display()  — README-Anzeige beim Start
└── main_menu()        — Interaktives Rich-Menü
```

**Pro Aufgabe werden 3 Dateien erzeugt:**

| Datei | Format | Inhalt |
|---|---|---|
| `reports/task_N_<titel>.md` | Markdown | Fertiger Report |
| `streams/stream_N_<titel>_<ts>.txt` | Text | Raw-Chunks (live-geflusht) |
| `streams/stream_N_<titel>_<ts>.jsonl` | JSON-Lines | Chunks mit Timestamps |

---

## Docker-Sandbox

Die CLI kann in einer isolierten Docker-Umgebung ausgeführt werden:

```bash
# Image bauen
docker build -t openclaw-cert-cli .

# Einzelne Aufgabe im Container
docker run --rm --env-file .env \
  -v $(pwd)/reports:/app/reports \
  openclaw-cert-cli 3

# Alle Aufgaben
docker run --rm --env-file .env \
  -v $(pwd)/reports:/app/reports \
  openclaw-cert-cli all
```

### Watchdog (automatisch alle 5 Minuten)

```bash
# Einmal-Check: fehlende Tasks ausführen
bash watchdog.sh --once

# Endlos-Watchdog (alle 5 Min)
bash watchdog.sh

# Status anzeigen
bash watchdog.sh --status
```

---

## Sicherheit

- `.env` ist in `.gitignore` — wird **niemals** committed
- API-Keys erscheinen nicht in Logs oder Reports
- Docker-Container läuft als non-root User (`openclaw`, UID 1000)
- Container ist read-only mit Memory-Limit (512 MB)
- Kein Absturz bei fehlendem `python-dotenv` — stiller Fallback auf `os.environ`

---

## Anforderungen

- **Python** 3.12+
- **Pakete:** `rich`, `openai`, `python-dotenv`
- **OpenAI API-Key** mit Zugriff auf das konfigurierte Modell
- **Docker** (optional, für Sandbox-Modus)

---

## Autor

**Danijel Jokic** · [HyperDashboard-ONE.DE](https://hyperdashboard-one.de)

---

## Lizenz

MIT — siehe [LICENSE](LICENSE) für Details.
