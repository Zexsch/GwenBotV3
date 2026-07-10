import logging

from discord.ext import commands

from gwenbotv3.database import GwenSubHandler, SymbolHandler, DatabaseHandler
from gwenbotv3.utils import get_user


class OwnerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.gwensub_handler = GwenSubHandler()
        self.symbol_handler = SymbolHandler()
        self.database_handler = DatabaseHandler()
        self.logger = logging.getLogger(__name__)

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

        self.logger.info(
            "Added to blacklist by owner: user=%s, server=%s",
            ctx.author.id,
            ctx.guild.id,
        )
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

        self.gwensub_handler.remove_blacklist_by_ids(
            user_id, ctx.guild.id, by_owner=True
        )
        self.logger.info(
            "Removed from blacklist by owner: user=%s, server=%s",
            ctx.author.id,
            ctx.guild.id,
        )
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
        self.logger.info(
            "Removed from subs by owner: user=%s, server=%s",
            ctx.author.id,
            ctx.guild.id,
        )
        await ctx.send("User removed from GwenBot subscription.")

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx: commands.Context) -> None:
        await ctx.send("Shutting down!")

        self.logger.critical("Bot shut down forcefully!")

        await self.bot.close()

    @commands.command()
    @commands.is_owner()
    async def modify(self, ctx: commands.Context) -> None:
        self.database_handler.modify_db()
        await ctx.send("Ran modify script.")

    @modify.error
    @unfuckyou.error
    @fuckyou.error
    @fuckyouremove.error
    @shutdown.error
    async def _not_owner(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CheckFailure):
            self.logger.info(
                "Some idiot tried running my command. user=%s, username=%s",
                ctx.author.id,
                ctx.author.name,
            )
            await ctx.send("Who do you think you are...")
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
