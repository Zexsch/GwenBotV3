"""Exceptions for the Gwensub service."""


# pylint: disable=missing-class-docstring
class GwensubError(Exception):
    pass


class UserIsSubscribedError(GwensubError):
    pass


class UserNotSubscribedError(GwensubError):
    pass


class UserIsBlacklistedError(GwensubError):
    pass


class UserNotBlacklistedError(GwensubError):
    pass
