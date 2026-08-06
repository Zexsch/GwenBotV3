"""Houses the Gwensub cog."""

import contextlib
import logging
import sys
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

from gwenbotv3.exceptions import UserNotSubscribedError
from gwenbotv3.services import GwensubService, ServerService
from gwenbotv3.utils import get_mention


class GwensubCog(commands.Cog):
    """Anything to do with gwenbot subscription.

    For the actual gwen response, see listener_cog."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.gwensub_service = GwensubService()
        self.server_service = ServerService()
        self.logger = logging.getLogger()

    @commands.hybrid_command(
        name="gwenadd",
        aliases=["gwen_add"],
        description="Subscribe to GwenBot and life gets better!",
    )
    async def add(self, ctx: commands.Context) -> None:
        """Command to add user to the subscribed database"""
        assert ctx.guild is not None

        server = await self.server_service.select_server(server_id=ctx.guild.id)

        assert server is not None  # Should technically never trigger

        if server.quote:
            await ctx.send("The server has blocked this function.")
            return

        if await self.gwensub_service.select_any_blacklist_by_ids(
            user_id=ctx.author.id, server_id=ctx.guild.id
        ):
            await ctx.send("You are blacklisted from using this function.")
            return

        if await self.gwensub_service.select_sub_by_ids(
            user_id=ctx.author.id, server_id=ctx.guild.id
        ):
            await ctx.send("You are already subscribed to GwenBot.")
            return

        await self.gwensub_service.insert_sub(
            user_id=ctx.author.id, server_id=ctx.guild.id
        )

        await ctx.send("Successfully subscribed to GwenBot.")

    @commands.hybrid_command(
        name="remove",
        aliases=["gwenremove", "rem", "removesub", "gwen_remove"],
        description="Remove your subscription from GwenBot.",
    )
    async def remove(self, ctx: commands.Context) -> None:
        """Command to remove user from the subscribed database"""
        assert ctx.guild is not None

        if await self.gwensub_service.select_any_blacklist_by_ids(
            user_id=ctx.author.id, server_id=ctx.guild.id
        ):
            await ctx.send("You are blacklisted from using this command.")
            return

        if not await self.gwensub_service.select_sub_by_ids(
            user_id=ctx.author.id, server_id=ctx.guild.id
        ):
            await ctx.send(
                "You are not currently subscribed to GwenBot.", ephemeral=True
            )
            return

        await self.gwensub_service.delete_sub(
            user_id=ctx.author.id, server_id=ctx.guild.id
        )

        await ctx.send("Successfully removed from the GwenBot Subscription.")

    @commands.hybrid_command(name="checkgs", aliases=["checksub"])
    async def checkgs(self, ctx: commands.Context, user_id: str | None = None) -> None:
        """Command to check if a user is subbed. +checkgs id[optional]"""
        assert ctx.guild is not None

        if user_id is None:
            if await self.gwensub_service.select_sub_by_ids(
                user_id=ctx.author.id, server_id=ctx.guild.id
            ):
                await ctx.send("You are subscribed.")
                return

            await ctx.send("You are not subscribed.")
            return

        u_id = get_mention(ctx, user_id)

        if not u_id:
            await ctx.send("Invalid id...")
            return

        if await self.gwensub_service.select_sub_by_ids(
            user_id=u_id, server_id=ctx.guild.id
        ):
            await ctx.send("User is subscribed.")
            return

        await ctx.send("User is not subscribed.")

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="quote")
    async def quote(self, ctx: commands.Context) -> None:
        """Command to add/undo Quote."""
        assert ctx.guild is not None

        server = await self.server_service.select_server(server_id=ctx.guild.id)

        assert server is not None

        if server.quote:
            await self.server_service.update_server(server_id=ctx.guild.id, quote=False)
            await ctx.send("Gwen will now respond to chat.")
            return

        await self.server_service.update_server(server_id=ctx.guild.id, quote=True)
        await ctx.send("Gwen will no longer respond to chat.")

    @commands.hybrid_command(name="modremove")
    @commands.has_permissions(kick_members=True)
    async def removesubmod(
        self, ctx: commands.Context, user_id: str | None = None
    ) -> None:
        """Command to forcefully remove a user from the GwenBot subscription.
        Usable only by users with kick_members permissions."""
        assert ctx.guild is not None
        assert user_id is not None

        u_id = get_mention(ctx, user_id)

        if not u_id:
            await ctx.send("Invalid id...")
            return

        try:
            await self.gwensub_service.delete_sub(user_id=u_id, server_id=ctx.guild.id)
        except UserNotSubscribedError:
            await ctx.send("User is not subscribed!")
            return

        await ctx.send("User removed from GwenBot subscription.")

    @commands.hybrid_command(aliases=["bl"])
    @commands.has_permissions(kick_members=True)
    @app_commands.describe(
        user_id="ID of the user. Mentions are not supported with slash commands!"
    )
    async def blacklist(
        self, ctx: commands.Context, user_id: str | None = None
    ) -> None:
        """Command to add a user to the blacklist.
        Usable only by users with kick_members permissions."""
        assert ctx.guild is not None
        assert user_id is not None

        u_id = get_mention(ctx, user_id)

        if not u_id:
            await ctx.send("Invalid id...")
            return

        if await self.gwensub_service.select_blacklist_by_ids(
            user_id=u_id, server_id=ctx.guild.id
        ):
            await ctx.send("User is already blacklisted.")
            return

        if await self.gwensub_service.select_blacklist_by_ids(
            user_id=u_id, server_id=ctx.guild.id, by_owner=True
        ):
            await ctx.send("User was blacklisted by the bot owner.")
            return

        await self.gwensub_service.select_sub_by_ids(
            user_id=u_id, server_id=ctx.guild.id
        )

        with contextlib.suppress(UserNotSubscribedError):
            await self.gwensub_service.delete_sub(user_id=u_id, server_id=ctx.guild.id)

        await ctx.send("User successfully added to the Blacklist.")

    @commands.hybrid_command(
        name="unblacklist", aliases=["blr", "blacklistremove", "blremove", "unbl"]
    )
    @commands.has_permissions(kick_members=True)
    @app_commands.describe(
        user_id="ID of the user. Mentions are not supported with slash commands!"
    )
    async def unblacklist(
        self, ctx: commands.Context, user_id: str | None = None
    ) -> None:
        """Command to remove a user from the blacklist.
        Usable only by users with kick_members permissions."""

        assert ctx.guild is not None
        assert user_id is not None

        u_id = get_mention(ctx, user_id)

        if not u_id:
            await ctx.send("Invalid id...")
            return

        if not await self.gwensub_service.select_blacklist_by_ids(
            user_id=u_id, server_id=ctx.guild.id
        ):
            await ctx.send("User is not Blacklisted.")
            return

        await self.gwensub_service.delete_blacklist(
            user_id=u_id, server_id=ctx.guild.id
        )

        await ctx.send("User successfully removed from the Blacklist.")

    @commands.hybrid_command(name="checkbl", aliases=["check", "checkblacklist"])
    async def checkbl(self, ctx: commands.Context, user_id: str | None = None) -> None:
        """Command to check if a user is blacklisted. +checkbl id[optional]"""

        assert ctx.guild is not None

        if user_id is None:
            if await self.gwensub_service.select_blacklist_by_ids(
                user_id=ctx.author.id, server_id=ctx.guild.id
            ):
                await ctx.send("You are Blacklisted.")
                return
            await ctx.send("You are not Blacklisted.")
            return

        u_id = get_mention(ctx, user_id)

        if not u_id:
            await ctx.send("Invalid id...")
            return

        if await self.gwensub_service.select_blacklist_by_ids(
            user_id=u_id, server_id=ctx.guild.id
        ):
            await ctx.send("User is Blacklisted.")
            return

        await ctx.send("User is not Blacklisted.")

    @quote.error
    @removesubmod.error
    @unblacklist.error
    @blacklist.error
    async def _error(
        self, ctx: commands.Context[commands.Bot], error: discord.DiscordException
    ) -> None:
        """Run if a user does not have the permissions necessary to run a command."""

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "Oh no! You do not have the permissions to use this command~"
            )
            return

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
