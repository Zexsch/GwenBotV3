"""Exceptions for the Gwenseek service."""


# pylint: disable=missing-class-docstring


class UserError(Exception):
    pass


class UserIdOrNameNotGivenError(UserError):
    pass


class UserNotFoundError(UserError):
    pass


class UserIsAnonymisedError(UserError):
    pass


class UserNotAnonymisedError(UserError):
    pass
