import logging


class WinrateNotFoundException(Exception):
    def __init__(self, **kwargs) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.critical("Winrate was not found with kwargs=%s", kwargs)
        super().__init__(f"Winrate not found with {kwargs=}")


class StatsNotFoundException(Exception):
    def __init__(self, **kwargs) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.critical("Stats were not found with kwargs=%s", kwargs)
        super().__init__(f"Stats not found with {kwargs=}")


class ChampionNotFoundException(Exception):
    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.error("Champion not found with name=%s", name)
        super().__init__(f"Champion not found with {name=}")
