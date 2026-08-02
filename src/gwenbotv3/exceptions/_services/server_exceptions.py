"""Exceptions for the Server service."""


# pylint: disable=missing-class-docstring


class ServerError(Exception):
    pass


class ServerIdNotGivenError(ServerError):
    pass


class ServerNotFoundError(ServerError):
    pass


class PrefixTooLongError(ServerError):
    pass
