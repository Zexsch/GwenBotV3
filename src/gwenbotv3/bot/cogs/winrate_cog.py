"""Houses the winrate cog."""

import logging
from typing import ClassVar

from discord import Interaction, app_commands
from discord.ext import commands

from gwenbotv3.bot.winrate import Champion, WinrateFetcher
from gwenbotv3.config.winrate_values import ELO_LIST
from gwenbotv3.exceptions import (
    ChampionNotFoundError,
    FailedRequestError,
    Page404Error,
    RoleNotGivenError,
    StatsNotFoundError,
    WinrateNotFoundError,
)


class WinrateCog(commands.Cog):
    """Anything to do with the winrate commands."""

    ELO_CHOICES: ClassVar[list[app_commands.Choice[str]]] = [
        app_commands.Choice(name=elo if elo else "none", value=elo) for elo in ELO_LIST
    ]

    _ROLES: ClassVar[list[str]] = ["Top", "Jungle", "Mid", "Bot", "Support"]

    ROLE_CHOICES: ClassVar[list[app_commands.Choice[str]]] = [
        app_commands.Choice(name=role, value=role) for role in _ROLES
    ]

    def __init__(self, bot: commands.Bot, winrate_fetcher: WinrateFetcher) -> None:
        self.bot = bot
        self.winrate_fetcher = winrate_fetcher
        self.logger = logging.getLogger(__name__)

        self.beautified_elo_list: dict[str, str] = {
            "platinum_plus": "Plat+",
            "d2_plus": "D2+",
            "diamond_plus": "D+",
            "master_plus": "M+",
            "grandmaster_plus": "GM+",
        }

    async def _winrate(self, champion_name: str, *args) -> str:  # type: ignore[no-untyped-def]
        """See wr docstring"""
        # pylint: disable=too-many-return-statements, too-many-branches # Makes sense here
        self.logger.debug(
            "Calling winrate for champ=%s with args=%s", champion_name, args
        )

        champ = Champion(name=champion_name)

        try:
            result = await self.winrate_fetcher.get_stats(champ, args)
        except FailedRequestError as e:
            self.logger.critical(
                "Unable to request lolalytics with champ=%s, args=%s, exc=%s",
                champion_name,
                args,
                e,
            )
            return (
                "Oh no! Seems like Gwen was unable to fetch lolalytics! "
                "Is it currently down?"
            )
        except WinrateNotFoundError:
            self.logger.critical(
                "Unable to fetch winrate for champ=%s, args=%s",
                champion_name,
                args,
            )
            return (
                "Oh no! Seems like Gwen ran into some issues whilst fetching"
                " the winrate! Are you sure that there's enough matches played?"
            )
        except StatsNotFoundError:
            self.logger.critical(
                "Unable to fetch stats for champ=%s, args=%s",
                champion_name,
                args,
            )
            return (
                "Oh no! Seems like Gwen ran into some issues whilst"
                " fetching the winrate!"
            )
        except ChampionNotFoundError:
            return (
                "Gwen was unable to find your specified champion... Please check +list "
                "for a list of all accepted champion names!"
            )
        except RoleNotGivenError:
            return "Gwen needs a lane if you give an opponent!"
        except Page404Error:
            return (
                "Gwen ran into some issues! Are you sure that there are "
                "enough matches played?"
            )

        if champ.patch:
            minor_patch = self.winrate_fetcher.patch_minor_version

            try:
                if champ.patch and (int(champ.patch[-2:]) < int(minor_patch) - 5):
                    return (
                        "Gwen can only gets stats for the past 5 patches! The current "
                        f"patch is {self.winrate_fetcher.patch}."
                    )
            except ValueError:
                if champ.patch and (int(champ.patch[-1:]) < int(minor_patch) - 5):
                    return (
                        "Gwen can only gets stats for the past 5 patches! The current "
                        f"patch is {self.winrate_fetcher.patch}."
                    )

        if result.champ.elo:
            result.champ.beautify_elo(self.beautified_elo_list)

        message: list[str] = [
            f"{result.champ.name.capitalize()} has a {result.win_rate} winrate"
        ]

        if result.champ.elo:
            message.append(f"in {result.champ.elo}")

        if result.champ.role:
            message.append(f"in {result.champ.role}")

        message.append(result.final_string)

        if result.champ.patch:
            message.append(f"in patch {result.champ.patch}")

        return " ".join(p for p in message if p)

    @commands.command(aliases=["winrate"])
    async def wr(
        self, ctx: commands.Context[commands.Bot], champion_name: str, *args: str
    ) -> None:
        """Fetches the winrate of a champion. Uses u.gg for the winrate.

        *args
        ----------
        :elo: Given elo.
        :role: Given role.
        :patch: Given patch.
        :opponent: Given opponent.

        Args:
            ctx (commands.Context): Discord Context.
            champion_name (str): Name of the champion.
        """
        msg = await self._winrate(champion_name, *args)
        await ctx.send(msg)

    # Necessary here
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    @app_commands.command(
        name="winrate", description="Fetches the winrate of a champion."
    )
    @app_commands.describe(
        champion_name="Name of the champion",
        elo="Elo (e.g. d2+, plat+)",
        role="Role/lane",
        patch="Patch version",
        opponent="Opponent champion for matchup winrate",
    )
    @app_commands.choices(elo=ELO_CHOICES)
    @app_commands.choices(role=ROLE_CHOICES)
    async def wr_slash(
        self,
        interaction: Interaction,
        champion_name: str,
        elo: str | None = None,
        role: str | None = None,
        patch: str | None = None,
        opponent: str | None = None,
    ) -> None:
        """Same as wr but for slash commands."""
        await interaction.response.defer()
        msg = await self._winrate(champion_name, *(elo, role, patch, opponent))
        await interaction.followup.send(msg)

    @commands.hybrid_command(aliases=["checkver", "patch"])
    async def version(self, ctx: commands.Context) -> None:
        """Sends the current league patch."""
        await ctx.send(f"Currently on league patch {self.winrate_fetcher.patch}.")

    @wr_slash.error
    async def on_wr_slash_error(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ) -> None:
        """Error handling for wr slash command.

        Not done via global handler.
        """
        self.logger.error(
            "Unhandled exception in command '%s' (invoked by %s in #%s)",
            interaction.command,
            interaction.user.id,
            interaction.channel,
            exc_info=error,
        )

        await interaction.followup.send(
            "Oh no! Gwen ran into some issues when running this command..."
        )
