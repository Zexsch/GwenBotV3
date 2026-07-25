"""Used for configuration."""

import os

from dotenv import load_dotenv

load_dotenv()

OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))  # Change to your own discord user ID
DEFAULT_CHANNEL: int = int(
    os.getenv("DEFAULT_CHANNEL", "0")
)  # Default channel that the sendshit 'command' sends to.
MESSAGE_CHANNEL: int = int(
    os.getenv("MESSAGE_CHANNEL", "0")
)  # Default channel to count messages
PREFIX: str = "+"  # Bot prefix.


class DatabaseConfig:
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", 3306)
    DB_NAME = os.getenv("DB_NAME")
