import datetime
import logging

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from gwenbotv3.database import connect
from gwenbotv3.database.models import Gwenseek, Subs, Users


class DatabaseService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    @connect
    async def purge_stale_users(self, session: AsyncSession) -> None:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=180)
        epoch = datetime.datetime(1970, 1, 1)

        last_activity = func.greatest(
            Users.modified_at,
            func.coalesce(func.max(Subs.created_at), epoch),
            func.coalesce(func.max(Gwenseek.created_at), epoch),
        )

        stmt = (
            select(Users.user_id)
            .outerjoin(Subs, Subs.user_id == Users.user_id)
            .outerjoin(Gwenseek, Gwenseek.user_id == Users.user_id)
            .group_by(Users.user_id, Users.modified_at)
            .having(last_activity < cutoff)
        )
        stale_user_ids = (await session.execute(stmt)).scalars().all()

        if not stale_user_ids:
            return

        stmt = delete(Subs).where(Subs.user_id.in_(stale_user_ids))
        await session.execute(stmt)

        stmt = delete(Gwenseek).where(Gwenseek.user_id.in_(stale_user_ids))
        await session.execute(stmt)

        stmt = (
            update(Users)
            .where(Users.user_id.in_(stale_user_ids))
            .where(Users.user_name != "Unknown User")
            .values(user_name="Unknown User")
        )

        await session.execute(stmt)
