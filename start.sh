#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║   OpenClaw Master-Zertifizierungs-CLI                       ║
# ║   HyperDashboard-ONE.DE  ·  Entwickelt von Danijel Jokic    ║
# ╚══════════════════════════════════════════════════════════════╝

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  🦞  OpenClaw Master-Zertifizierungs-CLI             ║${NC}"
echo -e "${CYAN}║      HyperDashboard-ONE.DE                           ║${NC}"
echo -e "${CYAN}║      Entwickelt von Danijel Jokic                    ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# ── Python-Interpreter bestimmen ─────────────────────────────────
VENV_PY="/home/danijel-jd/.openclaw/.venv/bin/python3"
if [ -x "$VENV_PY" ]; then
    PYTHON="$VENV_PY"
    echo -e "${GREEN}✓ venv aktiv: $VENV_PY${NC}"
elif command -v python3 &> /dev/null; then
    PYTHON="python3"
    echo -e "${YELLOW}⚠  Kein venv gefunden – verwende System-Python3${NC}"
else
    echo -e "${RED}✗ Python3 nicht gefunden. Abbruch.${NC}"
    exit 1
fi

# ── .env laden (falls vorhanden) ─────────────────────────────────
if [ -z "$OPENAI_API_KEY" ] && [ -f ".env" ]; then
    # shellcheck disable=SC2046
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
    echo -e "${GREEN}✓ .env geladen${NC}"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠  OPENAI_API_KEY nicht gesetzt.${NC}"
    echo -e "${YELLOW}   → cp .env.example .env  und API-Key eintragen${NC}"
    echo ""
fi

# ── Abhängigkeiten prüfen ─────────────────────────────────────────
if ! "$PYTHON" -c "import rich, openai" 2>/dev/null; then
    echo -e "${YELLOW}📦 Installiere Abhängigkeiten...${NC}"
    "$PYTHON" -m pip install rich openai python-dotenv -q
fi

echo -e "${GREEN}✓ Bereit${NC}"
echo ""

# ── Starten ───────────────────────────────────────────────────────
exec "$PYTHON" -m openclaw_cert "$@"
