"""Houses the Servers ORM Model."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gwenbotv3.database.base import Base

if TYPE_CHECKING:
    from gwenbotv3.database.models.gwenseek import Gwenseek
    from gwenbotv3.database.models.gwensub import Blacklist, Subs
    from gwenbotv3.database.models.symbols import SymbolCounter, SymbolUser


class Servers(Base):
    """ORM Model for Discord guilds.

    Relations
    ---------
    :gwenseek_entries: Maps to the ``Gwenseek`` model
    :symbol_count: Maps to the ``SymbolCounter`` model
    :symbol_user_entries: Maps to the ``SymbolUser`` model
    :subs: Maps to the ``Subs`` model
    :blacklist_entries: Maps to the ``Blacklist`` model
    """

    __tablename__ = "servers"
    # ruff: noqa: RUF012
    __table_args__ = {"mysql_engine": "InnoDB"}

    # Base
    server_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    owner_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    member_count: Mapped[int] = mapped_column(Integer, nullable=True)
    quote: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    prefix: Mapped[str] = mapped_column(String(5), nullable=False, default="+")

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
    gwenseek_entries: Mapped[list["Gwenseek"]] = relationship(
        back_populates="server_ref"
    )
    symbol_count: Mapped["SymbolCounter"] = relationship(
        back_populates="server_ref", uselist=False
    )
    symbol_user_entries: Mapped[list["SymbolUser"]] = relationship(
        back_populates="server_ref"
    )
    subs: Mapped[list["Subs"]] = relationship(back_populates="server_ref")
    blacklist_entries: Mapped[list["Blacklist"]] = relationship(
        back_populates="server_ref"
    )

    # Funcs
    @property
    def full_server(self) -> str:
        """Full server string, will all information."""
        return (
            f"ID: {self.server_id} | Owner: {self.owner_id} | "
            f"Members: {self.member_count} | Quote: {self.quote} | "
            f"Prefix: {self.prefix} | "
            f"Created: {self.created_at} | Modified: {self.modified_at}"
        )

    def __repr__(self) -> str:
        return str(self.server_id)

    def __str__(self) -> str:
        return self.full_server

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Servers):
            return NotImplemented
        return self.server_id == other.server_id

    def __hash__(self) -> int:
        return hash(self.server_id)
