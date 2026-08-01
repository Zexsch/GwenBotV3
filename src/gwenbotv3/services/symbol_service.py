"""Houses the symbol service."""

import logging
from collections.abc import Sequence

from sqlalchemy import Row, asc, delete, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from gwenbotv3.database import connect
from gwenbotv3.database.models import SymbolCounter, SymbolUser, Users
from gwenbotv3.exceptions import (
    LimitTooLargeError,
    SymbolAlreadySetupError,
    SymbolNotSetupError,
    SymbolTooLongError,
)


class SymbolService:
    """Interacts with the SymbolCounter and SymbolUser database tables."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    # Server stuff

    @connect
    async def select_counter(
        self, session: AsyncSession, symbol_id: int
    ) -> SymbolCounter | None:
        """Selects a symbol counter on it's symbol_id primary key.

        Parameters
        ----------
        symbol_id : int
            Primary key.

        Returns
        -------
        SymbolCounter | None
            SymbolCounter if found, else None
        """
        return await session.get(SymbolCounter, symbol_id)

    @connect
    async def select_counter_by_ids(
        self, session: AsyncSession, server_id: int
    ) -> SymbolCounter | None:
        """Selects a symbol counter on the server_id.

        One server may only have one symbol counter set up.

        Parameters
        ----------
        server_id : int
            ID of the guild.

        Returns
        -------
        SymbolCounter | None
            SymbolCounter if found, else None.
        """
        stmt = select(SymbolCounter).where(SymbolCounter.server_id == server_id)
        return (await session.execute(stmt)).scalar_one_or_none()

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    @connect
    async def insert_counter(
        self,
        session: AsyncSession,
        server_id: int,
        channel_id: int,
        creating_user: int,
        symbol: str,
        *,
        strict: bool = False,
        strict_channel: int | None = None,
    ) -> None:
        """Inserts a symbol counter into the database.

        Parameters
        ----------
        server_id : int
            ID of the guild.
        channel_id : int
            ID of the channel to start counting in.
        creating_user : int
            ID of the user who created the counter.
        symbol : str
            The symbol to count.
        strict : bool, optional
            Whether to be strict or not.
            When strict, GwenBot only counts symbols that were not sent
            by the same user twice in a row, and if the user sends a symbol
            twice in a row or sends a message that isn't the symbol,
            then GwenBot will ping the ``creating_user`` in the ``strict_channel``.
            By default True.
        strict_channel: int, optional
            See ``strict``.

        Raises
        ------
        SymbolAlreadySetupError
            If the server already has a symbol counter set up.
        SymbolTooLongError
            If the symbol to count is too long. Limit is 200 characters.
        """
        check = await self.select_counter_by_ids(server_id=server_id)

        if check:
            raise SymbolAlreadySetupError

        if len(symbol) > 200:
            raise SymbolTooLongError

        counter = SymbolCounter(
            server_id=server_id,
            channel_id=channel_id,
            creating_user=creating_user,
            symbol=symbol,
            strict=strict,
            strict_channel=strict_channel,
        )
        self.logger.info("Setting up a counter: %s", str(counter))

        session.add(counter)

    @connect
    async def delete_counter(self, session: AsyncSession, server_id: int) -> None:
        """Deletes a counter from a server.

        Parameters
        ----------
        server_id : int
            ID of the guild.

        Raises
        ------
        SymbolNotSetupError
            If the server has no symbol counter set up.
        """
        check = await self.select_counter_by_ids(server_id=server_id)

        if not check:
            raise SymbolNotSetupError

        stmt = delete(SymbolCounter).where(SymbolCounter.server_id == server_id)

        self.logger.warning("Deleting a counter: %s", str(check))

        await session.execute(stmt)

    @connect
    async def select_amount(self, session: AsyncSession, server_id: int) -> int:
        """Selects the amount from a counter.

        Parameters
        ----------
        server_id : int
            ID of the guild.

        Returns
        -------
        int
            Amount.
        """
        stmt = select(SymbolCounter.amount).where(SymbolCounter.server_id == server_id)

        return (await session.execute(stmt)).scalar_one()

    @connect
    async def update_server_amount(self, session: AsyncSession, server_id: int) -> None:
        """Updates the server amount. Increments it by one.

        Parameters
        ----------
        server_id : int
            ID of the guild.

        Raises
        ------
        SymbolNotSetupError
            If the server has no counter set up.
        """
        check = await self.select_counter_by_ids(server_id=server_id)

        if not check:
            raise SymbolNotSetupError

        current_amount = await self.select_amount(server_id=server_id) + 1

        stmt = (
            update(SymbolCounter)
            .where(
                SymbolCounter.server_id == server_id,
            )
            .values(amount=current_amount)
        )

        await session.execute(stmt)

    @connect
    async def flip_strictness(self, session: AsyncSession, server_id: int) -> bool:
        """Updates a counter's strictness. Sets it either to true or false.

        Parameters
        ----------
        server_id : int
            ID of the guild.

        Raises
        ------
        SymbolNotSetupError
            If the server has no symbol counter set up.
        """
        check = await self.select_counter_by_ids(server_id=server_id)

        if not check:
            raise SymbolNotSetupError

        strict = not check.strict

        stmt = (
            update(SymbolCounter)
            .where(
                SymbolCounter.server_id == server_id,
            )
            .values(strict=strict)
        )

        self.logger.info(
            "Updating strictness to %s for server: %s", strict, repr(check)
        )

        await session.execute(stmt)
        return strict

    @connect
    async def update_strictness_channel(
        self, session: AsyncSession, server_id: int, channel_id: int
    ) -> None:
        """Flips a counter's strictness.

        Parameters
        ----------
        server_id : int
            ID of the server.
        channel_id : int
            ID of the channel to set strictness_channel to.
            This will be set even if strictness gets flipped to False.
        """
        stmt = (
            update(SymbolCounter)
            .where(SymbolCounter.server_id == server_id)
            .values(strict_channel=channel_id)
        )

        await session.execute(stmt)

    @connect
    async def update_latest_user_server(
        self, session: AsyncSession, server_id: int, user_id: int
    ) -> None:
        """Updates the latest user of a counter.

        Parameters
        ----------
        server_id : int
            ID of the guild.
        user_id : int
            ID of the user.

        Raises
        ------
        SymbolNotSetupError
            If the server has no counter set up.
        """
        check = await self.select_counter_by_ids(server_id=server_id)

        if not check:
            raise SymbolNotSetupError

        stmt = (
            update(SymbolCounter)
            .where(SymbolCounter.server_id == server_id)
            .values(latest_user=user_id)
        )

        await session.execute(stmt)

    @connect
    async def update_symbol(
        self, session: AsyncSession, server_id: int, symbol: str
    ) -> None:
        """Updates the symbol of a counter.

        Parameters
        ----------
        server_id : int
            ID of the guild.
        symbol : str
            Symbol to set it to.

        Raises
        ------
        SymbolNotSetupError
            If the server has no counter set up.
        SymbolTooLongError
            If the given symbol is too long. Max is 200 characters.
        """
        server = await self.select_counter_by_ids(server_id=server_id)

        if not server:
            raise SymbolNotSetupError

        if len(symbol) > 200:
            raise SymbolTooLongError

        stmt = (
            update(SymbolCounter)
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
        """Selects a user counter by its s_user_id primary key.

        Parameters
        ----------
        s_user_id : int
            Primary key.

        Returns
        -------
        SymbolUser | None
            SymbolUser if found, else None.
        """
        stmt = select(SymbolUser).where(SymbolUser.s_user_id == s_user_id)
        return (await session.execute(stmt)).scalar_one_or_none()

    @connect
    async def select_user_counter_by_ids(
        self, session: AsyncSession, server_id: int, user_id: int
    ) -> SymbolUser | None:
        """Selects a SymbolUser by its server ID and user ID.

        Parameters
        ----------
        server_id : int
            ID of the guild.
        user_id : int
            ID of the user.

        Returns
        -------
        SymbolUser | None
            SymbolUser if found, else None.
        """
        stmt = select(SymbolUser).where(
            SymbolUser.user_id == user_id, SymbolUser.symbols_server == server_id
        )
        return (await session.execute(stmt)).scalar_one_or_none()

    @connect
    async def insert_user_counter(
        self, session: AsyncSession, server_id: int, user_id: int
    ) -> SymbolUser:
        """Inserts a SymbolUser.

        One user may only have a single SymbolUser per server.

        Parameters
        ----------
        server_id : int
            ID of the guild.
        user_id : int
            ID of the user.

        Returns
        -------
        SymbolUser
            Inserted SymbolUser.
        """
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
        """Updates a SymbolUser's amount.

        Automatically increments the amount by one when called.

        Parameters
        ----------
        server_id : int
            ID of the guild.
        user_id : int
            ID of the user.
        """
        user = await self.select_user_counter_by_ids(
            server_id=server_id, user_id=user_id
        )

        if not user:
            user = await self.insert_user_counter(server_id=server_id, user_id=user_id)

        stmt = (
            update(SymbolUser)
            .where(SymbolUser.user_id == user_id)
            .values(amount=user.amount + 1)
        )

        await session.execute(stmt)

    # General

    async def update_counters(self, server_id: int, user_id: int) -> None:
        """Updates the counter.

        Increments the server amount by one.
        Updates the server's last_user to the user.
        Increments the user's amount by one.

        Parameters
        ----------
        server_id : int
            ID of the guild.
        user_id : int
            ID of the user.

        Raises
        ------
        SymbolNotSetupError
            If the server has no counter set up.
        """
        counter = await self.select_counter_by_ids(server_id=server_id)

        if not counter:
            raise SymbolNotSetupError

        await self.update_server_amount(server_id=server_id)
        await self.update_latest_user_server(server_id=server_id, user_id=user_id)
        await self.update_user_counter_amount(server_id=server_id, user_id=user_id)

    @connect
    async def leaderboard(
        self, session: AsyncSession, server_id: int, limit: int
    ) -> Sequence[Row[tuple[int, str, int]]]:
        """Selects the leaderboard.

        Fetches the users with the highest amount up to ``limit``.

        Parameters
        ----------
        server_id : int
            ID of the guild.
        limit : int
            Amount of users up to ``limit``. Max 20.

        Returns
        -------
        Sequence[Row[tuple[int, str, int]]]
            Selected rows.

        Raises
        ------
        SymbolNotSetupError
            If the server has no counter set up.
        LimitTooLargeError
            If the limit > 20.
        """
        counter = await self.select_counter_by_ids(server_id=server_id)

        if not counter:
            raise SymbolNotSetupError

        if limit > 20:
            raise LimitTooLargeError

        stmt = (
            select(Users.user_id, Users.user_name, SymbolUser.amount)
            .join(Users, Users.user_id == SymbolUser.user_id)
            .where(SymbolUser.symbols_server == server_id)
            .order_by(desc(SymbolUser.amount), asc(Users.user_id))
            .limit(limit)
        )

        return (await session.execute(stmt)).all()
