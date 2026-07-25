"""Anything to do with the database itself, not specific tables."""

import logging
from pathlib import Path
from sqlite3 import Cursor

from gwenbotv3.database import connect


class DatabaseHandler:
    """Interacts with the database. Not tied to any tables."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.sql_files = Path(__file__).resolve().parent / "sql_files"

    @connect
    def initialise(self, cur: Cursor) -> None:
        """Initialises the database.

        This should run every time the bot starts.
        """
        self.logger.info("Attempting to create Database tables.")

        init_file = self.sql_files / "tables.sql"
        trigger_file = self.sql_files / "triggers.sql"
        pseudonymise_file = self.sql_files / "pseudonymise.sql"

        with open(str(init_file), encoding="utf-8") as f:
            cur.executescript(f.read())

        with open(str(trigger_file), encoding="utf-8") as f:
            cur.executescript(f.read())

        with open(str(pseudonymise_file), encoding="utf-8") as f:
            cur.executescript(f.read())

    @connect
    def modify_db(self, cur: Cursor) -> None:
        """Runs the modify sql script.

        This script is found in ./sql_files. It can be used to alter
            the database in any way.
        """
        self.logger.warning("Running modify sql script")

        change_file = self.sql_files / "change.sql"

        with open(str(change_file), encoding="utf-8") as f:
            cur.executescript(f.read())
