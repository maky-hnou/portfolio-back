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

    chat_id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    off_topic_response_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
