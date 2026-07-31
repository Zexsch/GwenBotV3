"""For the SQLAlchemy base model.

Defined outside ``models`` to avoid partial imports."""

from sqlalchemy.orm import DeclarativeBase


# pylint: disable=too-few-public-methods
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    Inherit from this in every SQLAlchemy model."""

    # pylint: disable=unnecessary-pass
