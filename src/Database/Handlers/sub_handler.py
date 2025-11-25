from sqlite3 import Cursor

from discord.ext.commands import Context

from logger import SingletonLogger
from Database.database_connector import connect
from Database.Handlers.server_handler import ServerHandler
from Database.Handlers.user_handler import UserHandler
from Database.exceptions import (ServerNotFoundException, 
                                 UserNotSubscribedException, 
                                 UserNotBlacklistedException)


class SubHandler():
    def __init__(self):
        self.logger = SingletonLogger().get_logger()
        self.server_handler = ServerHandler()
        self.user_handler = UserHandler()
        raise NotImplementedError
    
    @connect
    def fetch_gwen_sub(self, cur: Cursor, ctx: Context) -> bool:
        """Return True if user is subbed, else return False
        """

        user = self.user_handler._fetch_user(ctx)
        server = self.server_handler._fetch_server(ctx)

        if not server:
            raise ServerNotFoundException(self.fetch_gwen_sub)
        
        res = cur.execute("SELECT * FROM Subs WHERE user=(?) AND server=(?)", (user.id, server.id))

        return True if res else False
    
    @connect
    def fetch_blacklist(self, cur: Cursor, ctx: Context) -> bool:
        """Return True if user is blacklisted, else return False
        """

        user = self.user_handler._fetch_user(ctx)
        server = self.server_handler._fetch_server(ctx)

        if not server:
            raise ServerNotFoundException(self.fetch_blacklist)
        
        res = cur.execute("SELECT * FROM Blacklist WHERE user=(?) AND server=(?)", (user.id, server.id))

        return True if res else False
    
    @connect
    def add_to_gwen_sub(self, cur: Cursor, ctx: Context) -> None:
        user = self.user_handler._fetch_user(ctx)
        server = self.server_handler._fetch_server(ctx)

        if not server:
            raise ServerNotFoundException(self.add_to_gwen_sub)
        
        cur.execute("INSERT INTO Subs(user, server) VALUES(?,?)", (user.id, server.id))

    @connect
    def add_to_blacklist(self, cur: Cursor, ctx: Context) -> None:
        user = self.user_handler._fetch_user(ctx)
        server = self.server_handler._fetch_server(ctx)

        if not server:
            raise ServerNotFoundException(self.add_to_blacklist)
        
        cur.execute("INSERT INTO Blacklist(user, server) VALUES(?,?)", (user.id, server.id))
  
    @connect
    def remove_from_gwen_sub(self, cur: Cursor, ctx: Context) -> None:
        user = self.user_handler._fetch_user(ctx)
        server = self.server_handler._fetch_server(ctx)

        if not self.fetch_gwen_sub(ctx):
            raise UserNotSubscribedException(user)
        
        cur.execute('DELETE FROM Subs WHERE user=? AND server=?', (user.id, server.id))

    @connect
    def remove_from_blacklist(self, cur: Cursor, ctx: Context) -> None:
        user = self.user_handler._fetch_user(ctx)
        server = self.server_handler._fetch_server(ctx)

        if not self.fetch_gwen_sub(ctx):
            raise UserNotBlacklistedException(user)
        
        cur.execute("DELETE FROM Blacklist WHERE user=? AND server=?", (user.id, server.id))
    