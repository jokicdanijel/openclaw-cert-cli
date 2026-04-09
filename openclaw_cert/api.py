"""
OpenAI-Client-Initialisierung und Retry-fähiges Streaming.

Zentrale Stelle für API-Kommunikation.  ``stream_with_retry`` kapselt die
3-Versuch-Retry-Logik (RateLimitError, APITimeoutError, APIConnectionError)
und gibt einen StreamTee zurück.
"""
from __future__ import annotations

import logging
import os
import sys
import time

import openai
from openai import OpenAI
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from openclaw_cert import config
from openclaw_cert.stream_tee import StreamTee

_RETRY_DELAYS: tuple[int, ...] = (1, 2, 4)
_RETRIABLE_ERRORS = (openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError)


def get_openai_client() -> OpenAI:
    """Erstellt einen OpenAI-Client.  Beendet das Programm, wenn kein Key vorhanden."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        config.console.print("[bold red]Fehler:[/bold red] OPENAI_API_KEY nicht gesetzt.")
        sys.exit(1)
    return OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")


def stream_with_retry(
    client: OpenAI,
    *,
    task_num: int,
    task_title: str,
    prompt: str,
    panel_title: str,
) -> StreamTee:
    """Streamt die API-Antwort mit bis zu 3 Versuchen und Live-Panel.

    Gibt den (bereits geschlossenen) StreamTee zurück.
    Bei totalem Fehlschlag ist ``tee.full_text()`` leer.
    """
    tee: StreamTee | None = None

    for attempt in range(1, 4):
        tee = StreamTee(
            task_num=task_num,
            task_title=task_title,
            save_raw=config.STREAM_CONFIG["save_raw"],
            save_jsonl=config.STREAM_CONFIG["save_jsonl"],
        )
        try:
            logging.debug("%s: Versuch %d/3", task_title, attempt)
            stream = client.chat.completions.create(
                model=config.OPENCLAW_MODEL,
                messages=[
                    {"role": "system", "content": config.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_completion_tokens=4096,
                stream=True,
            )
            with Live(console=config.console, refresh_per_second=15) as live:
                for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    tee.write(delta)
                    live.update(Panel(
                        Markdown(tee.full_text()),
                        title=(
                            f"[bold cyan]{panel_title} · Live[/bold cyan]  "
                            f"[dim]{len(tee.full_text())} Zeichen[/dim]"
                        ),
                        border_style="cyan",
                        padding=(0, 2),
                    ))
            logging.debug("%s: erfolgreich · %d Zeichen", task_title, len(tee.full_text()))
            tee.close()
            return tee

        except _RETRIABLE_ERRORS as exc:
            wait = _RETRY_DELAYS[attempt - 1]
            logging.warning("%s: Retry %d/3 – warte %ds – %s", task_title, attempt, wait, exc)
            tee.close()
            if attempt < 3:
                config.console.print(f"\n[yellow]⚠  API-Fehler (Versuch {attempt}/3): {exc}[/yellow]")
                config.console.print(f"[dim]Warte {wait}s vor erneutem Versuch...[/dim]")
                time.sleep(wait)
            else:
                logging.error("%s: Alle 3 Versuche fehlgeschlagen – %s", task_title, exc)
                config.console.print(f"\n[bold red]✗ Alle 3 Versuche fehlgeschlagen:[/bold red] {exc}")
                return tee  # leer, aber geschlossen

        except Exception as exc:
            tee.close()
            logging.error("%s: Unerwarteter Fehler – %s", task_title, exc)
            config.console.print(f"[bold red]API-Fehler:[/bold red] {exc}")
            return tee  # leer, aber geschlossen

    # Fallback (sollte nicht erreicht werden)
    assert tee is not None
    return tee
