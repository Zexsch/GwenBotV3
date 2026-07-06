from dataclasses import dataclass
from typing import Optional

from discord.ext.commands import Context
from discord import Message


@dataclass
class User:
    id: int
    name: str
    is_anonymised: bool


@dataclass
class Server:
    id: Optional[int]
    owner_id: Optional[int]
    member_count: Optional[int]
    quote: bool


@dataclass
class UserContext:
    user: Optional[User]
    server: Server
    message: Optional[str]
    ctx: Context | Message
