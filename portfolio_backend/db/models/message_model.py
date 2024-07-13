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
