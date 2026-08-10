import logging
from collections.abc import Sequence

from sqlalchemy import Row, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from gwenbotv3.database import connect
from gwenbotv3.database.models import UserPrivacy
from gwenbotv3.exceptions import UserAlreadyPrivateError, UserNotPrivateError


class PrivacyService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @connect
    async def select_all_private_users(
        self, session: AsyncSession
    ) -> Sequence[Row[tuple[int]]]:
        stmt = select(UserPrivacy.user_id)

        return (await session.execute(stmt)).all()

    @connect
    async def select_private_user(
        self, session: AsyncSession, user_id: int
    ) -> UserPrivacy | None:
        stmt = select(UserPrivacy).where(UserPrivacy.user_id == user_id)

        return (await session.execute(stmt)).scalar_one_or_none()

    @connect
    async def insert_private_user(self, session: AsyncSession, user_id: int) -> None:
        user_check = await self.select_private_user(user_id=user_id)

        if user_check:
            raise UserAlreadyPrivateError

        user = UserPrivacy(user_id=user_id)

        session.add(user)

    @connect
    async def delete_private_user(self, session: AsyncSession, user_id: int) -> None:
        user_check = await self.select_private_user(user_id=user_id)

        if not user_check:
            raise UserNotPrivateError

        stmt = delete(UserPrivacy).where(UserPrivacy.user_id == user_id)

        await session.execute(stmt)
