from datetime import datetime

from pydantic import BaseModel


class TextDataDTO(BaseModel):
    text_id: str
    filename: str
    text: str
    source: str
    topic: str
    created_at: datetime
