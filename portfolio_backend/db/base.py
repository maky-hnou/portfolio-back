from sqlalchemy.orm import DeclarativeBase

from portfolio_backend.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
