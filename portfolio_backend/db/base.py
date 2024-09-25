"""Module defining the base class for SQLAlchemy models.

This module provides a `Base` class that serves as the foundation for all SQLAlchemy models in the application.
The `Base` class inherits from `DeclarativeBase` and is associated with custom metadata.

Classes:
    Base: A base class for SQLAlchemy models that includes custom metadata.

Dependencies:
    - sqlalchemy.orm.DeclarativeBase: The SQLAlchemy base class for declarative model definitions.
    - portfolio_backend.db.meta.meta: Custom metadata used for the SQLAlchemy models in the project.
"""

from sqlalchemy.orm import DeclarativeBase

from portfolio_backend.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
