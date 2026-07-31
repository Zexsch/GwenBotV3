"""Winrate fetcher.

Gets winrate for champions from u.gg.
"""

from .models import Champion, Result
from .winrate_fetcher import WinrateFetcher

__all__ = ["Champion", "Result", "WinrateFetcher"]
