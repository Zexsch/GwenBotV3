import logging
from discord.ext import commands

from gwenbotv3.database.handlers.user_handler import UserHandler
from gwenbotv3.database.get_context import context
from gwenbotv3.database import GwenSubHandler, GwenseekHandler
from gwenbotv3.database._models.exceptions import UserNotAnonymised


class PrivacyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.user_handler = UserHandler()
        self.gwensub_handler = GwenSubHandler()
        self.gwenseek_handler = GwenseekHandler()

    @commands.command(aliases=["anonymize", "pseudonymise", "pseudonymize"])
    async def anonymise(self, ctx: commands.Context) -> None:
        if not ctx.guild:
            await ctx.send("Command must be used in a server!")

        user_context = context(ctx)

        self.user_handler.anonymise_user(ctx)
        self.gwensub_handler.remove_sub(user_context)
        self.gwenseek_handler.clear_all_context(user_context)

        return_message = (
            "Gwen has done the following:\n"
            + "> Deleted your username from her database!\n"
            + "> Made sure that your username does not end up in the database "
            + "again until you unanonymise through +unanonymise!\n"
            + "> Cleared all your active GwenBot subscriptions!\n"
            + "> Cleared all your Gwenseek history!\n\n"
            + "Gwen holds logs for at most 3 months before they're deleted!\n"
            + "Your username may still be found in these logs.\n\n"
            + "What gwen has not done:\n"
            + "> Deleted your discord ID. This is necessary to keep blacklists working "
            + "and can't be deleted! :(\n\n"
            + "Snip Snip!"
        )

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
    async def unanonymise(self, ctx: commands.Context) -> None:
        if not ctx.guild:
            await ctx.send("Command must be used in a server!")

        try:
            self.user_handler.deanonymise_user(ctx)
        except UserNotAnonymised:
            await ctx.send("You are not pseudonymised!")
            return

        self.logger.info("Unanonymised user=%s", ctx.author.id)

        await ctx.send("You were successfully unpseudonymised.")
