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
    if len(user_id) < 3:
        return None

    if user_id.isdigit():
        return int(user_id)

    if user_id.startswith("<@") and user_id.endswith(">"):
        inner = user_id[2:-1]
        if inner.isdigit():
            return int(inner)
        return None

    if ctx.message.mentions:
        return ctx.message.mentions[0].id

    return None
