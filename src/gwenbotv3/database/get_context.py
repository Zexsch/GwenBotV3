"""Houses the context function."""

from discord import Message
from discord.ext.commands import Bot, Context

from gwenbotv3.database import UserContext
from gwenbotv3.database.handlers.server_handler import ServerHandler
from gwenbotv3.database.handlers.user_handler import UserHandler


def context(ctx: Context[Bot] | Message) -> UserContext:
    """Takes in either a Context or Message object and returns a UserContext.

    Args:
        ctx (Context | Message): discord.commands.Context or discord.Message object

    Returns:
        UserContext: See database._models.models
    """
    user = UserHandler().fetch_user_by_id(ctx.author.id)
    server = ServerHandler().fetch_server(ctx)

    message = ""

    if isinstance(ctx, Message):
        message = ctx.content

    if isinstance(ctx, Context):
        message = ctx.message.content

    user_context = UserContext(user=user, server=server, message=message, ctx=ctx)

    return user_context
