"""Tests für Konfiguration (openclaw_cert.config)."""

import os
import sys

import pytest


def test_stream_config_defaults():
    from openclaw_cert.config import STREAM_CONFIG
    assert STREAM_CONFIG["save_markdown"] is True
    assert STREAM_CONFIG["save_raw"] is True
    assert STREAM_CONFIG["save_jsonl"] is True
    assert STREAM_CONFIG["flush_interval"] == 1


def test_openclaw_model_fallback(monkeypatch):
    monkeypatch.delenv("OPENCLAW_MODEL", raising=False)
    fallback = os.environ.get("OPENCLAW_MODEL", "gpt-4o")
    assert fallback == "gpt-4o"


def test_get_openai_client_with_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-testing")
    from openclaw_cert.api import get_openai_client
    client = get_openai_client()
    assert client is not None
    assert hasattr(client, "chat")


def test_get_openai_client_no_key(monkeypatch, silent_console):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from openclaw_cert.api import get_openai_client
    with pytest.raises(SystemExit) as exc:
        get_openai_client()
    assert exc.value.code == 1
    assert "OPENAI_API_KEY" in silent_console.getvalue()


def test_ensure_dirs(tmp_path, monkeypatch):
    """ensure_dirs() erstellt alle drei Verzeichnisse."""
    from openclaw_cert import config
    monkeypatch.setattr(config, "REPORT_DIR", tmp_path / "r")
    monkeypatch.setattr(config, "STREAM_DIR", tmp_path / "s")
    monkeypatch.setattr(config, "LOG_DIR", tmp_path / "l")
    config.ensure_dirs()
    assert (tmp_path / "r").is_dir()
    assert (tmp_path / "s").is_dir()
    assert (tmp_path / "l").is_dir()
