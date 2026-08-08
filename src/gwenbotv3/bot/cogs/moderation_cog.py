"""Houses the moderation cog."""

import logging

import discord
from discord.ext import commands
from discord.ext.commands import Bot, Context

from gwenbotv3.services import ServerService
from gwenbotv3.types import AppType


class ModerationCog(commands.Cog):
    """Anything to do with server moderation."""

    def __init__(self, bot: AppType) -> None:
        self.bot = bot
        self.server_service = ServerService()
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(description="Change the server's prefix!")
    @commands.has_permissions(kick_members=True)
    async def prefix(self, ctx: Context, new_prefix: str) -> None:
        """Changes a server's prefix.

        Args:
            ctx (Context): Discord Context.
            new_prefix (str): The prefix to be set.
        """
        assert ctx.guild is not None
        if not new_prefix:
            await ctx.send("Please input a valid prefix.")
            return

        if len(new_prefix) > 5:
            await ctx.send("Your prefix can be at most 5 characters long!")
            return

        await self.server_service.update_server(
            server_id=ctx.guild.id, prefix=new_prefix
        )

        self.bot.prefix_cache[ctx.guild.id] = new_prefix

        await ctx.send(f"Changed prefix to {new_prefix}")

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
