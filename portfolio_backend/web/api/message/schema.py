import re
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core.core_schema import ValidationInfo


class MessageBy(str, Enum):
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"


class MessageDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    message_id: UUID = Field(default_factory=uuid4)
    chat_id: UUID
    message_text: str
    message_by: MessageBy
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("message_text", mode="before")
    @classmethod
    def replace_pronouns(cls: type["MessageDTO"], v: str, values: ValidationInfo) -> str:
        if values.data.get("message_by") == "human":
            return re.sub(
                r"\b(he|him|his)\b",
                lambda match: "Hani" if match.group(0) in {"he", "him"} else "Hani's",
                v,
            )
        return v
