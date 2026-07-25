"""All exceptions regarding the database."""

import logging
from collections.abc import Callable
from typing import Any

from gwenbotv3.database._models import User


class ServerNotFoundException(Exception):
    """If a server was not found in the database."""

    def __init__(self, func: Callable[..., Any]) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.error("No servers were found when running func=%s", func.__name__)
        super().__init__(f"No servers were found in {func.__name__}")


class NotInAGuildException(Exception):
    """If a command which needs a server was not run in a server."""

    def __init__(self, func: Callable[..., Any]) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.error("No servers were given in command %s", func.__name__)
        super().__init__(f"No server was given in command {func=}")


class UserNotSubscribedException(Exception):
    """If a user is not subscribed, yet tried to run a subscription-only command."""

    def __init__(self, user: User) -> None:
        super().__init__(f"User was not subscribed. {user=}")


class UserNotBlacklistedException(Exception):
    """If a user is not blacklisted, yet an unblacklist was attempted."""

    def __init__(self, user: User) -> None:
        super().__init__(f"User was not blacklisted. {user=}")


class UserOrCtxNotGiven(Exception):
    """If neither a User object nor a discord.commands.Context or discord.Message object
    was given, despite one being necessary."""

    def __init__(self, func: Callable[..., Any]) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.error("No ctx or user was given in func=%s", func.__name__)
        super().__init__(f"Ctx or User must be given in func {func.__name__}")


class EmptyDataclass(Exception):
    """If a dataclass given to a function has no set properties."""

    def __init__(self, dc: object, func: Callable[..., Any]) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.error("Dataclass %s given in func=%s is None", dc, func.__name__)
        super().__init__(f"Dataclass {dc} given in {func.__name__} is None")


class AmountNotInt(Exception):
    """If the amount fetched by a function was not an integer."""

    def __init__(self) -> None:
        super().__init__("Amount fetched was not an integer.")


class NoUserFound(Exception):
    """If no user was found when trying to fetch one."""

    def __init__(self) -> None:
        super().__init__("No user was found.")


class LimitTooHigh(Exception):
    """If the limit given in a function was higher than the maximum amount."""

    def __init__(self, limit: int) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.warning("Limit given was too high. limit=%i", limit)
        super().__init__("Limit is too high.")


class UserNotInDb(Exception):
    """If a user is not in the database."""

    def __init__(self) -> None:
        super().__init__("The given user is not in the database.")


class UserNotAnonymised(Exception):
    """If a user tried to deanonymise themself, even though they were not anonymised."""

    def __init__(self) -> None:
        super().__init__("User is not anonymised.")
