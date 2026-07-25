"""Everything to do with logging.

init_logging must be imported and ran before any other project code.
This is to properly initialise the root logger and its handlers.
"""

from .init_logging import init_logging

__all__ = ["init_logging"]
