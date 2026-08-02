"""Houses the ``SymbolCounter`` and ``SymbolUser`` ORM models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gwenbotv3.database.base import Base

if TYPE_CHECKING:
    from gwenbotv3.database.models.servers import Servers
    from gwenbotv3.database.models.users import Users


class SymbolCounter(Base):
    """Symbol Counter ORM Model.

    I'm too tired of this fucking piece of shit to explain it.
    See the help cog instead."""

    __tablename__ = "symbol_counter"
    __table_args__ = ({"mysql_engine": "InnoDB"},)

    symbol_id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int] = mapped_column(Integer, default=0)
    latest_user: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.user_id"), nullable=True
    )
    server_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("servers.server_id"), unique=True, nullable=False
    )
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    symbol: Mapped[str] = mapped_column(String(200), nullable=False, default="?")
    creating_user: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id"), nullable=False
    )
    strict: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    strict_channel: Mapped[int] = mapped_column(BigInteger, nullable=True)
    setup_at: Mapped[datetime] = mapped_column(
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
    last_recount: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # ruff: noqa: UP037
    server_ref: Mapped["Servers"] = relationship(back_populates="symbol_count")
    latest_user_ref: Mapped["Users"] = relationship(foreign_keys=[latest_user])
    creating_user_ref: Mapped["Users"] = relationship(foreign_keys=[creating_user])

    def __repr__(self) -> str:
        return f"{self.server_id} : {self.amount}"

    def __str__(self) -> str:
        return (
            f"<{self.symbol_id=}> <{self.server_id=}> <{self.channel_id=}> "
            f"<{self.amount=}> <{self.symbol=}> <{self.creating_user=}> "
            f"<{self.setup_at=}>"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SymbolCounter):
            return NotImplemented
        return self.symbol_id == other.symbol_id


class SymbolUser(Base):
    """Symbol User ORM Model.

    I'm too tired of this fucking piece of shit to explain it.
    See the help cog instead."""

    __tablename__ = "symbol_user"
    __table_args__ = (
        UniqueConstraint("user_id", "symbols_server"),
        {"mysql_engine": "InnoDB"},
    )

    s_user_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id"), nullable=False
    )
    symbols_server: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("servers.server_id"), nullable=False
    )
    amount: Mapped[int] = mapped_column(BigInteger, default=0)

    user_ref: Mapped[Users] = relationship(back_populates="symbol_counts")
    server_ref: Mapped[Servers] = relationship(back_populates="symbol_user_entries")

    def __repr__(self) -> str:
        return f"<{self.user_id=}>,<{self.symbols_server=}>,<{self.amount=}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SymbolUser):
            return NotImplemented
        return self.s_user_id == other.s_user_id
