from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Concatenate, cast

import discord
from discord import Interaction

from gwenbotv3.exceptions import NoViewError


class _ConfirmationButton(discord.ui.View):
    def __init__(
        self, author: discord.User | discord.Member, timeout: float = 30.0
    ) -> None:
        super().__init__(timeout=timeout)
        self.author = author
        self.value = False
        self.message: discord.InteractionMessage | None = None

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("Nice try...", ephemeral=True)
            return False

        return True

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(
        self, interaction: Interaction, button: discord.ui.Button
    ) -> None:
        self.value = True
        await interaction.response.edit_message(content="Confirmed.", view=None)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: Interaction, button: discord.ui.Button) -> None:
        self.value = False
        await interaction.response.edit_message(content="Cancelled.", view=None)
        self.stop()

    async def on_timeout(self) -> None:
        self.value = False
        if self.message:
            await self.message.edit(content="How could you take so long...", view=None)


def confirmation_button[Self, **P, R](
    *, message: str = "Are you sure you want to do this?"
) -> Callable[
    [Callable[Concatenate[Self, Interaction, P], Awaitable[R]]],
    Callable[Concatenate[Self, Interaction, P], Awaitable[R]],
]:
    """Decorator for app_commands callbacks that adds a confirm/cancel step.

    Must go BELOW app_commands.command so it wraps the raw callback.
    """

    def decorator(
        func: Callable[Concatenate[Self, Interaction, P], Awaitable[R]],
    ) -> Callable[Concatenate[Self, Interaction, P], Awaitable[R]]:
        @wraps(func)
        async def wrapper(
            self: Self, interaction: Interaction, *args: P.args, **kwargs: P.kwargs
        ) -> R:
            view = _ConfirmationButton(author=interaction.user)
            await interaction.response.send_message(message, view=view, ephemeral=True)
            view.message = await interaction.original_response()

            await view.wait()

            if not view.value:
                raise NoViewError

            return await func(self, interaction, *args, **kwargs)

        return cast(Callable[Concatenate[Self, Interaction, P], Awaitable[R]], wrapper)

    return decorator
