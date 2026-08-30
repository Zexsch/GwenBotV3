from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gwenbotv3.database.base import Base

if TYPE_CHECKING:
    # For mappings, otherwise we have partial imports
    from gwenbotv3.database.models.grow_the_gwen.players import Players


class Inventory(Base):
    """Player's inventory."""

    __tablename__ = "inventory"
    # ruff: noqa: RUF012
    __table_args__ = {"mysql_engine": "InnoDB"}

    inventory_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.player_id"), unique=True
    )

    grid_size_x: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    grid_size_y: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

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
    player_ref: Mapped["Players"] = relationship(back_populates="inventory_ref")

    item_ref: Mapped[list["InventoryItem"]] = relationship(
        back_populates="inventory_ref"
    )
    equipped_item_ref: Mapped[list["EquippedItems"]] = relationship(
        back_populates="inventory_ref"
    )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Inventory):
            return NotImplemented
        return self.inventory_id == other.inventory_id

    def __hash__(self) -> int:
        return hash(self.inventory_id)

    def __repr__(self) -> str:
        return (
            f"{self.inventory_id=}, {self.player_id=}, "
            f"grid={self.grid_size_x}:{self.grid_size_y}"
        )


class InventoryItem(Base):
    """Each row corresponds to one item."""

    __tablename__ = "inventory_item"
    # ruff: noqa: RUF012
    __table_args__ = {"mysql_engine": "InnoDB"}

    inventory_item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inventory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory.inventory_id")
    )

    item_id: Mapped[int] = mapped_column(Integer, nullable=False)
    bonus_stats: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSON), default=dict
    )

    # +Levels, not actual item tier, that's defined in the JSON
    tier: Mapped[int] = mapped_column(Integer, default=0)

    acquired_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    inventory_ref: Mapped["Inventory"] = relationship(back_populates="item_ref")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InventoryItem):
            return NotImplemented
        return self.inventory_item_id == other.inventory_item_id

    def __hash__(self) -> int:
        return hash(self.inventory_item_id)

    def __repr__(self) -> str:
        return f"{self.inventory_item_id=}, {self.item_id=}, {self.tier=}"


class EquippedItems(Base):
    """Items currently equipped."""

    __tablename__ = "equipped_items"
    # ruff: noqa: RUF012
    __table_args__ = (
        UniqueConstraint("inventory_id", "slot", name="uq_equipped_inv_slot"),
        {"mysql_engine": "InnoDB"},
    )

    equipped_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inventory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory.inventory_id")
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_item.inventory_item_id")
    )
    slot: Mapped[int] = mapped_column(Integer, nullable=False)

    equipped_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    inventory_ref: Mapped["Inventory"] = relationship(
        back_populates="equipped_item_ref"
    )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EquippedItems):
            return NotImplemented
        return self.equipped_id == other.equipped_id

    def __hash__(self) -> int:
        return hash(self.equipped_id)

    def __repr__(self) -> str:
        return f"{self.equipped_id=}, {self.inventory_id=}, {self.item_id=}"
