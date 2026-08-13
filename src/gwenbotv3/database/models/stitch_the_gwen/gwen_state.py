from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gwenbotv3.database.base import Base
from gwenbotv3.game import Champion, ResourceLoader

if TYPE_CHECKING:
    # For mappings, otherwise we have partial imports
    from gwenbotv3.database.models.stitch_the_gwen.players import Players

gwen_stats = ResourceLoader().get_resource(
    resource_type="player", model=Champion, name="gwen"
)


class GwenState(Base):
    __tablename__ = "gwen_state"
    # ruff: noqa: RUF012
    __table_args__ = {"mysql_engine": "InnoDB"}

    gwen_state_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False
    )
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.player_id"))

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
    aspd: Mapped[float] = mapped_column(
        Float, nullable=False, default=gwen_stats.stats.aspd
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
