"""Models and dataclasses for use in the database module."""

from dataclasses import dataclass

from discord import Message
from discord.ext.commands import Bot, Context


@dataclass
class User:
    """A User object.

    Contains their discord ID, name and if they have been anonymised.
    Use UserHandler.fetch_user.
    """

    id: int
    name: str
    is_anonymised: bool


@dataclass
class Server:
    """A Server object.

    Contains the server's discord ID, the discord ID of the owner,
        the server member count and if it has quote enabled.
    Use ServerHandler.fetch_server.
    """

    id: int | None
    owner_id: int | None
    member_count: int | None
    quote: bool


@dataclass
class UserContext:
    """A UserContext object.

    Contains all context the database would need, including
        a User object, a Server object, the message that the user sent
        and the discord.commands.Context or discord.Message object tied
        to the message.
    """

    user: User | None
    server: Server
    message: str | None
    ctx: Context[Bot] | Message
