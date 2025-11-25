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