# ╔══════════════════════════════════════════════════════════════╗
# ║   OpenClaw Master-Zertifizierungs-CLI — Docker Sandbox       ║
# ║   HyperDashboard-ONE.DE  ·  Entwickelt von Danijel Jokic     ║
# ╚══════════════════════════════════════════════════════════════╝
FROM python:3.13-slim

# Sicherheit: kein Root-User
RUN useradd -m -u 1000 openclaw
WORKDIR /app

# Nur notwendige Dateien kopieren (kein .env, kein .git)
COPY openclaw_cert.py ./
COPY start.sh ./
COPY .env.example ./
COPY cert-cli-uc/ ./cert-cli-uc/

# Abhängigkeiten installieren
RUN pip install --no-cache-dir rich openai python-dotenv

# Reports- und Streams-Verzeichnisse anlegen (werden als Volume gemountet)
RUN mkdir -p /app/reports /app/streams /app/logs \
    && chown -R openclaw:openclaw /app

USER openclaw

# Umgebungsvariablen (werden zur Laufzeit über --env oder .env gesetzt)
ENV OPENCLAW_MODEL=gpt-4o
ENV OPENCLAW_DEBUG=false
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python3", "openclaw_cert.py"]
CMD ["--help"]
