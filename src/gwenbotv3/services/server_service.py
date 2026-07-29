"""Houses the Server service."""

import logging

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from gwenbotv3.database import connect
from gwenbotv3.database.models import Servers
from gwenbotv3.exceptions import ServerIdNotGivenError


class ServerService:
    """Interacts with the servers database table."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    @connect
    async def select_server(
        self, session: AsyncSession, server_id: int
    ) -> Servers | None:
        """Selects a server via it's server_id primary key.

        Parameters
        ----------
        server_id : int
            Primary key.

        Returns
        -------
        Servers | None
            Server if found, else None.
        """
        return await session.get(Servers, server_id)

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    @connect
    async def insert_server(
        self,
        session: AsyncSession,
        server_id: int,
        owner_id: int | None,
        member_count: int | None,
        quote: bool | None = False,
        prefix: str | None = "+",
    ) -> None:
        """Inserts a server into the database.

        Parameters
        ----------
        server_id : int
            ID of the guild.
        owner_id : int | None
            User ID of the owner.
        member_count : int | None
            Current server member count.

        Raises
        ------
        ServerIdNotGivenError
            If the server ID isn't given.
        """
        if server_id is None:
            raise ServerIdNotGivenError

        server = await self.select_server(server_id)

        if server:
            return

        server = Servers(
            server_id=server_id,
            owner_id=owner_id,
            member_count=member_count,
            quote=quote,
            prefix=prefix,
        )

        self.logger.info("Adding user: %s", repr(server))
        session.add(server)

    @connect
    async def update_server(
        self,
        session: AsyncSession,
        server_id: int,
        *,
        owner_id: int | None,
        member_count: int | None,
        quote: bool | None,
        prefix: str | None,
    ) -> None:
        """Updates a server in the database.

        This will automatically insert the server if it isn't found.

        Parameters
        ----------
        server_id : int
            ID of the guild.
        owner_id : int | None
            ID of the owner.
        member_count : int | None
            Amount of members.
        quote : bool | None
            If the server has quote enabled or not.
        prefix : bool | None
            Custom prefix of the server.
        """
        server = await self.select_server(server_id=server_id)

        if server is None:
            await self.insert_server(
                server_id=server_id,
                owner_id=owner_id,
                member_count=member_count,
                quote=quote,
                prefix=prefix,
            )

        values = {
            "owner_id": owner_id,
            "member_count": member_count,
            "quote": quote,
            "prefix": prefix,
        }

        values = {k: v for k, v in values.items() if v is not None}

        if not values:
            return

        stmt = update(Servers).where(Servers.server_id == server_id).values(**values)

        self.logger.info("Updated server: %s - Updated: %s", server_id, str(stmt))

        await session.execute(stmt)
