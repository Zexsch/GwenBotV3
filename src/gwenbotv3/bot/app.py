import discord
from discord.ext import commands

from gwenbotv3.config import (
    OWNER_ID,
    PREFIX,
)
from gwenbotv3 import SingletonLogger
from gwenbotv3.bot.winrate_fetcher import WinrateFetcher


class App(commands.Bot):
    """
    Used to run all discord-related commands, such as sending or fetching messages.
    """

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=None,
            owner_id=OWNER_ID,
            case_insensitive=True,
        )

        self.logger = SingletonLogger().get_logger()
        self.winrate_fetcher = WinrateFetcher()

    async def setup_hook(self) -> None:
        from gwenbotv3.bot.cogs import ListenerCog
        from gwenbotv3.bot.cogs import GwensubCog
        from gwenbotv3.bot.cogs import OwnerCog
        from gwenbotv3.bot.cogs import WinrateCog
        from gwenbotv3.bot.cogs import DMCog
        from gwenbotv3.bot.cogs import CommandsCog
        from gwenbotv3.bot.cogs import LeaderboardCog
        from gwenbotv3.bot.cogs import DeepseekCog

        self.logger.info("Initialising cogs.")
        await self.add_cog(ListenerCog(bot=self, logger=self.logger))
        await self.add_cog(GwensubCog(bot=self, logger=self.logger))
        await self.add_cog(OwnerCog(bot=self, logger=self.logger))
        await self.add_cog(
            WinrateCog(
                bot=self, winrate_fetcher=self.winrate_fetcher, logger=self.logger
            )
        )
        await self.add_cog(DMCog(bot=self, winrate_fetcher=self.winrate_fetcher))
        await self.add_cog(CommandsCog(bot=self))
        await self.add_cog(LeaderboardCog(bot=self))
        await self.add_cog(DeepseekCog(bot=self, logger=self.logger))
        self.logger.info("Finished initialising cogs.")
