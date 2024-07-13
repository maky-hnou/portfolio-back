from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ChatDTO(BaseModel):
    chat_id: UUID = Field(default_factory=uuid4)
    off_topic_response_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
