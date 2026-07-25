"""The main module for the discord app itself."""

import logging
import sys
from typing import Any

import discord
from discord.ext import commands

from gwenbotv3.bot.winrate_fetcher import WinrateFetcher
from gwenbotv3.config import (
    OWNER_ID,
    PREFIX,
)

# pylint: disable=arguments-differ


class App(commands.Bot):
    """The app itself. This will run all cogs and handle generic discord errors."""

    def __init__(self) -> None:
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
        from gwenbotv3.bot.cogs import (
            CommandsCog,
            DeepseekCog,
            DMCog,
            GwensubCog,
            HelpCog,
            LeaderboardCog,
            ListenerCog,
            ModerationCog,
            OwnerCog,
            PrivacyCog,
            WinrateCog,
        )

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

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        self.logger.error(
            "Unhandled exception in event '%s' (args=%s, kwargs=%s)",
            event_method,
            args,
            kwargs,
            exc_info=sys.exc_info(),
        )

    async def _command_errors(
        self, ctx: commands.Context[Any], error: commands.CommandError
    ) -> None:
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

    async def _permission_errors(
        self, ctx: commands.Context[Any], error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(
                "Unfortunately, you do not have the permissions to do this!"
            )
            return

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.reply(
                "Oh no! Seems like gwen doesn't have the following neccesary "
                + f"permissions: {', '.join(error.missing_permissions)}"
            )
            return

    async def on_command_error(
        self,
        ctx: commands.Context[Any],
        error: commands.CommandError,
    ) -> None:
        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)

        await self._command_errors(ctx, error)
        await self._permission_errors(ctx, error)

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
