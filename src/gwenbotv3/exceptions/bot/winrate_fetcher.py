"""Exceptions for the Winrate Fetcher."""


class WinrateError(Exception):
    pass


class WinrateNotFoundError(WinrateError):
    pass


class StatsNotFoundError(WinrateError):
    pass


class ChampionNotFoundError(WinrateError):
    pass
