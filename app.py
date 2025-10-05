import re
import uuid

import streamlit as st
import anthropic

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
</style>
"""

try:
    st.html(SIDEBAR_CSS)
except AttributeError:
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)


# --- Initialize session state ---
def init_chat_state():
    if "chats" not in st.session_state:
        st.session_state.chats = [
            {
                "id": str(uuid.uuid4()),
                "title": "New chat",
                "messages": [],
            }
        ]
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = st.session_state.chats[0]["id"]


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
    st.session_state["chat_list_radio"] = chat_id


def truncate_title(text: str, max_length: int = 30) -> str:
    text = text.strip()
    if not text:
        return "New chat"
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def update_chat_title(chat: dict) -> None:
    for message in chat.get("messages", []):
        if message["role"] == "user" and message.get("content"):
            chat["title"] = truncate_title(message["content"])
            return
    chat["title"] = "New chat"


def move_chat_to_top(chat_id: str) -> None:
    for index, chat in enumerate(st.session_state.chats):
        if chat["id"] == chat_id:
            st.session_state.chats.insert(0, st.session_state.chats.pop(index))
            break


def create_new_chat() -> None:
    new_chat = {
        "id": str(uuid.uuid4()),
        "title": "New chat",
        "messages": [],
    }
    st.session_state.chats.insert(0, new_chat)
    set_current_chat(new_chat["id"])



CHATGPT_LOGO = """
<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#0c0c10" stroke-width="1.2">
  <path d="M12.03 2.25c1.76 0 3.42.69 4.67 1.94a6.58 6.58 0 0 1 1.7 2.93 5.2 5.2 0 0 1 3.54 4.96c0 .92-.23 1.83-.68 2.64a5.19 5.19 0 0 1-1.72 1.83 6.59 6.59 0 0 1-4.65 4.88 6.59 6.59 0 0 1-8.2-4.72 5.2 5.2 0 0 1-3.54-4.96c0-.92.23-1.83.68-2.64a5.22 5.22 0 0 1 1.72-1.83 6.59 6.59 0 0 1 4.65-4.88 6.56 6.56 0 0 1 2.83-.65Z" opacity="0.12" fill="#0c0c10"/>
  <path d="M11.99 4.4a4.53 4.53 0 0 1 3.21 1.33 4.51 4.51 0 0 1 1.1 1.83 3.6 3.6 0 0 1 2.52 3.44c0 .6-.15 1.2-.49 1.72-.33.52-.78.91-1.28 1.2a4.54 4.54 0 0 1-6.54 3.27 4.53 4.53 0 0 1-3.21-1.33 4.51 4.51 0 0 1-1.1-1.83 3.6 3.6 0 0 1-2.52-3.44c0-.6.15-1.2.49-1.72.33-.52.78-.91 1.28-1.2a4.54 4.54 0 0 1 6.54-3.27Zm2.26 3.55-2.82-1.44a.53.53 0 0 0-.77.47v2.9L8.62 8.32a.53.53 0 0 0-.78.46v2.88l-.5-.25a.53.53 0 0 0-.48.95l2.81 1.44a.53.53 0 0 0 .78-.46v-2.9l2.05 1.02v2.88a.53.53 0 0 0 .78.46l2.81-1.44a.53.53 0 0 0-.47-.95l-.5.26V8.41a.53.53 0 0 0-.78-.46Z"/>
</svg>
"""

COLLAPSE_ICON = """
<svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg" stroke="#0c0c10" stroke-width="1.2" fill="none">
  <rect x="3" y="4" width="6" height="12" rx="1.2"/>
  <rect x="11" y="4" width="6" height="12" rx="1.2"/>
</svg>
"""

CHATS_HEADER_HTML = """
<div class="sidebar-subheader">Chats <span class="caret">&#9662;</span></div>
"""

PROFILE_HTML = """
<div class="sidebar-profile">
  <div class="avatar">DA</div>
  <div class="profile-copy">
    <span class="profile-name">Danny Tayara</span>
    <span class="profile-plan">Pro</span>
  </div>
  <div class="profile-caret">&#8250;</div>
</div>
"""
def render_sidebar() -> None:
    sidebar = st.sidebar
    sidebar.markdown(
        f"<div class='sidebar-top-row'><div class='icon icon-logo'>{CHATGPT_LOGO}</div><div class='icon icon-collapse'>{COLLAPSE_ICON}</div></div>",
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
    with st.chat_message("user"):
        st.markdown(prompt)

    do_new_turn()

    
