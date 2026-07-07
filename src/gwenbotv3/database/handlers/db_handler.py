from sqlite3 import Cursor
from pathlib import Path

from gwenbotv3 import SingletonLogger
from gwenbotv3.database import connect


class DatabaseHandler:
    def __init__(self):
        self.logger = SingletonLogger().get_logger()
        self.sql_files = Path(__file__).resolve().parent / "sql_files"

    @connect
    def initialise(self, cur: Cursor) -> None:
        """Try to create the Database tables each time the bot runs."""
        self.logger.debug("Attempting to create Database tables.")

        init_file = self.sql_files / "tables.sql"
        trigger_file = self.sql_files / "triggers.sql"
        pseudonymise_file = self.sql_files / "pseudonymise.sql"

        with open(str(init_file), "r", encoding="utf-8") as f:
            cur.executescript(f.read())

        with open(str(trigger_file), "r", encoding="utf-8") as f:
            cur.executescript(f.read())

        with open(str(pseudonymise_file), "r", encoding="utf-8") as f:
            cur.executescript(f.read())

    @connect
    def modify_db(self, cur: Cursor) -> None:
        self.logger.debug("Running modify sql script")

        change_file = self.sql_files / "change.sql"

        with open(str(change_file), "r", encoding="utf-8") as f:
            cur.executescript(f.read())
