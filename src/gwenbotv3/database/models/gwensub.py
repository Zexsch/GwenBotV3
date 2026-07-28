"""Houses the Subs and Blacklist ORM Models."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gwenbotv3.database.base import Base

if TYPE_CHECKING:
    # For mappings, otherwise we have partial imports
    from gwenbotv3.database.models.servers import Servers
    from gwenbotv3.database.models.users import Users


class Subs(Base):
    """ORM Model for GwenBot Subscriptions.

    Once a user is subscribed in a server,
    GwenBot will respond in chat if a user mentions gwen.

    Relations
    ---------
    :user_ref: Foreign key relationship to the ``Users`` table.
    :server_ref: Foreign key relationship to the ``Servers`` table.
    """

    __tablename__ = "subs"
    __table_args__ = (
        UniqueConstraint("user_id", "server_id"),
        {"mysql_engine": "InnoDB"},
    )

    sub_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    server_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("servers.server_id"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    user_ref: Mapped[Users] = relationship(back_populates="subs")
    server_ref: Mapped[Servers] = relationship(back_populates="subs")

    def __repr__(self) -> str:
        return f"<Sub:{self.sub_id}><User:{self.user_id}><Server:{self.server_id}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Subs):
            return NotImplemented
        return self.sub_id == other.sub_id


class Blacklist(Base):
    """ORM Model for GwenBot blacklists.

    Blacklists are a tool for moderators to stop a user
    from interacting with Gwen in specific ways.
    Those include GwenBot Subscriptions or using GwenBot to interact
    with the deepseek API.

    Relations
    ---------
    :user_ref: Foreign key relationship to the ``Users`` table.
    :server_ref: Foreign key relationship to the ``Servers`` table.
    """

    __tablename__ = "blacklist"
    __table_args__ = (
        UniqueConstraint("user_id", "server_id", "by_owner"),
        {"mysql_engine": "InnoDB"},
    )

    blacklist_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    server_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("servers.server_id"))
    by_owner: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    user_ref: Mapped[Users] = relationship(back_populates="blacklist_entries")
    server_ref: Mapped[Servers] = relationship(back_populates="blacklist_entries")

    def __repr__(self) -> str:
        return (
            f"<Sub:{self.blacklist_id}><User:{self.user_id}><Server:{self.server_id}>"
            f"<Owner:{self.by_owner}>"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Blacklist):
            return NotImplemented
        return self.blacklist_id == other.blacklist_id
