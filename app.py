import json
import re
import uuid
import os
from pathlib import Path

import streamlit as st
import anthropic
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Alice, Bob, and Dizzy's Chatroom",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

SIDEBAR_CSS = """
<style>
:root {
    --sidebar-bg: #f7f7f8;
    --sidebar-border: #ececf1;
    --sidebar-text: #0c0c10;
    --sidebar-muted: #8e8ea0;
}
section[data-testid="stSidebar"] {
    background: var(--sidebar-bg);
    border-right: 1px solid var(--sidebar-border);
    min-width: 288px;
    width: 312px !important;
    max-width: 312px !important;
    flex: 0 0 312px !important;
    opacity: 1 !important;
    margin-left: 0 !important;
    left: 0 !important;
    position: relative !important;
    transform: translateX(0) !important;
    visibility: visible !important;
    box-shadow: none;
    z-index: 2;
    display: block !important;
    pointer-events: auto !important;
}
div[data-testid="collapsedControl"] {
    display: none !important;
}
section[data-testid="stSidebar"] > div:first-child {
    height: 100vh;
    opacity: 1 !important;
    transition: none !important;
    padding: 20px 12px 20px 12px;
    overflow-y: auto;
}
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
    padding: 0;
}
.sidebar-top-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
}
.sidebar-top-row .icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 16px;
    background: #ffffff;
    border: 1px solid var(--sidebar-border);
}
.sidebar-top-row .icon-logo {
    border: none;
    background: none;
}
.sidebar-top-row .icon svg {
    width: 24px;
    height: 24px;
}
section[data-testid="stSidebar"] button[kind="secondary"] {
    border: 1px solid var(--sidebar-border);
    background: #ffffff;
    color: var(--sidebar-text);
    justify-content: flex-start;
    gap: 12px;
    font-weight: 500;
    font-size: 0.95rem;
    border-radius: 12px;
    padding: 12px 14px;
    box-shadow: none;
    margin-bottom: 24px;
}
section[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: #ececf1;
    border-color: #dedee3;
}
section[data-testid="stSidebar"] button[kind="secondary"]::before {
    content: '';
    width: 18px;
    height: 18px;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    margin-right: 4px;
    background-image: url('data:image/svg+xml;utf8,<svg stroke="%230c0c10" fill="none" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" d="M18.38 7.74 9.54 16.6l-3.9.98.99-3.92 8.83-8.85a2.37 2.37 0 1 1 3.35 3.35Z"/><path stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" d="M13.97 5.02 18.98 10.03"/></svg>');
}
.sidebar-subheader {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--sidebar-muted);
    display: flex;
    align-items: center;
    gap: 6px;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    margin: 0 0 12px 4px;
}
.sidebar-subheader .caret {
    font-size: 0.75rem;
    color: var(--sidebar-muted);
}
section[data-testid="stSidebar"] div[role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 24px;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    border-radius: 12px;
    padding: 10px 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    position: relative;
    color: var(--sidebar-text);
}
section[data-testid="stSidebar"] div[role="radiogroup"] label span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: #ececf1;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: #e4e4eb;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    flex-shrink: 0;
    width: 18px;
    height: 18px;
    border-radius: 6px;
    border: 1px solid var(--sidebar-border);
    margin-right: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) > div:first-child {
    opacity: 1;
    border-color: #0c0c10;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) > div:first-child::after {
    content: '';
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #0c0c10;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label::after {
    content: '\\u2022\\u2022\\u2022';
    margin-left: auto;
    color: var(--sidebar-muted);
    font-size: 1.2rem;
    opacity: 0;
    transition: opacity 0.2s ease;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover::after,
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked)::after {
    opacity: 1;
}
.sidebar-profile {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-radius: 12px;
    background: #f1f1f3;
}
.sidebar-profile .avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, #fdb022, #f97316);
    color: #ffffff;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
}
.sidebar-profile .profile-copy {
    display: flex;
    flex-direction: column;
    line-height: 1.1;
    flex: 1;
}
.sidebar-profile .profile-name {
    font-weight: 600;
    color: var(--sidebar-text);
}
.sidebar-profile .profile-plan {
    font-size: 0.8rem;
    color: var(--sidebar-muted);
}
.sidebar-profile .profile-caret {
    font-size: 1.1rem;
    color: var(--sidebar-muted);
}
.chat-context-menu {
    position: fixed;
    display: none;
    background: #ffffff;
    border: 1px solid var(--sidebar-border);
    border-radius: 12px;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.12);
    padding: 6px 0;
    min-width: 180px;
    z-index: 10000;
}
.chat-context-menu button {
    width: 100%;
    background: none;
    border: none;
    text-align: left;
    padding: 10px 18px;
    font-size: 0.9rem;
    color: var(--sidebar-text);
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
}
.chat-context-menu button:hover {
    background: #f3f3f6;
}
.chat-context-menu button.rename {
    font-weight: 500;
}
.chat-context-menu button.rename::before {
    content: '';
    width: 18px;
    height: 18px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="%230c0c10" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.129-1.897l8.933-8.931z"/><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 7.125L16.875 4.5"/><path stroke-linecap="round" stroke-linejoin="round" d="M18 14v4.75A2.25 2.25 0 0115.75 21h-9.5A2.25 2.25 0 014 18.75v-9.5A2.25 2.25 0 016.25 7H11"/></svg>');
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
}
</style>
"""

