from sqlite3 import Cursor

from discord.ext.commands import Context

from Database.database_connector import connect
from logger import SingletonLogger
from Database.models import Server
from Database.exceptions import NotInAGuildException

class ServerHandler():
    def __init__(self):
        self.logger = SingletonLogger().get_logger()
        raise NotImplementedError
    
    def _create_server(self, ctx: Context) -> Server:
        if not ctx.guild:
            raise NotInAGuildException(self._create_server)
        
        return Server(ctx.guild.id, ctx.guild.owner_id, ctx.guild.member_count, False)
    
    @connect
    def _insert_server(self, cur: Cursor, server: Server) -> None:
        cur.execute("INSERT INTO Servers(server_id, owner_id, member_count, quote) VALUES(?,?,?,?)", 
                    (server.id, server.owner_id, server.member_count, server.quote))
        
    @connect
    def _fetch_server(self, cur: Cursor, ctx: Context) -> Server:
        
        server = self._create_server(ctx)

        res = cur.execute("SELECT * FROM Servers WHERE server_id=(?)", (server.id,)).fetchone()

        if not res:
            self._insert_server(server)
            return server

        if res[4]:
            server.quote = True

        if res[2] != server.owner_id:
            cur.execute("UPDATE Servers SET owner_id=(?) WHERE server_id=(?)", (server.owner_id,))

        if res[3] != server.member_count:
            cur.execute("UPDATE Servers SET member_count=(?) WHERE server_id=(?)", (server.member_count,))

        return server

    
    