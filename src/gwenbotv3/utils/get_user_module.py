from typing import Optional

from discord.ext.commands import Context


def get_user(ctx: Context, user_id: int | str) -> Optional[int]:
    try:
        user_id = int(user_id)  # Type: ignore
    except ValueError:
        if len(ctx.message.mentions) == 0:
            return None

    return ctx.message.mentions[0].id
