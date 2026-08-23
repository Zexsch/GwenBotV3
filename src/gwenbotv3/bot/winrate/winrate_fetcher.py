"""The main logic behind getting champion winrates from lolalytics."""

import json
import logging

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from gwenbotv3.bot.winrate.models import Champion, Result
from gwenbotv3.config.winrate_values import (
    CHAMPION_LOOKUP,
    ELO_LIST,
    ELO_LOOKUP,
    ROLE_LIST,
    ROLE_LOOKUP,
)
from gwenbotv3.exceptions import (
    ChampionNotFoundError,
    Page404Error,
    RoleNotGivenError,
    WinrateNotFoundError,
)
from gwenbotv3.utils.request import request


class WinrateFetcher:
    """Used to get winrates"""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

        self.patch_version = ""
        self.patch_major_version = ""
        self.patch_minor_version = ""
        self.aiohttp_session = ClientSession()

        self.all_champions: list[str] = []

        # bs4 seems to have been more consistent with sets over tuples...
        # don't ask me why
        self.labels = {"Win Rate", "Pick Rate", "Ban Rate", "Games"}

    # ruff: noqa: UP037
    @classmethod
    async def create(cls) -> "WinrateFetcher":
        """Creates a WinrateFetcher.

        Use this instead of initialising directly.
        Otherwise champ list and patch will be empty.
        """
        self = cls()
        self.all_champions = await self._get_champion_list()
        self.patch_version = await self._get_current_patch()
        self.patch_major_version = self.patch_version.split(".")[0]
        self.patch_minor_version = self.patch_version.split(".")[1]
        return self

    async def _get_champion_list(self) -> list[str]:
        """Gets the full list of champions currently in league.

        Always up to date, as it queries ddragon.

        Returns:
            list[str]: The list.
        """
        self.logger.debug("Fetching champion.json")
        url: str = (
            "https://ddragon.leagueoflegends.com/cdn/"
            f"{self.patch_version}/data/en_US/champion.json"
        )

        champion_response = await request(session=self.aiohttp_session, url=url)
        champion_json: dict[str, str] = json.loads(champion_response)
        return [i.lower() for i in champion_json["data"]]

    async def _get_current_patch(self) -> str:
        """Gets the current league of legends patch.

        Always up to date, as it queries ddragon.

        Returns:
            str: The patch formatted as a standard patch format: ab.cd, example 15.21
        """
        url = "https://ddragon.leagueoflegends.com/realms/na.json"
        patch_response = await request(session=self.aiohttp_session, url=url)

        patch: str = json.loads(patch_response)["v"]
        self.logger.info("Fetched current patch: %s", patch)
        return patch

    def _alternative_elo_check(self, elo: str) -> str:
        return ELO_LOOKUP.get(elo, elo)

    def _alternate_champion_check(self, name: str) -> str:
        return CHAMPION_LOOKUP.get(name, name)

    def _alternative_role_check(self, lane: str) -> str:
        return ROLE_LOOKUP.get(lane, lane)

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

    # pylint: disable=line-too-long
    def _check_404(self, soup: BeautifulSoup) -> bool:
        not_found = soup.find(  # type: ignore[unused-ignore] # ty: ignore[no-matching-overload]
            string=lambda label: label and label.strip() == "Resource Not Found"  # type: ignore[unused-ignore]
        )
        return not_found is None

    def _get_base_url(self, champ: Champion) -> str:
        if not champ.opponent:
            return f"https://lolalytics.com/lol/{champ.name}/build/?"

        return f"https://lolalytics.com/lol/{champ.name}/vs/{champ.opponent}/build/?"

    def _get_url(self, champ: Champion) -> str:
        base_url = self._get_base_url(champ=champ)

        elo_str = ""
        role_str = ""
        patch_str = ""
        extra_lane = ""

        if champ.elo:
            elo_str = f"&tier={champ.elo}"

        if champ.role:
            role_str = f"&lane={champ.role}"

        if champ.patch:
            patch_str = f"&patch={champ.patch}"

        if champ.opponent:
            extra_lane = f"&lane={champ.role}&vslane={champ.role}"

        url = f"{base_url}{elo_str}{role_str}{patch_str}{extra_lane}"

        self.logger.debug("Created url=%s", url)

        return url

    def __is_target_label(self, label: str) -> bool:
        return bool(label and label.strip() in self.labels)

    def _get_result(self, soup: BeautifulSoup, champ: Champion) -> Result:
        result = {}

        for label_node in soup.find_all(string=self.__is_target_label):  # type: ignore[unused-ignore] # ty: ignore[no-matching-overload]
            label = label_node.strip()

            if label in result:
                continue

            if not label_node.parent:
                continue

            grandparent = label_node.parent.parent

            if not grandparent:
                continue

            value_div = grandparent.find("div")

            if value_div:
                value = "".join(value_div.strings).strip()
                result[label] = value

            if len(result) == 4:
                break

        win_rate = result.get("Win Rate", "")

        if not win_rate:
            raise WinrateNotFoundError

        pick_rate = result.get("Pick Rate", "")
        ban_rate = result.get("Ban Rate", "")
        match_count = result.get("Games", "")
        final_string = ""

        if champ.opponent:
            final_string = final_string + f"against {champ.opponent} "

        final_string = final_string + f"with {match_count} games played"

        if pick_rate and ban_rate:
            final_string = (
                final_string + f", a {pick_rate} pick rate and a {ban_rate} ban rate"
            )

        return Result(
            champ=champ,
            win_rate=win_rate,
            match_count=match_count,
            final_string=final_string,
        )

    async def _get_soup(self, champ: Champion) -> BeautifulSoup:
        url = self._get_url(champ=champ)

        res = await request(session=self.aiohttp_session, url=url)

        return BeautifulSoup(res, "html.parser")

    async def get_stats(self, champ: Champion, args: tuple[str, ...]) -> Result:
        """Gets the stats of of a Champion

        Uses the optional parametres of opponent, elo, role, rank and patch.
        These parametres are given in the args argument.
        Builds the necessary lolalytics url to fetch the winrate.

        Args:
            champ (Champion): Champion object.
            args (tuple[str, ...]): Optional arguments for the lolalytics url.

        Raises:
            ChampionNotFoundException: If the champion give is not a valid champion.

        Returns:
            Result: The resulting stats, formatted in a dataclass.
        """
        champ.name = self._alternate_champion_check(champ.name)

        if champ.name not in self.all_champions:
            raise ChampionNotFoundError()

        for arg in args:
            arg = arg.lower()

            arg = self._alternate_champion_check(arg)
            if arg in self.all_champions:
                champ.opponent = arg
                continue

            arg = self._alternative_role_check(arg)
            if arg in ROLE_LIST:
                champ.role = arg
                continue

            if self._check_patch(arg):
                champ.patch = arg
                continue

            arg = self._alternative_elo_check(arg)
            if arg in ELO_LIST:
                champ.elo = arg

        if champ.opponent and not champ.role:
            raise RoleNotGivenError

        soup = await self._get_soup(champ=champ)

        if not self._check_404(soup=soup):
            raise Page404Error

        return self._get_result(soup=soup, champ=champ)

    @property
    def patch(self) -> str:
        """Current patch."""
        return ".".join(self.patch_version.split(".")[:-1])
