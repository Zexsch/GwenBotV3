"""Houses the privacy service."""

import logging
from collections.abc import Sequence

from sqlalchemy import Row, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from gwenbotv3.database import connect
from gwenbotv3.database.models import UserPrivacy
from gwenbotv3.exceptions import UserAlreadyPrivateError, UserNotPrivateError


class PrivacyService:
    """Anything to do with user privacy."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    @connect
    async def select_all_private_users(
        self, session: AsyncSession
    ) -> Sequence[Row[tuple[int]]]:
        """Selects all private users in the DB.

        Returns:
            Sequence[Row[tuple[int]]]: All private users.
        """
        stmt = select(UserPrivacy.user_id)

        return (await session.execute(stmt)).all()

    @connect
    async def select_private_user(
        self, session: AsyncSession, user_id: int
    ) -> UserPrivacy | None:
        """Select a private user.

        Args:
            user_id (int): ID of the user.

        Returns:
            UserPrivacy | None: UserPrivacy if found, else None.
        """
        stmt = select(UserPrivacy).where(UserPrivacy.user_id == user_id)

        return (await session.execute(stmt)).scalar_one_or_none()

    @connect
    async def insert_private_user(self, session: AsyncSession, user_id: int) -> None:
        """Insert a private user.

        Args:
            user_id (int): ID of the user.

        Raises:
            UserAlreadyPrivateError: If the user is already private.
        """
        user_check = await self.select_private_user(user_id=user_id)

        if user_check:
            raise UserAlreadyPrivateError

        user = UserPrivacy(user_id=user_id)

        session.add(user)

    @connect
    async def delete_private_user(self, session: AsyncSession, user_id: int) -> None:
        """Deletes a private user.

        Args:
            user_id (int): ID of the user.

        Raises:
            UserNotPrivateError: If the user is not privated.
        """
        user_check = await self.select_private_user(user_id=user_id)

        if not user_check:
            raise UserNotPrivateError

        stmt = delete(UserPrivacy).where(UserPrivacy.user_id == user_id)

        await session.execute(stmt)
