"""Houses the owner cog."""

import logging

import discord
from discord.ext import commands

from gwenbotv3.services import GwensubService
from gwenbotv3.utils import get_mention


class OwnerCog(commands.Cog):
    """Any commands that only the bot owner should be able to execute go in here."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.gwensub_service = GwensubService()
        self.logger = logging.getLogger(__name__)

    #  These 2 commands make it so that the owner of the bot can always add or
    #  remove users from the blacklist.
    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def fuckyou(
        self, ctx: commands.Context[commands.Bot], user_id: int | str | None
    ) -> None:
        """Adds a user to the blacklist in a specific server.

        Unlike ModerationCog's blacklist command, this command will set
        by_owner to true.

        Args:
            ctx (commands.Context): Discord Context.
            user_id (_type_): ID of the user to be blacklisted.
        """
        assert ctx.guild is not None

        if user_id is None:
            await ctx.send("How could you have forgotten...")
            return

        user_id = get_mention(ctx, user_id)

        if not user_id:
            await ctx.send("Invalid id...")
            return

        if await self.gwensub_service.select_blacklist_by_ids(
            user_id=user_id, server_id=ctx.guild.id, by_owner=True
        ):
            await ctx.send("User is already blacklisted.")
            return

        await self.gwensub_service.insert_blacklist(
            user_id=user_id, server_id=ctx.guild.id, by_owner=True
        )
        await self.gwensub_service.delete_sub(user_id=user_id, server_id=ctx.guild.id)

        self.logger.info(
            "Added to blacklist by owner: user=%s, server=%s",
            ctx.author.id,
            ctx.guild.id,
        )
        await ctx.send("User added to the Blacklist.")

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def unfuckyou(
        self, ctx: commands.Context[commands.Bot], user_id: str | int | None
    ) -> None:
        """Removes a user from the blacklist in a specific server.

        Unlike ModerationCog's unblacklist command, this command removes
        the blacklist row where by_owner is set to true.

        Args:
            ctx (commands.Context): Discord Context.
            user_id (_type_): ID of the user to be unblacklisted.
        """
        assert ctx.guild is not None

        if not user_id:
            await ctx.send("How could you have forgotten...")
            return

        user_id = get_mention(ctx, user_id)

        if not user_id:
            await ctx.send("Invalid id...")
            return

        if not await self.gwensub_service.select_blacklist_by_ids(
            user_id=user_id, server_id=ctx.guild.id, by_owner=True
        ):
            await ctx.send("User is not Blacklisted.")
            return

        await self.gwensub_service.delete_blacklist(
            user_id=user_id, server_id=ctx.guild.id, by_owner=True
        )

        self.logger.info(
            "Removed from blacklist by owner: user=%s, server=%s",
            ctx.author.id,
            ctx.guild.id,
        )
        await ctx.send("User removed from the Blacklist.")

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def fuckyouremove(
        self, ctx: commands.Context[commands.Bot], user_id: str | int | None
    ) -> None:
        """Removes a person from GwenSubs. Only usable by Owner."""
        assert ctx.guild is not None

        if not user_id:
            await ctx.send("How could you have forgotten...")
            return

        user_id = get_mention(ctx, user_id)

        if not user_id:
            await ctx.send("Invalid id...")
            return

        if not await self.gwensub_service.select_sub_by_ids(
            user_id=user_id, server_id=ctx.guild.id
        ):
            await ctx.send("User is not subscribed to GwenBot.")
            return

        await self.gwensub_service.delete_sub(user_id=user_id, server_id=ctx.guild.id)

        self.logger.info(
            "Removed from subs by owner: user=%s, server=%s",
            ctx.author.id,
            ctx.guild.id,
        )
        await ctx.send("User removed from GwenBot subscription.")

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx: commands.Context[commands.Bot]) -> None:
        """Shuts down the bot in case of emergency."""
        await ctx.send("Shutting down!")

        self.logger.critical("Bot shut down forcefully!")

        await self.bot.close()

    @unfuckyou.error
    @fuckyou.error
    @fuckyouremove.error
    @shutdown.error
    async def _not_owner(
        self, ctx: commands.Context[commands.Bot], error: discord.DiscordException
    ) -> None:
        """Overloads the bot's error handling."""
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
