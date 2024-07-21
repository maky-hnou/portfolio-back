from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class TextDataDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    text_id: UUID = Field(default_factory=uuid4)
    filename: str
    text: str
    source: str
    topic: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
