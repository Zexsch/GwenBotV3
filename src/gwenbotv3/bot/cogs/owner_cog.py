from logging import Logger

from discord.ext import commands

from gwenbotv3.database import GwenSubHandler, SymbolHandler
from gwenbotv3.database.get_context import context
from gwenbotv3.utils import get_user


class OwnerCog(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: Logger):
        self.bot = bot
        self.gwensub_handler = GwenSubHandler()
        self.symbol_handler = SymbolHandler()
        self.logger = logger

    #  These 2 commands make it so that the owner of the bot can always add and remove users from the blacklist.
    @commands.command()
    @commands.is_owner()
    async def fuckyou(self, ctx: commands.Context, user_id) -> None:
        """Alternative to +blacklist. Instead of permissions this requires the sender to be the owner of the bot.
        Change OWNER_ID in Config.config to your ID."""

        if ctx.guild is None:
            await ctx.send("Command must be used in a server.")
            return

        user_id = get_user(ctx, user_id)

        if not user_id:
            await ctx.send("Invalid id...")
            return

        if self.gwensub_handler.fetch_blacklist_by_ids(user_id, ctx.guild.id):
            await ctx.send("User is already blacklisted.")
            return

        self.gwensub_handler.blacklist_by_ids(user_id, ctx.guild.id, by_owner=True)
        self.gwensub_handler.remove_sub_by_ids(user_id, ctx.guild.id)

        self.logger.info(f"User {user_id} was added to the blacklist by owner.")
        await ctx.send("User added to the Blacklist.")

    @commands.command()
    @commands.is_owner()
    async def unfuckyou(self, ctx: commands.Context, user_id) -> None:
        """Alternative to +blremove. Instead of permissions this requires the sender to be the owner of the bot.
        Change OWNER_ID in Config.config to your ID."""

        if ctx.guild is None:
            await ctx.send("Command must be used in a server.")
            return

        user_id = get_user(ctx, user_id)

        if not user_id:
            await ctx.send("Invalid id...")
            return

        if not self.gwensub_handler.fetch_blacklist_by_ids(user_id, ctx.guild.id):
            await ctx.send("User is not Blacklisted.")
            return

        self.gwensub_handler.remove_blacklist_by_ids(user_id, ctx.guild.id, by_owner=True)
        self.logger.info(f"User {user_id} was removed from the blacklist by owner.")
        await ctx.send("User removed from the Blacklist.")

    @commands.command()
    @commands.is_owner()
    async def fuckyouremove(self, ctx: commands.Context, user_id) -> None:
        """Removes a person from GwenSubs. Only usable by Owner."""

        if ctx.guild is None:
            await ctx.send("Command must be used in a server.")
            return

        user_id = get_user(ctx, user_id)

        if not user_id:
            await ctx.send("Invalid id...")
            return

        if not self.gwensub_handler.fetch_sub_by_ids(user_id, ctx.guild.id):
            await ctx.send("User is not subscribed to GwenBot.")
            return

        self.gwensub_handler.remove_sub_by_ids(user_id, ctx.guild.id)
        self.logger.info(f"User {user_id} was removed from gwensubs by owner.")
        await ctx.send("User removed from GwenBot subscription.")

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx: commands.Context) -> None:
        await ctx.send("Shutting down!")

        self.logger.critical("Bot shut down forcefully!")

        await self.bot.close()

    @commands.command()
    @commands.is_owner()
    async def set_questions(self, ctx: commands.Context, amount: int) -> None:
        user_context = context(ctx)

        self.symbol_handler.set_amount(user_context, amount)

        await ctx.send(f"Setting amount to {amount}.")
        self.logger.info(f"Setting question mark count to {amount}.")

    @set_questions.error
    @unfuckyou.error
    @fuckyou.error
    @fuckyouremove.error
    @shutdown.error
    async def _not_owner(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CheckFailure):
            await ctx.send("Who do you think you are...")