try:
    st.html(SIDEBAR_CSS)
except AttributeError:
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)


# where to persist chats for this local user
CHATS_FILE = Path(os.path.expanduser("~")) / ".ai_group_chat_chats.json"


def load_chats():
    """Load chats from disk. Returns a list of chat dicts or None on failure."""
    try:
        if not CHATS_FILE.exists():
            return None
        with CHATS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        # If the file is malformed or unreadable, ignore and start fresh
        return None
    return None


def save_chats():
    """Save the current st.session_state.chats to disk. Non-fatal on errors."""
    try:
        CHATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with CHATS_FILE.open("w", encoding="utf-8") as f:
            json.dump(st.session_state.get("chats", []), f, ensure_ascii=False, indent=2)
    except Exception as e:
        # Don't crash the app if saving fails; surface a warning in the UI when possible
        try:
            st.warning("Could not save chats to disk: %s" % str(e))
        except Exception:
            pass


# --- Initialize session state ---
def init_chat_state():
    # Try to load persisted chats first
    if "chats" not in st.session_state:
        saved = load_chats()
        if saved:
            st.session_state.chats = saved
        else:
            st.session_state.chats = [
                {
                    "id": str(uuid.uuid4()),
                    "title": "New chat",
                    "raw_title": "New chat",
                    "custom_title": False,
                    "messages": [],
                }
            ]
    else:
        for chat in st.session_state.chats:
            chat.setdefault("messages", [])
            chat.setdefault("title", "New chat")
            chat.setdefault("raw_title", chat.get("title", "New chat"))
            chat.setdefault("custom_title", False)
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = st.session_state.chats[0]["id"]
    # Ensure persisted state is written back (helps upgrade/clean malformed data)
    save_chats()


init_chat_state()
if "chat_list_radio" not in st.session_state:
    st.session_state.chat_list_radio = st.session_state.current_chat_id


def get_current_chat():
    for chat in st.session_state.chats:
        if chat["id"] == st.session_state.current_chat_id:
            return chat
    # Fallback to the first chat if the current id was not found
    st.session_state.current_chat_id = st.session_state.chats[0]["id"]
    return st.session_state.chats[0]


def get_current_chat_messages():
    return get_current_chat()["messages"]


def set_current_chat(chat_id: str) -> None:
    st.session_state.current_chat_id = chat_id


def truncate_title(text: str, max_length: int = 30) -> str:
    text = text.strip()
    if not text:
        return "New chat"
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def update_chat_title(chat: dict) -> None:
    if chat.get("custom_title"):
        return
    for message in chat.get("messages", []):
        if message["role"] == "user" and message.get("content"):
            chat["raw_title"] = message["content"].strip()
            chat["title"] = truncate_title(chat["raw_title"])
            return
    chat["title"] = "New chat"
    chat["raw_title"] = "New chat"


def move_chat_to_top(chat_id: str) -> None:
    for index, chat in enumerate(st.session_state.chats):
        if chat["id"] == chat_id:
            st.session_state.chats.insert(0, st.session_state.chats.pop(index))
            save_chats()
            break


def create_new_chat() -> None:
    new_chat = {
        "id": str(uuid.uuid4()),
        "title": "New chat",
        "raw_title": "New chat",
        "custom_title": False,
        "messages": [],
    }
    st.session_state.chats.insert(0, new_chat)
    set_current_chat(new_chat["id"])
    st.session_state["chat_list_radio"] = new_chat["id"]
    save_chats()


def find_chat(chat_id: str):
    for chat in st.session_state.chats:
        if chat["id"] == chat_id:
            return chat
    return None


