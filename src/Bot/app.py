import discord
from discord.ext import commands

from logger import SingletonLogger
from Database.database import DatabaseHandler
from Config.config import (OWNER_ID, PREFIX,)
from Bot.winrate_fetcher import WinrateFetcher

class App(commands.Bot):
    """
        Used to run all discord-related commands, such as sending or fetching messages.
    """
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = super().__init__(command_prefix=PREFIX, intents=intents, help_command=None, owner_id=OWNER_ID)
        
        self.logger = SingletonLogger().get_logger()
        self.database = DatabaseHandler()
        self.winrate_fetcher = WinrateFetcher()
        
        self.database.create_db()
    
    async def setup_hook(self) -> None:
        from Bot.Cogs.listener_cog import ListenerCog
        from Bot.Cogs.gwensub_cog import GwensubCog
        from Bot.Cogs.owner_cog import OwnerCog
        from Bot.Cogs.winrate_cog import WinrateCog
        from Bot.Cogs.dm_cog import DMCog
        from Bot.Cogs.commands_cog import CommandsCog
        from Bot.Cogs.leaderboard_cog import LeaderboardCog
        from Bot.Cogs.deepseek_cog import DeepseekCog
        
        self.logger.info("Initialising cogs.")
        await self.add_cog(ListenerCog(bot=self, database=self.database, logger=self.logger))
        await self.add_cog(GwensubCog(bot=self, database=self.database, logger=self.logger))
        await self.add_cog(OwnerCog(bot=self, database=self.database, logger=self.logger))
        await self.add_cog(WinrateCog(bot=self, winrate_fetcher=self.winrate_fetcher, logger=self.logger))
        await self.add_cog(DMCog(bot=self, winrate_fetcher=self.winrate_fetcher))
        await self.add_cog(CommandsCog(bot=self, database=self.database))
        await self.add_cog(LeaderboardCog(bot=self, database=self.database))
        await self.add_cog(DeepseekCog(bot=self, database=self.database, logger=self.logger))
        self.logger.info("Finished initialising cogs.")