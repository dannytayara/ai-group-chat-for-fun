import anthropic
import streamlit as st

from app_core.config import MAX_AUTO_TURNS, build_system_prompts
from app_core.llm import choose_next_speaker, normalize_name, respond_as
from app_core.state import (
    append_message,
    create_new_chat,
    delete_chat,
    ensure_chat_state,
    get_current_chat,
    get_current_chat_messages,
    move_chat_to_top,
    persist_chats,
    rename_chat,
    set_current_chat,
    update_chat_title,
)
from app_core.ui import inject_sidebar_css, render_messages

st.set_page_config(
    page_title="Alice, Bob, and Dizzy's Chatroom",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

CHATGPT_LOGO = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" width="24" height="24" preserveAspectRatio="xMidYMid meet" style="width:24px;height:24px;max-width:24px;max-height:24px;display:block;">
    <path d="M341.8 72.6C329.5 61.2 310.5 61.2 298.3 72.6L74.3 280.6C64.7 289.6 61.5 303.5 66.3 315.7C71.1 327.9 82.8 336 96 336L112 336L112 512C112 547.3 140.7 576 176 576L464 576C499.3 576 528 547.3 528 512L528 336L544 336C557.2 336 569 327.9 573.8 315.7C578.6 303.5 575.4 289.5 565.8 280.6L341.8 72.6zM304 384L336 384C362.5 384 384 405.5 384 432L384 528L256 528L256 432C256 405.5 277.5 384 304 384z"/>
</svg>
"""

inject_sidebar_css()
ensure_chat_state(st.session_state)

SYSTEM_PROMPTS = build_system_prompts()
client = anthropic.Anthropic()


def render_sidebar() -> None:
    sidebar = st.sidebar
    sidebar.markdown(
        f"<div class='sidebar-top-row'><div class='icon icon-logo'>{CHATGPT_LOGO}</div></div>",
        unsafe_allow_html=True,
    )

    if sidebar.button("New chat", key="sidebar-new-chat", use_container_width=True):
        create_new_chat(st.session_state)
        persist_chats(st.session_state)

    sidebar.markdown("<div class='sidebar-subheader'>Chats</div>", unsafe_allow_html=True)

    for chat in st.session_state.chats:
        c0, c1, c2 = sidebar.columns([6, 1, 1])
        if c0.button(chat.title, key=f"select_{chat.id}", use_container_width=True):
            set_current_chat(st.session_state, chat.id)
        if c1.button("✏️", key=f"edit_{chat.id}"):
            st.session_state["editing_chat_id"] = chat.id
            st.session_state["rename_input"] = chat.raw_title
        if c2.button("🗑️", key=f"del_{chat.id}"):
            st.session_state["deleting_chat_id"] = chat.id

    if st.session_state.get("editing_chat_id"):
        target = st.session_state["editing_chat_id"]
        chat = next((c for c in st.session_state.chats if c.id == target), None)
        if chat:
            sidebar.markdown("---")
            sidebar.markdown(f"**Rename chat:** {chat.title}")
            new_title = sidebar.text_input(
                "New title",
                value=st.session_state.get("rename_input", chat.raw_title),
                key="rename_text",
            )
            if sidebar.button("Save", key="save_rename"):
                rename_chat(st.session_state, target, new_title)
                st.session_state.pop("editing_chat_id", None)
                st.session_state.pop("rename_input", None)
                persist_chats(st.session_state)
                st.rerun()
            if sidebar.button("Cancel", key="cancel_rename"):
                st.session_state.pop("editing_chat_id", None)
                st.session_state.pop("rename_input", None)
                st.rerun()

    if st.session_state.get("deleting_chat_id"):
        target = st.session_state["deleting_chat_id"]
        chat = next((c for c in st.session_state.chats if c.id == target), None)
        if chat:
            sidebar.markdown("---")
            sidebar.warning(f"Delete chat '{chat.title}'? This cannot be undone.")
            if sidebar.button("Confirm delete", key="confirm_delete"):
                delete_chat(st.session_state, target)
                st.session_state.pop("deleting_chat_id", None)
                persist_chats(st.session_state)
                st.rerun()
            if sidebar.button("Cancel", key="cancel_delete"):
                st.session_state.pop("deleting_chat_id", None)
                st.rerun()


def run_auto_turns() -> int:
    chat = get_current_chat(st.session_state)
    last_speaker = chat.messages[-1].role if chat.messages else None
    turns = 0
    while turns < MAX_AUTO_TURNS:
        selection = choose_next_speaker(client, chat.messages, last_speaker)
        next_speaker = normalize_name(selection, SYSTEM_PROMPTS.keys())
        if not next_speaker or next_speaker == "User" or next_speaker not in SYSTEM_PROMPTS:
            break

        response_text = respond_as(client, next_speaker, SYSTEM_PROMPTS, chat.messages)
        if not response_text:
            break

        append_message(chat, next_speaker, response_text)
        persist_chats(st.session_state)
        last_speaker = next_speaker
        turns += 1

    if turns == MAX_AUTO_TURNS:
        st.info("Auto-responses paused. Reply to continue the conversation.")
    return turns


render_sidebar()
st.title("Alice, Bob, and Dizzy's Chatroom")

render_messages(get_current_chat_messages(st.session_state))

prompt = st.chat_input("Enter text here")
if prompt:
    chat = get_current_chat(st.session_state)
    append_message(chat, "user", prompt)
    update_chat_title(chat)
    move_chat_to_top(st.session_state, chat.id)
    persist_chats(st.session_state)

    with st.chat_message("user"):
        st.markdown(prompt)

    new_responses = run_auto_turns()
    if new_responses:
        st.rerun()
