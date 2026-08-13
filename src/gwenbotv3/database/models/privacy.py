"""Houses the UserPrivacy model.

Private users will not trigger on_message listeners."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from gwenbotv3.database.base import Base


# pylint: disable=too-few-public-methods
class UserPrivacy(Base):
    """Any user added in this DB will not trigger on_message listeners."""

    __tablename__ = "user_privacy"
    # ruff: noqa: RUF012
    __table_args__ = {"mysql_engine": "InnoDB"}

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
