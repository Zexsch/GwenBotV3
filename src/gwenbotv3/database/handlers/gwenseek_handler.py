import logging
from sqlite3 import Cursor
from typing import Any

from gwenbotv3.database import connect
from gwenbotv3.database import UserContext
from gwenbotv3.database.get_context import context
from gwenbotv3.database.handlers.user_handler import UserHandler


class GwenseekHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
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

        self.logger.debug(
            "Added gwenseek context for user=%s on server=%s, message=%s",
            ctx.user.id,
            ctx.server.id,
            message,
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

        self.logger.info(
            "Deleted gwenseek context for user=%s from server=%s",
            ctx.user.id,
            ctx.server.id,
        )

    @connect
    def clear_all_context(self, cur: Cursor, ctx: UserContext) -> None:
        if not ctx.user:
            self.user_handler.insert_user(ctx.ctx)
            ctx = context(ctx.ctx)

        if not ctx.user:
            return

        cur.execute("DELETE FROM Gwenseek WHERE user=?", (ctx.user.id,))

        self.logger.info("Deleted all gwenseek context for user=%s", ctx.user.id)

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

        self.logger.debug(
            "Deleted oldest gwenseek context for user=%s on server=%s",
            ctx.user.id,
            ctx.server.id,
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

        self.logger.debug(
            "Fetched gwenseek context amount=%s from user=%s on server=%s",
            res[0],
            ctx.user.id,
            ctx.server.id,
        )

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

        self.logger.debug(
            "Fetched gwenseek context for user=%s and server=%s",
            ctx.user.id,
            ctx.server.id,
        )

        return res
