from sqlite3 import Cursor
from typing import Optional

from discord import Message
from discord.ext.commands import Context

from gwenbotv3 import SingletonLogger
from gwenbotv3.database import connect
from gwenbotv3.database import Server
from gwenbotv3.config import PREFIX
from gwenbotv3.database._models.models import UserContext
from gwenbotv3.database._models.exceptions import (
    NotInAGuildException,
    UserOrCtxNotGiven,
    EmptyDataclass,
)


class ServerHandler:
    def __init__(self):
        self.logger = SingletonLogger().get_logger()

    def _create_server(self, ctx: Context | Message) -> Server:
        if not ctx.guild:
            raise NotInAGuildException(self._create_server)

        return Server(ctx.guild.id, ctx.guild.owner_id, ctx.guild.member_count, False)

    @connect
    def insert_server(
        self,
        cur: Cursor,
        ctx: Optional[Context | Message] = None,
        server: Optional[Server] = None,
    ) -> None:
        if server is None and ctx is None:
            raise UserOrCtxNotGiven(self.insert_server)

        if ctx:
            server = self._create_server(ctx)

        if not server:
            raise EmptyDataclass(server, self.insert_server)

        cur.execute(
            "INSERT INTO Servers(server_id, owner_id, member_count, quote, prefix) VALUES(?,?,?,?,?)",
            (server.id, server.owner_id, server.member_count, server.quote, PREFIX),
        )

    @connect
    def fetch_server(self, cur: Cursor, ctx: Context | Message) -> Server:

        server = self._create_server(ctx)

        res = cur.execute(
            "SELECT * FROM Servers WHERE server_id=?", (server.id,)
        ).fetchone()

        if not res:
            self.insert_server(ctx)
            return server

        if res[3]:
            server.quote = True

        if res[1] != server.owner_id:
            cur.execute(
                "UPDATE Servers SET owner_id=? WHERE server_id=?",
                (server.owner_id, server.id),
            )

        if res[2] != server.member_count:
            cur.execute(
                "UPDATE Servers SET member_count=? WHERE server_id=?",
                (server.member_count, server.id),
            )

        return server

    @connect
    def add_quote(self, cur: Cursor, server: Server) -> bool:

        if server.quote:
            return False

        cur.execute("UPDATE Servers SET quote=? WHERE server_id=?", (True, server.id))

        return True

    @connect
    def remove_quote(self, cur: Cursor, server: Server) -> bool:

        if not server.quote:
            return False

        cur.execute("UPDATE Servers SET quote=? WHERE server_id=?", (False, server.id))

        return True

    @connect
    def fetch_server_by_id(self, cur: Cursor, server_id: int) -> Optional[Server]:
        res = cur.execute(
            "SELECT * FROM Servers WHERE server_id=?", (server_id,)
        ).fetchone()

        if not res:
            return

        server = Server(id=res[0], owner_id=res[1], member_count=res[2], quote=res[3])

        return server

    @connect
    def change_prefix(self, cur: Cursor, ctx: UserContext, new_prefix: str) -> None:
        cur.execute(
            "UPDATE Servers SET prefix=? WHERE server_id=?", (new_prefix, ctx.server.id)
        )

    @connect
    def fetch_prefix(self, cur: Cursor, ctx: UserContext) -> str:
        res = cur.execute(
            "SELECT prefix FROM Servers WHERE server_id=?", (ctx.server.id,)
        ).fetchone()

        if not res:
            return PREFIX

        return res[0]
