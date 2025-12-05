import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .config import DEFAULT_TITLE


@dataclass
class Message:
    role: str
    content: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(role=str(data.get("role", "user")), content=str(data.get("content", "")))

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class Chat:
    id: str
    title: str = DEFAULT_TITLE
    raw_title: str = DEFAULT_TITLE
    custom_title: bool = False
    messages: List[Message] = field(default_factory=list)

    @classmethod
    def new(cls) -> "Chat":
        return cls(id=str(uuid.uuid4()))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Chat":
        messages = [
            Message.from_dict(msg)
            for msg in data.get("messages", [])
            if isinstance(msg, dict) and "content" in msg
        ]
        return cls(
            id=str(data.get("id", uuid.uuid4())),
            title=str(data.get("title", DEFAULT_TITLE)),
            raw_title=str(data.get("raw_title", data.get("title", DEFAULT_TITLE))),
            custom_title=bool(data.get("custom_title", False)),
            messages=messages,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "raw_title": self.raw_title,
            "custom_title": self.custom_title,
            "messages": [m.to_dict() for m in self.messages],
        }
