"""Exceptions for bot modules."""

from .winrate_fetcher import (
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
