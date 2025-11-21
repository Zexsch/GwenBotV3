class WinrateNotFoundException(Exception):
    def __init__(self, **kwargs) -> None:
        super().__init__(f"Winrate not found with {kwargs=}")
        
class StatsNotFoundException(Exception):
    def __init__(self, **kwargs) -> None:
        super().__init__(f"Stats not found with {kwargs=}")
        
class ChampionNotFoundException(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"Champion not found with {name=}")