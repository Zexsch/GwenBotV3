"""Used for configuration."""

import os

OWNER_ID: int = int(os.environ["OWNER_ID"])  # Change to your own discord user ID
DEFAULT_CHANNEL: int = int(
    os.environ["DEFAULT_CHANNEL"]
)  # Default channel that the sendshit 'command' sends to.
MESSAGE_CHANNEL: int = int(
    os.environ["MESSAGE_CHANNEL"]
)  # Default channel to count messages
PREFIX: str = "+"  # Bot prefix.


class DatabaseConfig:
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", 3306)
    DB_NAME = os.getenv("DB_NAME")
