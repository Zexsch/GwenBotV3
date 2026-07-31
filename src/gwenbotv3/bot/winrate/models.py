"""All models and dataclasses used by winrate_fetcher"""

from dataclasses import dataclass, field


@dataclass
class Champion:
    """
    Represents a league Champion together with data in order to fetch the
    winrate from u.gg.
    """

    name: str
    patch: str = field(default="")
    role: str | None = field(default="")
    elo: str | None = field(default="")
    opponent: str | None = field(default="")

    def beautify_elo(self, beautified_elo_list: dict[str, str]) -> None:
        """Beautifies the elo given.

        An example would be turning platinum_plus to plat+.

        Args:
            beautified_elo_list (dict[str, str]): See winrate_fetcher
        """
        for key, value in beautified_elo_list.items():
            if self.elo == key:
                self.elo = value


@dataclass
class Result:
    """
    Represents the result of a u.gg winrate query.
    """

    champ: Champion
    with_opponent: bool
    win_rate: str | None
    match_count: str | None
    final_string: str = field(default="")
