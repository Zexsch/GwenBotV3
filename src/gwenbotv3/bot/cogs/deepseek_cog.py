"""Houses the Deepseek cog."""

import logging
import os
from typing import Any, Union

from discord.ext import commands
from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from gwenbotv3.config.deepseek import BANNED_PHRASES, MODEL, SYSTEM_PROMPT
from gwenbotv3.services import GwenseekService, GwensubService, UserService

# ruff: noqa: UP007
Message = Union[
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
]


class DeepseekCog(commands.Cog):
    """Any commands to interact with the Deepseek API."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.gwenseek_service = GwenseekService()
        self.gwensub_service = GwensubService()
        self.user_service = UserService()
        self.__token = os.environ["DEEPSEEK_TOKEN"]
        self.deepseek_client = AsyncOpenAI(
            api_key=self.__token, base_url="https://api.deepseek.com"
        )

    async def create_response(
        self, full_messages: list[Any], tokens: int = 1024
    ) -> ChatCompletion:
        """Creates the necessary ChatCompletion to request to Deepseek API."""
        return await self.deepseek_client.chat.completions.create(
            model=MODEL,
            messages=full_messages,
            max_tokens=tokens,
            temperature=0.7,
            stream=False,
        )

    async def create_response_reasoning(
        self, full_messages: list[Any], tokens: int = 1024
    ) -> ChatCompletion:
        """Creates the necessary Chatcompletion to request to Deepseek API.
        With reasoning."""
        return await self.deepseek_client.chat.completions.create(
            model=MODEL,
            messages=full_messages,
            max_tokens=tokens,
            temperature=0.7,
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}},
        )

    async def choose_mode(
        self, full_messages: list[Any], reasoning: bool, tokens: int = 1024
    ) -> ChatCompletion:
        """Chooses whether to use reasoning or not."""
        if reasoning:
            return await self.create_response_reasoning(
                full_messages=full_messages, tokens=tokens
            )

        return await self.create_response(full_messages=full_messages, tokens=tokens)

    async def _pre_check(
        self, ctx: commands.Context[commands.Bot], message: str
    ) -> bool:
        assert ctx.guild is not None

        if await self.gwensub_service.select_blacklist_by_ids(
            user_id=ctx.author.id, server_id=ctx.guild.id
        ):
            await ctx.send("You have been blacklisted from using this command.")
            return True

        if any(phrase in message for phrase in BANNED_PHRASES):
            self.logger.warning(
                "User %s tried to make gwenseek ping. original_message=%s",
                ctx.message.author.id,
                message,
            )

            await ctx.send("Oh no! You cannot try to make me ping someone!")
            return True

        return False

    async def gwenseekfunc(
        self,
        ctx: commands.Context[commands.Bot],
        model: str,
        original_message: str,
        reasoning: bool,
    ) -> None:
        """Logic to interact and handle the Deepseek API."""
        # pylint: disable=too-many-return-statements
        # Could avoid this via exceptions but too much effort
        assert ctx.guild is not None

        pre_check = await self._pre_check(ctx=ctx, message=original_message)

        if pre_check:
            return

        await ctx.send("Gwen is thinking...")
        response = None

        full_messages = []
        full_messages.append(SYSTEM_PROMPT)

        user = await self.user_service.select_user(user_id=ctx.author.id)

        if not user:
            user = await self.user_service.insert_user(
                user_id=ctx.author.id, user_name=ctx.author.name
            )

        previous_context = await self.gwenseek_service.select_seeks_by_ids(
            user_id=user.user_id, server_id=ctx.guild.id
        )

        for context in previous_context:
            # Maybe make a response dataclass object instead of using indices here?
            full_messages.append({"role": "user", "content": context.user_message})
            full_messages.append(
                {"role": "assistant", "content": context.reasoning_content}
            )

        full_messages.append({"role": "user", "content": original_message})

        response = await self.choose_mode(
            full_messages=full_messages, reasoning=reasoning
        )

        content = response.choices[0].message.content

        if response.choices[0].finish_reason == "length":
            for i in range(1, 3):
                tokens = 1024 * (2**i)
                self.logger.info(
                    "Gwenseek hit the length limit, loop=%i, tokens=%i", i, tokens
                )
                await ctx.send(
                    "Gwen's message seems to have been too long! "
                    "Gwen will try again, please be patient!"
                )
                response = await self.choose_mode(
                    full_messages, reasoning=reasoning, tokens=tokens
                )

                content = response.choices[0].message.content

                if content:
                    break

            if not response.choices[0].message.content:
                self.logger.warning(
                    "Gwenseek gives up trying to get deepseek responses."
                )
                await ctx.send("Gwen gives up.")
                return

        if response.choices[0].finish_reason == "content_filter":
            await ctx.send(
                "Oh no! It seems like you tried to ask Gwen something "
                "that she does not like!"
            )
            self.logger.warning(
                "User %s hit the content filter with original_message='%s'",
                user.user_id,
                original_message,
            )
            return

        if not content:
            self.logger.critical(
                (
                    "Empty message was returned from Deepseek API call with arguments: "
                    "model=%s, full_messages=%s, finish_reason=%s"
                ),
                model,
                full_messages,
                response.choices[0].finish_reason,
            )
            await ctx.send("Oh no! It seems like Gwen ran into some issues!")
            return

        if any(phrase in content for phrase in BANNED_PHRASES):
            await ctx.send(
                "Oh no! It seems like my message contained a banned phrase..."
            )
            return

        if len(content) > 2000:
            self.logger.warning(
                "User %s tried to make gwenseek ping. original_message=%s",
                ctx.message.author.id,
                original_message,
            )
            await ctx.send(
                "Oh no! It seems like I can't send the message because it is too long. "
                "Blame discord..."
            )
            return

        await self.gwenseek_service.add_seek(
            user_id=user.user_id,
            server_id=ctx.guild.id,
            message=original_message,
            reasoning_content=content,
        )

        if not response.choices[0].message.content:
            self.logger.critical(
                (
                    "Empty message was returned from Deepseek API call with arguments: "
                    "model=%s, full_messages=%s, finish_reason=%s"
                ),
                model,
                full_messages,
                response.choices[0].finish_reason,
            )
            await ctx.send("Oh no! It seems like Gwen ran into some issues!")
            return

        await ctx.send(response.choices[0].message.content)
        await ctx.send(f"||<@{ctx.message.author.id}>||")

    @commands.hybrid_command(aliases=["deepseek", "seek"])
    @commands.guild_only()
    async def gwenseek(self, ctx: commands.Context, *, message: str) -> None:
        """Ask Gwen something, with reasoning!"""
        # pylint: disable=line-too-long
        # Check https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html?highlight=Keyword-Only%20Arguments
        # To see how *, message works
        await self.gwenseekfunc(ctx, "reasoner", message, reasoning=True)

    @commands.command(aliases=["deepseekbasic", "seekbasic", "gwenseekb"])
    @commands.guild_only()
    async def gwenseekbasic(
        self, ctx: commands.Context[commands.Bot], *, message: str
    ) -> None:
        """Ask gwen something, but without reasoning!"""
        await self.gwenseekfunc(ctx, "chat", message, reasoning=False)

    @commands.hybrid_command(aliases=["ch", "clear"])
    async def clearhistory(self, ctx: commands.Context) -> None:
        """Clears your gwenseek history in a server!"""
        if not ctx.guild:
            await ctx.send(
                "This command must be used in a server! If you want to"
                " clear all history, including other servers, "
                "use the *clearhistoryall* command instead!"
            )
            return

        await self.gwenseek_service.delete_seeks_by_server(
            user_id=ctx.author.id, server_id=ctx.guild.id
        )
        await ctx.send("Cleared your Gwenseek history, snip snip!")

    @commands.hybrid_command(aliases=["cha", "chall"])
    async def clearhistoryall(self, ctx: commands.Context) -> None:
        """Clears your entire gwenseek history, in every server!"""
        await self.gwenseek_service.delete_all_seeks(user_id=ctx.author.id)
        await ctx.send("Cleared all your Gwenseek history, snip snip!")
