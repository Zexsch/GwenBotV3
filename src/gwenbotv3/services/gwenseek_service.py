import logging
from collections.abc import Sequence

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from gwenbotv3.database import connect
from gwenbotv3.database.models import Gwenseek


class GwenseekService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    @connect
    async def select_seek(self, session: AsyncSession, seek_id: int) -> Gwenseek | None:
        seek = await session.get(Gwenseek, seek_id)
        return seek

    @connect
    async def select_seeks_by_ids(
        self, session: AsyncSession, user_id: int, server_id: int
    ) -> Sequence[Gwenseek]:
        stmt = select(Gwenseek).where(
            Gwenseek.user_id == user_id, Gwenseek.server_id == server_id
        )
        return (await session.execute(stmt)).scalars().all()

    @connect
    async def _select_seek_count(
        self, session: AsyncSession, user_id: int, server_id: int
    ) -> int | None:
        stmt = select(func.count(Gwenseek.user_id)).where(
            Gwenseek.user_id == user_id, Gwenseek.server_id == server_id
        )

        return (await session.execute(stmt)).scalar_one_or_none()

    @connect
    async def _delete_oldest_seek(
        self, session: AsyncSession, user_id: int, server_id: int
    ) -> None:
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
            + "<user_id=%i> <server_id=%i> <user_message=%s> <reasoning_message=%s>",
            user_id,
            server_id,
            message,
            reasoning_content,
        )

        session.add(seek)