def rename_chat(chat_id: str, new_title: str) -> None:
    chat = find_chat(chat_id)
    if not chat:
        return
    cleaned = new_title.strip()
    if not cleaned:
        chat["custom_title"] = False
        update_chat_title(chat)
        save_chats()
        return
    chat["raw_title"] = cleaned
    chat["title"] = truncate_title(cleaned)
    chat["custom_title"] = True
    save_chats()


CHATGPT_LOGO = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" width="24" height="24" preserveAspectRatio="xMidYMid meet" style="width:24px;height:24px;max-width:24px;max-height:24px;display:block;">
    <!--!Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.-->
    <path d="M341.8 72.6C329.5 61.2 310.5 61.2 298.3 72.6L74.3 280.6C64.7 289.6 61.5 303.5 66.3 315.7C71.1 327.9 82.8 336 96 336L112 336L112 512C112 547.3 140.7 576 176 576L464 576C499.3 576 528 547.3 528 512L528 336L544 336C557.2 336 569 327.9 573.8 315.7C578.6 303.5 575.4 289.5 565.8 280.6L341.8 72.6zM304 384L336 384C362.5 384 384 405.5 384 432L384 528L256 528L256 432C256 405.5 277.5 384 304 384z"/>
</svg>
"""

# COLLAPSE_ICON removed — sidebar uses only the logo now

CHATS_HEADER_HTML = """
<div class="sidebar-subheader">Chats</div>
"""

PROFILE_HTML = """
<div class="sidebar-profile">
  </div>
