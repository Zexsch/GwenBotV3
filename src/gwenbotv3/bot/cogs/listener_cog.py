from random import randint
from logging import Logger

import discord
from discord.ext import commands

from gwenbotv3.database import context, UserContext
from gwenbotv3.database import SymbolHandler, GwenSubHandler, ServerHandler
from gwenbotv3.config import DEFAULT_CHANNEL, OWNER_ID


class ListenerCog(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: Logger):
        self.bot = bot
        self.symbol_handler = SymbolHandler()
        self.gwensub_handler = GwenSubHandler()
        self.server_handler = ServerHandler()
        self.logger = logger

    async def _symbol_check(self, ctx: UserContext, msg: discord.Message) -> None:
        channel = self.symbol_handler.fetch_channel(ctx)

        if not channel:
            return

        if channel != msg.channel.id:
            return

        symbol = self.symbol_handler.fetch_symbol(ctx)
        latest_user = self.symbol_handler.fetch_latest_user(ctx)

        if ctx.message == symbol and latest_user != ctx.user.id:
            self.symbol_handler.update(ctx)
            return

        creating_user = self.symbol_handler.fetch_creating_user(ctx)

        base_message = (
            f"<@{creating_user} Somebody did a little fucky wuckie >.<!! "
            "A small oopsie woopsie uwu! Someone dared ruin the ? chain nya~!!! "
            f"<@{msg.author.id}> what have you done!! (⁄ ⁄•⁄ω⁄•⁄ ⁄) "
        )

        default_channel_id = self.symbol_handler.fetch_channel(ctx)
        default_channel = self.bot.get_channel(default_channel_id)

        if not "@" in msg.content:
            self.logger.warning(
                f"User {ctx.user.id} - Username {ctx.user.name} sent a non-question mark in the question mark channel."
            )

            await default_channel.send(base_message + f'They dared send "{msg.content}" in our holy channel nya!')  # type: ignore
            return

        if "@" in msg.content:
            self.logger.warning(
                f"User {msg.author.id} sent a mention in the question mark channel."
            )

            await default_channel.send(base_message + 'They dared use an "@" in our holy channel nya!')  # type: ignore
            return

        if ctx.user.id == latest_user:
            await default_channel.send(base_message + "They dared send two messages in a row in our holy channel nya!")  # type: ignore
            return

    async def _sendshit(self, msg: discord.Message) -> None:
        """Make the bot send any message. Only usable by bot owner.
        sendshit (message)$(channel id)[optional]
        Trigger on-message, not a command."""
        if msg.author.id == OWNER_ID and "sendshit" in msg.content.lower():
            res: str = msg.content
            res = res.replace("sendshit", "")
            channel = self.bot.get_channel(
                DEFAULT_CHANNEL
            )  # Default channel to send to. Change in Config.config.

            if "$" in msg.content:
                split = res.split("$", 1)
                channel = self.bot.get_channel(int(split[1]))
                res = split[0]
                res = res.replace("$", "")

            self.logger.debug(f"Sent message '{res}' in channel {channel.id} by owner")  # type: ignore
            await channel.send(res)  # type: ignore
            return

    async def _gwen_check(self, ctx: UserContext, msg: discord.Message) -> None:
        if not "gwen" in msg.content.lower() or not "gw3n" in msg.content.lower():
            return

        if msg.author == self.bot.user:
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

        user_context = context(msg)

        await self._symbol_check(user_context, msg)
        await self._sendshit(msg)
        await self._gwen_check(user_context, msg)
