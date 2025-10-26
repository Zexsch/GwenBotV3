import os

OWNER_ID: int = int(os.environ["OWNER_ID"])  # Change to your own discord user ID
DEFAULT_CHANNEL: int = int(os.environ["DEFAULT_CHANNEL"])  # Default channel that the sendshit 'command' sends to.
MESSAGE_CHANNEL: int = int(os.environ["MESSAGE_CHANNEL"]) # Default channel to count messages
PREFIX: str = '+'  # Bot prefix.