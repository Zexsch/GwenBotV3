"""Exceptions for bot modules."""

from .winrate_exceptions import (
    ChampionNotFoundError,
    Page404Error,
    RoleNotGivenError,
    StatsNotFoundError,
    WinrateError,
    WinrateNotFoundError,
)

__all__ = [
    "ChampionNotFoundError",
    "Page404Error",
    "RoleNotGivenError",
    "StatsNotFoundError",
    "WinrateError",
    "WinrateNotFoundError",
]
