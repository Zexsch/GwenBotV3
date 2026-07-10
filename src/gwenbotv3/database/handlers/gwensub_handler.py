import logging
from sqlite3 import Cursor

from gwenbotv3.database import connect
from gwenbotv3.database import UserContext
from gwenbotv3.database.get_context import context
from gwenbotv3.database.handlers.user_handler import UserHandler


class GwenSubHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_handler = UserHandler()

    @connect
    def fetch_sub(self, cur: Cursor, ctx: UserContext) -> bool:
        if not ctx.user:
            return False

        res = cur.execute(
            "SELECT * FROM Subs WHERE user=? AND server=?",
            (ctx.user.id, ctx.server.id),
        ).fetchone()

        return True if res else False

    @connect
    def add_sub(self, cur: Cursor, ctx: UserContext) -> None:
        if not ctx.user:
            self.user_handler.insert_user(ctx.ctx)
            ctx = context(ctx.ctx)

        if not ctx.user:
            self.logger.warning(
                "Tried to fetch sub for a UserContext with no user. ctx=%s", ctx
            )
            return

        cur.execute(
            "INSERT INTO Subs(user, server) VALUES(?,?) "
            "ON CONFLICT(user, server) DO NOTHING",
            (ctx.user.id, ctx.server.id),
        )

        self.logger.info(
            "Added user=%s to subs on server=%s", ctx.user.id, ctx.server.id
        )

    @connect
    def remove_sub(self, cur: Cursor, ctx: UserContext) -> bool:
        if not ctx.user:
            return False

        cur.execute(
            "DELETE FROM Subs WHERE user=? AND server=?",
            (ctx.user.id, ctx.server.id),
        )

        if cur.rowcount < 1:
            return False

        self.logger.info(
            "Removed sub for user=%s on server=%s", ctx.user.id, ctx.server.id
        )
        return True

    @connect
    def fetch_blacklist(self, cur: Cursor, ctx: UserContext) -> bool:
        if not ctx.user:
            return False

        res = cur.execute(
            "SELECT * FROM Blacklist WHERE user=? AND server=?",
            (ctx.user.id, ctx.server.id),
        ).fetchone()

        return True if res else False

    @connect
    def add_blacklist(self, cur: Cursor, ctx: UserContext, by_owner: bool = False):
        if not ctx.user:
            self.user_handler.insert_user(ctx.ctx)
            ctx = context(ctx.ctx)

        if not ctx.user:
            return

        cur.execute(
            "INSERT INTO Blacklist(user, server, by_owner) VALUES (?,?,?) "
            "ON CONFLICT(user, server, by_owner) DO NOTHING",
            (ctx.user.id, ctx.server.id, by_owner),
        )

        self.logger.info(
            "Added user=%s to blacklist in server=%s and by_owner=%s",
            ctx.user.id,
            ctx.server.id,
            by_owner,
        )

    @connect
    def remove_blacklist(self, cur: Cursor, ctx: UserContext, by_owner: bool = False):
        if not ctx.user:
            return False

        cur.execute(
            "DELETE FROM Blacklist WHERE user=? AND server=? AND by_owner=?",
            (ctx.user.id, ctx.server.id, by_owner),
        )

        if cur.rowcount < 1:
            return False

        self.logger.info(
            "Removed user=%s from blacklist in server=%s and by_owner=%s",
            ctx.user.id,
            ctx.server.id,
            by_owner,
        )

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

        self.logger.info(
            "Removed sub from user=%s, server=%s by id", user_id, server_id
        )

        return True

    @connect
    def fetch_blacklist_by_ids(self, cur: Cursor, user_id: int, server_id: int) -> bool:
        res = cur.execute(
            "SELECT * FROM Blacklist WHERE user=? AND server=?", (user_id, server_id)
        ).fetchone()

        self.logger.debug(
            "Fetched blacklist by id: user=%s, server=%s", user_id, server_id
        )

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

        self.logger.info(
            "Added user=%s to blacklist by id in server=%s and by_owner=%s",
            user_id,
            server_id,
            by_owner,
        )

        return True

    @connect
    def remove_blacklist_by_ids(
        self, cur: Cursor, user_id: int, server_id: int, by_owner: bool = False
    ) -> bool:
        cur.execute(
            "DELETE FROM Blacklist WHERE user=? AND server=? AND by_owner=?",
            (user_id, server_id, by_owner),
        )

        if cur.rowcount < 1:
            return False

        self.logger.info(
            "Removed user=%s from blacklist by id in server=%s and by_owner=%s",
            user_id,
            server_id,
            by_owner,
        )

        return True
