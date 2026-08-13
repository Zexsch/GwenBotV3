"""Exceptions for privacy service."""


# pylint: disable=missing-class-docstring
class PrivacyError(Exception):
    pass


class UserAlreadyPrivateError(PrivacyError):
    pass


class UserNotPrivateError(PrivacyError):
    pass
