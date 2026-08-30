from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gwenbotv3.database.base import Base

if TYPE_CHECKING:
    # For mappings, otherwise we have partial imports
    from gwenbotv3.database.models.grow_the_gwen.gwen_state import GwenState
    from gwenbotv3.database.models.grow_the_gwen.inventory import Inventory
    from gwenbotv3.database.models.grow_the_gwen.match_log import MatchLog
    from gwenbotv3.database.models.users import Users


class Players(Base):
    """Everything related to the player itself.

    For Gwen specific rows, see gwen_state"""

    __tablename__ = "players"
    # ruff: noqa: RUF012
    __table_args__ = {"mysql_engine": "InnoDB"}

    player_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    gold: Mapped[int] = mapped_column(BigInteger, default=0)
    threads: Mapped[int] = mapped_column(Integer, default=0)
    cotton: Mapped[int] = mapped_column(Integer, default=0)

    # 0 for iron, +1 per elo
    elo: Mapped[Integer] = mapped_column(Integer, default=0)

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

    # ruff: noqa: UP037
    user_ref: Mapped["Users"] = relationship(back_populates="player")
    gwen_state_ref: Mapped["GwenState"] = relationship(
        back_populates="player_ref", cascade="all, delete-orphan"
    )
    inventory_ref: Mapped[list["Inventory"]] = relationship(
        back_populates="player_ref", cascade="all, delete-orphan"
    )
    match_ref: Mapped[list["MatchLog"]] = relationship(
        back_populates="player_ref", cascade="all, delete-orphan"
    )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Players):
            return NotImplemented
        return self.player_id == other.player_id

    def __hash__(self) -> int:
        return hash(self.player_id)

    def __repr__(self) -> str:
        return f"{self.player_id} - {self.user_id}: {self.gold=}, {self.elo=}"
