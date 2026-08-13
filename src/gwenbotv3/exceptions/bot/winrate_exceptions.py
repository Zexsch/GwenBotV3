"""Exceptions for the Winrate Fetcher."""


# pylint: disable=missing-class-docstring
class WinrateError(Exception):
    pass


class WinrateNotFoundError(WinrateError):
    pass


class StatsNotFoundError(WinrateError):
    pass


class ChampionNotFoundError(WinrateError):
    pass
