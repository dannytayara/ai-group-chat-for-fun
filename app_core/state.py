from typing import List, Optional

from .config import DEFAULT_TITLE
from .models import Chat, Message
from .storage import load_chats, save_chats


def truncate_title(text: str, max_length: int = 30) -> str:
    cleaned = text.strip()
    if not cleaned:
        return DEFAULT_TITLE
    if len(cleaned) <= max_length:
        return cleaned
    return cleaned[: max_length - 3] + "..."


def ensure_chat_state(state) -> None:
    """Ensure Streamlit session_state has normalized chat objects."""
    if "chats" not in state:
        loaded = load_chats()
        state.chats = loaded if loaded else [Chat.new()]
    else:
        normalized: List[Chat] = []
        for chat in state.chats:
            if isinstance(chat, Chat):
                normalized.append(chat)
            elif isinstance(chat, dict):
                normalized.append(Chat.from_dict(chat))
        state.chats = normalized or [Chat.new()]

    if not state.chats:
        state.chats = [Chat.new()]

    current_id = state.get("current_chat_id")
    if not current_id or not any(chat.id == current_id for chat in state.chats):
        state.current_chat_id = state.chats[0].id


def persist_chats(state) -> None:
    save_chats(state.chats)


def find_chat(state, chat_id: str) -> Optional[Chat]:
    for chat in state.chats:
        if chat.id == chat_id:
            return chat
    return None


def get_current_chat(state) -> Chat:
    chat = find_chat(state, state.current_chat_id)
    if chat:
        return chat
    state.current_chat_id = state.chats[0].id
    return state.chats[0]


def get_current_chat_messages(state) -> List[Message]:
    return get_current_chat(state).messages


def set_current_chat(state, chat_id: str) -> None:
    state.current_chat_id = chat_id


def update_chat_title(chat: Chat) -> None:
    if chat.custom_title:
        return
    for message in chat.messages:
        if message.role == "user" and message.content:
            chat.raw_title = message.content.strip()
            chat.title = truncate_title(chat.raw_title)
            return
    chat.title = DEFAULT_TITLE
    chat.raw_title = DEFAULT_TITLE


def move_chat_to_top(state, chat_id: str) -> None:
    for index, chat in enumerate(state.chats):
        if chat.id == chat_id:
            state.chats.insert(0, state.chats.pop(index))
            break


def create_new_chat(state) -> Chat:
    new_chat = Chat.new()
    state.chats.insert(0, new_chat)
    state.current_chat_id = new_chat.id
    return new_chat


def rename_chat(state, chat_id: str, new_title: str) -> None:
    chat = find_chat(state, chat_id)
    if not chat:
        return
    cleaned = new_title.strip()
    if not cleaned:
        chat.custom_title = False
        update_chat_title(chat)
        return
    chat.raw_title = cleaned
    chat.title = truncate_title(cleaned)
    chat.custom_title = True


def delete_chat(state, chat_id: str) -> None:
    idx = None
    for i, chat in enumerate(state.chats):
        if chat.id == chat_id:
            idx = i
            break
    if idx is None:
        return
    state.chats.pop(idx)
    if not state.chats:
        state.chats = [Chat.new()]
    if state.current_chat_id == chat_id:
        state.current_chat_id = state.chats[0].id


def append_message(chat: Chat, role: str, content: str) -> Message:
    message = Message(role=role, content=content)
    chat.messages.append(message)
    return message
