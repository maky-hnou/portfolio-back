from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import UUID, DateTime, Integer

from portfolio_backend.db.base import Base


class ChatModel(Base):
    __tablename__ = "chats"

    chat_id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    off_topic_response_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
