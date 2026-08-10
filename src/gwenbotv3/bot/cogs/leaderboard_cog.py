"""Houses the leaderboard cog."""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import discord
from discord import Interaction, app_commands
from discord.ext import commands

from gwenbotv3.database.models import SymbolCounter
from gwenbotv3.exceptions import (
    LimitTooLargeError,
    SymbolAlreadySetupError,
    SymbolNotSetupError,
)
from gwenbotv3.services import SymbolService, UserService
from gwenbotv3.utils import confirm, get_mention


class LeaderboardCog(commands.Cog):
    """Anything to do with the symbol counter."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.symbol_service = SymbolService()
        self.user_service = UserService()
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        aliases=["initialize"],
        description="Initialise a counter. See the help command for more information.",
    )
    @commands.has_permissions(kick_members=True)
    @discord.app_commands.describe(
        symbol="The symbol to start counting.",
        channel="The channel to start counting in.",
        strict="Enables strictness. Once set, also requires a strict channel.",
        strict_channel="Channel for mentions on rule breaks.",
    )
    async def initialise(
        self,
        ctx: commands.Context,
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
            return
        except SymbolAlreadySetupError:
            await ctx.send("This server already has a counter set up!")
            return

        await ctx.send(
            f"Initialisation complete for channel {channel.name}, symbol {symbol}"
        )

    @app_commands.command(
        name="uninitialise",
        description="Deletes the server's counter and all information stored for it.",
    )  # type: ignore
    @confirm(
        message=(
            "Are you sure you want to uninitialise? "
            "You will need to recount if you initialise again."
        )
    )
    async def uninitialise(self, interaction: Interaction) -> None:
        assert interaction.guild is not None

        try:
            await self.symbol_service.delete_all_user_counters(
                server_id=interaction.guild.id
            )
            await self.symbol_service.delete_all_ping_users(
                server_id=interaction.guild.id
            )
            await self.symbol_service.delete_counter(server_id=interaction.guild.id)
        except SymbolNotSetupError:
            await interaction.followup.send("This server has no counter set up!")
            return

        await interaction.followup.send("Successfully deleted the counter.")

    @commands.hybrid_command(
        description=(
            "Flips your counter's strictness. "
            "See the help command for more information."
        )
    )
    @commands.has_permissions(kick_members=True)
    async def strict(self, ctx: commands.Context) -> None:
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

    async def _check_last_recount(self, counter: SymbolCounter) -> bool:
        if counter.last_recount is None:
            return False

        since_last_recount = datetime.now(UTC) - counter.last_recount

        return since_last_recount <= timedelta(hours=24)

    @commands.hybrid_command()
    @commands.has_permissions(kick_members=True)
    async def recount(self, ctx: commands.Context) -> None:
        """Recounts the symbols sent in the initialised channel. Has a 24h cooldown!"""
        assert ctx.guild is not None

        counter = await self.symbol_service.select_counter_by_ids(
            server_id=ctx.guild.id
        )

        if not counter:
            await ctx.send("This server doesn't have a symbol counter set up!")
            return

        last_recount_check = await self._check_last_recount(counter=counter)

        if last_recount_check:
            await ctx.send("You may only recount every 24 hours!")
            return

        channel_object = self.bot.get_channel(counter.channel_id)

        if not isinstance(channel_object, discord.TextChannel):
            await ctx.send(
                "It seems like the initialised channel is not a text channel... "
                "how is this even possible?"
            )
            return

        await self.symbol_service.update_last_recount(server_id=ctx.guild.id)

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

    @commands.hybrid_command(
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
    async def amount(self, ctx: commands.Context) -> None:
        """Fetches the amount of symbols sent in the counter."""
        assert ctx.guild is not None

        counter = await self.symbol_service.select_counter_by_ids(
            server_id=ctx.guild.id
        )

        if not counter:
            await ctx.send("This server doesn't have any counters set up!")
            return

        await ctx.send(f"The current amount is {counter.amount}!")

    @commands.hybrid_command(
        aliases=[
            "question_user",
            "questions_user",
            "qm_user",
            "qms_user",
            "questionmarks_user",
            "questionmark_user",
            "?_u",
            "?u",
        ],
        description="Checks the amoutn of symbols sent by a user.",
    )
    async def amount_user(
        self, ctx: commands.Context, user_id: str | None = None
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

        if not user_id:
            user_id = str(ctx.author.id)  # lmao.

        u_id = get_mention(ctx, user_id)

        if not u_id:
            await ctx.send("Invalid id...")
            return

        user_counter = await self.symbol_service.select_user_counter_by_ids(
            server_id=ctx.guild.id, user_id=u_id
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

    @commands.hybrid_command(
        description="Make yourself be pinged when the counter's rules are broken."
    )
    @commands.has_permissions(kick_members=True)
    async def ping(self, ctx: commands.Context) -> None:
        assert ctx.guild is not None

        symbol_counter = await self.symbol_service.select_counter_by_ids(
            server_id=ctx.guild.id
        )

        if not symbol_counter:
            await ctx.send("This server doesn't have any counters set up!")
            return

        ping_user_check = await self.symbol_service.select_ping_user_by_ids(
            server_id=ctx.guild.id, user_id=ctx.author.id
        )

        if ping_user_check is not None:
            await ctx.send("You are already being pinged!")
            return

        await self.symbol_service.insert_ping_user(
            server_id=ctx.guild.id, user_id=ctx.author.id
        )

        self.logger.debug(
            "Added user=%s to ping users in server=%s", ctx.guild.id, ctx.author.id
        )

        await ctx.send("Added you to the list of users to be pinged!")

    @commands.hybrid_command(description="Remove yourself from the list of pings.")
    @commands.has_permissions(kick_members=True)
    async def unping(self, ctx: commands.Context) -> None:
        assert ctx.guild is not None

        symbol_counter = await self.symbol_service.select_counter_by_ids(
            server_id=ctx.guild.id
        )

        if not symbol_counter:
            await ctx.send("This server doesn't have any counters set up!")
            return

        ping_user_check = await self.symbol_service.select_ping_user_by_ids(
            server_id=ctx.guild.id, user_id=ctx.author.id
        )

        if ping_user_check is None:
            await ctx.send("You are not being pinged!")
            return

        await self.symbol_service.delete_ping_user_by_ids(
            server_id=ctx.guild.id, user_id=ctx.author.id
        )

        self.logger.debug(
            "Removed user=%s from ping users in server=%s", ctx.guild.id, ctx.author.id
        )

        await ctx.send("You will no longer be pinged!")

    @commands.hybrid_command(
        aliases=["lb"], description="Replies with the leaderboard for counter."
    )
    @app_commands.describe(limit="The length of the leaderboard. It can at most be 20.")
    async def leaderboard(self, ctx: commands.Context, limit: int = 10) -> None:
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
            base_message += f"**{user_name}** - {amount}\n"

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
