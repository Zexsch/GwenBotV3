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
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    @connect
    async def select_user(self, session: AsyncSession, user_id: int) -> Users | None:
        user = await session.get(Users, user_id)
        return user

    @connect
    async def insert_user(
        self, session: AsyncSession, user_id: int, user_name: str
    ) -> None:
        # Better have this here than not; having empty users in the DB would be bad.
        if user_id is None or user_name is None:  # type: ignore[redundant-expr]
            raise UserIdOrNameNotGivenError

        user = await self.select_user(user_id)

        if user:
            return

        user = Users(user_id=user_id, user_name=user_name)

        self.logger.info("Adding user: %s", repr(user))
        session.add(user)

    @connect
    async def anonymise_user(self, session: AsyncSession, user_id: int) -> None:
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
