"""All exceptions used for the winrate fetcher."""

import logging
from typing import Any


class WinrateNotFoundException(Exception):
    """If a winrate isn't found for a champion."""

    def __init__(self, **kwargs: Any) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.critical("Winrate was not found with kwargs=%s", kwargs)
        super().__init__(f"Winrate not found with {kwargs=}")


class StatsNotFoundException(Exception):
    """
    If the stats are not found for a champion.
    These include the match count and ban rate.
    """

    def __init__(self, **kwargs: Any) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.critical("Stats were not found with kwargs=%s", kwargs)
        super().__init__(f"Stats not found with {kwargs=}")


class ChampionNotFoundException(Exception):
    """If a given champion is not in the list of valid champions."""

    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.error("Champion not found with name=%s", name)
        super().__init__(f"Champion not found with {name=}")
