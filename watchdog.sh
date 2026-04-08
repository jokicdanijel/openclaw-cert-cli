#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║   OpenClaw Master-Zertifizierungs-CLI — Watchdog             ║
# ║   Prüft alle 5 Min. ob fehlende Aufgaben nachgeholt werden   ║
# ║   Ausführung: in Docker-Sandbox (sicher, isoliert)           ║
# ║   HyperDashboard-ONE.DE  ·  Entwickelt von Danijel Jokic     ║
# ╚══════════════════════════════════════════════════════════════╝
#
# Verwendung:
#   bash watchdog.sh             # Watchdog starten (läuft im Vordergrund)
#   bash watchdog.sh --once      # Nur einmalig prüfen und beenden
#   bash watchdog.sh --status    # Nur Status anzeigen
#
# Voraussetzungen:
#   - Docker läuft
#   - .env mit OPENAI_API_KEY vorhanden
#   - Docker-Image gebaut: bash watchdog.sh --build

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Konfiguration ────────────────────────────────────────────────
INTERVAL=300            # 5 Minuten in Sekunden
IMAGE_NAME="openclaw-cert-cli"
REPORTS_DIR="$SCRIPT_DIR/reports"
STREAMS_DIR="$SCRIPT_DIR/streams"
LOGS_DIR="$SCRIPT_DIR/logs"
TOTAL_TASKS=6

# ── Farben ───────────────────────────────────────────────────────
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
DIM='\033[2m'
NC='\033[0m'

# ── Hilfsfunktionen ──────────────────────────────────────────────
log() { echo -e "${DIM}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $*"; }
ok()  { echo -e "${GREEN}✓${NC} $*"; }
warn(){ echo -e "${YELLOW}⚠${NC}  $*"; }
err() { echo -e "${RED}✗${NC} $*"; }

banner() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  🦞  OpenClaw Cert-CLI — Watchdog                    ║${NC}"
    echo -e "${CYAN}║      Intervall: ${INTERVAL}s (alle 5 Min.)                  ║${NC}"
    echo -e "${CYAN}║      Sandbox: Docker-Container                       ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# ── Voraussetzungen prüfen ───────────────────────────────────────
check_requirements() {
    if ! command -v docker &>/dev/null; then
        err "Docker nicht gefunden. Bitte installieren."
        exit 1
    fi
    if ! docker info &>/dev/null; then
        err "Docker-Daemon nicht erreichbar. Bitte starten: sudo systemctl start docker"
        exit 1
    fi
    if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
        warn "Docker-Image '$IMAGE_NAME' nicht gefunden."
        echo -e "  → Baue Image jetzt..."
        build_image
    fi
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        err ".env fehlt. Bitte erstellen: cp .env.example .env && nano .env"
        exit 1
    fi
    # API-Key prüfen (ohne ihn anzuzeigen)
    if ! grep -q "OPENAI_API_KEY=sk-" "$SCRIPT_DIR/.env" 2>/dev/null; then
        err "OPENAI_API_KEY nicht gesetzt oder ungültig in .env"
        exit 1
    fi
    # Verzeichnisse anlegen
    mkdir -p "$REPORTS_DIR" "$STREAMS_DIR" "$LOGS_DIR"
}

# ── Docker-Image bauen ───────────────────────────────────────────
build_image() {
    log "Baue Docker-Image: $IMAGE_NAME..."
    docker build -t "$IMAGE_NAME" "$SCRIPT_DIR" \
        --label "maintainer=Danijel Jokic" \
        --label "project=openclaw-cert-cli" \
        2>&1 | tail -5
    ok "Image gebaut: $IMAGE_NAME"
}

# ── Fehlende Aufgaben ermitteln ──────────────────────────────────
get_missing_tasks() {
    local missing=()
    for i in $(seq 1 $TOTAL_TASKS); do
        if ! ls "$REPORTS_DIR"/task_${i}_*.md &>/dev/null 2>&1; then
            missing+=("$i")
        fi
    done
    echo "${missing[@]:-}"
}

# ── Status anzeigen ──────────────────────────────────────────────
show_status() {
    echo ""
    echo -e "${CYAN}── Aufgaben-Status ────────────────────────────────────${NC}"
    local done_count=0
    for i in $(seq 1 $TOTAL_TASKS); do
        if ls "$REPORTS_DIR"/task_${i}_*.md &>/dev/null 2>&1; then
            local fname
            fname=$(ls "$REPORTS_DIR"/task_${i}_*.md 2>/dev/null | head -1 | xargs basename)
            echo -e "  ${GREEN}✅ Aufgabe $i${NC}  ${DIM}$fname${NC}"
            ((done_count++))
        else
            echo -e "  ${YELLOW}⏳ Aufgabe $i${NC}  ${DIM}[fehlt]${NC}"
        fi
    done
    echo ""
    echo -e "  Abgeschlossen: ${GREEN}$done_count${NC}/$TOTAL_TASKS"
    echo ""
}

# ── Aufgabe in Docker-Sandbox ausführen ─────────────────────────
run_task_in_sandbox() {
    local task_num="$1"
    log "Starte Aufgabe $task_num in Docker-Sandbox..."

    docker run --rm \
        --name "openclaw-task-${task_num}-$$" \
        --env-file "$SCRIPT_DIR/.env" \
        --env "OPENCLAW_DEBUG=false" \
        --volume "$REPORTS_DIR:/app/reports" \
        --volume "$STREAMS_DIR:/app/streams" \
        --volume "$LOGS_DIR:/app/logs" \
        --network "host" \
        --memory "512m" \
        --cpus "1.0" \
        --read-only \
        --tmpfs /tmp \
        "$IMAGE_NAME" "$task_num" 2>&1

    if ls "$REPORTS_DIR"/task_${task_num}_*.md &>/dev/null 2>&1; then
        ok "Aufgabe $task_num erfolgreich abgeschlossen"
        return 0
    else
        warn "Aufgabe $task_num: kein Report erzeugt"
        return 1
    fi
}

# ── Einmal prüfen und ggf. nachholen ────────────────────────────
run_once() {
    log "Prüfe fehlende Aufgaben..."
    show_status

    local missing
    missing=$(get_missing_tasks)

    if [ -z "$missing" ]; then
        ok "Alle $TOTAL_TASKS Aufgaben sind abgeschlossen. Kein Handlungsbedarf."
        return 0
    fi

    warn "Fehlende Aufgaben: $missing"
    echo ""

    for task_num in $missing; do
        run_task_in_sandbox "$task_num" || true
        sleep 2
    done

    show_status
}

# ── Watchdog-Loop ────────────────────────────────────────────────
run_watchdog() {
    banner
    check_requirements
    ok "Watchdog gestartet. Intervall: ${INTERVAL}s"
    log "Stoppen mit: Ctrl+C"
    echo ""

    local cycle=1
    while true; do
        echo -e "${CYAN}── Zyklus $cycle ── $(date '+%Y-%m-%d %H:%M:%S') ──────────────────${NC}"
        run_once
        echo ""
        log "Nächste Prüfung in ${INTERVAL}s (Ctrl+C zum Beenden)..."
        sleep "$INTERVAL"
        ((cycle++))
    done
}

# ── Entry Point ──────────────────────────────────────────────────
case "${1:-}" in
    --build)
        build_image
        ;;
    --status)
        show_status
        ;;
    --once)
        check_requirements
        run_once
        ;;
    "")
        run_watchdog
        ;;
    *)
        echo "Verwendung: bash watchdog.sh [--build | --once | --status]"
        exit 1
        ;;
esac
