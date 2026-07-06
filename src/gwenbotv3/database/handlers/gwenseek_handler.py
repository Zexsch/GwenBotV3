from sqlite3 import Cursor
from typing import Any

from gwenbotv3 import SingletonLogger
from gwenbotv3.database import connect
from gwenbotv3.database import UserContext
from gwenbotv3.database.get_context import context
from gwenbotv3.database.handlers.user_handler import UserHandler


class GwenseekHandler:
    def __init__(self):
        self.logger = SingletonLogger().get_logger()
        self.user_handler = UserHandler()

    @connect
    def add_context(
        self,
        cur: Cursor,
        ctx: UserContext,
        message: str,
        reasoning_content: str,
    ) -> None:

        if not ctx.user:
            self.user_handler.insert_user(ctx.ctx)
            ctx = context(ctx.ctx)

        if not ctx.user:
            return

        cur.execute(
            "INSERT INTO Gwenseek(user, server, user_message, reasoning_content) "
            "VALUES(?,?,?,?)",
            (ctx.user.id, ctx.server.id, message, reasoning_content),
        )

    @connect
    def clear_context(self, cur: Cursor, ctx: UserContext) -> None:
        if not ctx.user:
            self.user_handler.insert_user(ctx.ctx)
            ctx = context(ctx.ctx)

        if not ctx.user:
            return

        cur.execute(
            "DELETE FROM Gwenseek WHERE user=? AND server=?",
            (ctx.user.id, ctx.server.id),
        )

    @connect
    def clear_all_context(self, cur: Cursor, ctx: UserContext) -> None:
        if not ctx.user:
            self.user_handler.insert_user(ctx.ctx)
            ctx = context(ctx.ctx)

        if not ctx.user:
            return

        cur.execute("DELETE FROM Gwenseek WHERE user=?", (ctx.user.id,))

    @connect
    def delete_oldest_context(self, cur: Cursor, ctx: UserContext) -> None:
        if not ctx.user:
            self.user_handler.insert_user(ctx.ctx)
            ctx = context(ctx.ctx)

        if not ctx.user:
            return

        cur.execute(
            "DELETE FROM Gwenseek WHERE g_id = (SELECT MIN(g_id) FROM Gwenseek WHERE user=? AND server=?)",
            (ctx.user.id, ctx.server.id),
        )

    @connect
    def get_count(self, cur: Cursor, ctx: UserContext) -> int:
        if not ctx.user:
            self.user_handler.insert_user(ctx.ctx)
            ctx = context(ctx.ctx)

        if not ctx.user:
            return 0

        res = cur.execute(
            "SELECT COUNT(*) FROM Gwenseek WHERE user=? AND server=?",
            (ctx.user.id, ctx.server.id),
        ).fetchone()

        if not res:
            return 0

        return res[0]

    @connect
    def fetch_context(self, cur: Cursor, ctx: UserContext) -> list[Any]:
        if not ctx.user:
            self.user_handler.insert_user(ctx.ctx)
            ctx = context(ctx.ctx)

        if not ctx.user:
            return []

        res = cur.execute(
            "SELECT * FROM Gwenseek WHERE user=? AND server=?",
            (ctx.user.id, ctx.server.id),
        ).fetchall()

        return res
