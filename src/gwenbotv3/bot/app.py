import sys
import logging

import discord
from discord.ext import commands

from gwenbotv3.config import (
    OWNER_ID,
    PREFIX,
)
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

        self.logger = logging.getLogger(__name__)
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
        from gwenbotv3.bot.cogs import ModerationCog
        from gwenbotv3.bot.cogs import PrivacyCog
        from gwenbotv3.bot.cogs import HelpCog

        self.logger.info("Initialising cogs.")
        await self.add_cog(ListenerCog(bot=self))
        await self.add_cog(GwensubCog(bot=self))
        await self.add_cog(OwnerCog(bot=self))
        await self.add_cog(DMCog(bot=self, winrate_fetcher=self.winrate_fetcher))
        await self.add_cog(CommandsCog(bot=self))
        await self.add_cog(LeaderboardCog(bot=self))
        await self.add_cog(DeepseekCog(bot=self))
        await self.add_cog(ModerationCog(bot=self))
        await self.add_cog(PrivacyCog(bot=self))
        await self.add_cog(HelpCog(bot=self))
        await self.add_cog(WinrateCog(bot=self, winrate_fetcher=self.winrate_fetcher))
        self.logger.info("Finished initialising cogs.")

    async def on_error(
        self, event_method, *args, **kwargs
    ):  # pylint: disable=arguments-differ
        self.logger.error(
            "Unhandled exception in event '%s' (args=%s, kwargs=%s)",
            event_method,
            args,
            kwargs,
            exc_info=sys.exc_info(),
        )

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):  # pylint: disable=arguments-differ
        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            self.logger.debug("Command not found: %s", ctx.message.content)
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(
                f"You're missing some arguments! Here's some help: `{error.param.name}`"
            )
            return

        if isinstance(error, commands.BadArgument):
            await ctx.reply(
                f"Oh no! One of your arguments was wrong. Here's some help: {error}"
            )
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(
                "Unfortunately, you do not have the permissions to do this!"
            )
            return

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.reply(
                f"Oh no! Seems like gwen doesn't have the following neccesary permissions: {', '.join(error.missing_permissions)}"
            )
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"Slow down! Try again in {error.retry_after:.1f}s.")
            return

        if isinstance(error, commands.CheckFailure):
            await ctx.reply("Oh no! Gwen doesn't want you to use this command here...")
            return

        self.logger.error(
            "Unhandled exception in command '%s' (invoked by %s in #%s)",
            ctx.command,
            ctx.author,
            ctx.channel,
            exc_info=error,
        )
        await ctx.reply("Oh no! Gwen ran into some issues when running this command...")
