"""Module containing SQLAlchemy models for messages in a chat system.

This module defines a `MessageModel` class that represents message-related data stored in the database.
The model includes fields for a unique message identifier, foreign key to the chat, message text, sender ID,
and a timestamp indicating when the message was created.

Classes:
    MessageModel: Represents a message entity with fields for message ID, chat ID, message text, sender, and creation timestamp.

Dependencies:
    - sqlalchemy.orm.Mapped: Type hint for SQLAlchemy mapped class attributes.
    - sqlalchemy.orm.mapped_column: Helper for defining columns in SQLAlchemy models.
    - sqlalchemy.sql.sqltypes.UUID: SQLAlchemy column type for UUID.
    - sqlalchemy.sql.sqltypes.DateTime: SQLAlchemy column type for DateTime.
    - sqlalchemy.sql.sqltypes.String: SQLAlchemy column type for String.
    - sqlalchemy.ForeignKey: SQLAlchemy ForeignKey for setting up relationships between tables.
    - portfolio_backend.db.base.Base: Custom base class for SQLAlchemy models in the project.
    - uuid: Standard library for generating UUIDs.
    - uuid.uuid4: Function for generating a random UUID.
    - datetime: Standard library for working with date and time objects.
"""

import uuid
from datetime import datetime
from uuid import uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import UUID, DateTime, String

from portfolio_backend.db.base import Base


class MessageModel(Base):
    """SQLAlchemy model class representing messages in a chat system.

    Attributes:
        __tablename__ (str): The name of the database table for messages.
        message_id (Mapped[str]): Unique identifier for each message, stored as UUID.
        chat_id (Mapped[str]): Foreign key referencing the chat to which the message belongs.
        message_text (Mapped[str]): Content of the message.
        message_by (Mapped[str]): Identifier of the user who sent the message.
        created_at (Mapped[datetime]): Timestamp indicating when the message was created.

    """

    __tablename__ = "messages"

    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chats.chat_id", ondelete="CASCADE"),
        nullable=False,
    )
    message_text: Mapped[str] = mapped_column(String)
    message_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
