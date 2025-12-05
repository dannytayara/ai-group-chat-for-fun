import json
from typing import List, Optional

from .config import CHATS_FILE
from .models import Chat


def load_chats() -> Optional[List[Chat]]:
    """Load chats from disk; return None if missing or malformed."""
    if not CHATS_FILE.exists():
        return None
    try:
        with CHATS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return None
        chats = [Chat.from_dict(item) for item in data if isinstance(item, dict)]
        return chats or None
    except Exception as exc:  # pragma: no cover - defensive guard
        print(f"Failed to load chats: {exc}")
        return None


def save_chats(chats: List[Chat]) -> None:
    """Persist chats to disk; non-fatal on failure."""
    try:
        CHATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with CHATS_FILE.open("w", encoding="utf-8") as f:
            json.dump([chat.to_dict() for chat in chats], f, ensure_ascii=False, indent=2)
    except Exception as exc:  # pragma: no cover - defensive guard
        print(f"Could not save chats: {exc}")
