from logging import Logger

from discord.ext import commands
from discord.ext.commands import Context

from gwenbotv3.database.handlers.server_handler import ServerHandler
from gwenbotv3.database.get_context import context


class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: Logger):
        self.bot = bot
        self.server_handler = ServerHandler()
        self.logger = logger

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def prefix(self, ctx: Context, new_prefix: str):
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
    async def _error(self, ctx: commands.Context, error) -> None:
        """Run if a user does not have the permissions necessary to run a command."""

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have the permissions to use this command.")
