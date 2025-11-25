import sqlite3
from pathlib import Path
from functools import wraps
from typing import Callable, TypeVar, ParamSpec, Concatenate

class DatabaseConnector:
    def __init__(self):
        self.database_path: str = str(Path(__file__).resolve().parent / "GwenUsers.db")

    def __enter__(self):
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = 1")
        self.cursor = self.connection.cursor()

        return self.cursor
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()


Self = TypeVar("Self")
P = ParamSpec("P")
R = TypeVar("R")

def connect(func: Callable[Concatenate[Self, sqlite3.Cursor, P], R]) -> Callable[Concatenate[Self, P], R]:
    """
    Use as a decorator to connect to the database
    Name conflict with sqlite3.connect, so either rename this or use import sqlite3 to avoid name space collusion
    
    :param func: Function to connect to the database with.
    :type func: Callable[Concatenate[Self, sqlite3.Cursor, P], R]
    :return: Will inject the following parameter types: self, sqlite3.Cursor, *args, **kwargs
    :rtype: Callable[Concatenate[Self, P], R]
    """
    @wraps(func)
    def wrapper(self: Self, *args: P.args, **kwargs: P.kwargs) -> R:
        with DatabaseConnector() as cursor:
            return func(self, cursor, *args, **kwargs)
    return wrapper
