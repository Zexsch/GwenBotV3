"""Houses the User Service."""

import logging

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from gwenbotv3.database import connect
from gwenbotv3.database.models import Users
from gwenbotv3.exceptions import (
    UserIdOrNameNotGivenError,
    UserIsAnonymisedError,
    UserNotAnonymisedError,
    UserNotFoundError,
)


class UserService:
    """Interacts with the users database table."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    @connect
    async def select_user(self, session: AsyncSession, user_id: int) -> Users | None:
        """Selects a user by their user_id primary key.

        Parameters
        ----------
        user_id : int
            ID of the user.

        Returns
        -------
        Users | None
            Users if found, else None.
        """
        return await session.get(Users, user_id)

    @connect
    async def update_username(
        self, session: AsyncSession, user_id: int, user_name: str
    ) -> None:
        """Updates a username.

        Parameters
        ----------
        user_id : int
            ID of the user.
        user_name : str
            Current name of the user.
        """
        stmt = update(Users).where(Users.user_id == user_id).values(user_name=user_name)
        await session.execute(stmt)

    @connect
    async def insert_user(
        self, session: AsyncSession, user_id: int, user_name: str
    ) -> None:
        """Inserts a user into the database.

        Parameters
        ----------
        user_id : int
            ID of the user.
        user_name : str
            Name of the user. NOT server specific nicknames.
        """
        # Better have this here than not; having empty users in the DB would be bad.
        if user_id is None or user_name is None:  # type: ignore[redundant-expr]
            raise UserIdOrNameNotGivenError

        user = await self.select_user(user_id)

        if user and user.user_name == user_name:
            return

        if not user:
            user = Users(user_id=user_id, user_name=user_name)

            self.logger.info("Adding user: %s", repr(user))
            session.add(user)
            return

        if user.user_name != user_name:
            await self.update_username(user_name=user_name, user_id=user_id)

    @connect
    async def anonymise_user(self, session: AsyncSession, user_id: int) -> None:
        """Anonymises a user.

        See the privacy cog for what anonymisation does.

        Parameters
        ----------
        user_id : int
            ID of the user.

        Raises
        ------
        UserNotFoundError
            If the user isn't in the database.
        UserIsAnonymisedError
            If the user is already anonymised.
        """
        user = await self.select_user(user_id)
        if not user:
            raise UserNotFoundError

        if user.is_anonymised:
            raise UserIsAnonymisedError

        stmt = (
            update(Users)
            .where(Users.user_id == user_id)
            .values(is_anonymised=True, user_name="Unknown User")
        )
        self.logger.info("Anonymising user: %s", user_id)
        await session.execute(stmt)

    @connect
    async def unanonymise_user(
        self, session: AsyncSession, user_id: int, user_name: str
    ) -> None:
        """Unanonymises a user.

        See the privacy cog for what anonymisation does.

        Parameters
        ----------
        user_id : int
            ID of the user.
        user_name : str
            Name of the user.

        Raises
        ------
        UserNotFoundError
            If the user is not in the database.
        UserNotAnonymisedError
            If the user is not anonymised.
        """
        user = await self.select_user(user_id)

        if not user:
            raise UserNotFoundError

        if not user.is_anonymised:
            raise UserNotAnonymisedError

        stmt = (
            update(Users)
            .where(Users.user_id == user_id)
            .values(is_anonymised=False, user_name=user_name)
        )
        self.logger.info("Unanonymising user: %s", repr(user))
        await session.execute(stmt)
