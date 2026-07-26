import logging
from collections.abc import Sequence

from sqlalchemy import Row, asc, delete, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from gwenbotv3.database import connect
from gwenbotv3.database.models import SymbolCounter, SymbolUser, Users
from gwenbotv3.exceptions import (
    StrictnessAlreadySetError,
    SymbolAlreadySetupError,
    SymbolNotSetupError,
    SymbolTooLongError,
)


class SymbolService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    # Server stuff

    @connect
    async def select_counter(
        self, session: AsyncSession, symbol_id: int
    ) -> SymbolCounter | None:
        return await session.get(SymbolCounter, symbol_id)

    @connect
    async def select_counter_by_ids(
        self, session: AsyncSession, server_id: int
    ) -> SymbolCounter | None:
        stmt = select(SymbolCounter).where(SymbolCounter.server_id == server_id)
        return (await session.execute(stmt)).scalar_one_or_none()

    @connect
    async def insert_counter(
        self,
        session: AsyncSession,
        server_id: int,
        channel_id: int,
        creating_user: int,
        symbol: str,
        *,
        strict: bool = True,
    ) -> None:
        check = await self.select_counter_by_ids(server_id=server_id)

        if check:
            raise SymbolAlreadySetupError

        if len(symbol) > 50:
            raise SymbolTooLongError

        counter = SymbolCounter(
            server_id=server_id,
            channel_id=channel_id,
            creating_user=creating_user,
            symbol=symbol,
            strict=strict,
        )
        self.logger.info("Setting up a counter: %s", str(counter))

        session.add(counter)

    @connect
    async def delete_counter(self, session: AsyncSession, server_id: int) -> None:
        check = await self.select_counter_by_ids(server_id=server_id)

        if not check:
            raise SymbolNotSetupError

        stmt = delete(SymbolCounter).where(SymbolCounter.server_id == server_id)

        self.logger.warning("Deleting a counter: %s", str(check))

        await session.execute(stmt)

    @connect
    async def select_amount(self, session: AsyncSession, server_id: int) -> int:
        stmt = select(SymbolCounter.amount).where(SymbolCounter.server_id == server_id)

        return (await session.execute(stmt)).scalar_one()

    @connect
    async def update_server_amount(self, session: AsyncSession, server_id: int) -> None:
        check = await self.select_counter_by_ids(server_id=server_id)

        if not check:
            raise SymbolNotSetupError

        current_amount = await self.select_amount(server_id=server_id)

        stmt = (
            update(SymbolCounter.amount)
            .where(
                SymbolCounter.server_id == server_id,
            )
            .values(amount=current_amount + 1)
        )

        await session.execute(stmt)

    @connect
    async def update_strictness(
        self, session: AsyncSession, server_id: int, strict: bool
    ) -> None:
        check = await self.select_counter_by_ids(server_id=server_id)

        if not check:
            raise SymbolNotSetupError

        if check.strict == strict:
            raise StrictnessAlreadySetError

        stmt = (
            update(SymbolCounter.strict)
            .where(
                SymbolCounter.server_id == server_id,
            )
            .values(strict=strict)
        )

        self.logger.info(
            "Updating strictness to %s for server: %s", strict, repr(check)
        )

        await session.execute(stmt)

    @connect
    async def update_latest_user_server(
        self, session: AsyncSession, server_id: int, user_id: int
    ) -> None:
        check = await self.select_counter_by_ids(server_id=server_id)

        if not check:
            raise SymbolNotSetupError

        stmt = (
            update(SymbolCounter.latest_user)
            .where(SymbolCounter.server_id == server_id)
            .values(latest_user=user_id)
        )

        await session.execute(stmt)

    @connect
    async def update_symbol(
        self, session: AsyncSession, server_id: int, symbol: str
    ) -> None:
        server = await self.select_counter_by_ids(server_id=server_id)

        if not server:
            raise SymbolNotSetupError

        if len(symbol) > 50:
            raise SymbolTooLongError

        stmt = (
            update(SymbolCounter.symbol)
            .where(SymbolCounter.server_id == server_id)
            .values(symbol=symbol)
        )

        self.logger.info("Updated symbol to %s on server=%s", symbol, repr(server))

        await session.execute(stmt)

    # User stuff

    @connect
    async def select_user_counter(
        self, session: AsyncSession, s_user_id: int
    ) -> SymbolUser | None:
        stmt = select(SymbolUser).where(SymbolUser.s_user_id == s_user_id)
        return (await session.execute(stmt)).scalar_one_or_none()

    @connect
    async def select_user_counter_by_ids(
        self, session: AsyncSession, server_id: int, user_id: int
    ) -> SymbolUser | None:
        stmt = select(SymbolUser).where(
            SymbolUser.user_id == user_id, SymbolUser.symbols_server == server_id
        )
        return (await session.execute(stmt)).scalar_one_or_none()

    @connect
    async def insert_user_counter(
        self, session: AsyncSession, server_id: int, user_id: int
    ) -> SymbolUser:
        check = await self.select_user_counter_by_ids(
            server_id=server_id, user_id=user_id
        )

        if check:
            return check

        user = SymbolUser(user_id=user_id, symbols_server=server_id)
        self.logger.info("Adding symbol user: %s", repr(user))
        session.add(user)

        return user

    @connect
    async def update_user_counter_amount(
        self, session: AsyncSession, server_id: int, user_id: int
    ) -> None:
        user = await self.select_user_counter_by_ids(
            server_id=server_id, user_id=user_id
        )

        if not user:
            user = await self.insert_user_counter(server_id=server_id, user_id=user_id)

        stmt = (
            update(SymbolUser.amount)
            .where(SymbolUser.user_id == user_id)
            .values(amount=user.amount + 1)
        )

        await session.execute(stmt)

    # General

    async def update_counters(self, server_id: int, user_id: int) -> None:
        counter = await self.select_counter_by_ids(server_id=server_id)

        if not counter:
            raise SymbolNotSetupError

        await self.update_server_amount(server_id=server_id)
        await self.update_latest_user_server(server_id=server_id, user_id=user_id)
        await self.update_user_counter_amount(server_id=server_id, user_id=user_id)

    async def leaderboard(
        self, session: AsyncSession, server_id: int, limit: int
    ) -> Sequence[Row[tuple[int, str, int]]]:
        counter = await self.select_counter_by_ids(server_id=server_id)

        if not counter:
            raise SymbolNotSetupError

        stmt = (
            select(Users.user_id, Users.user_name, SymbolUser.amount)
            .join(Users, Users.user_id == SymbolUser.user_id)
            .where(SymbolUser.symbols_server == server_id)
            .order_by(desc(SymbolUser.amount), asc(Users.user_id))
            .limit(limit)
        )

        return (await session.execute(stmt)).all()
