import sqlite3
from pathlib import Path
from functools import wraps
from typing import Callable, TypeVar, ParamSpec, Concatenate


class _DatabaseConnector:
    def __init__(self):
        db_folder = Path(__file__).resolve().parent.parent / "db"

        if not db_folder.exists():
            db_folder.mkdir()

        self.database_path: str = str(db_folder / "GwenUsers.db")

    def __enter__(self):
        # pylint: disable=attribute-defined-outside-init
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = 1")
        self.cursor = self.connection.cursor()

        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()

        self.connection.close()


Self = TypeVar("Self")
P = ParamSpec("P")
R = TypeVar("R")


def connect(
    func: Callable[Concatenate[Self, sqlite3.Cursor, P], R],
) -> Callable[Concatenate[Self, P], R]:
    """
    Use as a decorator to connect to the database
    Name conflict with sqlite3.connect, so either rename this or use module import to avoid name space collusion

    :param func: Function to connect to the database with.
    :type func: Callable[Concatenate[Self, sqlite3.Cursor, P], R]
    :return: Will inject the following parameter types: self, sqlite3.Cursor, *args, **kwargs
    :rtype: Callable[Concatenate[Self, P], R]
    """

    @wraps(func)
    def wrapper(self: Self, *args: P.args, **kwargs: P.kwargs) -> R:
        with _DatabaseConnector() as cursor:
            return func(self, cursor, *args, **kwargs)

    return wrapper
