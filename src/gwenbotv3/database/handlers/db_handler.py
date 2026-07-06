from sqlite3 import Cursor
from pathlib import Path

from gwenbotv3 import SingletonLogger
from gwenbotv3.database import connect


class DatabaseHandler:
    def __init__(self):
        self.logger = SingletonLogger().get_logger()
        self.sql_files = Path(__file__).resolve().parent / "sql_files"

    @connect
    def create_db(self, cur: Cursor) -> None:
        """Try to create the Database tables each time the bot runs."""
        self.logger.debug("Attempting to create Database tables.")

        init_file = self.sql_files / "tables.sql"

        with open(str(init_file), "r", encoding="utf-8") as f:
            cur.executescript(f.read())
