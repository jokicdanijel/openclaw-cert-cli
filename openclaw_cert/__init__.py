"""
OpenClaw Master-Zertifizierungs-CLI — Paketstruktur.

Module:
  config       Konfiguration, Pfade, Console, Logging
  tasks        Task-Definitionen (Prompts)
  stream_tee   StreamTee-Klasse (paralleles Datei-Streaming)
  api          OpenAI-Client + Retry-Logik
  reports      Report-Generierung
  display      UI (Banner, Status, Streams)
  cli          Hauptmenü + CLI-Dispatch
  docs         KI-Dokumentation
"""

__version__ = "2.0.0"
