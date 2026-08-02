"""Houses the DM Cog."""

from discord.ext import commands

from gwenbotv3.bot.winrate import WinrateFetcher
from gwenbotv3.config.winrate_values import ELO_LIST, ROLE_LIST


class DMCog(commands.Cog):
    """Anything to do with interacting with a user's DMs."""

    def __init__(self, bot: commands.Bot, winrate_fetcher: WinrateFetcher) -> None:
        self.bot = bot
        self.winrate_fetcher = winrate_fetcher

    @commands.hybrid_command()
    async def list(self, ctx: commands.Context) -> None:
        """Sends a list of all champions."""
        to_send = ", ".join(map(str, self.winrate_fetcher.all_champions))
        if ctx.interaction is not None:
            await ctx.send(to_send, ephemeral=True)
            return

        user = ctx.message.author
        await user.send(to_send)

    @commands.hybrid_command()
    async def elolist(self, ctx: commands.Context) -> None:
        """Sends a list of all elos."""
        to_send = ", ".join(map(str, ELO_LIST))
        if ctx.interaction is not None:
            await ctx.send(to_send, ephemeral=True)
            return

        user = ctx.message.author
        await user.send(to_send)

    @commands.hybrid_command(aliases=["roles", "role", "rolelist"])
    async def role_list(self, ctx: commands.Context) -> None:
        """Sends a list of all roles."""
        to_send = ", ".join(map(str, ROLE_LIST))
        if ctx.interaction is not None:
            await ctx.send(to_send, ephemeral=True)
            return

        user = ctx.message.author
        await user.send(to_send)
