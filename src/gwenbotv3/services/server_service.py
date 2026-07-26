import logging

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from gwenbotv3.database import connect
from gwenbotv3.database.models import Servers
from gwenbotv3.exceptions import ServerIdNotGivenError, ServerNotFoundError


class ServerService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    @connect
    async def select_server(
        self, session: AsyncSession, server_id: int
    ) -> Servers | None:
        server = await session.get(Servers, server_id)
        return server

    @connect
    async def insert_server(
        self,
        session: AsyncSession,
        server_id: int,
        owner_id: int | None,
        member_count: int | None,
    ) -> None:
        if server_id is None:
            raise ServerIdNotGivenError

        server = await self.select_server(server_id)

        if server:
            return

        server = Servers(
            server_id=server_id, owner_id=owner_id, member_count=member_count
        )

        self.logger.info("Adding user: %s", repr(server))
        session.add(server)

    @connect
    async def update_server(
        self,
        session: AsyncSession,
        server_id: int,
        owner_id: int | None,
        member_count: int | None,
        quote: bool | None,
        prefix: bool | None,
    ) -> None:
        server = self.select_server(server_id=server_id)

        if server is None:
            raise ServerNotFoundError

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
