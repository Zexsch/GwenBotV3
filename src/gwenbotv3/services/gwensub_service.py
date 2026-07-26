import logging
from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from gwenbotv3.database import connect
from gwenbotv3.database.models import Blacklist, Subs
from gwenbotv3.exceptions import (
    UserIsBlacklistedError,
    UserIsSubscribedError,
    UserNotBlacklistedError,
    UserNotSubscribedError,
)


class GwensubService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    @connect
    async def select_sub(self, session: AsyncSession, sub_id: int) -> Subs | None:
        sub = await session.get(Subs, sub_id)
        return sub

    @connect
    async def select_sub_by_ids(
        self, session: AsyncSession, user_id: int, server_id: int
    ) -> Subs | None:
        stmt = select(Subs).where(Subs.user_id == user_id, Subs.server_id == server_id)
        return (await session.execute(stmt)).scalar_one_or_none()

    @connect
    async def select_all_subs_by_id(
        self, session: AsyncSession, user_id: int
    ) -> Sequence[Subs] | None:
        stmt = select(Subs).where(Subs.user_id == user_id)
        return (await session.execute(stmt)).scalars().all()

    @connect
    async def insert_sub(
        self, session: AsyncSession, user_id: int, server_id: int
    ) -> None:
        sub = await self.select_sub_by_ids(user_id=user_id, server_id=server_id)

        if sub:
            raise UserIsSubscribedError

        sub = Subs(user_id=user_id, server_id=server_id)

        self.logger.info("Adding sub: %s", repr(sub))
        session.add(sub)

    @connect
    async def delete_sub(
        self, session: AsyncSession, user_id: int, server_id: int
    ) -> None:
        sub = await self.select_sub_by_ids(user_id=user_id, server_id=server_id)

        if not sub:
            raise UserNotSubscribedError

        stmt = delete(Subs).where(Subs.user_id == user_id, Subs.server_id == server_id)
        self.logger.info("Deleting sub: <user_id=%s><server_id=%s>", user_id, server_id)
        await session.execute(stmt)

    @connect
    async def delete_all_subs(self, session: AsyncSession, user_id: int) -> None:
        subs = await self.select_all_subs_by_id(user_id=user_id)

        if not subs:
            raise UserNotSubscribedError

        stmt = delete(Subs).where(Subs.user_id == user_id)
        self.logger.info("Deleting all subs for <user_id=%s>", user_id)
        await session.execute(stmt)

    @connect
    async def select_blacklist(
        self, session: AsyncSession, blacklist_id: int
    ) -> Blacklist | None:
        return await session.get(Blacklist, blacklist_id)

    @connect
    async def select_blacklist_by_ids(
        self, session: AsyncSession, user_id: int, server_id: int, *, by_owner: bool
    ) -> Blacklist | None:
        stmt = select(Blacklist).where(
            Blacklist.user_id == user_id,
            Blacklist.server_id == server_id,
            Blacklist.by_owner == by_owner,
        )
        return (await session.execute(stmt)).scalar_one_or_none()

    @connect
    async def insert_blacklist(
        self,
        session: AsyncSession,
        user_id: int,
        server_id: int,
        *,
        by_owner: bool = False,
    ) -> None:
        blacklist = self.select_blacklist_by_ids(
            user_id=user_id, server_id=server_id, by_owner=by_owner
        )

        if blacklist is None:
            raise UserIsBlacklistedError

        blacklist_add = Blacklist(
            user_id=user_id, server_id=server_id, by_owner=by_owner
        )
        self.logger.info(
            "Blacklisting user: <user_id=%s>,<server_id=%s>,<by_owner=%s>",
            user_id,
            server_id,
            by_owner,
        )
        session.add(blacklist_add)

    @connect
    async def delete_blacklist(
        self,
        session: AsyncSession,
        user_id: int,
        server_id: int,
        *,
        by_owner: bool = False,
    ) -> None:
        blacklist = await self.select_blacklist_by_ids(
            user_id=user_id, server_id=server_id, by_owner=by_owner
        )

        if not blacklist:
            raise UserNotBlacklistedError

        stmt = delete(Blacklist).where(
            Blacklist.user_id == user_id,
            Blacklist.server_id == server_id,
            Blacklist.by_owner == by_owner,
        )
        self.logger.info(
            "Removing blacklist from user: <user_id=%s>,<server_id=%s>,<by_owner=%s>",
            user_id,
            server_id,
            by_owner,
        )
        await session.execute(stmt)
