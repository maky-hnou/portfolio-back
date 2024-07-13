from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MessageBy(str, Enum):
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"


class MessageDTO(BaseModel):
    message_id: UUID = Field(default_factory=uuid4)
    chat_id: UUID
    message_text: str
    message_by: MessageBy
    created_at: datetime = Field(default_factory=datetime.utcnow)
