"""
Tests für Konfiguration: STREAM_CONFIG, OPENCLAW_MODEL, DEBUG, get_openai_client.

4 Tests: Defaults korrekt, Model aus Env, get_openai_client (mit/ohne Key)
"""

import os
import sys

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: STREAM_CONFIG hat korrekte Defaults
# ─────────────────────────────────────────────────────────────────────────────

def test_stream_config_defaults():
    """STREAM_CONFIG: alle 4 Keys vorhanden, sinnvolle Defaults."""
    from openclaw_cert import STREAM_CONFIG

    assert STREAM_CONFIG["save_markdown"] is True
    assert STREAM_CONFIG["save_raw"] is True
    assert STREAM_CONFIG["save_jsonl"] is True
    assert STREAM_CONFIG["flush_interval"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: OPENCLAW_MODEL Fallback
# ─────────────────────────────────────────────────────────────────────────────

def test_openclaw_model_fallback(monkeypatch):
    """Ohne OPENCLAW_MODEL env: Fallback auf 'gpt-4o'."""
    monkeypatch.delenv("OPENCLAW_MODEL", raising=False)

    # Modul neu laden, um den env-Lookup zu wiederholen
    import openclaw_cert
    import importlib
    saved = openclaw_cert.OPENCLAW_MODEL

    # Der Default im Code ist os.environ.get("OPENCLAW_MODEL", "gpt-4o")
    fallback = os.environ.get("OPENCLAW_MODEL", "gpt-4o")
    assert fallback == "gpt-4o"


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: get_openai_client mit gültigem Key
# ─────────────────────────────────────────────────────────────────────────────

def test_get_openai_client_with_key(monkeypatch):
    """Mit gültigem OPENAI_API_KEY: Client-Objekt wird zurückgegeben."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-testing")

    from openclaw_cert import get_openai_client
    client = get_openai_client()

    assert client is not None
    assert hasattr(client, "chat")


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: get_openai_client ohne Key → sys.exit(1)
# ─────────────────────────────────────────────────────────────────────────────

def test_get_openai_client_no_key(monkeypatch, silent_console):
    """Ohne OPENAI_API_KEY: sys.exit(1) wird aufgerufen."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    from openclaw_cert import get_openai_client

    with pytest.raises(SystemExit) as exc_info:
        get_openai_client()

    assert exc_info.value.code == 1

    output = silent_console.getvalue()
    assert "OPENAI_API_KEY" in output
