"""Houses the get_mention function."""

from discord.ext.commands import Bot, Context


def get_mention(ctx: Context[Bot], user_id: str) -> int | None:
    """Get the first mention of a message.

    Args:
        ctx (Context): Context of the message
        user_id (int | str): Not always an id, can be a mention too.

    Returns:
        Optional[int]: id of the mention or None
    """
    try:
        int(user_id)
    except ValueError:
        if len(ctx.message.mentions) == 0:
            return None

    return ctx.message.mentions[0].id
