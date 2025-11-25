from sqlite3 import Cursor

from discord.ext.commands import Context

from Database.database_connector import connect
from Database.Handlers.server_handler import ServerHandler
from Database.exceptions import ServerNotFoundException
from logger import SingletonLogger

class QuoteHandler():
    def __init__(self):
        self.logger = SingletonLogger().get_logger()
        self.server_handler = ServerHandler()
        raise NotImplementedError

    @connect
    def fetch_quote(self, cur: Cursor, ctx: Context) -> bool:
        """Return True if server disabled quote, else return False
        """

        server = self.server_handler._fetch_server(ctx)

        if not server:
            raise ServerNotFoundException(self.fetch_quote)
        
        res = cur.execute("SELECT * FROM Quote WHERE server=(?)", (server.id,))

        return True if res else False
    
    @connect
    def add_to_quote(self, cur: Cursor, ctx: Context) -> None:
        server = self.server_handler._fetch_server(ctx)

        if not server:
            raise ServerNotFoundException(self.add_to_quote)
        
        cur.execute("INSERT INTO Quote(server) VALUES(?)", (server.id, ))

    @connect
    def remove_from_quote(self, cur: Cursor, ctx: Context) -> None:
        server = self.server_handler._fetch_server(ctx)

        if not server:
            raise ServerNotFoundException(self.remove_from_quote)
        
        cur.execute("DELETE FROM Quote WHERE server=(?)", (server.id,))
        
