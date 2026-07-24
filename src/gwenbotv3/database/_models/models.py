from dataclasses import dataclass

from discord import Message
from discord.ext.commands import Context


@dataclass
class User:
    id: int
    name: str
    is_anonymised: bool


@dataclass
class Server:
    id: int | None
    owner_id: int | None
    member_count: int | None
    quote: bool


@dataclass
class UserContext:
    user: User | None
    server: Server
    message: str | None
    ctx: Context | Message
