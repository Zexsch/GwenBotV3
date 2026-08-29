"""The main module for the discord app itself."""

import logging
import os
import sys
from typing import Any, Self

import discord
from aiohttp import ClientSession
from discord import app_commands
from discord.ext import commands

from gwenbotv3.bot.winrate import WinrateFetcher
from gwenbotv3.config import (
    OWNER_ID,
    PREFIX,
)
from gwenbotv3.exceptions import (
    NoViewError,
    ServerIdNotGivenError,
    UserIdOrNameNotGivenError,
)
from gwenbotv3.services import (
    DatabaseService,
    PrivacyService,
    ServerService,
    UserService,
)


# pylint: disable=arguments-differ, too-many-instance-attributes
class App(commands.Bot):
    """The app itself. This will run all cogs and handle generic discord errors."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=None,
            owner_id=OWNER_ID,
            case_insensitive=True,
        )

        self.logger = logging.getLogger(__name__)
        self.user_service = UserService()
        self.server_service = ServerService()
        self.database_service = DatabaseService()
        self.privacy_service = PrivacyService()
        self.aiohttp_session = ClientSession()

        self.prefix_cache: dict[int, str] = {}
        self.private_users: list[int] = []

    async def setup_hook(self) -> None:
        self.before_invoke(self.dispatch_before_hooks)
        self.after_invoke(self.after_hook)
        self.register_app_command_error()
        await self.get_private_users()

        await self.database_service.purge_stale_users()

        from gwenbotv3.bot.cogs import (
            CommandsCog,
            DeepseekCog,
            DMCog,
            GwensubCog,
            HelpCog,
            LeaderboardCog,
            ListenerCog,
            ModerationCog,
            OwnerCog,
            PrivacyCog,
            WinrateCog,
        )

        self.winrate_fetcher = await WinrateFetcher.create(session=self.aiohttp_session)

        self.logger.info("Initialising cogs.")
        await self.add_cog(ListenerCog(bot=self))
        await self.add_cog(GwensubCog(bot=self))
        await self.add_cog(OwnerCog(bot=self))
        await self.add_cog(DMCog(bot=self, winrate_fetcher=self.winrate_fetcher))
        await self.add_cog(CommandsCog(bot=self))
        await self.add_cog(LeaderboardCog(bot=self))
        await self.add_cog(DeepseekCog(bot=self))
        await self.add_cog(ModerationCog(bot=self))
        await self.add_cog(PrivacyCog(bot=self))
        await self.add_cog(HelpCog(bot=self))
        await self.add_cog(WinrateCog(bot=self, winrate_fetcher=self.winrate_fetcher))
        self.logger.info("Finished initialising cogs.")

        test_guild = os.getenv("TEST_GUILD", "")

        if not test_guild:
            return

        guild = discord.Object(id=test_guild)

        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def close(self):
        fetcher = getattr(self, "winrate_fetcher", None)
        if fetcher is not None:
            await self.winrate_fetcher.aiohttp_session.close()

        await super().close()

    async def get_prefix(self, msg: discord.Message) -> list[str]:
        # This overwrites Bot.get_prefix
        if msg.guild is None:
            return commands.when_mentioned_or(PREFIX)(self, msg)

        if msg.guild.id not in self.prefix_cache:
            self.prefix_cache[msg.guild.id] = await self.server_service.select_prefix(
                msg.guild.id
            )

        return commands.when_mentioned_or(self.prefix_cache.get(msg.guild.id, PREFIX))(
            self, msg
        )

    async def get_private_users(self) -> None:
        """Gets all private users from the DB.

        Private users will not trigger any on_message listeners.
        """
        rows = await self.privacy_service.select_all_private_users()

        for row in rows:
            user = row.tuple()[0]

            self.private_users.append(user)

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        self.logger.error(
            "Unhandled exception in event '%s' (args=%s, kwargs=%s)",
            event_method,
            args,
            kwargs,
            exc_info=sys.exc_info(),
        )

    async def on_command_error(
        self,
        ctx: commands.Context[Any],
        error: commands.CommandError,
    ) -> None:
        # pylint: disable=too-many-return-statements
        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            self.logger.debug("Command not found: %s", ctx.message.content)
            return

        if isinstance(error, commands.NoPrivateMessage):
            await ctx.reply("Command must be used in a server!")
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(
                f"You're missing some arguments! Here's some help: `{error.param.name}`"
            )
            return

        if isinstance(error, commands.BadArgument):
            await ctx.reply(
                f"Oh no! One of your arguments was wrong. Here's some help: {error}"
            )
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(
                "Unfortunately, you do not have the permissions to do this!"
            )
            return

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.reply(
                "Oh no! Seems like gwen doesn't have the following neccesary "
                f"permissions: {', '.join(error.missing_permissions)}"
            )
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"Slow down! Try again in {error.retry_after:.1f}s.")
            return

        if isinstance(error, commands.CheckFailure):
            await ctx.reply("Oh no! Gwen doesn't want you to use this command here...")
            return

        self.logger.error(
            "Unhandled exception in command '%s' (invoked by %s in #%s)",
            ctx.command,
            ctx.author.id,
            ctx.channel,
            exc_info=error,
        )

        await ctx.reply("Oh no! Gwen ran into some issues when running this command...")

    def register_app_command_error(self) -> None:
        """Registers the on_app_command_error overload.

        This overloard requires access to the bot's tree, which is bound to self.
        See the actual error handling inside the nested function.
        """

        @self.tree.error
        async def on_app_command_error(
            interaction: discord.Interaction, error: app_commands.AppCommandError
        ) -> None:
            original = (
                error.original
                if isinstance(error, app_commands.CommandInvokeError)
                else error
            )

            if isinstance(original, NoViewError):
                return

            self.logger.error(
                "Unhandled exception in app command '%s'",
                interaction.command.qualified_name
                if interaction.command
                else "unknown",
                exc_info=original,
            )

    async def dispatch_before_hooks(self, ctx: commands.Context[Self]) -> None:
        """Before hooks run before commands get executed.

        This function will cause the ``before_hook_servers`` and ``before_hook_users``
        hooks to run before every command.
        """
        await self.before_hook_servers(ctx)
        await self.before_hook_users(ctx)

    async def before_hook_servers(self, ctx: commands.Context[Self]) -> None:
        """Before hook for servers.

        See ``before_hook_users`` for more information.
        """
        if not ctx.guild:
            return

        try:
            await self.server_service.insert_server(
                server_id=ctx.guild.id,
                owner_id=ctx.guild.owner_id,
                member_count=ctx.guild.member_count,
            )
        except ServerIdNotGivenError as exc:
            self.logger.exception(
                "Server ID was not given in before_hook. Context: %s", ctx
            )
            raise commands.CommandError(str(exc)) from exc
        except Exception as exc:
            self.logger.exception("Uncaught exception in before_hook. Context: %s", ctx)
            raise commands.CommandError(str(exc)) from exc

    async def before_hook_users(self, ctx: commands.Context[Self]) -> None:
        """Before hook for users.

        Adds user to the db with every command call
        This could be done on a cog level basis, but easier to have it here
        Triggers on_error or on_command_error if failed,
        and doesn't allow further execution
        Necessary because a lot of the db commands rely on a user being in the db
        But having coupling the services together isn't a good idea,
        nor is it a good idea to have to manually add users in every command
        """

        if ctx.author is None:
            return  # type: ignore[unreachable] # Better to have than not

        try:
            await self.user_service.insert_user(ctx.author.id, ctx.author.name)
        except UserIdOrNameNotGivenError as exc:
            self.logger.exception(
                "User ID or name was not given in before_hook. Context: %s", ctx
            )
            raise commands.CommandError(str(exc)) from exc
        except Exception as exc:
            self.logger.exception("Uncaught exception in before_hook. Context: %s", ctx)
            raise commands.CommandError(str(exc)) from exc

    async def after_hook(self, ctx: commands.Context[Self]) -> None:
        """Logs commands used."""
        if ctx.command_failed:
            return

        self.logger.debug(
            "Invoked command <%s> by user <%s>", ctx.command, ctx.author.id
        )
