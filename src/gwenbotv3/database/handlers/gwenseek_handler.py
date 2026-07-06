from sqlite3 import Cursor
from typing import Any

from gwenbotv3 import SingletonLogger
from gwenbotv3.database import connect
from gwenbotv3.database import UserContext


class GwenseekHandler:
    def __init__(self):
        self.logger = SingletonLogger().get_logger()

    @connect
    def add_context(
        self,
        cur: Cursor,
        context: UserContext,
        message: str,
        reasoning_content: str,
    ) -> None:
        cur.execute(
            "INSERT INTO Gwenseek(user, server, user_message, reasoning_content) "
            "VALUES(?,?,?,?)",
            (context.user.id, context.server.id, message, reasoning_content),
        )

    @connect
    def clear_context(self, cur: Cursor, context: UserContext) -> None:
        cur.execute(
            "DELETE FROM Gwenseek WHERE user=? AND server=?",
            (context.user.id, context.server.id),
        )

    @connect
    def clear_all_context(self, cur: Cursor, context: UserContext) -> None:
        cur.execute("DELETE FROM Gwenseek WHERE user=?", (context.user.id,))

    @connect
    def delete_oldest_context(self, cur: Cursor, context: UserContext) -> None:
        cur.execute(
            "DELETE FROM Gwenseek WHERE g_id = (SELECT MIN(g_id) FROM Gwenseek WHERE user=? AND server=?)",
            (context.user.id, context.server.id),
        )

    @connect
    def get_count(self, cur: Cursor, context: UserContext) -> int:
        res = cur.execute(
            "SELECT COUNT(*) FROM Gwenseek WHERE user=? AND server=?",
            (context.user.id, context.server.id),
        ).fetchone()

        if not res:
            return 0

        return res[0]

    @connect
    def fetch_context(self, cur: Cursor, context: UserContext) -> list[Any]:
        res = cur.execute(
            "SELECT * FROM Gwenseek WHERE user=? AND server=?",
            (context.user.id, context.server.id),
        ).fetchall()

        return res
