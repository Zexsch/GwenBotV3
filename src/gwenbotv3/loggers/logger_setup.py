import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class _LevelEqualsFilter(logging.Filter):
    def __init__(self, level: int):
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == self.level


def setup_logging(log_dir: Path, logger_name: str | None = None) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    def make_file_handler(
        filename: str, when: str, interval: int, backup_count: int, level: int
    ) -> TimedRotatingFileHandler:
        handler = TimedRotatingFileHandler(
            filename=str(log_dir / filename),
            when=when,
            interval=interval,
            backupCount=backup_count,
            encoding="utf-8",
            utc=False,
        )
        handler.setLevel(level)
        handler.setFormatter(formatter)
        return handler

    debug_file_handler = make_file_handler(
        "debug.log", when="midnight", interval=1, backup_count=14, level=logging.DEBUG
    )

    info_file_handler = make_file_handler(
        "info.log", when="W0", interval=1, backup_count=4, level=logging.INFO
    )
    info_file_handler.addFilter(_LevelEqualsFilter(logging.INFO))

    warning_file_handler = make_file_handler(
        "warning.log", when="W0", interval=1, backup_count=13, level=logging.WARNING
    )

    info_console_handler = logging.StreamHandler()
    info_console_handler.setLevel(logging.INFO)
    info_console_handler.setFormatter(formatter)
    info_console_handler.addFilter(_LevelEqualsFilter(logging.INFO))

    warning_console_handler = logging.StreamHandler()
    warning_console_handler.setLevel(logging.WARNING)
    warning_console_handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # let handlers do the level filtering
    logger.propagate = False

    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    for handler in (
        debug_file_handler,
        info_file_handler,
        warning_file_handler,
        info_console_handler,
        warning_console_handler,
    ):
        logger.addHandler(handler)

    return logger
