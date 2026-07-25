from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gwenbotv3.database.base import Base

if TYPE_CHECKING:
    from gwenbotv3.database.models.gwenseek import Gwenseek
    from gwenbotv3.database.models.gwensub import Blacklist, Subs
    from gwenbotv3.database.models.symbols import SymbolUser


class Users(Base):
    __tablename__ = "users"
    # ruff: noqa: RUF012
    __table_args__ = {"mysql_engine": "InnoDB"}

    # Base
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_anonymised: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
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

    # Relations
    gwenseek_entries: Mapped[list[Gwenseek]] = relationship(back_populates="user_ref")
    symbol_counts: Mapped[list[SymbolUser]] = relationship(back_populates="user_ref")
    subs: Mapped[list[Subs]] = relationship(back_populates="user_ref")
    blacklist_entries: Mapped[list[Blacklist]] = relationship(back_populates="user_ref")

    # Funcs
    @property
    def full_user(self) -> str:
        return (
            f"Name: {self.user_name} | ID: {self.user_id} | Anon.: {self.is_anonymised}"
            + f" | Created: {self.created_at} | Modified: {self.modified_at}"
        )

    def __repr__(self) -> str:
        return f"{self.user_id} : {self.user_name}"

    def __str__(self) -> str:
        return self.full_user
