"""Houses the Privacy cog."""

import logging
from textwrap import dedent

from discord.ext import commands

from gwenbotv3.database import GwenseekHandler, GwenSubHandler
from gwenbotv3.database._models.exceptions import UserNotAnonymised
from gwenbotv3.database.get_context import context
from gwenbotv3.database.handlers.user_handler import UserHandler


class PrivacyCog(commands.Cog):
    """Anything to do with user privacy, mostly anonymise and unanonymise."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.user_handler = UserHandler()
        self.gwensub_handler = GwenSubHandler()
        self.gwenseek_handler = GwenseekHandler()

    @commands.command(aliases=["anonymize", "pseudonymise", "pseudonymize"])
    async def anonymise(self, ctx: commands.Context[commands.Bot]) -> None:
        """Anonymises a user.

        In practice, it is a pseudonymisation. It sets the user's name to Unknown user
            and prevents their username from ending up in the database again.
        This also removes all subscriptions and deepseek context.

        The user ID is kept for blacklists to work."""

        if not ctx.guild:
            await ctx.send("Command must be used in a server!")
            return

        user_context = context(ctx)

        self.user_handler.anonymise_user(ctx)
        self.gwensub_handler.remove_all_sub(user_context)
        self.gwenseek_handler.clear_all_context(user_context)

        # ruff: noqa: E501
        # pylint: disable=line-too-long
        return_message = dedent("""\
        Gwen has done the following:
        > Deleted your username from her database!
        > Made sure that your username does not end up in the database again until you unanonymise through +unanonymise!
        > Cleared all your active GwenBot subscriptions!
        > Cleared all your gwenseek history!

        Gwen holds logs for at most 3 months before they're deleted!
        Your username may still be found in these logs.

        What gwen has not done:
        > Deleted your discord ID. This is necessary to keep blacklists working and can't be deleted! :(

        Snip Snip!
        """)

        self.logger.info("Anonymised user=%s", ctx.author.id)

        await ctx.send(return_message)

    @commands.command(
        aliases=[
            "deanonymize",
            "deanonymise",
            "unpseudonymise",
            "depseudonymise",
            "depseudonymize",
            "unpseudonymize",
        ]
    )
    async def unanonymise(self, ctx: commands.Context[commands.Bot]) -> None:
        """Unanonymises a user. Puts their username back into the database."""
        if not ctx.guild:
            await ctx.send("Command must be used in a server!")
            return

        try:
            self.user_handler.deanonymise_user(ctx)
        except UserNotAnonymised:
            await ctx.send("You are not pseudonymised!")
            return

        self.logger.info("Unanonymised user=%s", ctx.author.id)

        await ctx.send("You were successfully unpseudonymised.")
