"""Main logic for the bot itself.

This includes the app itself and the winrate fetcher.
See bot.cogs for the discord command cogs.
"""

from .app import App
from .models import Champion, Result

__all__ = ["App", "Champion", "Result"]
