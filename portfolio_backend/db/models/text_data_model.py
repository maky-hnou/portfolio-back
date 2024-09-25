"""Module containing SQLAlchemy models for textual data.

This module defines a `TextDataModel` class that represents textual data entries stored in the database.
The model includes fields for a unique text identifier, filename, textual content, source, topic,
and a timestamp indicating when the text data was created.

Classes:
    TextDataModel: Represents a textual data entity with fields for text ID, filename, content, source, topic, and creation timestamp.

Dependencies:
    - sqlalchemy.orm.Mapped: Type hint for SQLAlchemy mapped class attributes.
    - sqlalchemy.orm.mapped_column: Helper for defining columns in SQLAlchemy models.
    - sqlalchemy.sql.sqltypes.DateTime: SQLAlchemy column type for DateTime.
    - sqlalchemy.sql.sqltypes.String: SQLAlchemy column type for String.
    - portfolio_backend.db.base.Base: Custom base class for SQLAlchemy models in the project.
    - uuid: Standard library for generating UUIDs.
    - datetime: Standard library for working with date and time objects.
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime, String

from portfolio_backend.db.base import Base


class TextDataModel(Base):
    """SQLAlchemy model class representing textual data.

    Attributes:
        __tablename__ (str): The name of the database table for textual data.
        text_id (Mapped[str]): Primary key identifier for each text data entry.
        filename (Mapped[str]): Name of the file associated with the text data.
        text (Mapped[str]): The textual content itself.
        source (Mapped[str]): The source or origin of the text data.
        topic (Mapped[str]): The topic or category to which the text data relates.
        created_at (Mapped[datetime]): Timestamp indicating when the text data was created.

    """

    __tablename__ = "text_data"

    text_id: Mapped[uuid.UUID] = mapped_column(String, primary_key=True)
    filename: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)
    topic: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
