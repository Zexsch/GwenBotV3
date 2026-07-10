import logging
from random import randint

import discord
from discord.ext import commands

from gwenbotv3.database import UserContext
from gwenbotv3.database import SymbolHandler, GwenSubHandler
from gwenbotv3.database.get_context import context
from gwenbotv3.database.handlers.server_handler import ServerHandler
from gwenbotv3.database.handlers.user_handler import UserHandler
from gwenbotv3.config import DEFAULT_CHANNEL, OWNER_ID


class ListenerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.symbol_handler = SymbolHandler()
        self.gwensub_handler = GwenSubHandler()
        self.server_handler = ServerHandler()
        self.user_handler = UserHandler()
        self.logger = logging.getLogger(__name__)

    async def _symbol_check(self, ctx: UserContext, msg: discord.Message) -> None:
        channel = self.symbol_handler.fetch_channel(ctx)

        if not channel:
            return

        if channel != msg.channel.id:
            return

        symbol = self.symbol_handler.fetch_symbol(ctx)
        latest_user = self.symbol_handler.fetch_latest_user(ctx)

        if ctx.message == symbol and latest_user != msg.author.id:
            self.symbol_handler.update(ctx)
            return

        creating_user = self.symbol_handler.fetch_creating_user(ctx)

        base_message = (
            f"<@{creating_user}> Somebody did a little fucky wuckie >.<!! "
            "A small oopsie woopsie uwu! Someone dared ruin the ? chain nya~!!! "
            f"<@{msg.author.id}> what have you done!! (⁄ ⁄•⁄ω⁄•⁄ ⁄) "
        )

        default_channel_id = self.symbol_handler.fetch_channel(ctx)
        default_channel = self.bot.get_channel(default_channel_id)

        if not "@" in msg.content:
            self.logger.debug(
                "User %s sent a non-question mark in counter for server=%s",
                ctx.user,
                ctx.server.id,
            )

            await default_channel.send(base_message + f'They dared send "{msg.content}" in our holy channel nya!')  # type: ignore
            return

        if "@" in msg.content:
            self.logger.warning(
                "User %s sent a mention in counter for server=%s",
                ctx.user,
                ctx.server.id,
            )

            await default_channel.send(base_message + 'They dared use an "@" in our holy channel nya!')  # type: ignore
            return

        if msg.author.id == latest_user:
            self.logger.debug(
                "User %s sent two messages in a row in server=%s",
                ctx.user,
                ctx.server.id,
            )
            await default_channel.send(base_message + "They dared send two messages in a row in our holy channel nya!")  # type: ignore
            return

    async def _sendshit(self, msg: discord.Message) -> None:
        """Make the bot send any message. Only usable by bot owner.
        sendshit (message)$(channel id)[optional]
        Trigger on-message, not a command."""
        if not msg.author.id == OWNER_ID:
            return

        if not "sendshit" in msg.content.lower():
            return

        res: str = msg.content
        res = res.replace("sendshit", "")
        channel = self.bot.get_channel(
            DEFAULT_CHANNEL
        )  # Default channel to send to. Change in env.

        if "$" in msg.content:
            split = res.split("$", 1)
            channel = self.bot.get_channel(int(split[1]))
            res = split[0]
            res = res.replace("$", "")

        if not channel:
            self.logger.warning("Unable to get channel for id=%s", channel)
            await msg.channel.send("Gwen was unable to get the channel!")
            return

        if not isinstance(channel, discord.TextChannel):
            self.logger.warning("Channel found was not a GuildChannel, id=%s", channel)
            await msg.channel.send("Gwen can only send messages in normal channels!")
            return

        self.logger.debug("Sent message %s in channel %s by owner.", res, channel.id)

        await channel.send(res)

    async def _gwen_check(self, ctx: UserContext, msg: discord.Message) -> None:
        if not ("gwen" in msg.content.lower() or "gw3n" in msg.content.lower()):
            return

        if not msg.content:
            return

        server_prefix = self.server_handler.fetch_prefix(ctx)

        if msg.content[0] == server_prefix:
            return

        if not self.user_handler.fetch_user_by_id(msg.author.id):
            return

        if not self.gwensub_handler.fetch_sub(ctx):
            return

        server = self.server_handler.fetch_server(msg)

        if server.quote:
            return

        if "gw3n" in msg.content.lower():
            await msg.channel.send("Gwen is immune. You cannot escape.")
            return

        ran_num: int = randint(0, 99)

        if ran_num == 1:
            await msg.channel.send("Gwen is... not immune?")
            return

        await msg.channel.send("Gwen is immune.")

    @commands.Cog.listener("on_message")
    async def on_message(self, msg: discord.Message) -> None:
        if msg.guild is None:
            return

        if msg.author == self.bot.user:
            return

        user_context = context(msg)

        await self._symbol_check(user_context, msg)
        await self._sendshit(msg)
        await self._gwen_check(user_context, msg)
