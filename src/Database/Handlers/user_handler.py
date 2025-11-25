from datetime import datetime
from sqlite3 import Cursor

from discord.ext.commands import Context

from Database.database_connector import connect
from Database.models import User
from logger import SingletonLogger

class UserHandler():
    def __init__(self):
        self.logger = SingletonLogger().get_logger()
        raise NotImplementedError
    
    def _create_user(self, ctx: Context) -> User:
        return User(ctx.author.id, ctx.author.name, ctx.author.created_at)
    
    @connect
    def _insert_user(self, cur: Cursor, user: User) -> None:
        cur.execute("INSERT INTO Users(user_id, user_name, created_at) VALUES(?,?,?)", 
                    (user.id, user.name, datetime.strftime(user.created_at, "%Y/%M/%D")))

    @connect
    def _fetch_user(self, cur: Cursor, ctx: Context) -> User:
        user = self._create_user(ctx)

        res = cur.execute("SELECT * FROM Users WHERE user_id=", (user.id,)).fetchone()

        if not res:
            self._insert_user(user)
            return user
        
        if res[2] != user.name:
            cur.execute("UPDATE Users SET user_name=(?)", (ctx.author.name,))

        return user