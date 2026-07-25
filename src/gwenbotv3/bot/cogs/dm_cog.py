"""Houses the DM Cog."""

import discord
from discord.ext import commands

from gwenbotv3.bot.winrate_fetcher import WinrateFetcher


class DMCog(commands.Cog):
    """Anything to do with interacting with a user's DMs."""

    def __init__(self, bot: commands.Bot, winrate_fetcher: WinrateFetcher) -> None:
        self.bot = bot
        self.winrate_fetcher = winrate_fetcher

    @commands.command()
    async def list(self, ctx: commands.Context[commands.Bot]) -> None:
        """Sends the user a list of all champions."""
        user: discord.Member | discord.User = ctx.message.author
        await user.send(", ".join(map(str, self.winrate_fetcher.all_champions)))

    @commands.command()
    async def elolist(self, ctx: commands.Context[commands.Bot]) -> None:
        """Sends the user a list of all elos."""
        user: discord.Member | discord.User = ctx.message.author
        await user.send(", ".join(map(str, self.winrate_fetcher.elo_list)))

    @commands.command(aliases=["roles", "role", "rolelist"])
    async def role_list(self, ctx: commands.Context[commands.Bot]) -> None:
        """Sends the user a list of all roles."""
        user: discord.Member | discord.User = ctx.message.author
        await user.send(", ".join(map(str, self.winrate_fetcher.role_list)))
