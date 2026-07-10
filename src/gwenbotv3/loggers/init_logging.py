import sys
import logging
from pathlib import Path

from gwenbotv3.loggers.logger_setup import setup_logging


def init_logging(log_dir: Path) -> None:
    setup_logging(log_dir)
    logger = logging.getLogger("exception_handler")

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.critical(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception
    logger.info("Set up exception logging.")
