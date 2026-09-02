"""Main entry point.

Either run this file directly or use the gwenbot-init command.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# pylint: disable=import-outside-toplevel, wrong-import-position
from gwenbotv3.loggers import init_logging

log_dir = Path("/home/container/Logs")

init_logging(log_dir)

# ruff: noqa: E402
# Import here because logging needs to be set up first
from gwenbotv3 import App


def main() -> None:
    """Main entry point."""
    logger = logging.getLogger(__name__)
    logger.info("Starting app.")
    app = App()
    app.run(token=os.environ["TOKEN"])


if __name__ == "__main__":
    main()
