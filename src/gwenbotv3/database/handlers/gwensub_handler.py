"""Interacts with the Subs and Blacklist database tables."""

import logging
from sqlite3 import Cursor

from gwenbotv3.database import UserContext, connect
from gwenbotv3.database.get_context import context
from gwenbotv3.database.handlers.user_handler import UserHandler


class GwenSubHandler:
    """Anything to do with the Subs and Blacklist database tables."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.user_handler = UserHandler()

    @connect
    def fetch_sub(self, cur: Cursor, ctx: UserContext) -> bool:
        """Checks if a user is subscribed in a specific server.

        Args:
            ctx (UserContext): UserContext object.

        Returns:
            bool: True if the user is subscribed, else False.
        """
        if not ctx.user:
            return False

        res = cur.execute(
            "SELECT * FROM Subs WHERE user=? AND server=?",
            (ctx.user.id, ctx.server.id),
        ).fetchone()

        return bool(res)

    @connect
    def add_sub(self, cur: Cursor, ctx: UserContext) -> None:
        """Subscribes a user to gwenbot in a specific server.

        Args:
            ctx (UserContext): UserContext object
        """
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
        """Removes a user from gwenbot subscription in a specific server.

        Args:
            ctx (UserContext): UserContext object.

        Returns:
            bool: False if the user wasn't subscribed or if
                the UserContext object has no user property, else True.
        """
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
    def remove_all_sub(self, cur: Cursor, ctx: UserContext) -> bool:
        """Removes a user from gwenbot subscriptions in all servers.

        Args:
            ctx (UserContext): UserContext object.

        Returns:
            bool: False if the user wasn't subscribed or if
                the UserContext object has no user property, else True.
        """
        if not ctx.user:
            return False

        cur.execute(
            "DELETE FROM Subs WHERE user=?",
            (ctx.user.id,),
        )

        if cur.rowcount < 1:
            return False

        self.logger.info(
            "Removed all subs for user=%s",
            ctx.user.id,
        )
        return True

    @connect
    def fetch_blacklist(self, cur: Cursor, ctx: UserContext) -> bool:
        """Checks if a user is blacklisted in a server.

        Args:
            ctx (UserContext): UserContext object.

        Returns:
            bool: True if blacklisted, else False.
        """
        if not ctx.user:
            return False

        res = cur.execute(
            "SELECT * FROM Blacklist WHERE user=? AND server=?",
            (ctx.user.id, ctx.server.id),
        ).fetchone()

        return bool(res)

    @connect
    def add_blacklist(
        self, cur: Cursor, ctx: UserContext, by_owner: bool = False
    ) -> None:
        """Adds a user to the blacklist in a server.

        Args:
            ctx (UserContext): UserContext object.
            by_owner (bool, optional): If the command was invoked by the bot owner.
                Defaults to False.
        """
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
    def remove_blacklist(
        self, cur: Cursor, ctx: UserContext, by_owner: bool = False
    ) -> bool:
        """Removes a user from the blacklist in a server.

        Args:
            ctx (UserContext): UserContext object.
            by_owner (bool, optional): If the command was invoked by the bot owner.
                Defaults to False.

        Returns:
            bool: False if the UserContext object has no user property
                or if the user was not blacklisted. True if the user
                was successfully removed.
        """
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
        """Checks if a user is blacklisted in a server via their ID.

        This is useful if no UserContext object can be made.

        Args:
            user_id (int): ID of the user.
            server_id (int): ID of the server.

        Returns:
            bool: True if the user is subscribed, else False.
        """
        res = cur.execute(
            "SELECT * FROM Subs WHERE user=? AND server=?", (user_id, server_id)
        ).fetchone()

        return bool(res)

    @connect
    def remove_sub_by_ids(self, cur: Cursor, user_id: int, server_id: int) -> bool:
        """Remove a user from the blacklist in a server via their ID.

        This is useful if no UserContext object can be made.

        Args:
            user_id (int): ID of the user.
            server_id (int): ID of the server.

        Returns:
            bool: True if the user was successfully removed, else False.
        """
        cur.execute("DELETE FROM Subs WHERE user=? AND server=?", (user_id, server_id))

        if cur.rowcount < 1:
            return False

        self.logger.info(
            "Removed sub from user=%s, server=%s by id", user_id, server_id
        )

        return True

    @connect
    def fetch_blacklist_by_ids(self, cur: Cursor, user_id: int, server_id: int) -> bool:
        """Check if a user is blacklisted in a server via their ID.

        This is useful if no UserContext object can be made.

        Args:
            user_id (int): ID of the user.
            server_id (int): ID of the server.

        Returns:
            bool: True if the user is blacklisted, else False.
        """
        res = cur.execute(
            "SELECT * FROM Blacklist WHERE user=? AND server=?", (user_id, server_id)
        ).fetchone()

        self.logger.debug(
            "Fetched blacklist by id: user=%s, server=%s", user_id, server_id
        )

        return bool(res)

    @connect
    def blacklist_by_ids(
        self, cur: Cursor, user_id: int, server_id: int, by_owner: bool = False
    ) -> bool:
        """Blacklist a user in a server via on their ID.

        This is useful if no UserContext object can be made.

        Args:
            user_id (int): ID of the user.
            server_id (int): ID of the server.
            by_owner (bool, optional): If the command was invoked by the bot owner.
                Defaults to False.

        Returns:
            bool: True if the user was successfully blacklisted, else False.
        """
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
        """Remove a user from the blacklist in a server via their ID.

        This is useful if no UserContext object can be made.

        Args:
            user_id (int): ID of the user.
            server_id (int): ID of the server.
            by_owner (bool, optional): If the command was invoked by the bot owner.
                Defaults to False.

        Returns:
            bool: True if the user was successfully removed from the blacklist,
                else False.
        """
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
