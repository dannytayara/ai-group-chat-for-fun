from pathlib import Path
from typing import Sequence

import streamlit as st

from .models import Message

SIDEBAR_CSS_PATH = Path(__file__).resolve().parent.parent / "static/sidebar.css"


def inject_sidebar_css() -> None:
    if not SIDEBAR_CSS_PATH.exists():
        return
    css = SIDEBAR_CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_messages(messages: Sequence[Message]) -> None:
    for message in messages:
        with st.chat_message(message.role):
            st.markdown(message.content)
