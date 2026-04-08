#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║   OpenClaw Master-Zertifizierungs-CLI — Setup               ║
# ║   HyperDashboard-ONE.DE  ·  Entwickelt von Danijel Jokic    ║
# ╚══════════════════════════════════════════════════════════════╝
#
# Einmalig ausführen: bash setup.sh
# Danach täglich: bash start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

VENV_PATH="/home/danijel-jd/.openclaw/.venv"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  🦞  OpenClaw Cert-CLI — Setup                       ║${NC}"
echo -e "${CYAN}║      HyperDashboard-ONE.DE · Danijel Jokic           ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# ── 1. Python3 prüfen ────────────────────────────────────────────
echo -e "${CYAN}[1/4]${NC} Python3 prüfen..."
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}✗ Python3 nicht gefunden. Bitte installieren:${NC}"
    echo "    sudo apt install python3 python3-venv python3-pip"
    exit 1
fi
PY_VERSION=$(python3 --version)
echo -e "${GREEN}✓ $PY_VERSION${NC}"

# ── 2. venv erstellen (falls nicht vorhanden) ────────────────────
echo ""
echo -e "${CYAN}[2/4]${NC} Virtual Environment prüfen..."
if [ -x "$VENV_PATH/bin/python3" ]; then
    echo -e "${GREEN}✓ venv bereits vorhanden: $VENV_PATH${NC}"
else
    echo -e "${YELLOW}  → Erstelle venv: $VENV_PATH${NC}"
    python3 -m venv "$VENV_PATH"
    echo -e "${GREEN}✓ venv erstellt${NC}"
fi

PYTHON="$VENV_PATH/bin/python3"
PIP="$VENV_PATH/bin/pip"

# ── 3. Abhängigkeiten installieren ───────────────────────────────
echo ""
echo -e "${CYAN}[3/4]${NC} Abhängigkeiten installieren..."
"$PIP" install --upgrade pip -q
"$PIP" install rich openai python-dotenv -q
echo -e "${GREEN}✓ Installiert: rich, openai, python-dotenv${NC}"

# Versionen anzeigen
echo ""
"$PYTHON" -c "import openai, dotenv; from importlib.metadata import version; print('  rich', version('rich'), '· openai', openai.__version__, '· python-dotenv', dotenv.__version__)"

# ── 4. .env anlegen (falls nicht vorhanden) ──────────────────────
echo ""
echo -e "${CYAN}[4/4]${NC} Konfiguration prüfen..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env bereits vorhanden${NC}"
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}  → .env aus .env.example erstellt${NC}"
        echo -e "${YELLOW}  → Bitte OPENAI_API_KEY eintragen:${NC}"
        echo ""
        echo -e "     ${CYAN}nano .env${NC}"
    else
        echo -e "${RED}✗ .env.example nicht gefunden${NC}"
    fi
fi

# ── Abschluss ────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Setup abgeschlossen!                              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Nächster Schritt: ${CYAN}bash start.sh${NC}"
echo ""
