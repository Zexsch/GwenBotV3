"""Houses the Privacy cog."""

import contextlib
import logging
from textwrap import dedent

from discord.ext import commands

from gwenbotv3.exceptions import (
    UserIsAnonymisedError,
    UserNotAnonymisedError,
    UserNotSubscribedError,
)
from gwenbotv3.services import GwenseekService, GwensubService, UserService


class PrivacyCog(commands.Cog):
    """Anything to do with user privacy, mostly anonymise and unanonymise."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.user_service = UserService()
        self.gwensub_service = GwensubService()
        self.gwenseek_service = GwenseekService()

    @commands.hybrid_command(
        aliases=["anonymize", "pseudonymise", "pseudonymize"],
        description="Remove your name from Gwen's database. See the privacy help command for more information.",
    )
    async def anonymise(self, ctx: commands.Context) -> None:
        """Anonymises a user.

        In practice, it is a pseudonymisation. It sets the user's name to Unknown user
            and prevents their username from ending up in the database again.
        This also removes all subscriptions and deepseek context.

        The user ID is kept for blacklists to work.
        """
        try:
            await self.user_service.anonymise_user(user_id=ctx.author.id)
        except UserIsAnonymisedError:
            await ctx.send("You are already anonymised!")
            return

        with contextlib.suppress(UserNotSubscribedError):
            await self.gwensub_service.delete_all_subs(user_id=ctx.author.id)

        await self.gwenseek_service.delete_all_seeks(user_id=ctx.author.id)

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

    @commands.hybrid_command(
        aliases=[
            "deanonymize",
            "deanonymise",
            "unpseudonymise",
            "depseudonymise",
            "depseudonymize",
            "unpseudonymize",
        ],
        description="Unanonymise yourself. See the privacy help command for more information.",
    )
    async def unanonymise(self, ctx: commands.Context) -> None:
        """Unanonymises a user. Puts their username back into the database."""

        try:
            await self.user_service.unanonymise_user(
                user_id=ctx.author.id, user_name=ctx.author.name
            )
        except UserNotAnonymisedError:
            await ctx.send("You are not anonymised!")
            return

        self.logger.info("Unanonymised user=%s", ctx.author.id)

        await ctx.send("You were successfully unpseudonymised.")
