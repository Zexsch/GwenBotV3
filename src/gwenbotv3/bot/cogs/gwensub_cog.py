from logging import Logger

from discord.ext import commands

from gwenbotv3.database import GwenSubHandler
from gwenbotv3.database.handlers.server_handler import ServerHandler
from gwenbotv3.database.get_context import context
from gwenbotv3.utils import get_user


class GwensubCog(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: Logger):
        self.bot = bot
        self.gwensub_handler = GwenSubHandler()
        self.server_handler = ServerHandler()
        self.logger = logger

    @commands.command(name="GwenAdd", aliases=["add"])
    async def gwen_add(self, ctx: commands.Context) -> None:
        """Command to add user to the subscribed database"""

        if ctx.guild is None:
            await ctx.send("Command must be used in a server.")
            return

        user_context = context(ctx)

        if self.gwensub_handler.fetch_blacklist(user_context):
            await ctx.send("You are blacklisted from using this function.")
            return

        server = self.server_handler.fetch_server(ctx)

        if server.quote:
            await ctx.send("The server has blocked this function.")
            return

        if self.gwensub_handler.fetch_sub(user_context):
            await ctx.send("You are already subscribed to GwenBot.")
            return

        self.gwensub_handler.add_sub(user_context)

        await ctx.send("Successfully subscribed to GwenBot.")
        self.logger.debug(f"Added user {ctx.author.id} to GwenSubs in guild {ctx.guild.id}")  # type: ignore

    @commands.command(name="remove", aliases=["gwenremove", "rem", "removesub"])
    async def gwen_remove(self, ctx: commands.Context) -> None:
        """Command to remove user from the subscribed database"""

        if ctx.guild is None:
            await ctx.send("Command must be used in a server.")
            return

        user_context = context(ctx)

        if self.gwensub_handler.fetch_blacklist(user_context):
            await ctx.send("You are blacklisted from using this function.")
            return

        if not self.gwensub_handler.fetch_sub(user_context):
            await ctx.send(
                "You are not currently subscribed to GwenBot.", ephemeral=True
            )
            return

        self.gwensub_handler.remove_sub(user_context)

        await ctx.send("Successfully removed from the GwenBot Subscription.")
        self.logger.debug(f"Removed user {ctx.author.id} from GwenSubs in guild {ctx.guild.id}")  # type: ignore

    @commands.command(name="checkgs", aliases=["checksub"])
    async def checkgs(
        self, ctx: commands.Context, user_id: str | int | None = None
    ) -> None:
        """Command to check if a user is subbed. +checkgs id[optional]"""

        if ctx.guild is None:
            await ctx.send("Command must be used in a server.")
            return

        user_context = context(ctx)

        if user_id is None:
            if self.gwensub_handler.fetch_sub(user_context):
                await ctx.send("You are subscribed.")
                return

            await ctx.send("You are not subscribed.")
            return

        user_id = get_user(ctx, user_id)

        if not user_id:
            await ctx.send("Invalid id...")
            return

        if self.gwensub_handler.fetch_sub_by_ids(user_id, ctx.guild.id):
            await ctx.send("User is subscribed.")
            return

        await ctx.send("User is not subscribed.")

    @commands.has_permissions(kick_members=True)
    @commands.command(name="quote")
    async def quote(self, ctx: commands.Context) -> None:
        """Command to add/undo Quote"""

        if ctx.guild is None:
            await ctx.send("Command must be used in a server.")
            return

        user_context = context(ctx)

        has_no_quote = self.server_handler.add_quote(user_context.server)

        if not has_no_quote:
            self.server_handler.remove_quote(user_context.server)
            await ctx.send("Gwen will now respond to chat.")
            self.logger.warning(f"Removed quote from guild {ctx.guild.id}")

            return

        self.logger.warning(f"Enabled quote in guild {ctx.guild.id}")
        await ctx.send("Gwen will no longer respond to chat.")

    @commands.command(name="modremove")
    @commands.has_permissions(kick_members=True)
    async def removesubmod(self, ctx: commands.Context, user_id) -> None:
        """Command to forcefully remove a user from the GwenBot subscription.
        Usable only by users with kick_members permissions."""

        if ctx.guild is None:
            await ctx.send("Command must be used in a server.")
            return

        id = get_user(ctx, user_id)

        if not id:
            await ctx.send("Invalid id...")
            return

        was_removed = self.gwensub_handler.remove_sub_by_ids(id, ctx.guild.id)

        if not was_removed:
            await ctx.send("User is not subscribed to GwenBot.")
            return

        self.logger.debug(
            f"Forcefully removed user {id} from GwenSub in guild {ctx.guild.id} by {ctx.author.id}"
        )
        await ctx.send("User removed from GwenBot subscription.")

    @commands.command(aliases=["bl"])
    @commands.has_permissions(kick_members=True)
    async def blacklist(self, ctx: commands.Context, user_id) -> None:
        """Command to add a user to the blacklist. Requires the user to have kick_members permissions."""

        if ctx.guild is None:
            await ctx.send("Command must be used in a server.")
            return

        user_id = get_user(ctx, user_id)

        if not user_id:
            await ctx.send("Invalid id...")
            return

        if self.gwensub_handler.fetch_blacklist_by_ids(user_id, ctx.guild.id):
            await ctx.send("User is already in blacklist.")
            return

        self.gwensub_handler.remove_sub_by_ids(user_id, ctx.guild.id)
        self.gwensub_handler.blacklist_by_ids(user_id, ctx.guild.id)

        await ctx.send("User successfully added to the Blacklist.")

        self.logger.debug(
            f"Blacklisted user {user_id} from GwenSub in guild {ctx.guild.id} by {ctx.author.id}"
        )

    @commands.command(
        name="blremove", aliases=["blr", "blacklistremove", "unblacklist", "unbl"]
    )
    @commands.has_permissions(kick_members=True)
    async def blremove(self, ctx: commands.Context, user_id) -> None:
        """Command to remove a user from the blacklist. Requires the user to have kick_members permissions."""

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

        self.gwensub_handler.remove_blacklist_by_ids(user_id, ctx.guild.id)

        await ctx.send("User successfully removed from the Blacklist.")

        self.logger.debug(
            f"Removed user {user_id} from blacklist in guild {ctx.guild.id} by {ctx.author.id}"
        )

    @commands.command(name="checkbl", aliases=["check", "checkblacklist"])
    async def checkbl(self, ctx: commands.Context, user_id=None) -> None:
        """Command to check if a user is blacklisted. +checkbl id[optional]"""

        if ctx.guild is None:
            await ctx.send("Command must be used in a server.")
            return

        if user_id is None:
            user_context = context(ctx)
            if self.gwensub_handler.fetch_blacklist(user_context):
                await ctx.send("You are Blacklisted.")
                return
            await ctx.send("You are not Blacklisted.")
            return

        user_id = get_user(ctx, user_id)

        if not user_id:
            await ctx.send("Invalid id...")
            return

        if self.gwensub_handler.fetch_blacklist_by_ids(user_id, ctx.guild.id):
            await ctx.send("User is Blacklisted.")
            return

        await ctx.send("User is not Blacklisted.")

    #  To add any permissions command error:
    #  Add @commands.has_permissions(permissions) before the command. Then add:
    #  @command.error
    #  To this command.

    @quote.error
    @removesubmod.error
    @blremove.error
    @blacklist.error
    async def _error(self, ctx: commands.Context, error) -> None:
        """Run if a user does not have the permissions necessary to run a command."""

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have the permissions to use this command.")
