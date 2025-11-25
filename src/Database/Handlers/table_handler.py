import sqlite3
from sqlite3 import Cursor

from logger import SingletonLogger
from Database.database_connector import connect


class TableHandler():
    def __init__(self) -> None:
        self.logger = SingletonLogger().get_logger()
        raise NotImplementedError

    @connect
    def create_db(self, cur: Cursor) -> None:
        """Try to create the Database tables each time the bot runs."""
        self.logger.debug("Attempting to create Database tables.")
        try:
            cur.execute('''CREATE TABLE Users(
                        u_id INTEGER PRIMARY KEY, 
                        user_id INTEGER, 
                        user_name TEXT, 
                        created_at TEXT)''')
            
            cur.execute('''CREATE TABLE Servers(
                        s_id INTEGER PRIMARY KEY,
                        server_id INTEGER, 
                        owner_id INTEGER, 
                        member_count INTEGER, 
                        quote BOOLEAN)''')
            
            cur.execute('''CREATE TABLE Gwenseek(
                        g_id INTEGER PRIMARY KEY, 
                        user INTEGER, 
                        FOREIGN KEY (user) REFERENCES Users(u_id), 
                        user_message TEXT, 
                        reasoning_content TEXT)''')
            
            cur.execute('''CREATE TABLE QuestionCount(
                        q_id INTEGER PRIMARY KEY,
                        amount INTEGER, 
                        latest_user INTEGER,
                        FOREIGN KEY (latest_user) REFERENCES Users(u_id),
                        server INTEGER,
                        FOREIGN KEY (server) REFERENCES Servers(s_id))''')
            
            cur.execute('''CREATE TABLE QuestionUser(
                        q_user_id INTEGER PRIMARY KEY, 
                        user INTEGER,
                        FOREIGN KEY (user) REFERENCES Users(u_id)),
                        questions_server INTEGER,
                        FOREIGN KEY (questions_server) REFERENCES QuestionCount(q_id),
                        amount INTEGER)''')
            
            cur.execute('''CREATE TABLE Subs(
                        sub_id INTEGER PRIMARY KEY, 
                        user INTEGER,
                        FOREIGN KEY (user) REFERENCES Users(u_id)),
                        server INTEGER,
                        FOREIGN KEY (server) REFERENCES Servers(s_id))''')
            
            cur.execute('''CREATE TABLE Blacklist(
                        blacklist_id INTEGER PRIMARY KEY, 
                        user INTEGER,
                        FOREIGN KEY (user) REFERENCES Users(u_id)),
                        server INTEGER,
                        FOREIGN KEY (server) REFERENCES Servers(s_id))''')
            
            self.logger.info("Created Database Tables.")
        except sqlite3.OperationalError:
            self.logger.debug("Database Tables were already created.")
            pass