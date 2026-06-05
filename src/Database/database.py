import sqlite3
from typing import Type, TypeVar
from pathlib import Path

from logger import SingletonLogger

T = TypeVar("T", bound="DatabaseHandler")


class DatabaseHandler:
    """Use to interact with the database"""

    def __new__(cls: Type[T], *args, **kwargs) -> T:
        if not hasattr(cls, "instance"):
            cls.instance = super(DatabaseHandler, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if (
            hasattr(self, "_initialised") and self._initialised #pylint: disable=access-member-before-definition
        ):
            return

        self.database = Path(__file__).resolve().parent / "GwenUsers.db"
        self.logger = SingletonLogger().get_logger()
        self._initialised = True

    def create_db(self) -> None:
        """Try to create the Database tables each time the bot runs."""
        self.logger.debug("Attempting to create Database tables.")
        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            try:
                cur.execute(
                    "CREATE TABLE Gwenseek(id INTEGER PRIMARY KEY, user_id INTEGER, user_message TEXT, reasoning_content TEXT)"
                )
                cur.execute(
                    "CREATE TABLE Question(id INTEGER PRIMARY KEY, amount INTEGER, latest_user INTEGER)"
                )
                cur.execute(
                    "CREATE TABLE Subs(id INTEGER PRIMARY KEY, user_id INTEGER, server_id INTEGER)"
                )
                cur.execute(
                    "CREATE TABLE Blacklist(id INTEGER PRIMARY KEY, user_id INTEGER, server_id INTEGER)"
                )
                cur.execute(
                    "CREATE TABLE Quote(id INTEGER PRIMARY KEY, server_id INTEGER)"
                )
                self.logger.debug("Created Database Tables.")
            except sqlite3.OperationalError:
                self.logger.debug("Database Tables were already created.")
                pass

    def fetch_gwen_sub(self, user_id: int, server_id: int) -> bool:
        """Return True if user is subbed, else return False"""

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            res = cur.execute(
                "SELECT * FROM Subs WHERE user_id=? AND server_id=?",
                (user_id, server_id),
            ).fetchall()
            self.logger.debug(f"Fetched {res} from function fetch_gwen_sub")

            return True if res else False

    def fetch_blacklist(self, user_id: int, server_id: int) -> bool:
        """Return True if user is blacklisted, else return False"""

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            res = cur.execute(
                "SELECT * FROM Blacklist WHERE user_id=? AND server_id=?",
                (user_id, server_id),
            ).fetchall()
            self.logger.debug(f"Fetched {res} from function fetch_blacklist")

            return True if res else False

    def fetch_quote(self, server_id: int) -> bool:
        """Return True if server uses quote, else return False"""

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            res = cur.execute(
                "SELECT * FROM Quote WHERE server_id=?", (server_id,)
            ).fetchall()
            self.logger.debug(f"Fetched {res} from function fetch_quote")

            return True if res else False

    def _fetch_entire_blacklist(self):
        """Return everything from Blacklist table."""

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            res = cur.execute("SELECT * FROM Blacklist").fetchall()
            self.logger.debug(f"Fetched {res} from function _fetch_entire_blacklist")

            return res

    def _fetch_all_subs(self):
        """Return everything from Subs table."""

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            res = cur.execute("SELECT * FROM Subs").fetchall()
            self.logger.debug(f"Fetched {res} from function _fetch_all_subs")

            return res

    def add_to_gwen_sub(self, user_id: int, server_id: int) -> None:
        """Add user to the subscribed user database"""

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO Subs(user_id, server_id) VALUES(?,?)", (user_id, server_id)
            )

            self.logger.debug(
                f"Executed function add_to_gwen_sub with arguments {user_id=}, {server_id=}"
            )

    def add_to_blacklist(self, user_id: int, server_id: int) -> None:
        """Add user to the blacklist."""

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO Blacklist(user_id, server_id) VALUES(?,?)",
                (user_id, server_id),
            )

            self.logger.debug(
                f"Executed function add_to_blacklist with arguments {user_id=}, {server_id=}"
            )

    def add_to_quote(self, server_id: int) -> None:
        """Add server to quote"""

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO Quote(server_id) VALUES(?)", (server_id,))

            self.logger.debug(
                f"Executed function add_to_quote with arguments {server_id=}"
            )

    def remove_from_gwen_sub(self, user_id: int, server_id: int) -> bool:
        """Remove user from GwenBot subscription. Return true if successfull else false."""

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()

            res = cur.execute(
                "SELECT * FROM Subs WHERE user_id=? AND server_id=?",
                (user_id, server_id),
            ).fetchall()

            if not res:
                return False

            cur.execute(
                "DELETE FROM Subs WHERE user_id=? AND server_id=?", (user_id, server_id)
            )
            self.logger.debug(
                f"Executed function remove_from_gwen_sub with arguments {user_id=}, {server_id=}"
            )
            return True

    def remove_from_blacklist(self, user_id: int, server_id: int) -> None:
        """Remove user from the blacklist."""

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()

            cur.execute(
                "DELETE FROM Blacklist WHERE user_id=? AND server_id=?",
                (user_id, server_id),
            )
            self.logger.debug(
                f"Executed function remove_from_blacklist with arguments {user_id=}, {server_id=}"
            )

    def remove_from_quote(self, server_id: int) -> None:
        """Remove server from quote"""

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            cur.execute("DELETE FROM Quote WHERE server_id=?", (server_id,))

            self.logger.debug(
                f"Executed function remove_from_quote with arguments {server_id=}"
            )

    def set_amount(self, amount: int) -> None:
        """Set the amount of question marks."""

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            cur.execute("UPDATE Question SET amount=(?)", (amount,))

            self.logger.debug(f"Executed function set_amount with arguments {amount=}")

    def fetch_amount(self) -> int:
        """Fetch the amount of question marks"""

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            res = cur.execute("SELECT amount FROM Question").fetchone()[0]

            self.logger.debug(f"Executed function fetch_amount with result {res}")

            return res

    def set_latest_user(self, user_id) -> None:

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            cur.execute("UPDATE Question SET latest_user=(?)", (user_id,))

            self.logger.debug(
                f"Executed function set_latest_user with arguments {user_id}"
            )

    def fetch_latest_user(self) -> int:

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            res = cur.execute("SELECT latest_user FROM Question").fetchone()[0]

            self.logger.debug(f"Executed function fetch_latest_user with result {res}")
            return res

    # Deepseek integration

    def add_context_ds(
        self, user_id: int, user_message: str, reasoning_content: str
    ) -> None:

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO Gwenseek(user_id, user_message, reasoning_content) VALUES(?,?,?)",
                (user_id, user_message, reasoning_content),
            )

            self.logger.debug(
                f"Executed function add_context_ds with arguments {user_id=}, {user_message=}, {reasoning_content=}"
            )

    def clear_context_ds(self, user_id: int) -> None:

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            cur.execute("DELETE FROM Gwenseek WHERE user_id=?", (user_id,))

            self.logger.debug(
                f"Executed function clear_context_ds with arguments {user_id=}"
            )

    def delete_oldest_context_ds(self, user_id: int) -> None:

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            cur.execute(
                "DELETE FROM Gwenseek WHERE id = (SELECT MIN(id) FROM Gwenseek WHERE user_id = ?)",
                (user_id,),
            )

            self.logger.debug(
                f"Executed function delete_oldest_context_ds with arguments {user_id=}"
            )

    def fetch_user_count_ds(self, user_id: int):

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            res = cur.execute(
                "SELECT COUNT(*) FROM Gwenseek WHERE user_id=?", (user_id,)
            ).fetchone()

            self.logger.debug(
                f"Executed function fetch_user_count_ds with arguments {user_id=} and {res=}"
            )
            return res

    def fetch_context_ds(self, user_id: int):

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            res = cur.execute(
                "SELECT * FROM Gwenseek WHERE user_id=? ORDER BY id", (user_id,)
            ).fetchall()

            self.logger.debug(
                f"Executed function fetch_context_ds with arguments {user_id=} and {res=}"
            )
            return res
