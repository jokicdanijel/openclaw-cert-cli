#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║   OpenClaw Master-Zertifizierungs-CLI                       ║
# ║   HyperDashboard-ONE.DE  ·  Entwickelt von Danijel Jokic    ║
# ╚══════════════════════════════════════════════════════════════╝

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

# Python prüfen
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Fehler: Python3 nicht gefunden.${NC}"
    exit 1
fi

# .env laden falls vorhanden
if [ -z "$OPENAI_API_KEY" ] && [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo -e "${GREEN}✓ .env geladen${NC}"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}Hinweis: OPENAI_API_KEY nicht gesetzt.${NC}"
    echo -e "${YELLOW}Erstelle eine .env Datei: cp .env.example .env${NC}"
    echo ""
fi

# Abhängigkeiten prüfen
python3 -c "import rich, openai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Installiere Abhängigkeiten...${NC}"
    pip3 install rich openai python-dotenv -q
fi

echo -e "${GREEN}✓ Bereit${NC}"
echo ""

# Starten
if [ -n "$1" ]; then
    python3 openclaw_cert.py "$1"
else
    python3 openclaw_cert.py
fi
