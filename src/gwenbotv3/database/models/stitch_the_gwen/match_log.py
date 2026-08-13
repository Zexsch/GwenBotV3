from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gwenbotv3.config.enums import EnemyType
from gwenbotv3.database.base import Base
from gwenbotv3.game import Config, ResourceLoader

if TYPE_CHECKING:
    # For mappings, otherwise we have partial imports
    from gwenbotv3.database.models.stitch_the_gwen.players import Players

config = ResourceLoader().get_resource(
    resource_type="config", model=Config, name="general"
)


class MatchLog(Base):
    """Each row is one match."""

    __tablename__ = "match_log"
    # ruff: noqa: RUF012
    __table_args__ = {"mysql_engine": "InnoDB"}

    match_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.player_id"))
    version: Mapped[str] = mapped_column(
        String(32), nullable=False, default=config.version
    )
    rng_seed: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # win/loss
    result: Mapped[bool] = mapped_column(Boolean, nullable=False)

    enemy_id: Mapped[int] = mapped_column(Integer, nullable=False)

    enemy_type: Mapped[EnemyType] = mapped_column(Enum(EnemyType), nullable=False)

    player_cooldowns: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSON), default=dict, nullable=False
    )
    enemy_cooldowns: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSON), default=dict, nullable=False
    )

    gold_gained: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    xp_gained: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # ruff: noqa: UP037
    player_ref: Mapped["Players"] = relationship(back_populates="match_ref")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MatchLog):
            return NotImplemented
        return self.match_id == other.match_id

    def __repr__(self) -> str:
        return f"{self.match_id=}, {self.result=}, {self.enemy_id=}, {self.enemy_type=}"
