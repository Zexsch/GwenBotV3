from sqlite3 import Cursor

from gwenbotv3 import SingletonLogger
from gwenbotv3.database import connect
from gwenbotv3.database import UserContext


class GwenSubHandler:
    def __init__(self):
        self.logger = SingletonLogger().get_logger()

    @connect
    def fetch_sub(self, cur: Cursor, context: UserContext) -> bool:
        res = cur.execute(
            "SELECT * FROM Subs WHERE user=? AND server=?",
            (context.user.id, context.server.id),
        ).fetchone()

        return True if res else False

    @connect
    def add_sub(self, cur: Cursor, context: UserContext) -> None:
        cur.execute(
            "INSERT INTO Subs(user, server) VALUES(?,?) "
            "ON CONFLICT(user, server) DO NOTHING",
            (context.user.id, context.server.id),
        )

    @connect
    def remove_sub(self, cur: Cursor, context: UserContext) -> bool:
        cur.execute(
            "DELETE FROM Subs WHERE user=? AND server=?",
            (context.user.id, context.server.id),
        )

        if cur.rowcount < 1:
            return False

        return True

    @connect
    def fetch_blacklist(self, cur: Cursor, context: UserContext) -> bool:
        res = cur.execute(
            "SELECT * FROM Blacklist WHERE user=? AND server=?",
            (context.user.id, context.server.id),
        ).fetchone()

        return True if res else False

    @connect
    def add_blacklist(self, cur: Cursor, context: UserContext, by_owner: bool = False):
        cur.execute(
            "INSERT INTO Blacklist(user, server, by_owner) VALUES (?,?,?) "
            "ON CONFLICT(user, server, by_owner) DO NOTHING",
            (context.user.id, context.server.id, by_owner),
        )

    @connect
    def remove_blacklist(
        self, cur: Cursor, context: UserContext, by_owner: bool = False
    ):
        cur.execute(
            "DELETE FROM Blacklist WHERE user=? AND server=? AND by_owner=?",
            (context.user.id, context.server.id, by_owner),
        )

        if cur.rowcount < 1:
            return False

        return True

    @connect
    def fetch_sub_by_ids(self, cur: Cursor, user_id: int, server_id: int) -> bool:
        res = cur.execute(
            "SELECT * FROM Subs WHERE user=? AND server=?", (user_id, server_id)
        ).fetchone()

        return True if res else False

    @connect
    def remove_sub_by_ids(self, cur: Cursor, user_id: int, server_id: int) -> bool:
        cur.execute("DELETE FROM Subs WHERE user=? AND server=?", (user_id, server_id))

        if cur.rowcount < 1:
            return False

        return True

    @connect
    def fetch_blacklist_by_ids(self, cur: Cursor, user_id: int, server_id: int) -> bool:
        res = cur.execute(
            "SELECT * FROM Blacklist WHERE user=? AND server=?", (user_id, server_id)
        ).fetchone()

        return True if res else False

    @connect
    def blacklist_by_ids(
        self, cur: Cursor, user_id: int, server_id: int, by_owner: bool = False
    ) -> bool:
        cur.execute(
            "INSERT INTO Blacklist(user, server, by_owner) VALUES (?,?,?) "
            "ON CONFLICT(user, server, by_owner) DO NOTHING",
            (user_id, server_id, by_owner),
        )

        if cur.rowcount < 1:
            return False

        return True

    @connect
    def remove_blacklist_by_ids(
        self, cur: Cursor, user_id: int, server_id: int
    ) -> bool:
        cur.execute(
            "DELETE FROM Blacklist WHERE user=? AND server=?", (user_id, server_id)
        )

        if cur.rowcount < 1:
            return False

        return True
