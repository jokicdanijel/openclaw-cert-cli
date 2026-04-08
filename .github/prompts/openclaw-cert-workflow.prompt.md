---
description: "OpenClaw Cert-CLI Workflow: Aufgabe ausführen, Dotenv-Fallback prüfen, Retry-Logik testen oder Report generieren. Nutze wenn: Zertifizierungsaufgabe, python-dotenv, StreamTee, start.sh, .env, run_task, generate_docs."
name: "OpenClaw Cert-CLI Workflow"
argument-hint: "z.B. 'Aufgabe 3 ausführen', 'Dotenv-Fallback testen', 'Report für alle Aufgaben generieren'"
agent: "agent"
---

# OpenClaw Master-Zertifizierungs-CLI — Workflow-Prompt

## Systemkontext

- **Projekt:** `openclaw-cert-cli` — Python-CLI zur OpenClaw-Zertifizierung via GPT-4o Streaming
- **Hauptdatei:** [openclaw_cert.py](../openclaw_cert.py)
- **Einstieg:** [start.sh](../start.sh) (empfohlen) oder `python3 openclaw_cert.py [--debug] [1-6 | all | report | streams | docs | ende]`
- **Python-Umgebung:** `/home/danijel-jd/.openclaw/.venv/bin/python3`
- **Abhängigkeiten:** `openai`, `rich`, `python-dotenv` (optional, stiller Fallback auf `os.environ`)

## Umgebung & .env

```
OPENAI_API_KEY=sk-...      # Pflichtfeld
OPENCLAW_MODEL=gpt-4o      # Standard, überschreibbar
OPENCLAW_DEBUG=false       # true = Debug-Logging auf stderr + Datei
```

**Ladereihenfolge:**
1. `start.sh` lädt `.env` via `export $(grep -v '^#' .env ...)`
2. `openclaw_cert.py` lädt `.env` via `python-dotenv` (falls installiert)
3. Fallback: `os.environ` (bereits gesetzte Variablen bleiben erhalten — kein Absturz)

## Aufgaben

| # | Titel | Inhalt |
|---|-------|--------|
| 1 | Kernkonzepte | Architektur, Tools, Task-Flows, OpenAI-API |
| 2 | Telegram Bot | Setup, Webhook, Sicherheit, Sequenzdiagramm |
| 3 | openclaw.json | Alle Parameter, Sandbox, Guardrails, Referenz |
| 4 | Sicherheitsarchitektur | GuardrailProvider, Docker, Fail-Closed |
| 5 | Docker Compose | Orchestrierung, Volumes, Netzwerk |
| 6 | Master-Zertifizierung | Audit, Guardrail-Skript, Best Practices, Abschluss |

## Streaming-Ausgabe

Jede Aufgabe schreibt gleichzeitig in:
- `reports/task_N_<titel>.md` — fertiger Markdown-Report
- `streams/stream_N_<titel>_<ts>.txt` — Raw-Chunks (live-geflusht)
- `streams/stream_N_<titel>_<ts>.jsonl` — JSON-Lines mit Timestamps

## Häufige Aufgaben für diesen Prompt

### Aufgabe direkt ausführen
```bash
source /home/danijel-jd/.openclaw/.venv/bin/activate
python3 openclaw_cert.py 3
```

### Dotenv-Fallback smoke-testen
```bash
# Mit python-dotenv (Standard)
python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.environ.get('OPENAI_API_KEY', 'NICHT GESETZT'))"

# Ohne python-dotenv (Fallback-Pfad)
python3 -c "import sys; sys.modules['dotenv'] = None" openclaw_cert.py --help 2>&1 | head -5
```

### Gesamtreport generieren (ohne API-Key)
```bash
python3 openclaw_cert.py report
```

### Debug-Modus
```bash
python3 openclaw_cert.py --debug 1
# → Logs in logs/debug_<timestamp>.log
```

## Konventionen

- `DEVELOPER = "Danijel Jokic"` — darf NIE geändert werden
- `PRODUCT = "HyperDashboard-ONE.DE"`
- Retry-Logik: 3 Versuche, Backoff 1s → 2s → 4s (nur `RateLimitError`, `APITimeoutError`, `APIConnectionError`)
- Kein stiller Fehler bei `OPENAI_API_KEY` fehlt: → `sys.exit(1)` mit Hinweis
- `.env` niemals committen — nur `.env.example`
