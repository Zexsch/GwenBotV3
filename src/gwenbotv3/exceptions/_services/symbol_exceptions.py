"""Exceptions for the Symbol service."""


# pylint: disable=missing-class-docstring


class SymbolError(Exception):
    pass


class SymbolAlreadySetupError(SymbolError):
    pass


class SymbolNotSetupError(SymbolError):
    pass


class StrictnessAlreadySetError(SymbolError):
    pass


class UserExistsError(SymbolError):
    pass


class SymbolTooLongError(SymbolError):
    pass


class LimitTooLargeError(SymbolError):
    pass
