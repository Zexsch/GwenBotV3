"""Exceptions for various services."""

from .gwenseek_exceptions import GwenseekError
from .gwensub_exceptions import (
    UserIsBlacklistedError,
    UserIsSubscribedError,
    UserNotBlacklistedError,
    UserNotSubscribedError,
)
from .server_exceptions import ServerError, ServerIdNotGivenError, ServerNotFoundError
from .symbol_exceptions import (
    LimitTooLargeError,
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
