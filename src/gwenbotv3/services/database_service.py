"""Houses the Database Service."""

import datetime
import logging

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from gwenbotv3.database import connect
from gwenbotv3.database.models import Gwenseek, Subs, Users


class DatabaseService:
    """Interacts with the database itself, not any tables.

    Any and all changes that act upon the database directly, such as
    configuration, triggers, etc go in here. For table specific logic,
    see the other services."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    @connect
    async def purge_stale_users(self, session: AsyncSession) -> None:
        """Deletes user data for users that haven't been active.

        This will set is_anonymised for users to True, removing their username
        from the database. It will also remove any active GwenBot subscriptions
        and Gwenseek history.
        """
        cutoff = datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(days=180)
        epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.UTC)

        last_activity = func.greatest(
            Users.modified_at,
            func.coalesce(func.max(Subs.created_at), epoch),
            func.coalesce(func.max(Gwenseek.created_at), epoch),
        )

        s_stmt = (
            select(Users.user_id)
            .outerjoin(Subs, Subs.user_id == Users.user_id)
            .outerjoin(Gwenseek, Gwenseek.user_id == Users.user_id)
            .group_by(Users.user_id, Users.modified_at)
            .having(last_activity < cutoff)
        )
        stale_user_ids = (await session.execute(s_stmt)).scalars().all()

        if not stale_user_ids:
            return

        d_stmt_1 = delete(Subs).where(Subs.user_id.in_(stale_user_ids))
        await session.execute(d_stmt_1)

        d_stmt_2 = delete(Gwenseek).where(Gwenseek.user_id.in_(stale_user_ids))
        await session.execute(d_stmt_2)

        stmt = (
            update(Users)
            .where(Users.user_id.in_(stale_user_ids))
            .where(Users.user_name != "Unknown User")
            .values(user_name="Unknown User")
        )

        await session.execute(stmt)
