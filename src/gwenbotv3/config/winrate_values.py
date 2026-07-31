"""Hardcoded values for the winrate fetcher."""

alternative_elos: dict[str, list[str]] = {
    "platinum_plus": ["platplus", "plat+", "platinumplus"],
    "diamond_2_plus": [
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
}

alternative_champions: dict[str, list[str]] = {
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

alternative_roles: dict[str, list[str]] = {
    "support": ["sup", "supp", "s"],
    "adc": ["bot", "bottom", "b"],
    "mid": ["midlane", "m"],
    "jungle": ["jgl", "j"],
    "top": ["toplane", "t"],
}

elo_list: list[str] = [
    "overall",
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
    "diamond_2_plus",
    "master_plus",
    "diamond_plus",
    "platinum_plus",
    "",
]

elo_lookup: dict[str, str] = {
    alt: key for key, values in alternative_elos.items() for alt in values
}

champion_lookup: dict[str, str] = {
    alt: key for key, values in alternative_champions.items() for alt in values
}

role_lookup: dict[str, str] = {
    alt: key for key, values in alternative_roles.items() for alt in values
}

role_list: list[str] = ["top", "jungle", "mid", "adc", "support"]
