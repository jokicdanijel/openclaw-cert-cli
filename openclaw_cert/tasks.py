"""Task-Definitionen für die OpenClaw Master-Zertifizierung."""
from __future__ import annotations

TASKS: dict[int, dict[str, str]] = {
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
