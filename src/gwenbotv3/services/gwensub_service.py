"""Houses the Gwensub service."""

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
    """Interacts with the Subs and Blacklist database tables.

    Once a user is subscribed in a server,
    GwenBot will respond in chat if a user mentions gwen.
    Meanwhile blacklists work as a counterpart; they're a moderation feature to
    prevent users from subscribing to GwenBot or from using certain commands
    such as any deepseek integrations.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    @connect
    async def select_sub(self, session: AsyncSession, sub_id: int) -> Subs | None:
        """Selects a row using the sub_id primary key.

        Returns
        -------
        Subs | None
            Subs object if found, else None
        """
        return await session.get(Subs, sub_id)

    @connect
    async def select_sub_by_ids(
        self, session: AsyncSession, user_id: int, server_id: int
    ) -> Subs | None:
        """Selects a sub via a user_id and server_id.

        One user may only have one active subscription per server.

        Parameters
        ----------
        user_id : int
            ID of the user.
        server_id : int
            ID of the guild.

        Returns
        -------
        Subs | None
            Subs object if the user is subscribed in the given server, else None.
        """
        stmt = select(Subs).where(Subs.user_id == user_id, Subs.server_id == server_id)
        return (await session.execute(stmt)).scalar_one_or_none()

    @connect
    async def select_all_subs_by_id(
        self, session: AsyncSession, user_id: int
    ) -> Sequence[Subs]:
        """Selects every sub from a user, regardless of server.

        Parameters
        ----------
        user_id : int
            ID of the user.

        Returns
        -------
        Sequence[Subs]
            All found subscriptions.
        """
        stmt = select(Subs).where(Subs.user_id == user_id)
        return (await session.execute(stmt)).scalars().all()

    @connect
    async def insert_sub(
        self, session: AsyncSession, user_id: int, server_id: int
    ) -> None:
        """Adds a user to GwenBot subscription in a specific server.

        Whilst subscribed, GwenBot will respond with ``Gwen is immune.`` to
        any message of this user that mentions gwen in any way. Subscriptions are
        on a per-server basis.

        Parameters
        ----------
        user_id : int
            ID of the user.
        server_id : int
            ID of the server.

        Raises
        ------
        UserIsSubscribedError
            If the user is already subscribed.
        """
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
        """Deletes an active subscription of a user.

        Parameters
        ----------
        user_id : int
            ID of the user.
        server_id : int
            ID of the guild.

        Raises
        ------
        UserNotSubscribedError
            If the user is not currently subscribed.
        """
        sub = await self.select_sub_by_ids(user_id=user_id, server_id=server_id)

        if not sub:
            raise UserNotSubscribedError

        stmt = delete(Subs).where(Subs.user_id == user_id, Subs.server_id == server_id)
        self.logger.info("Deleting sub: <user_id=%s><server_id=%s>", user_id, server_id)
        await session.execute(stmt)

    @connect
    async def delete_all_subs(self, session: AsyncSession, user_id: int) -> None:
        """Deletes all active GwenBot subscriptions, irregardless of the server.

        Parameters
        ----------
        user_id : int
            ID of the user.

        Raises
        ------
        UserNotSubscribedError
            If the user has no active GwenBot subscriptions.
        """
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
        """Selects a Blacklist row using the blacklist_id primary key.

        Returns
        -------
        Blacklist | None
            Blacklist object if found, else None.
        """
        return await session.get(Blacklist, blacklist_id)

    @connect
    async def select_blacklist_by_ids(
        self, session: AsyncSession, user_id: int, server_id: int, *, by_owner: bool
    ) -> Blacklist | None:
        """Selects a blacklist row.

        Parameters
        ----------
        user_id : int
            ID of the user.
        server_id : int
            ID of the guild.
        by_owner : bool
            If the blacklist entry is by the owner.

        Returns
        -------
        Blacklist | None
            Blacklist object if the user is blacklisted in the given server and by the
            given by_owner, else None.
        """
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
        """Inserts a user into the blacklist table.

        Blacklists are a tool for moderators to stop a user from interacting with
        Gwen in specific ways. Those include GwenBot Subscriptions or
        using GwenBot to interact with the deepseek API.

        Parameters
        ----------
        user_id : int
            ID of the user.
        server_id : int
            ID of the guild.
        by_owner : bool, optional
            If the command was executed by the bot owner.
            A user may be blacklisted in a server both by the bot owner
            and by moderators. By default False

        Raises
        ------
        UserIsBlacklistedError
            If the user is already blacklisted.
        """
        blacklist = await self.select_blacklist_by_ids(
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
        """Removes a user from the blacklist.

        Parameters
        ----------
        user_id : int
            ID of the user.
        server_id : int
            ID of the guild.
        by_owner : bool, optional
            If the command was executed by the bot owner, by default False

        Raises
        ------
        UserNotBlacklistedError
            If the user isn't blacklisted.
        """
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
