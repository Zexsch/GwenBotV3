import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from types import TracebackType
from typing import Concatenate, cast

from sqlalchemy.ext.asyncio import AsyncSession

from gwenbotv3.database.engine import async_session as _session_factory


class _DatabaseConnector:
    """Async context manager to start a database session.

    Uses the shared engine's connection pool (see database/engine.py).
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self) -> AsyncSession:
        # pylint: disable=attribute-defined-outside-init
        self.session = _session_factory()
        return self.session

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        try:
            if exc_type is None:
                await self.session.commit()
            else:
                self.logger.exception("Error in Database connection, rolling back.")
                await self.session.rollback()
        finally:
            await self.session.close()


def connect[Self, **P, R](
    func: Callable[Concatenate[Self, AsyncSession, P], Awaitable[R]],
) -> Callable[Concatenate[Self, P], Awaitable[R]]:
    """Connect to the database.

    Use as a decorator every time a DB session is needed.
    This decorator will inject the session as the second positional argument
    into the decorated method.

    Returns:
        Callable[Concatenate[Self, P], R]: The decorated method,
            but with a Session object injected as the second
            positional argument.
    """

    @wraps(func)
    async def wrapper(self: Self, *args: P.args, **kwargs: P.kwargs) -> R:
        async with _DatabaseConnector() as session:
            return await func(self, session, *args, **kwargs)

    return cast(Callable[Concatenate[Self, P], Awaitable[R]], wrapper)
