import re
from typing import Dict, Iterable, List, Optional, Sequence

import anthropic

from .config import HISTORY_WINDOW, MODEL, REFEREE_MODEL, character_descriptions
from .models import Message


def _format_history(messages: Sequence[Message], speaker: str, history_window: int = HISTORY_WINDOW) -> List[dict]:
    trimmed = list(messages[-history_window:])
    formatted = []
    for msg in trimmed:
        role = "assistant" if msg.role == speaker else "user"
        formatted.append({"role": role, "content": f"{msg.role}: {msg.content}"})
    return formatted


def _referee_system_prompt(last_speaker: Optional[str]) -> str:
    participants = ", ".join([d.split(":")[0] for d in character_descriptions()])
    descriptions = "\n- ".join(character_descriptions())
    last = last_speaker or "None"
    return (
        f"Your job is to look at this group conversation between {participants} and a User "
        f"and decide who should speak next. The last speaker was: {last}.\n"
        f"Here are descriptions of each character:\n- {descriptions}\n"
        "- User: A human who created this chat room.\n\n"
        "Answer with only one word: the name of the person to speak next. "
        "Do not pick the same person twice in a row. Give the User opportunities to participate. "
        "If unsure, pick any participant at random to keep the conversation flowing."
    )


def normalize_name(raw_name: Optional[str], allowed: Iterable[str]) -> Optional[str]:
    if not raw_name:
        return None
    cleaned = re.sub(r"[^a-zA-Z]", "", raw_name).strip()
    for candidate in allowed:
        if cleaned.lower() == candidate.lower().replace(" ", ""):
            return candidate
    if cleaned.lower() == "user":
        return "User"
    return cleaned or None


def choose_next_speaker(
    client: anthropic.Anthropic,
    messages: Sequence[Message],
    last_speaker: Optional[str],
) -> Optional[str]:
    conversation = _format_history(messages, speaker="referee")
    try:
        response = client.messages.create(
            model=REFEREE_MODEL,
            max_tokens=48,
            system=_referee_system_prompt(last_speaker),
            messages=conversation,
        )
        if not response.content:
            return None
        return response.content[0].text.strip()
    except Exception as exc:  # pragma: no cover - defensive guard
        print(f"Referee selection failed: {exc}")
        return None


def respond_as(
    client: anthropic.Anthropic,
    name: str,
    system_prompts: Dict[str, str],
    messages: Sequence[Message],
    max_tokens: int = 1024,
) -> Optional[str]:
    system_prompt = system_prompts.get(name)
    if not system_prompt:
        return None
    conversation = _format_history(messages, speaker=name)
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=conversation,
        )
        if not response.content:
            return None
        return response.content[0].text
    except Exception as exc:  # pragma: no cover - defensive guard
        print(f"{name} failed to respond: {exc}")
        return None
