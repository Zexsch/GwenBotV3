"""Any on_message listeners."""

import logging
from random import randint

import discord
from discord.channel import TextChannel
from discord.ext import commands

from gwenbotv3.config import DEFAULT_CHANNEL, OWNER_ID
from gwenbotv3.database.models import SymbolCounter
from gwenbotv3.services import GwensubService, ServerService, SymbolService


class ListenerCog(commands.Cog):
    """Anything to do with on_message listens."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.symbol_service = SymbolService()
        self.gwensub_service = GwensubService()
        self.server_service = ServerService()
        self.logger = logging.getLogger(__name__)

    async def _strict_check(self, msg: discord.Message, counter: SymbolCounter) -> str:
        # ruff: noqa: RUF001 # For weird symbols
        base_message = (
            f"<@{counter.creating_user}> Somebody did a little fucky wuckie >.<!! "
            "A small oopsie woopsie uwu! Someone dared ruin the symbol chain nya~!!! "
            f"<@{msg.author.id}> what have you done!! (⁄ ⁄•⁄ω⁄•⁄ ⁄) "
        )

        if "@" not in msg.content and msg.content != counter.symbol:
            self.logger.debug(
                "User %s sent a non-symbol in counter for server=%s",
                msg.author.id,
                counter.server_id,
            )

            return (
                base_message
                + f'They dared send "{msg.content}" in our holy channel nya!'
            )

        if "@" in msg.content and msg.content != counter.symbol:
            self.logger.warning(
                "User %s sent a mention in counter for server=%s",
                msg.author.id,
                counter.server_id,
            )

            return base_message + 'They dared use an "@" in our holy channel nya!'

        if msg.author.id == counter.latest_user:
            self.logger.debug(
                "User %s sent two messages in a row in server=%s",
                msg.author.id,
                counter.server_id,
            )
            return (
                base_message
                + "They dared send two messages in a row in our holy channel nya!"
            )

        raise NotImplementedError

    async def _symbol_check(self, msg: discord.Message) -> None:
        """Checks if the message sent is in the symbol counter and if it's the symbol.

        Args:
            ctx (UserContext): UserContext object.
            msg (discord.Message): discord.Message object.
        """
        # pylint: disable=too-many-return-statements
        # Could avoid this via exceptions but too much effort
        assert msg.guild is not None

        counter = await self.symbol_service.select_counter_by_ids(
            server_id=msg.guild.id
        )

        if not counter:
            return

        if counter.channel_id != msg.channel.id:
            return

        if msg.content == counter.symbol and not counter.strict:
            await self.symbol_service.update_counters(
                server_id=msg.guild.id, user_id=msg.author.id
            )
            return

        if not counter.strict:
            return

        if not counter.strict_channel:
            return

        try:
            message = await self._strict_check(msg=msg, counter=counter)
        except NotImplementedError:
            await self.symbol_service.update_counters(
                server_id=msg.guild.id, user_id=msg.author.id
            )
            return

        reply_channel = self.bot.get_channel(counter.strict_channel)

        if not isinstance(reply_channel, TextChannel):
            return

        await reply_channel.send(message)

    async def _sendshit(self, msg: discord.Message) -> None:
        """Make the bot send any message. Only usable by bot owner.
        sendshit (message)$(channel id)[optional]
        Trigger on-message, not a command."""
        if msg.author.id != OWNER_ID:
            return

        if "sendshit" not in msg.content.lower():
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

    async def _gwen_check(self, msg: discord.Message) -> None:
        """Checks if ``gwen`` or ``gw3n`` is in the message.

        Args:
            ctx (UserContext): UserContext object.
            msg (discord.Message): discord.Message object.
        """
        # pylint: disable=too-many-return-statements # Makes sense here
        assert msg.guild is not None

        if not msg.content:
            return

        if not ("gwen" in msg.content.lower() or "gw3n" in msg.content.lower()):
            return

        server = await self.server_service.select_server(server_id=msg.guild.id)

        assert server is not None

        if server.quote:
            return

        if msg.content.lower()[0 : len(server.prefix)] == server.prefix:
            return

        if not await self.gwensub_service.select_sub_by_ids(
            user_id=msg.author.id, server_id=msg.guild.id
        ):
            return

        if "gw3n" in msg.content.lower():
            await msg.channel.send("Gwen is immune. You cannot escape.")
            return

        # This isn't a cryptographic purpose.
        ran_num: int = randint(0, 99)  # nosec B311

        if ran_num == 1:
            await msg.channel.send("Gwen is... not immune?")
            return

        await msg.channel.send("Gwen is immune.")

    @commands.Cog.listener("on_message")
    async def on_message(self, msg: discord.Message) -> None:
        """discord.Bot.on_message overload.

        Add all on_message listeners in here, as the bot can only have one.
        """
        if not msg.guild:
            return

        if msg.author == self.bot.user:
            return

        await self._symbol_check(msg)
        await self._sendshit(msg)
        await self._gwen_check(msg)
