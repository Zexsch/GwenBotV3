from discord.ext.commands import Context
from discord import Message

from gwenbotv3.database.handlers.user_handler import UserHandler
from gwenbotv3.database.handlers.server_handler import ServerHandler
from gwenbotv3.database import UserContext


def context(ctx: Context | Message) -> UserContext:
    user = UserHandler().fetch_user_by_id(ctx.author.id)
    server = ServerHandler().fetch_server(ctx)

    message = ""

    if isinstance(ctx, Message):
        message = ctx.content

    if isinstance(ctx, Context):
        message = ctx.message.content

    user_context = UserContext(user=user, server=server, message=message, ctx=ctx)

    return user_context
