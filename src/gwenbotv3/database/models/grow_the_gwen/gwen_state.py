from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gwenbotv3.database.base import Base
from gwenbotv3.game import Champion, ResourceLoader

if TYPE_CHECKING:
    # For mappings, otherwise we have partial imports
    from gwenbotv3.database.models.grow_the_gwen.players import Players

gwen_stats = ResourceLoader().get_resource(
    resource_type="player", model=Champion, name="gwen"
)


class GwenState(Base):
    """Current state of Gwen.

    Includes her stats, levels, etc.
    """

    __tablename__ = "gwen_state"
    # ruff: noqa: RUF012
    __table_args__ = {"mysql_engine": "InnoDB"}

    gwen_state_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False
    )
    player_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.player_id"), unique=True
    )

    # Starts at lv1, max lv18 before reset
    # on reset increase elo, which increases base stats
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # stacks
    # Max 5, fill every hour
    fill_stacks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Max 3, fill every 3h
    stitch_stacks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Max 2, fill every 6h
    train_stacks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    last_fill: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    last_stitch: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    last_train: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # stats
    hp_current: Mapped[float] = mapped_column(
        Float, nullable=False, default=gwen_stats.stats.hp
    )
    hp_max: Mapped[float] = mapped_column(
        Float, nullable=False, default=gwen_stats.stats.hp
    )
    ad: Mapped[float] = mapped_column(
        Float, nullable=False, default=gwen_stats.stats.ad
    )
    ap: Mapped[float] = mapped_column(
        Float, nullable=False, default=gwen_stats.stats.ap
    )
    armour: Mapped[float] = mapped_column(
        Float, nullable=False, default=gwen_stats.stats.armour
    )
    mr: Mapped[float] = mapped_column(
        Float, nullable=False, default=gwen_stats.stats.mr
    )

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
    player_ref: Mapped["Players"] = relationship(back_populates="gwen_state_ref")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GwenState):
            return NotImplemented
        return self.player_id == other.player_id

    def __hash__(self) -> int:
        return hash(self.gwen_state_id)

    @property
    def stats(self) -> dict[str, float]:
        """Stats as a dict."""
        return {
            "hp_current": self.hp_current,
            "hp_max": self.hp_max,
            "ad": self.ad,
            "ap": self.ap,
            "armour": self.armour,
            "mr": self.mr,
        }

    @property
    def stacks(self) -> dict[str, int]:
        """Stacks as a dict."""
        return {
            "fill_stacks": self.fill_stacks,
            "stitch_stacks": self.stitch_stacks,
            "train_stacks": self.train_stacks,
        }

    def __repr__(self) -> str:
        return f"{self.player_id=}, {self.level=}, {self.xp=}"
