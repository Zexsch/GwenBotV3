"""Houses the ``Users`` ORM Model."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gwenbotv3.database.base import Base

if TYPE_CHECKING:
    from gwenbotv3.database.models.gwenseek import Gwenseek
    from gwenbotv3.database.models.gwensub import Subs
    from gwenbotv3.database.models.stitch_the_gwen.players import Players
    from gwenbotv3.database.models.symbols import SymbolUser


class Users(Base):
    """ORM Model for Discord users.

    Relations
    ---------
    :gwenseek_entries: Maps to the ``Gwenseek`` model
    :symbol_counts: Maps to the ``SymbolUser`` model
    :subs: Maps to the ``Subs`` model
    :blacklist_entries: Maps to the ``Blacklist`` model
    """

    __tablename__ = "users"
    # ruff: noqa: RUF012
    __table_args__ = {"mysql_engine": "InnoDB"}

    # Base
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_anonymised: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    modified_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relations
    # ruff: noqa: UP037
    gwenseek_entries: Mapped[list["Gwenseek"]] = relationship(back_populates="user_ref")
    symbol_counts: Mapped[list["SymbolUser"]] = relationship(back_populates="user_ref")
    subs: Mapped[list["Subs"]] = relationship(back_populates="user_ref")
    player: Mapped[list["Players"]] = relationship(back_populates="user_ref")

    # Funcs
    @property
    def full_user(self) -> str:
        """Full user string, including all information."""
        return (
            f"Name: {self.user_name} | ID: {self.user_id} | Anon.: {self.is_anonymised}"
            f" | Created: {self.created_at} | Modified: {self.modified_at}"
        )

    def __repr__(self) -> str:
        return f"{self.user_id} : {self.user_name}"

    def __str__(self) -> str:
        return self.full_user

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Users):
            return NotImplemented
        return self.user_id == other.user_id

    def __hash__(self) -> int:
        return hash(self.user_id)
