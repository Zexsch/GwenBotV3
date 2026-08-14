from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gwenbotv3.database.base import Base

if TYPE_CHECKING:
    # For mappings, otherwise we have partial imports
    from gwenbotv3.database.models.stitch_the_gwen.players import Players


class InventoryItem(Base):
    """Each row corresponds to one item."""

    __tablename__ = "inventory"
    # ruff: noqa: RUF012
    __table_args__ = {"mysql_engine": "InnoDB"}

    inventory_item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.player_id"))
    item_id: Mapped[int] = mapped_column(Integer, nullable=False)
    bonus_stats: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSON), default=dict
    )

    # +Levels, not actual item tier, that's defined in the JSON
    tier: Mapped[int] = mapped_column(Integer, default=0)

    equipped: Mapped[bool] = mapped_column(Boolean)

    acquired_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    equipped_unequipped_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # ruff: noqa: UP037
    player_ref: Mapped["Players"] = relationship(back_populates="inventory_ref")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InventoryItem):
            return NotImplemented
        return self.inventory_item_id == other.inventory_item_id

    def __repr__(self) -> str:
        return f"{self.inventory_item_id=}, {self.player_id=}, {self.item_id=}"
