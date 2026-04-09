"""
Konfiguration, Umgebungsvariablen und Logging-Setup.

Zentrale Stelle für alle Konfigurationswerte.  Andere Module importieren
dieses Modul als Objekt (``from openclaw_cert import config``) und greifen
über ``config.REPORT_DIR`` etc. zu — so bleiben Monkeypatches in Tests wirksam.
"""
from __future__ import annotations

import datetime
import logging
import os
import sys
from pathlib import Path

# .env automatisch laden (python-dotenv), falls vorhanden
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=False)
except ImportError:
    pass  # python-dotenv nicht installiert → kein Problem, start.sh übernimmt das

try:
    from rich.console import Console
except ImportError:
    print("Fehler: 'rich' nicht installiert. Bitte: pip install rich")
    sys.exit(1)

# ── Pfade ────────────────────────────────────────────────────────────────────
REPORT_DIR: Path = Path("./reports")
STREAM_DIR: Path = Path("./streams")
LOG_DIR: Path = Path("./logs")

# ── Metadaten ────────────────────────────────────────────────────────────────
DEVELOPER: str = "Danijel Jokic"
PRODUCT: str = "HyperDashboard-ONE.DE"

# ── Streaming-Konfiguration ─────────────────────────────────────────────────
STREAM_CONFIG: dict[str, bool | int] = {
    "save_markdown": True,
    "save_raw": True,
    "save_jsonl": True,
    "flush_interval": 1,
}

# ── Modell ───────────────────────────────────────────────────────────────────
OPENCLAW_MODEL: str = os.environ.get("OPENCLAW_MODEL", "gpt-4o")

# ── Debug ────────────────────────────────────────────────────────────────────
DEBUG: bool = "--debug" in sys.argv
if DEBUG:
    sys.argv = [a for a in sys.argv if a != "--debug"]

# ── Console ──────────────────────────────────────────────────────────────────
console: Console = Console()

# ── System-Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT: str = r"""Du bist Firefly Copilot, ein zertifizierter Master-Experte für OpenClaw –
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

Du gibst IMMER vollständige, produktionsreife Antworten – niemals unvollständige Fragmente.
"""


def ensure_dirs() -> None:
    """Erstellt alle benötigten Verzeichnisse (idempotent)."""
    REPORT_DIR.mkdir(exist_ok=True)
    STREAM_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)


def setup_logging() -> None:
    """Konfiguriert Datei- und optionalen Console-Logger."""
    ensure_dirs()
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    logging.basicConfig(
        level=logging.DEBUG if DEBUG else logging.WARNING,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / f"debug_{ts}.log", encoding="utf-8"),
            *([] if not DEBUG else [logging.StreamHandler()]),
        ],
    )
    logging.info(
        "OpenClaw Cert-CLI gestartet · Debug=%s · Modell=%s", DEBUG, OPENCLAW_MODEL,
    )
