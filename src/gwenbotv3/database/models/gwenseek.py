"""Houses the Gwenseek Model.

See the model for more information."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gwenbotv3.database.base import Base

if TYPE_CHECKING:
    # For mappings, otherwise we have partial imports
    from gwenbotv3.database.models.servers import Servers
    from gwenbotv3.database.models.users import Users


class Gwenseek(Base):
    """Model for the ``Gwenseek`` database table.

    This table is used for storing interactions between users and the deepseek API.

    Relations
    ---------
    :user_ref: Foreign key relationship to the ``Users`` table.
    :server_ref: Foreign key relationship to the ``Servers`` table.
    """

    __tablename__ = "gwenseek"
    # ruff: noqa: RUF012
    __table_args__ = {"mysql_engine": "InnoDB"}

    seek_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    server_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("servers.server_id"))
    user_message: Mapped[str] = mapped_column(Text)
    reasoning_content: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # ruff: noqa: UP037
    user_ref: Mapped["Users"] = relationship(back_populates="gwenseek_entries")
    server_ref: Mapped["Servers"] = relationship(back_populates="gwenseek_entries")

    def __repr__(self) -> str:
        return f"Seek: {self.seek_id} | User: {self.user_id} | Server: {self.server_id}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Gwenseek):
            return NotImplemented
        return self.seek_id == other.seek_id

    def __hash__(self) -> int:
        return hash(self.seek_id)
