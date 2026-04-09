"""Entry Point: ``python -m openclaw_cert``."""

import sys

from openclaw_cert.config import setup_logging
from openclaw_cert.cli import dispatch_cli_args, main_menu


def main() -> None:
    """Startet das CLI — interaktiv oder per Argument."""
    setup_logging()
    if len(sys.argv) > 1:
        dispatch_cli_args()
    else:
        main_menu()


if __name__ == "__main__":
    main()
