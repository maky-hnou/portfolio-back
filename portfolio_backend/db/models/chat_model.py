"""Module containing SQLAlchemy models for chat entities.

This module defines a `ChatModel` class that represents chat-related data stored in the database.
The model includes fields for a unique chat identifier, off-topic response count, and a timestamp
indicating when the chat was created.

Classes:
    ChatModel: Represents a chat entity with fields for chat ID, off-topic response count, and creation timestamp.

Dependencies:
    - sqlalchemy.orm.Mapped: Type hint for SQLAlchemy mapped class attributes.
    - sqlalchemy.orm.mapped_column: Helper for defining columns in SQLAlchemy models.
    - sqlalchemy.sql.sqltypes.UUID: SQLAlchemy column type for UUID.
    - sqlalchemy.sql.sqltypes.DateTime: SQLAlchemy column type for DateTime.
    - sqlalchemy.sql.sqltypes.Integer: SQLAlchemy column type for Integer.
    - portfolio_backend.db.base.Base: Custom base class for SQLAlchemy models in the project.
    - uuid: Standard library for generating UUIDs.
    - datetime: Standard library for working with date and time objects.
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import UUID, DateTime, Integer

from portfolio_backend.db.base import Base


class ChatModel(Base):
    """SQLAlchemy model class representing chat entities.

    Attributes:
        __tablename__ (str): The name of the database table for chats.
        chat_id (Mapped[str]): Primary key identifier for each chat, stored as UUID.
        off_topic_response_count (Mapped[int]): Number of off-topic responses in the chat.
        created_at (Mapped[datetime]): Timestamp indicating when the chat was created.

    """

    __tablename__ = "chats"

    chat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    off_topic_response_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
