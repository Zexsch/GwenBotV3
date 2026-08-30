"""Exceptions for various services."""

from .grow_the_gwen_exceptions import (
    GrowTheGwenError,
    PlayerInsertionError,
    PlayerNotFoundError,
)
from .gwenseek_exceptions import GwenseekError
from .gwensub_exceptions import (
    UserIsBlacklistedError,
    UserIsSubscribedError,
    UserNotBlacklistedError,
    UserNotSubscribedError,
)
from .privacy_exceptions import (
    PrivacyError,
    UserAlreadyPrivateError,
    UserNotPrivateError,
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
    "GrowTheGwenError",
    "GwenseekError",
    "LimitTooLargeError",
    "PingUserAlreadyInsertedError",
    "PingUserNotInsertedError",
    "PlayerInsertionError",
    "PlayerNotFoundError",
    "PrefixTooLongError",
    "PrivacyError",
    "ServerError",
    "ServerIdNotGivenError",
    "ServerNotFoundError",
    "StrictnessAlreadySetError",
    "SymbolAlreadySetupError",
    "SymbolError",
    "SymbolNotSetupError",
    "SymbolTooLongError",
    "UserAlreadyPrivateError",
    "UserError",
    "UserIdOrNameNotGivenError",
    "UserIsAnonymisedError",
    "UserIsBlacklistedError",
    "UserIsSubscribedError",
    "UserNotAnonymisedError",
    "UserNotBlacklistedError",
    "UserNotFoundError",
    "UserNotPrivateError",
    "UserNotSubscribedError",
]
