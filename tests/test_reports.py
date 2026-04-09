"""
Tests für Report-Generierung: generate_combined_report() und generate_finale_readme().

6 Tests: combined_report (mit/ohne Reports, Inhalt), finale_readme (vollständig, partial, Zertifizierung)
"""

import datetime
from pathlib import Path

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# generate_combined_report()
# ─────────────────────────────────────────────────────────────────────────────

def test_combined_report_creates_file(fake_reports, isolated_dirs, silent_console):
    """generate_combined_report() erstellt OPENCLAW_MASTER_ZERTIFIZIERUNG_KOMPLETT.md."""
    from openclaw_cert import generate_combined_report

    generate_combined_report()

    out = isolated_dirs["reports"] / "OPENCLAW_MASTER_ZERTIFIZIERUNG_KOMPLETT.md"
    assert out.exists()


def test_combined_report_contains_all_tasks(fake_reports, isolated_dirs, silent_console):
    """Der Gesamtreport enthält Inhalte aller 6 Task-Reports."""
    from openclaw_cert import generate_combined_report

    generate_combined_report()

    out = isolated_dirs["reports"] / "OPENCLAW_MASTER_ZERTIFIZIERUNG_KOMPLETT.md"
    content = out.read_text(encoding="utf-8")

    # Inhaltsverzeichnis
    assert "Inhaltsverzeichnis" in content

    # Inhalt der einzelnen Reports
    for i in range(1, 7):
        assert f"Aufgabe {i}" in content

    # Zertifizierungsbestätigung am Ende
    assert "Zertifizierungsbestätigung" in content
    assert "ZERTIFIZIERT" in content
    assert "Danijel Jokic" in content
    assert "HyperDashboard-ONE.DE" in content


def test_combined_report_no_reports(isolated_dirs, silent_console):
    """Ohne vorhandene Reports gibt generate_combined_report() eine Warnung aus."""
    from openclaw_cert import generate_combined_report

    generate_combined_report()

    # Kein Output-File erstellt
    out = isolated_dirs["reports"] / "OPENCLAW_MASTER_ZERTIFIZIERUNG_KOMPLETT.md"
    assert not out.exists()

    # Warnung wurde in die Console geschrieben
    output = silent_console.getvalue()
    assert "Keine Reports" in output


# ─────────────────────────────────────────────────────────────────────────────
# generate_finale_readme()
# ─────────────────────────────────────────────────────────────────────────────

def test_finale_readme_all_complete(fake_reports, isolated_dirs, silent_console):
    """Bei 6/6 fertigen Tasks: Zertifizierungsbestätigung und Status-Tabelle."""
    from openclaw_cert import generate_finale_readme

    result = generate_finale_readme()

    assert result is not None
    out = Path(result)
    assert out.exists()
    assert "FINALE_ZUSAMMENFASSUNG" in out.name

    content = out.read_text(encoding="utf-8")

    # Status-Tabelle mit allen Tasks
    assert "Abgeschlossen" in content
    assert "6/6" in content

    # Zertifizierungsbestätigung (nur wenn alle fertig)
    assert "ZERTIFIZIERT" in content
    assert "Firefly Copilot" in content

    # Systemzustand
    assert "Modell" in content


def test_finale_readme_partial(isolated_dirs, silent_console):
    """Bei teilweise fertigen Tasks: offene Tasks als 'Offen' markiert."""
    from openclaw_cert import generate_finale_readme

    reports_dir = isolated_dirs["reports"]
    # Nur Tasks 1 und 3 vorhanden
    (reports_dir / "task_1_Test.md").write_text("# Task 1\n", encoding="utf-8")
    (reports_dir / "task_3_Test.md").write_text("# Task 3\n", encoding="utf-8")

    result = generate_finale_readme()

    content = Path(result).read_text(encoding="utf-8")

    assert "2/6" in content
    # Kein Zertifizierungs-Footer bei unvollständig
    assert "ZERTIFIZIERT" not in content
    assert "Offen" in content


def test_finale_readme_no_reports(isolated_dirs, silent_console):
    """Ohne Reports: 0/6, keine Zertifizierung, aber Datei wird trotzdem erstellt."""
    from openclaw_cert import generate_finale_readme

    result = generate_finale_readme()

    content = Path(result).read_text(encoding="utf-8")

    assert "0/6" in content
    assert "ZERTIFIZIERT" not in content
