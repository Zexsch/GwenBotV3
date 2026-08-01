"""Houses the leaderboard cog."""

import logging
from typing import Any

import discord
from discord.ext import commands

from gwenbotv3.exceptions import (
    LimitTooLargeError,
    SymbolAlreadySetupError,
    SymbolNotSetupError,
)
from gwenbotv3.services import SymbolService, UserService
from gwenbotv3.utils import get_mention


class LeaderboardCog(commands.Cog):
    """Anything to do with the symbol counter."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.symbol_service = SymbolService()
        self.user_service = UserService()
        self.logger = logging.getLogger(__name__)

    @commands.command(aliases=["initialize"])
    @commands.has_permissions(kick_members=True)
    async def initialise(
        self,
        ctx: commands.Context[commands.Bot],
        symbol: str,
        channel: discord.TextChannel,
        strict: bool = False,
        strict_channel: discord.TextChannel | None = None,
    ) -> None:
        """Initialises the symbol counter for a server.

        :symbol: The symbol to count.
        :channel: The channel to count in.

        Args:
            symbol (str): The symbol to count.
            channel (discord.TextChannel): The channel to count in.
        """
        assert ctx.guild is not None

        strict_channel_id = None if strict_channel is None else strict_channel.id

        if any([strict, strict_channel_id]) and not all([strict, strict_channel_id]):
            await ctx.send("If you want strictness, you need to give a strict channel!")
            return

        try:
            await self.symbol_service.insert_counter(
                server_id=ctx.guild.id,
                channel_id=channel.id,
                creating_user=ctx.author.id,
                symbol=symbol,
                strict=strict,
                strict_channel=strict_channel_id,
            )
        except LimitTooLargeError:
            await ctx.send("Your counting symbol can be at most 200 characters long!")
        except SymbolAlreadySetupError:
            await ctx.send("This server already has a counter set up!")

        await ctx.send(
            f"Initialisation complete for channel {channel.name}, symbol {symbol}"
        )

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def strict(self, ctx: commands.Context[commands.Bot]) -> None:
        """Flips a counter's strictness."""
        assert ctx.guild is not None

        try:
            new_strictness = await self.symbol_service.flip_strictness(
                server_id=ctx.guild.id
            )
        except SymbolNotSetupError:
            await ctx.send("This server does not have a counter set up!")
            return

        await self.symbol_service.update_strictness_channel(
            server_id=ctx.guild.id, channel_id=ctx.channel.id
        )

        if new_strictness:
            await ctx.send(
                f"Done! Updated your strictness to be {new_strictness}. "
                "Set the channel that you will be pinged in to the current channel."
            )
            return

        await ctx.send(f"Done! Updates your strictness to be {new_strictness}.")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def recount(self, ctx: commands.Context[commands.Bot]) -> None:
        """Recounts the symbols sent in the initialised channel."""
        assert ctx.guild is not None

        counter = await self.symbol_service.select_counter_by_ids(
            server_id=ctx.guild.id
        )

        if not counter:
            await ctx.send("This server doesn't have a symbol counter set up!")
            return

        channel_object = self.bot.get_channel(counter.channel_id)

        if not isinstance(channel_object, discord.TextChannel):
            await ctx.send(
                "It seems like the initialised channel is not a text channel... "
                "how is this even possible?"
            )
            return

        await ctx.send("Gwen is recounting. This might take a while.")

        self.logger.info("Started recounting for server=%s", ctx.guild.id)

        async for message in channel_object.history(limit=None):
            user = await self.user_service.select_user(user_id=message.author.id)

            if not user:
                user = await self.user_service.insert_user(
                    user_id=message.author.id, user_name=message.author.name
                )

            await self.symbol_service.update_counters(
                server_id=ctx.guild.id, user_id=user.user_id
            )

        self.logger.info("Finished recounting for server=%s", ctx.guild.id)
        await ctx.send(f"Gwen has finished counting! <@{ctx.author.id}>")

    @commands.command(
        aliases=[
            "question",
            "questions",
            "qm",
            "qms",
            "questionmarks",
            "questionmark",
            "?",
            "symbols",
        ]
    )
    async def amount(self, ctx: commands.Context[commands.Bot]) -> None:
        """Fetches the amount of symbols sent in a server."""
        assert ctx.guild is not None

        counter = await self.symbol_service.select_counter_by_ids(
            server_id=ctx.guild.id
        )

        if not counter:
            await ctx.send("This server doesn't have any counters set up!")
            return

        await ctx.send(f"The current amount is {counter.amount}!")

    @commands.command(
        aliases=[
            "question_user",
            "questions_user",
            "qm_user",
            "qms_user",
            "questionmarks_user",
            "questionmark_user",
            "?_u",
            "?u",
        ]
    )
    async def amount_user(
        self, ctx: commands.Context[commands.Bot], u_id: int | str | None
    ) -> None:
        """Checks the amount of symbols sent in a server by a user.

        Args:
            id (int | str | None): ID of the user. Optionally a mention.
                If None is given, check the user itself.
        """
        assert ctx.guild is not None
        symbol_counter = await self.symbol_service.select_counter_by_ids(
            server_id=ctx.guild.id
        )

        if not symbol_counter:
            await ctx.send("This server doesn't have any counters set up!")
            return

        if not u_id:
            u_id = ctx.author.id

        user_id = get_mention(ctx, u_id)

        if not user_id:
            await ctx.send("Invalid id...")
            return

        user_counter = await self.symbol_service.select_user_counter_by_ids(
            server_id=ctx.guild.id, user_id=user_id
        )

        if not user_counter:
            await ctx.send(
                f"The current amount of {symbol_counter.symbol} sent by this user is 0."
            )
            return

        await ctx.send(
            f"The current amount of {symbol_counter.symbol} sent by "
            f"{user_counter.user_ref.user_name} in "
            f"<#{symbol_counter.channel_id}> is {user_counter.amount}."
        )

    @commands.command(aliases=["lb"])
    async def leaderboard(
        self, ctx: commands.Context[commands.Bot], limit: int = 10
    ) -> None:
        """Respons with the symbol counter leaderboard of the server.

        Args:
            limit (int, optional): Amount of leaderbord spots to fetch. Defaults to 10.
            Maximum 20.
        """
        assert ctx.guild is not None

        try:
            leaderboard = await self.symbol_service.leaderboard(
                server_id=ctx.guild.id, limit=limit
            )
        except LimitTooLargeError:
            await ctx.send("The maximum limit is 20!")
            return
        except SymbolNotSetupError:
            await ctx.send("This server does not have a counter set up!")
            return

        base_message = "## --- Leaderboard ---\n\n"

        for row in leaderboard:
            _, user_name, amount = row.tuple()
            base_message += f"{user_name}: {amount}"

        await ctx.send(base_message)

    @initialise.error
    async def _error(
        self, ctx: commands.Context[commands.Bot], error: discord.DiscordException
    ) -> None:
        """Error overload."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have the permissions to use this command.")
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send("Gwen did not find the specified channel!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Gwen is missing some information here! Be sure to check the "
                "help command `+counterhelp`!"
            )
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

    def cog_check(self, ctx: commands.Context[Any]) -> bool:
        return ctx.guild is not None
