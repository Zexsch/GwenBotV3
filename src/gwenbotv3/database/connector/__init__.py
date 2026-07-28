"""Helper tools to connect to the database.

The connect function acts as a factory for sessions.
Do not manually create sessions within methods, always use the connect function.
A version of connect which works on functions as well could be useful,
but not needed currently.
"""

from .database_connector import connect

__all__ = ["connect"]
