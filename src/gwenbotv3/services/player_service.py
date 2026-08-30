"""Houses the User Service."""

import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from gwenbotv3.database import connect
from gwenbotv3.database.models import Players
from gwenbotv3.exceptions import PlayerInsertionError, PlayerNotFoundError


class PlayerService:
    """Interacts with the users database table."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    @connect
    async def select_player(
        self, session: AsyncSession, player_id: int
    ) -> Players | None:
        """Selects a player by their player_id primary key.

        Parameters
        ----------
        player_id : int
            ID of the player.

        Returns
        -------
        Players | None
            Players if found, else None.
        """
        return await session.get(Players, player_id)

    @connect
    async def select_player_by_userid(
        self, session: AsyncSession, user_id: int
    ) -> Players | None:
        """Selects a player by the discord user_id.

        Parameters
        ----------
        user_id : int
            ID of the user.

        Returns
        -------
        Players | None
            Players if found, else None.
        """
        stmt = select(Players).where(Players.user_id == user_id)
        return (await session.execute(stmt)).scalar_one_or_none()

    @connect
    async def insert_player(self, session: AsyncSession, user_id: int) -> None:
        """Inserts a new player.

        Parameters
        ----------
        user_id : int
            Discord ID of the player.

        Raises
        ------
        PlayerInsertionError
            If the player is already in the DB.
        """
        player = await self.select_player_by_userid(user_id=user_id)

        if player:
            raise PlayerInsertionError

        player = Players(user_id=user_id)
        self.logger.info("Adding player: %s", repr(player))
        session.add(player)

    @connect
    async def update_elo(self, session: AsyncSession, user_id: int, elo: int) -> None:
        """Sets the elo of a player to a specified elo.

        Parameters
        ----------
        user_id : int
            Discord ID of the player.
        elo : int
            Elo to be set.

        Raises
        ------
        PlayerNotFoundError
            If the player does not exist.
        """
        player = await self.select_player_by_userid(user_id=user_id)

        if not player:
            raise PlayerNotFoundError

        stmt = (
            update(Players).where(Players.player_id == player.player_id).values(elo=elo)
        )

        self.logger.debug("Updating elo to %s for player %s", elo, repr(player))

        await session.execute(stmt)

    @connect
    async def set_resources(
        self,
        session: AsyncSession,
        user_id: int,
        *,
        gold: int | None,
        threads: int | None,
        cotton: int | None,
    ) -> None:
        """Sets a player's resources to a specified value.

        Parameters
        ----------
        user_id : int
            Discord ID of the player.
        gold : int | None
            Gold to set to if necessary.
        threads : int | None
            Threads to set to if necessary.
        cotton : int | None
            Cotton to set to if necessary.

        Raises
        ------
        PlayerNotFoundError
            If the player does not exist.
        """

        player = await self.select_player_by_userid(user_id=user_id)

        if not player:
            raise PlayerNotFoundError

        values = {"gold": gold, "threads": threads, "cotton": cotton}

        values = {k: v for k, v in values.items() if v is not None}

        stmt = (
            update(Players)
            .where(Players.player_id == player.player_id)
            .values(**values)
        )

        self.logger.info("Updating player %s, setting values to %s", user_id, values)

        await session.execute(stmt)

    @connect
    async def update_resources(
        self,
        session: AsyncSession,
        user_id: int,
        *,
        gold: int | None,
        threads: int | None,
        cotton: int | None,
    ) -> None:
        """Adds values to a player's resources.

        This is *incremental*. It will add to the player's current resources.

        Parameters
        ----------
        user_id : int
            Discord ID of the player.
        gold : int | None
            Gold to set to if necessary.
        threads : int | None
            Threads to set to if necessary.
        cotton : int | None
            Cotton to set to if necessary.

        Raises
        ------
        PlayerNotFoundError
            If the player does not exist.
        """

        player = await self.select_player_by_userid(user_id=user_id)

        if not player:
            raise PlayerNotFoundError

        values = {}

        if gold:
            values["gold"] = player.gold + gold

        if threads:
            values["threads"] = player.threads + threads

        if cotton:
            values["cotton"] = player.cotton + cotton

        if not values:
            return

        stmt = (
            update(Players)
            .where(Players.player_id == player.player_id)
            .values(**values)
        )

        self.logger.debug("Updating resources for player %s: %s", user_id, values)

        await session.execute(stmt)
