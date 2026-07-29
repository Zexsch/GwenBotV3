"""Houses the Gwenseek service."""

import logging
from collections.abc import Sequence

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from gwenbotv3.database import connect
from gwenbotv3.database.models import Gwenseek


class GwenseekService:
    """Interacts with the Gwenseek database table."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    @connect
    async def select_seek(self, session: AsyncSession, seek_id: int) -> Gwenseek | None:
        """Selects a row using the seek_id primary key.

        Returns
        -------
        Gwenseek | None
            Gwenseek object if found, else None
        """
        return await session.get(Gwenseek, seek_id)

    @connect
    async def select_seeks_by_ids(
        self, session: AsyncSession, user_id: int, server_id: int
    ) -> Sequence[Gwenseek]:
        """Selects all seeks matching the user_id and server_id.

        Parameters
        ----------
        user_id : int
            ID of the user.
        server_id : int
            ID of the guild.

        Returns
        -------
        Sequence[Gwenseek]
            All found seeks. Empty sequence if none are found.
        """
        stmt = select(Gwenseek).where(
            Gwenseek.user_id == user_id, Gwenseek.server_id == server_id
        )
        return (await session.execute(stmt)).scalars().all()

    @connect
    async def _select_seek_count(
        self, session: AsyncSession, user_id: int, server_id: int
    ) -> int | None:
        """Selects how many seeks a user has in a specific server.

        Parameters
        ----------
        user_id : int
            ID of the user.
        server_id : int
            ID of the server.

        Returns
        -------
        int | None
            Amount fetched, None if no are found.
        """
        stmt = select(func.count(Gwenseek.user_id)).where(  # pylint: disable=not-callable
            Gwenseek.user_id == user_id, Gwenseek.server_id == server_id
        )

        return (await session.execute(stmt)).scalar_one_or_none()

    @connect
    async def _delete_oldest_seek(
        self, session: AsyncSession, user_id: int, server_id: int
    ) -> None:
        """Deletes the oldest seek from a user in a server.

        Parameters
        ----------
        user_id : int
            ID of the user.
        server_id : int
            ID of the server.
        """
        oldest_seek = (
            select(func.min(Gwenseek.seek_id))
            .where(Gwenseek.user_id == user_id, Gwenseek.server_id == server_id)
            .scalar_subquery()
        )

        stmt = delete(Gwenseek).where(Gwenseek.seek_id == oldest_seek)

        self.logger.info(
            "Deleting oldest seek for <user=%i> <server=%i>", user_id, server_id
        )
        await session.execute(stmt)

    @connect
    async def add_seek(
        self,
        session: AsyncSession,
        user_id: int,
        server_id: int,
        message: str,
        reasoning_content: str,
    ) -> None:
        """Adds a seek.

        Seeks are interactions with the Deepseek API, stored to include prior
        context in future responses.

        Parameters
        ----------
        user_id : int
            ID of the user.
        server_id : int
            ID of the guild.
        message : str
            Original message of the user, not including any commands.
        reasoning_content : str
            The AI's response to the query.
        """
        seek_count = await self._select_seek_count(user_id=user_id, server_id=server_id)

        if seek_count and seek_count > 5:
            await self._delete_oldest_seek(user_id=user_id, server_id=server_id)

        seek = Gwenseek(
            user_id=user_id,
            server_id=server_id,
            user_message=message,
            reasoning_content=reasoning_content,
        )

        self.logger.debug(
            "Adding seek: "
            "<user_id=%i> <server_id=%i> <user_message=%s> <reasoning_message=%s>",
            user_id,
            server_id,
            message,
            reasoning_content,
        )

        session.add(seek)
