import discord
from discord.ext import commands

from gwenbotv3.database._models.exceptions import AmountNotInt
from gwenbotv3.database import (
    SymbolHandler,
    UserContext,
)
from gwenbotv3.database.get_context import context
from gwenbotv3.database.handlers.user_handler import UserHandler
from gwenbotv3.database.handlers.server_handler import ServerHandler
from gwenbotv3.database._models.exceptions import LimitTooHigh
from gwenbotv3.utils import get_user


class LeaderboardCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.symbol_handler = SymbolHandler()
        self.user_handler = UserHandler()
        self.server_handler = ServerHandler()

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def initialise(
        self, ctx: commands.Context, symbol: str, channel: discord.TextChannel
    ):
        user_context = context(ctx)

        self.symbol_handler.initialise(user_context, symbol, channel.id)

        await ctx.send(
            f"Initialisation complete for channel {channel.name}, symbol {symbol}"
        )

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def recount(self, ctx: commands.Context):
        if not ctx.guild:
            await ctx.send("Command has to be used in a server!")
            return

        await ctx.send("Gwen is recounting. This might take a while.")

        user_context = context(ctx)

        channel = self.symbol_handler.fetch_channel(user_context)

        channel_object = self.bot.get_channel(channel)

        if not isinstance(channel_object, discord.TextChannel):
            await ctx.send(
                "It seems like the initialised channel is not a text channel... "
                "how is this even possible?"
            )
            return

        async for message in channel_object.history(limit=None):
            user = self.user_handler.fetch_user_by_id(message.author.id)

            if not user:
                user = self.user_handler.insert_user_by_id(
                    message.author.id, message.author.name
                )

            counting_user_context = UserContext(
                user=user, server=user_context.server, message="", ctx=ctx
            )

            self.symbol_handler.update(counting_user_context)

        await ctx.send(f"Gwen has finished counting! <@{ctx.author.id}>")

    @commands.command(
        aliases=[
            "question",
            "amount",
            "qm",
            "qms",
            "questionmarks",
            "questionmark",
            "?",
        ]
    )
    async def questions(self, ctx: commands.Context):
        if not ctx.guild:
            await ctx.send("Command must be used in a server!")

        user_context = context(ctx)

        try:
            amount = self.symbol_handler.fetch_amount(user_context)
        except AmountNotInt:
            await ctx.send("Oh no! It seems like gwen ran into some issues!")
            return

        await ctx.send(f"The current amount of question marks is {amount}.")

    @commands.command(
        aliases=[
            "question_user",
            "amount_user",
            "qm_user",
            "qms_user",
            "questionmarks_user",
            "questionmark_user",
            "?_u",
            "?u",
        ]
    )
    async def questions_user(self, ctx: commands.Context, id):
        if not ctx.guild:
            await ctx.send("Command must be used in a server!")
            return

        user_id = get_user(ctx, id)

        if not user_id:
            await ctx.send("Invalid id...")
            return

        user = self.user_handler.fetch_user_by_id(id)

        if not user:
            await ctx.send("User has not interacted with Gwen before!")
            return

        server = self.server_handler.fetch_server_by_id(ctx.guild.id)

        if not server:
            await ctx.send("This is odd... Gwen doesn't know this server at all??")
            return

        user_context = UserContext(user=user, server=server, message="", ctx=ctx)

        amount = self.symbol_handler.fetch_user_amount(user_context)
        symbol = self.symbol_handler.fetch_symbol(user_context)
        channel = self.symbol_handler.fetch_channel(user_context)

        if not user_context.user:
            return  # Should never fire but linter's complaining

        await ctx.send(
            f"The current amount of {symbol} sent by {user_context.user.id} in <#{channel}> is {amount}."
        )

    @commands.command(aliases=["lb"])
    async def leaderboard(self, ctx: commands.Context, limit: int = 10):
        if not ctx.guild:
            await ctx.send("Command has to be used in a server!")
            return

        user_context = context(ctx)

        try:
            lb = self.symbol_handler.fetch_lb(user_context, limit=limit)
        except LimitTooHigh:
            await ctx.send("The current maximum leaderboard length limit is 20!")
            return

        if not lb:
            await ctx.send("This server doesn't have any symbol counters set up!")
            return

        base_message = "--- Leaderboard ---\n\n"

        for res in lb:
            base_message += f"{res[0].name} - {res[1]}\n"

        await ctx.send(base_message)

    @initialise.error
    async def _error(self, ctx: commands.Context, error) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have the permissions to use this command.")
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send("Gwen did not find the specified channel!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Gwen is missing some information here! Be sure to check the help command!"
            )
        else:
            original = getattr(error, "original", error)
            print(f"Unhandled error: {type(original).__name__}: {original}")
            import traceback
            traceback.print_exception(type(original), original, original.__traceback__)
            await ctx.send(
                "Gwen ran into some issues whilst performing this command!"
            )
