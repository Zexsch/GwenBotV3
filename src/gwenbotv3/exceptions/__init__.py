"""Exceptions used around the bot.

All custom exceptions go into this module."""

from ._services import (
    GwenseekError,
    LimitTooLargeError,
    PrefixTooLongError,
    ServerError,
    ServerIdNotGivenError,
    ServerNotFoundError,
    StrictnessAlreadySetError,
    SymbolAlreadySetupError,
    SymbolError,
    SymbolNotSetupError,
    SymbolTooLongError,
    UserError,
    UserIdOrNameNotGivenError,
    UserIsAnonymisedError,
    UserIsBlacklistedError,
    UserIsSubscribedError,
    UserNotAnonymisedError,
    UserNotBlacklistedError,
    UserNotFoundError,
    UserNotSubscribedError,
)
from .bot import (
    ChampionNotFoundError,
    StatsNotFoundError,
    WinrateError,
    WinrateNotFoundError,
)
from .utils import FailedRequestError

__all__ = [
    "ChampionNotFoundError",
    "GwenseekError",
    "LimitTooLargeError",
    "PrefixTooLongError",
    "ServerError",
    "ServerIdNotGivenError",
    "ServerNotFoundError",
    "StatsNotFoundError",
    "StrictnessAlreadySetError",
    "SymbolAlreadySetupError",
    "SymbolError",
    "SymbolNotSetupError",
    "SymbolTooLongError",
    "UserError",
    "UserIdOrNameNotGivenError",
    "UserIsAnonymisedError",
    "UserIsBlacklistedError",
    "UserIsSubscribedError",
    "UserNotAnonymisedError",
    "UserNotBlacklistedError",
    "UserNotFoundError",
    "UserNotSubscribedError",
    "WinrateError",
    "WinrateNotFoundError",
    "FailedRequestError"
]
