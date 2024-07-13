from datetime import datetime

from pydantic import BaseModel


class ChatDTO(BaseModel):
    chat_id: str
    off_topic_response_count: int = 0
    created_at: datetime
