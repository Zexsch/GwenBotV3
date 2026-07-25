"""Houses the moderation cog."""

import logging

import discord
from discord.ext import commands
from discord.ext.commands import Bot, Context

from gwenbotv3.database_handling.get_context import context
from gwenbotv3.database_handling.handlers.server_handler import ServerHandler


class ModerationCog(commands.Cog):
    """Anything to do with server moderation."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.server_handler = ServerHandler()
        self.logger = logging.getLogger(__name__)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def prefix(self, ctx: Context[Bot], new_prefix: str) -> None:
        """Changes a server's prefix.

        Args:
            ctx (Context): Discord Context.
            new_prefix (str): The prefix to be set.
        """
        if not new_prefix:
            await ctx.send("Please input a valid prefix.")
            return

        if len(new_prefix) > 1:
            await ctx.send("Prefix must only be one character.")
            return

        user_context = context(ctx)

        self.server_handler.change_prefix(user_context, new_prefix)

        await ctx.send(f"Changed prefix to {new_prefix}.")

    @prefix.error
    async def _error(
        self, ctx: commands.Context[Bot], error: discord.DiscordException
    ) -> None:
        """Run if a user does not have the permissions necessary to run a command."""

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Unfortunately, you do not have the permissions to do this!")
        else:
            import sys

            original = getattr(error, "original", error)
            self.logger.error(
                "Unhandled error: %s: %s",
                type(original).__name__,
                original,
                exc_info=sys.exc_info(),
            )

            await ctx.send("Gwen ran into some issues whilst performing this command!")
