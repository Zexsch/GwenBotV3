from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    created_at: datetime


@dataclass
class Server:
    id: Optional[int] 
    owner_id: Optional[int] 
    member_count: Optional[int] 
    quote: bool