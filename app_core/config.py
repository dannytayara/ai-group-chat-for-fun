from pathlib import Path
from typing import Dict, List

DEFAULT_TITLE = "New chat"
MAX_AUTO_TURNS = 4
HISTORY_WINDOW = 30

MODEL = "claude-sonnet-4-5"
REFEREE_MODEL = "claude-3-haiku-20240307"

DATA_DIR = Path(__file__).resolve().parent.parent / ".data"
CHATS_FILE = DATA_DIR / "chats.json"

CHARACTERS: List[Dict[str, str]] = [
    {
        "name": "Alice",
        "prompt": "You are an expert in Shakespeare and always speak in iambic pentameter in an Elizabethan style.",
    },
    {
        "name": "Dizzy",
        "prompt": "You are a dolphin who only speaks in squeaks and clicks but is intelligent and tries very hard to communicate with humans.",
    },
    {
        "name": "Bob",
        "prompt": "You are a professional Tarot card reader, who always speaks by using a tarot card as a metaphor to help other reflect on themselves and to gain guidance for yourself.",
    },
]


def character_descriptions() -> List[str]:
    return [f'{character["name"]}: {character["prompt"]}' for character in CHARACTERS]


def build_system_prompts() -> Dict[str, str]:
    prompts: Dict[str, str] = {}
    for character in CHARACTERS:
        prompts[character["name"]] = (
            f'Your name is {character["name"]}.\n'
            f'{character["prompt"]}\n'
            "You are in a group conversation with a User and a couple other characters. "
            "Keep your responses concise."
        )
    return prompts
