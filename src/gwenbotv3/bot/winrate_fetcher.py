"""The main logic behind getting champion winrates from u.gg."""

import json
import logging

from bs4 import BeautifulSoup

from gwenbotv3.bot.exceptions import (
    ChampionNotFoundException,
    StatsNotFoundException,
    WinrateNotFoundException,
)
from gwenbotv3.bot.models import Champion, Result
from gwenbotv3.utils.request import request


class WinrateFetcher:
    """Used to get winrates"""

    def __init__(self) -> None:

        self.logger = logging.getLogger(__name__)

        self.alternative_elos: dict[str, list[str]] = {
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

        self.alternative_champions: dict[str, list[str]] = {
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

        self.alternative_roles: dict[str, list[str]] = {
            "support": ["sup", "supp", "s"],
            "adc": ["bot", "bottom", "b"],
            "mid": ["midlane", "m"],
            "jungle": ["jgl", "j"],
            "top": ["toplane", "t"],
        }

        self.elo_list: list[str] = [
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

        self._elo_lookup: dict[str, str] = {
            alt: key for key, values in self.alternative_elos.items() for alt in values
        }

        self._champion_lookup: dict[str, str] = {
            alt: key
            for key, values in self.alternative_champions.items()
            for alt in values
        }

        self._role_lookup: dict[str, str] = {
            alt: key for key, values in self.alternative_roles.items() for alt in values
        }

        self.patch_version: str = self._get_current_patch()
        self.patch_major_version = self.patch_version.split(".")[0]
        self.patch_minor_version: str = self.patch_version.split(".")[1]

        self.all_champions: list[str] = self._get_champion_list()

        self.role_list: list[str] = ["top", "jungle", "mid", "adc", "support"]

        self.ugg_div_values: list[str] = [
            "shinggo",
            "good",
            "okay",
            "volxd",
            "meh",
            "great",
        ]  # Don't ask
        self.ugg_div_values_reversed: list[str] = list(reversed(self.ugg_div_values))

    def _get_champion_list(self) -> list[str]:
        """Gets the full list of champions currently in league.

        Always up to date, as it queries ddragon.

        Returns:
            list[str]: The list.
        """
        self.logger.debug("Fetching champion.json")
        url: str = (
            "https://ddragon.leagueoflegends.com/cdn/"
            + f"{self.patch_version}/data/en_US/champion.json"
        )

        champion_response = request(url)
        champion_json: dict[str, str] = json.loads(champion_response.text)
        return [i.lower() for i in champion_json["data"]]

    def _get_current_patch(self) -> str:
        """Gets the current league of legends patch.

        Always up to date, as it queries ddragon.

        Returns:
            str: The patch formatted as a standard patch format: ab.cd, example 15.21
        """
        url = "https://ddragon.leagueoflegends.com/realms/na.json"
        patch_response = request(url)

        patch: str = json.loads(patch_response.content)["v"]
        self.logger.info("Fetched current patch: %s", patch)
        return patch

    def _alternative_elo_check(self, elo: str) -> str:
        return self._elo_lookup.get(elo, elo)

    def _alternate_champion_check(self, name: str) -> str:
        return self._champion_lookup.get(name, name)

    def _alternative_role_check(self, lane: str) -> str:
        return self._role_lookup.get(lane, lane)

    def _check_patch(self, patch: str) -> str:
        """Checks if an argument is a valid patch.

        Standard patch format: ab.cd, example 15.21

        Args:
            patch (str): The argument to check.

        Returns:
            str: The patch, or an empty string if it's not a patch.
        """
        # Standard patch format: ab.cd, example 15.21
        if (
            (len(patch) == 5 or len(patch) == 4)
            and patch[2] == "."
            and patch[:2].isdigit()
            and patch[3:].isdigit()
        ):
            return patch

        return ""

    def _get_url(self, champ: Champion) -> str:
        """Returns the url to query for the winrate.

        Takes the champion's elo, the opponent, the role and patch into account.
        Dynamically builds a u.gg link out of these parametres.

        Args:
            champ (Champion): Champion object, including all necessary data.

        Returns:
            str: The final link.
        """
        elo_str = ""
        opponent_str = ""
        role_str = ""
        patch_str = ""

        if champ.elo:
            elo_str = f"&rank={champ.elo}"

        if champ.opponent:
            opponent_str = f"&opp={champ.opponent}"

        if champ.role:
            role_str = f"{champ.role}"

        if champ.patch:
            patch_str = f"&patch={champ.patch.replace('.', '_')}"

        if role_str:
            self.logger.debug(
                "Created url https://u.gg/lol/champions/%s/build/%s?%s%s%s",
                champ.name,
                role_str,
                elo_str,
                opponent_str,
                patch_str,
            )
            return (
                "https://u.gg/lol/champions/"
                + f"{champ.name}/build/{role_str}?{elo_str}{opponent_str}{patch_str}"
            )

        self.logger.debug(
            "Created url https://u.gg/lol/champions/%s/build?%s%s%s",
            champ.name,
            elo_str,
            opponent_str,
            patch_str,
        )
        return (
            "https://u.gg/lol/champions/"
            + f"{champ.name}/build?{elo_str}{opponent_str}{patch_str}"
        )

    def _get_winrate(self, soup: BeautifulSoup) -> str:
        """Gets the winrate from the BeautifulSoup object.

        u.gg has a very odd and unfriendly html layout.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object. Use _get_url
                for the request to get the soup.

        Raises:
            WinrateNotFoundException: If no winrate was found.

        Returns:
            str: The winrate.
        """
        for value in self.ugg_div_values:
            elements = soup.find_all(
                "div", {"class": f"text-[14px] font-extrabold {value}-tier"}
            )
            for element in elements:
                text = element.get_text(strip=True)
                if "%" in text and any(char.isdigit() for char in text):
                    return text
        raise WinrateNotFoundException()

    def _get_match_count(self, soup: BeautifulSoup, with_opponent: bool) -> str | None:
        """Returns the match count of the u.gg lookup.

        Args:
            soup (BeautifulSoup): BeautifulSoup object.
            with_opponent (bool): If the query has an opponent or not.
                The u.gg layout changes based on if an opponent is given or not.

        Returns:
            str | None: The match count if found, else None.
        """
        if with_opponent:
            match_count = soup.find(
                "div",
                {
                    "class": "text-[20px] max-sm:text-[16px] "
                    + "max-xs:text-[14px] font-extrabold"
                },
            )

            if match_count is None:
                return None

            return match_count.text

        try:
            match_count = soup.find_all("div", {"class": "text-[14px] font-extrabold"})[
                3
            ]
        except IndexError:
            return None

        if match_count is None:
            return None  # type: ignore[unreachable]

        return match_count.text

    def _get_pick_rate(self, soup: BeautifulSoup) -> str | None:
        """Returns the pick rate of the u.gg lookup.

        Args:
            soup (BeautifulSoup): BeautifulSoup object

        Returns:
            float | None: Pick rate if found, else None.
        """
        try:
            pick_rate: str = soup.find_all(
                "div", {"class": "text-[14px] font-extrabold"}
            )[1].text
        except IndexError:
            return None

        return pick_rate

    def _get_ban_rate(self, soup: BeautifulSoup) -> str | None:
        """Returns the ban rate of the u.gg lookup.

        Args:
            soup (BeautifulSoup): BeautifulSoup object.

        Returns:
            float | None: Ban rate if found, else None.
        """
        try:
            ban_rate: str = soup.find_all(
                "div", {"class": "text-[14px] font-extrabold"}
            )[2].text
        except IndexError:
            return None

        return ban_rate

    def _get_all_no_opponent(self, champ: Champion) -> Result:
        """Gets all the stats if no opponent is given.

        See the Result object for all stats.

        Args:
            champ (Champion): Champion object

        Returns:
            Result: The resulting stats, formatted in a dataclass.
        """
        url = self._get_url(champ)
        web = request(url).content

        soup = BeautifulSoup(web, "html.parser")

        win_rate = self._get_winrate(soup)
        match_count = self._get_match_count(soup, with_opponent=False)
        pick_rate = self._get_pick_rate(soup)
        ban_rate = self._get_ban_rate(soup)

        if not match_count:
            self.logger.error(
                "Unable to fetch match count for champ=%s with url=%s", champ, url
            )
            match_count = "Unknown"

        if not pick_rate:
            self.logger.error(
                "Unable to fetch pick rate for champ=%s with url=%s", champ, url
            )
            pick_rate = "Unknown"

        if not ban_rate:
            self.logger.error(
                "Unable to fetch ban rate for champ=%s with url=%s", champ, url
            )
            ban_rate = "Unknown"

        final_string = (
            f"with {match_count} matches played, a {pick_rate} pick rate "
            + f"and a {ban_rate} ban rate"
        )

        result = Result(
            champ=champ,
            win_rate=win_rate,
            with_opponent=True,
            match_count=match_count,
            final_string=final_string,
        )

        return result

    def _get_all_with_opponent(self, champ: Champion) -> Result:
        """Gets all the stats if an opponent is given.

        See the Result object for all stats.
        No opponent and with opponent are separate functions, as u.gg changes its
        layout depending on if an opponent is given or not.

        Args:
            champ (Champion): Champion object

        Returns:
            Result: The resulting stats, formatted in a dataclass.
        """
        url = self._get_url(champ)
        web = request(url).content

        soup = BeautifulSoup(web, "html.parser")

        win_rate = self._get_winrate(soup)
        match_count = self._get_match_count(soup, with_opponent=True)

        if not match_count:
            self.logger.error(
                "Unable to fetch match count for champ=%s with url=%s", champ, url
            )
            match_count = "Unknown"

        if not champ.opponent:
            raise StatsNotFoundException(champ=champ)

        result = Result(
            champ=champ,
            with_opponent=False,
            win_rate=win_rate,
            match_count=match_count,
            final_string=(
                f"against {champ.opponent.capitalize()} with {match_count} "
                + "matches played"
            ),
        )

        return result

    def get_stats(self, champ: Champion, args: tuple[str, ...]) -> Result:
        """Gets the stats of of a Champion

        Uses the optional parametres of opponent, elo, role, rank and patch.
        These parametres are given in the args argument.
        Builds the necessary u.gg url to fetch the winrate.

        Args:
            champ (Champion): Champion object.
            args (tuple[str, ...]): Optional arguments for the u.gg url.

        Raises:
            ChampionNotFoundException: If the champion give is not a valid champion.

        Returns:
            Result: The resulting stats, formatted in a dataclass.
        """
        champ.name = self._alternate_champion_check(champ.name)

        if champ.name not in self.all_champions:
            raise ChampionNotFoundException(name=champ.name)

        for arg in args:
            arg = arg.lower()

            arg = self._alternate_champion_check(arg)
            if arg in self.all_champions:
                champ.opponent = arg
                continue

            arg = self._alternative_role_check(arg)
            if arg in self.role_list:
                champ.role = arg
                continue

            if self._check_patch(arg):
                champ.patch = arg
                continue

            arg = self._alternative_elo_check(arg)
            if arg in self.elo_list:
                champ.elo = arg

        if not champ.opponent:
            return self._get_all_no_opponent(champ)

        return self._get_all_with_opponent(champ)

    @property
    def patch(self) -> str:
        return ".".join(self.patch_version.split(".")[:-1])