</div>
"""
def render_sidebar() -> None:
    sidebar = st.sidebar
    sidebar.markdown(
        f"<div class='sidebar-top-row'><div class='icon icon-logo'>{CHATGPT_LOGO}</div></div>",
        unsafe_allow_html=True,
    )

    if sidebar.button("New chat", key="sidebar-new-chat", use_container_width=True):
        create_new_chat()

    sidebar.markdown(CHATS_HEADER_HTML, unsafe_allow_html=True)

    chat_ids = [chat["id"] for chat in st.session_state.chats]
    if not chat_ids:
        create_new_chat()
        chat_ids = [chat["id"] for chat in st.session_state.chats]

    if st.session_state.chat_list_radio not in chat_ids:
        st.session_state.chat_list_radio = chat_ids[0]

    chat_labels = {chat["id"]: chat["title"] for chat in st.session_state.chats}

    selected_chat_id = sidebar.radio(
        "Chats",
        chat_ids,
        label_visibility="collapsed",
        key="chat_list_radio",
        format_func=lambda chat_id: chat_labels.get(chat_id, "New chat"),
    )

    if selected_chat_id != st.session_state.current_chat_id:
        set_current_chat(selected_chat_id)

    sidebar.markdown(PROFILE_HTML, unsafe_allow_html=True)

    payload = {
        "chatIds": chat_ids,
        "chatTitles": [chat.get("raw_title", chat["title"]) for chat in st.session_state.chats],
    }

    rename_event = components.html(
        f"""
        <script>
        const payload = {json.dumps(payload)};
        const doc = window.parent.document;
        const labels = doc.querySelectorAll('section[data-testid="stSidebar"] div[role="radiogroup"] label');
        const menuId = 'chat-context-menu';

        function ensureMenu() {{
            let menu = doc.getElementById(menuId);
            if (!menu) {{
                menu = doc.createElement('div');
                menu.id = menuId;
                menu.className = 'chat-context-menu';
                menu.innerHTML = '<button type="button" class="rename" data-action="rename">Rename</button>';
                doc.body.appendChild(menu);
            }}
            return menu;
        }}

        const menu = ensureMenu();

        function hideMenu() {{
            menu.style.display = 'none';
        }}

        if (!window.parent.__chatMenuGlobalListeners) {{
            doc.addEventListener('click', hideMenu);
            doc.addEventListener('contextmenu', (event) => {{
                if (!event.target.closest('#' + menuId)) {{
                    hideMenu();
                }}
            }});
            doc.addEventListener('scroll', hideMenu, true);
            window.parent.__chatMenuGlobalListeners = true;
        }}

        labels.forEach((label, index) => {{
            const chatId = payload.chatIds[index];
            if (!chatId) return;
            label.dataset.chatId = chatId;
            label.dataset.chatTitle = payload.chatTitles[index] || '';
            if (label.dataset.contextmenuBound === 'true') return;
            label.dataset.contextmenuBound = 'true';
            label.addEventListener('contextmenu', (event) => {{
                event.preventDefault();
                menu.style.display = 'block';
                menu.style.top = `${{event.clientY}}px`;
                menu.style.left = `${{event.clientX}}px`;
                menu.dataset.chatId = chatId;
                menu.dataset.chatTitle = label.dataset.chatTitle || '';
            }});
        }});

        if (!menu.dataset.bound) {{
            menu.addEventListener('click', (event) => {{
                const actionButton = event.target.closest('button[data-action]');
                if (!actionButton) return;
                const action = actionButton.dataset.action;
                hideMenu();
                if (action === 'rename') {{
                    const chatId = menu.dataset.chatId;
                    const currentTitle = menu.dataset.chatTitle || '';
                    const newTitle = window.prompt('Rename chat', currentTitle);
                    if (newTitle !== null) {{
                        const payload = {{ action: 'rename', chatId, title: newTitle }};
                        window.parent.postMessage({{ type: 'streamlit:setComponentValue', value: JSON.stringify(payload) }}, '*');
                    }}
                }}
            }});
            menu.dataset.bound = 'true';
        }}
        </script>
        """,
        height=0,
    )

    if isinstance(rename_event, str) and rename_event:
        try:
            event_payload = json.loads(rename_event)
        except json.JSONDecodeError:
            event_payload = {}
        if event_payload.get("action") == "rename":
            rename_chat(event_payload.get("chatId", ""), event_payload.get("title", ""))
            if hasattr(st, "rerun"):
                st.rerun()
            else:
                st.experimental_rerun()
CHARACTERS = [
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

character_descriptions = [
    f'{character["name"]}: {character["prompt"][8:]}' for character in CHARACTERS
]

SYSTEM_PROMPTS = {}
for character in CHARACTERS:
    SYSTEM_PROMPTS[character["name"]] = (
        f'Your name is {character["name"]}.\n{character["prompt"]}\nYou are in a group conversation with a User, and a couple other characters.'
    )

# Make our Client
client = anthropic.Anthropic()
MODEL = "claude-3-5-sonnet-20241022"


def clean_messages(name):
    cleaned_messages = [
        {
            "role": "assistant" if message["role"] == name else "user",
            "content": f'{message["role"]}: {message["content"]}'
        }
        for message in get_current_chat_messages()
    ]
    return cleaned_messages


def choose_respondent():
    print("Choosing respondent... ", end="")
    participants = ', '.join(SYSTEM_PROMPTS.keys())
    descriptions = '\n- '.join(character_descriptions)
    system_prompt = (
        f"Your job is to look at this group conversation between {participants} and a User and to decide who should speak next.\n"
        f"Here are some descriptions of each of them: \n- {descriptions}\n"
        "- User: A human who created this chat room.\n\n"
        "Answer with only one word: the name of the person to speak next. This could be the User or any other character in the list. Be sure to give the User opportunities to participate. Do not add any extra commentary. If you are unsure, it is ok to pick one of the participants at random to keep the conversation flowing.\n"
        "Respond with only the name."
    )

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=48,
        system=system_prompt,
        messages=clean_messages("referree"),
    )
    print(message.content[0].text)
    return message.content[0].text


def respond(name):
    print("Responding...", end=" ")
    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPTS[name],
        messages=clean_messages(name),
    )
    print("Done")
    return message.content[0].text


# --- Function to simulate sending messages to a backend system ---
def send_messages_to_backend():
    name = re.sub(r"[^a-zA-Z]", "", choose_respondent())
    if name not in SYSTEM_PROMPTS:
        print("User's turn.")
        return []
    return [{"role": name, "content": respond(name)}]

def do_new_turn():
    # Send message to backend and get responses
    responses = send_messages_to_backend()

    if not responses:
        return

    # Persist responses so they display on the next render
    get_current_chat_messages().extend(responses)
    # Persist assistant responses
    save_chats()

    # Trigger a single rerun to refresh the UI once
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# --- Streamlit UI ---
render_sidebar()
st.title("Alice, Bob, and Dizzy's Chatroom")

# Display chat messages
for message in get_current_chat_messages():
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Enter text here"):
    # Add user message to the chat
    chat = get_current_chat()
    chat_messages = chat["messages"]
    chat_messages.append({"role": "user", "content": prompt})
    update_chat_title(chat)
    move_chat_to_top(chat["id"])
    # Persist the new user message and ordering
    save_chats()
    with st.chat_message("user"):
        st.markdown(prompt)

    do_new_turn()

    
