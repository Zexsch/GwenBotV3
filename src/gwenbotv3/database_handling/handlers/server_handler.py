"""Interacts with the Server database table."""

import logging
from sqlite3 import Cursor

from discord import Message
from discord.ext.commands import Bot, Context

from gwenbotv3.config import PREFIX
from gwenbotv3.database_handling import Server, connect
from gwenbotv3.database_handling._models.exceptions import (
    EmptyDataclass,
    NotInAGuildException,
    UserOrCtxNotGiven,
)
from gwenbotv3.database_handling._models.models import UserContext


class ServerHandler:
    """Anything to do with the Server database table."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def _create_server(self, ctx: Context[Bot] | Message) -> Server:
        """Creates a server object.

        Args:
            ctx (Context | Message): discord.commands.Context
                or discord.Message object

        Raises:
            NotInAGuildException: If the given object has no
                guild property, usually if the command is used
                in a DM

        Returns:
            Server: Server object, see _models.models
        """
        if not ctx.guild:
            raise NotInAGuildException(self._create_server)

        return Server(ctx.guild.id, ctx.guild.owner_id, ctx.guild.member_count, False)

    @connect
    def insert_server(
        self,
        cur: Cursor,
        ctx: Context[Bot] | Message | None = None,
        server: Server | None = None,
    ) -> None:
        """Inserts a server into the database.

        Inserts into Servers table.
        By default, quote is false and prefix is +.

        Args:
            ctx (Context | Message | None, optional): discord.commands.Context
                or discord.Message object. One of the two OR a
                Server object must be given.
                Defaults to None.
            server (Server | None, optional): Server object.
                Either this or a discord.commands.Context
                or a discord.Message object must be given. Defaults to None.

        Raises:
            UserOrCtxNotGiven: If no Server object or Ctx or Message object was given.
            EmptyDataclass: If the Server object given has no values.
        """
        if server is None and ctx is None:
            raise UserOrCtxNotGiven(self.insert_server)

        if ctx:
            server = self._create_server(ctx)

        if not server:
            raise EmptyDataclass(server, self.insert_server)

        cur.execute(
            "INSERT INTO Servers(server_id, owner_id, member_count, quote, prefix) "
            "VALUES(?,?,?,?,?)",
            (server.id, server.owner_id, server.member_count, server.quote, PREFIX),
        )

        self.logger.info(
            "Inserted new server: "
            "server_id=%s, owner_id=%s, member_count=%s, quote=%s, prefix=%s",
            server.id,
            server.owner_id,
            server.member_count,
            server.quote,
            PREFIX,
        )

    @connect
    def fetch_server(self, cur: Cursor, ctx: Context[Bot] | Message) -> Server:
        """Fetches a server from the database.

        Args:
            ctx (Context | Message): discord.commands.Context
                or discord.Message object

        Returns:
            Server: Server object. See _models.models
        """
        server = self._create_server(ctx)

        res = cur.execute(
            "SELECT * FROM Servers WHERE server_id=?", (server.id,)
        ).fetchone()

        if not res:
            self.insert_server(ctx)
            return server

        if len(res) < 3:
            self.logger.critical(
                "Fetched info from server=%s, yet not all information "
                "was fetched properly. Column count: %s",
                server.id,
                len(res),
            )
            self.insert_server(ctx)
            return server

        if res[3]:
            server.quote = True

        if res[1] != server.owner_id:
            cur.execute(
                "UPDATE Servers SET owner_id=? WHERE server_id=?",
                (server.owner_id, server.id),
            )

            self.logger.info(
                "Updated server owner for server=%s, new owner=%s",
                server.id,
                server.owner_id,
            )

        if res[2] != server.member_count:
            cur.execute(
                "UPDATE Servers SET member_count=? WHERE server_id=?",
                (server.member_count, server.id),
            )

        return server

    @connect
    def add_quote(self, cur: Cursor, server: Server) -> bool:
        """Sets quote to true on a server.

        Quote blocks all gwensub commands.

        Args:
            server (Server): Server to block on.

        Returns:
            bool: False if the server already has quote enabled.
                True if quote was enabled.
        """
        if server.quote:
            self.logger.info(
                "Tried to set quote to True on a server which already has "
                "quote enabled. server=%s",
                server.id,
            )
            return False

        cur.execute("UPDATE Servers SET quote=? WHERE server_id=?", (True, server.id))

        self.logger.info("Set quote to true on server=%s", server.id)

        return True

    @connect
    def remove_quote(self, cur: Cursor, server: Server) -> bool:
        """Sets quote to false on a server.

        Quote blocks all gwensub commands.

        Args:
            server (Server): Server to set quote to false on.

        Returns:
            bool: False if the server doesn't have quote set to true.
                True if quote was removed
        """
        if not server.quote:
            self.logger.info(
                "Tried to set quote to False on a server which does not "
                "have quote enabled. server=%s",
                server.id,
            )
            return False

        cur.execute("UPDATE Servers SET quote=? WHERE server_id=?", (False, server.id))

        self.logger.info("Set quote to false on server=%s", server.id)

        return True

    @connect
    def fetch_server_by_id(self, cur: Cursor, server_id: int) -> Server | None:
        """Fetches a server by its ID.

        Args:
            server_id (int): ID of the server.

        Returns:
            Server | None: Server object. See _models.models.
        """
        res = cur.execute(
            "SELECT * FROM Servers WHERE server_id=?", (server_id,)
        ).fetchone()

        if not res:
            self.logger.warning(
                "Tried to fetch server by id without the server existing in the db. "
                "server=%s",
                server_id,
            )
            return None

        return Server(id=res[0], owner_id=res[1], member_count=res[2], quote=res[3])

    @connect
    def change_prefix(self, cur: Cursor, ctx: UserContext, new_prefix: str) -> None:
        """Changes the prefix for a server.

        Args:
            ctx (UserContext): UserContext object.
            new_prefix (str): Prefix to set it to.
        """
        cur.execute(
            "UPDATE Servers SET prefix=? WHERE server_id=?", (new_prefix, ctx.server.id)
        )

        self.logger.info("Set prefix on server=%s to %s", ctx.server.id, new_prefix)

    @connect
    def fetch_prefix(self, cur: Cursor, ctx: UserContext) -> str:
        """Fetches the prefix for a server.

        Args:
            ctx (UserContext): UserContext object.

        Returns:
            str: the prefix.
        """
        res = cur.execute(
            "SELECT prefix FROM Servers WHERE server_id=?", (ctx.server.id,)
        ).fetchone()

        if not res:
            return PREFIX

        if not isinstance(res[0], str):
            self.logger.critical("Fetched non-str prefix")
            raise TypeError

        return res[0]
