"""Exceptions for various services."""

from .gwenseek_exceptions import GwenseekError
from .gwensub_exceptions import (
    UserIsBlacklistedError,
    UserIsSubscribedError,
    UserNotBlacklistedError,
    UserNotSubscribedError,
)
from .server_exceptions import (
    PrefixTooLongError,
    ServerError,
    ServerIdNotGivenError,
    ServerNotFoundError,
)
from .symbol_exceptions import (
    LimitTooLargeError,
    PingUserAlreadyInsertedError,
    PingUserNotInsertedError,
    StrictnessAlreadySetError,
    SymbolAlreadySetupError,
    SymbolError,
    SymbolNotSetupError,
    SymbolTooLongError,
)
from .user_exceptions import (
    UserError,
    UserIdOrNameNotGivenError,
    UserIsAnonymisedError,
    UserNotAnonymisedError,
    UserNotFoundError,
)

__all__ = [
    "GwenseekError",
    "LimitTooLargeError",
    "PingUserAlreadyInsertedError",
    "PingUserNotInsertedError",
    "PrefixTooLongError",
    "ServerError",
    "ServerIdNotGivenError",
    "ServerNotFoundError",
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
]
