import logging
import sqlite3
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from types import TracebackType
from typing import Concatenate, cast


class _DatabaseConnector:
    """Context manager to start a database connection.

    Enables foreign_keys intrinsically.
    """

    def __init__(self) -> None:
        db_folder = Path(__file__).resolve().parent.parent / "db"

        if not db_folder.exists():
            db_folder.mkdir()

        self.database_path: str = str(db_folder / "GwenUsers.db")
        self.logger = logging.getLogger(__name__)

    def __enter__(self) -> sqlite3.Cursor:
        # pylint: disable=attribute-defined-outside-init
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = 1")
        self.cursor = self.connection.cursor()

        return self.cursor

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        if exc_type is None:
            self.connection.commit()
        else:
            self.logger.exception("Error in Database connection, rolling back.")
            self.connection.rollback()

        self.connection.close()


def connect[Self, **P, R](
    func: Callable[Concatenate[Self, sqlite3.Cursor, P], R],
) -> Callable[Concatenate[Self, P], R]:
    """Connect to the database.

    Use as a decorator every time an sqlite3.Cursor object is needed.
    This decorator will inject the cursor object as the second positional argument
    into the decorated method.

    Returns:
        Callable[Concatenate[Self, P], R]: The decorated method,
            but with an sqlite3.Cursor object injected as the second
            positional argument.
    """

    @wraps(func)
    def wrapper(self: Self, *args: P.args, **kwargs: P.kwargs) -> R:
        with _DatabaseConnector() as cursor:
            return func(self, cursor, *args, **kwargs)

    return cast(Callable[Concatenate[Self, P], R], wrapper)
