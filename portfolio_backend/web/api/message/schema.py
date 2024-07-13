from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class MessageBy(str, Enum):
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"


class MessageDTO(BaseModel):
    message_id: str
    chat_id: str
    message_text: str
    message_by: MessageBy
    created_at: datetime
