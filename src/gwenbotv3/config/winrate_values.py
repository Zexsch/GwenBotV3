"""Constants for the winrate fetcher."""

_ALTERNATIVE_ELOS: dict[str, list[str]] = {
    "platinum_plus": ["platplus", "plat+", "platinumplus"],
    "d2_plus": [
        "d2+",
        "d2",
        "d2plus",
        "diamond2",
        "diamond2plus",
        "diamond2+",
        "diamond_2plus",
        "diamond_2+",
    ],
    "diamond_plus": ["d+", "dplus", "diamondplus"],
    "master_plus": [
        "m+",
        "master+",
        "masterplus",
        "masters",
        "masters+",
        "mastersplus",
    ],
    "emerald_plus": ["eme+", "emerald+", "emeplus", "emeraldplus"],
    "grandmaster_plus": ["gm+", "grandmaster+", "grandmasterplus"],
}

_ALTERNATIVE_CHAMPIONS: dict[str, list[str]] = {
    "monkeyking": ["wukong"],
    "drmundo": ["mundo"],
    "kogmaw": ["kog'maw"],
    "jarvaniv": ["jarvan", "j4"],
    "khazix": ["kha'zix"],
    "ksante": ["k'sante"],
    "masteryi": ["yi"],
    "aatrox": ["emo"],
    "tahmkench": ["tahm"],
    "twistedfate": ["tf"],
    "xinzhao": ["xin"],
    "aurelionsol": ["asol"],
    "leesin": ["lee"],
}

_ALTERNATIVE_ROLES: dict[str, list[str]] = {
    "support": ["sup", "supp", "s"],
    "bottom": ["bot", "adc", "b"],
    "middle": ["midlane", "m", "mid"],
    "jungle": ["jgl", "j"],
    "top": ["toplane", "t"],
}

ELO_LIST: list[str] = [
    "all",
    "1trick",
    "challenger",
    "master",
    "grandmaster",
    "diamond",
    "platinum",
    "emerald",
    "gold",
    "silver",
    "bronze",
    "iron",
    "grandmaster_plus",
    "d2_plus",
    "master_plus",
    "diamond_plus",
    "platinum_plus",
    "unranked",
    "",
]

ELO_LOOKUP: dict[str, str] = {
    alt: key for key, values in _ALTERNATIVE_ELOS.items() for alt in values
}

CHAMPION_LOOKUP: dict[str, str] = {
    alt: key for key, values in _ALTERNATIVE_CHAMPIONS.items() for alt in values
}

ROLE_LOOKUP: dict[str, str] = {
    alt: key for key, values in _ALTERNATIVE_ROLES.items() for alt in values
}

ROLE_LIST: list[str] = ["top", "jungle", "mid", "adc", "support"]
