import re
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    def replace_pronouns(cls, v: str, values: Any) -> str:
        if values.data.get("message_by") == "human":
            print(f"human, so editing {v}")
            return re.sub(
                r"\b(he|him|his)\b",
                lambda match: "Hani" if match.group(0) in {"he", "him"} else "Hani's",
                v,
            )
        print(f"ai, so not editing {v}")
        return v
