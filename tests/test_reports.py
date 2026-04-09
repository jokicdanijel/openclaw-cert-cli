"""Tests für Report-Generierung (openclaw_cert.reports)."""

from pathlib import Path

import pytest


def test_combined_report_creates_file(fake_reports, isolated_dirs, silent_console):
    from openclaw_cert.reports import generate_combined_report
    generate_combined_report()
    assert (isolated_dirs["reports"] / "OPENCLAW_MASTER_ZERTIFIZIERUNG_KOMPLETT.md").exists()


def test_combined_report_contains_all_tasks(fake_reports, isolated_dirs, silent_console):
    from openclaw_cert.reports import generate_combined_report
    generate_combined_report()
    content = (isolated_dirs["reports"] / "OPENCLAW_MASTER_ZERTIFIZIERUNG_KOMPLETT.md").read_text("utf-8")
    assert "Inhaltsverzeichnis" in content
    for i in range(1, 7):
        assert f"Aufgabe {i}" in content
    assert "ZERTIFIZIERT" in content


def test_combined_report_no_reports(isolated_dirs, silent_console):
    from openclaw_cert.reports import generate_combined_report
    generate_combined_report()
    assert not (isolated_dirs["reports"] / "OPENCLAW_MASTER_ZERTIFIZIERUNG_KOMPLETT.md").exists()
    assert "Keine Reports" in silent_console.getvalue()


def test_finale_readme_all_complete(fake_reports, isolated_dirs, silent_console):
    from openclaw_cert.reports import generate_finale_readme
    result = generate_finale_readme()
    content = Path(result).read_text("utf-8")
    assert "6/6" in content
    assert "ZERTIFIZIERT" in content


def test_finale_readme_partial(isolated_dirs, silent_console):
    reports_dir = isolated_dirs["reports"]
    (reports_dir / "task_1_Test.md").write_text("# 1\n", encoding="utf-8")
    (reports_dir / "task_3_Test.md").write_text("# 3\n", encoding="utf-8")

    from openclaw_cert.reports import generate_finale_readme
    result = generate_finale_readme()
    content = Path(result).read_text("utf-8")
    assert "2/6" in content
    assert "ZERTIFIZIERT" not in content


def test_finale_readme_no_reports(isolated_dirs, silent_console):
    from openclaw_cert.reports import generate_finale_readme
    result = generate_finale_readme()
    content = Path(result).read_text("utf-8")
    assert "0/6" in content
    assert "ZERTIFIZIERT" not in content
