from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gwenbotv3.database.base import Base

if TYPE_CHECKING:
    from gwenbotv3.database.models.servers import Servers
    from gwenbotv3.database.models.users import Users


class Subs(Base):
    __tablename__ = "subs"
    __table_args__ = (
        UniqueConstraint("user_id", "server_id"),
        {"mysql_engine": "InnoDB"},
    )

    sub_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    server_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("servers.server_id"))

    user_ref: Mapped[Users] = relationship(back_populates="subs")
    server_ref: Mapped[Servers] = relationship(back_populates="subs")

    def __repr__(self) -> str:
        return f"<Sub:{self.sub_id}><User:{self.user_id}><Server:{self.server_id}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Subs):
            return NotImplemented
        return self.sub_id == other.sub_id


class Blacklist(Base):
    __tablename__ = "blacklist"
    __table_args__ = (
        UniqueConstraint("user_id", "server_id", "by_owner"),
        {"mysql_engine": "InnoDB"},
    )

    blacklist_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    server_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("servers.server_id"))
    by_owner: Mapped[bool] = mapped_column(Boolean, default=False)

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
