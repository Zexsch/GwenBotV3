"""Initialises logging for the entire project.

Import this module and run init_logging before doing anything else.
"""

import logging
import sys
from pathlib import Path
from types import TracebackType

from gwenbotv3.loggers.logger_setup import setup_logging


def init_logging(log_dir: Path) -> None:
    """Initialises logging for the project.

    See loggers.logger_setup for the actual setup.

    Args:
        log_dir (Path): Path of the log directory.
    """
    setup_logging(log_dir)
    logger = logging.getLogger("exception_handler")

    def handle_exception(
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> None:

        if exc_type is None:
            logger.exception("Uncaught exception with no exc_type: ")
            return

        if exc_value is None:
            logger.exception("Uncaught exception with no exc_value: ")
            return

        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.exception("Uncaught exception: ")

    sys.excepthook = handle_exception
    logger.info("Set up exception logging.")
