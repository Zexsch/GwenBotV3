"""Handlers interact with the database directly."""

from .db_handler import DatabaseHandler
from .gwenseek_handler import GwenseekHandler
from .gwensub_handler import GwenSubHandler
from .symbol_handler import SymbolHandler

DatabaseHandler().initialise()

__all__ = ["DatabaseHandler", "GwenSubHandler", "GwenseekHandler", "SymbolHandler"]
