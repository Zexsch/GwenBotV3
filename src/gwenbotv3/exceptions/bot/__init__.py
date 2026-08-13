"""Exceptions for bot modules."""

from .winrate_exceptions import (
    ChampionNotFoundError,
    StatsNotFoundError,
    WinrateError,
    WinrateNotFoundError,
)

__all__ = [
    "ChampionNotFoundError",
    "StatsNotFoundError",
    "WinrateError",
    "WinrateNotFoundError",
]
