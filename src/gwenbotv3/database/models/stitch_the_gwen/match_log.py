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


class MatchLog(Base):
    __tablename__ = "gwen_state"
    # ruff: noqa: RUF012
    __table_args__ = {"mysql_engine": "InnoDB"}

    match_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.player_id"))

    config: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSON), default=dict)

    result: Mapped[bool] = mapped_column(Boolean, nullable=False)

    enemy_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # 0 for caster, 1 for melee, 2 for cannon, 3 for champ boss, 4 for uber boss
    enemy_type: Mapped[int] = mapped_column(Integer, nullable=False)

    gold_gained: Mapped[int] = mapped_column(Integer, nullable=True)
    xp_gained: Mapped[int] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # ruff: noqa: UP037
    player_ref: Mapped["Players"] = relationship(back_populates="match_ref")
