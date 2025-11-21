from dataclasses import dataclass, field

@dataclass
class Champion:
    name: str
    patch: str = field(default="")
    role: str | None = field(default="")
    elo: str | None = field(default="")
    opponent: str | None = field(default="")
    
    def beautify_elo(self, beautified_elo_list: dict[str, str]) -> None:
        for key, value in beautified_elo_list.items():
            if self.elo == key:
                self.elo = value


@dataclass
class Result:
    champ: Champion
    with_opponent: bool
    win_rate: str | None
    match_count: str | None
    final_string: str = field(default="")