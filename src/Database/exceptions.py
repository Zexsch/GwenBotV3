from typing import Callable
from Bot.models import Champion
from Database.models import User

class ServerNotFoundException(Exception):
    def __init__(self, func: Callable):
        super().__init__(f"No servers were found in {func.__name__}")

class WinrateNotFoundException(Exception):
    def __init__(self, champ: Champion):
        super().__init__(f"No winrate was found for {champ=}")

class NotInAGuildException(Exception):
    def __init__(self, func: Callable):
        super().__init__(f"No server was given in command {func=}")

class UserNotSubscribedException(Exception):
    def __init__(self, user: User):
        super().__init__(f"User was not subscribed. {user=}")

class UserNotBlacklistedException(Exception):
    def __init__(self, user: User):
        super().__init__(f"User was not blacklisted. {user=}")