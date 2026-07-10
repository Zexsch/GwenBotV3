import logging
from typing import Callable
from gwenbotv3.database._models import User


class ServerNotFoundException(Exception):
    def __init__(self, func: Callable):
        self.logger = logging.getLogger(__name__)
        self.logger.error("No servers were found when running func=%s", func.__name__)
        super().__init__(f"No servers were found in {func.__name__}")


class NotInAGuildException(Exception):
    def __init__(self, func: Callable):
        self.logger = logging.getLogger(__name__)
        self.logger.error("No servers were given in command %s", func.__name__)
        super().__init__(f"No server was given in command {func=}")


class UserNotSubscribedException(Exception):
    def __init__(self, user: User):
        super().__init__(f"User was not subscribed. {user=}")


class UserNotBlacklistedException(Exception):
    def __init__(self, user: User):
        super().__init__(f"User was not blacklisted. {user=}")


class UserOrCtxNotGiven(Exception):
    def __init__(self, func: Callable):
        self.logger = logging.getLogger(__name__)
        self.logger.error("No ctx or user was given in func=%s", func.__name__)
        super().__init__(f"Ctx or User must be given in func {func.__name__}")


class EmptyDataclass(Exception):
    def __init__(self, dc, func: Callable):
        self.logger = logging.getLogger(__name__)
        self.logger.error("Dataclass %s given in func=%s is None", dc, func.__name__)
        super().__init__(f"Dataclass {dc} given in {func.__name__} is None")


class AmountNotInt(Exception):
    def __init__(self):
        super().__init__("Amount fetched was not an integer.")


class NoUserFound(Exception):
    def __init__(self):
        super().__init__("No user was found.")


class LimitTooHigh(Exception):
    def __init__(self, limit):
        self.logger = logging.getLogger(__name__)
        self.logger.warning("Limit given was too high. limit=%i", limit)
        super().__init__("Limit is too high.")


class UserNotInDb(Exception):
    def __init__(self):
        super().__init__("The given user is not in the database.")


class UserNotAnonymised(Exception):
    def __init__(self):
        super().__init__("User is not anonymised.")
