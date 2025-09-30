import random
import re

import streamlit as st
import anthropic

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

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
        for message in st.session_state.messages
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

    # Display responses from different characters
    for response in responses:
        st.session_state.messages.append(response)
        with st.chat_message(response["role"]):
            st.markdown(response["content"])

    if responses:
        do_new_turn()

# --- Streamlit UI ---
st.title("Alice, Bob, and Dizzy's Chatroom")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Enter text here"):
    # Add user message to the chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    do_new_turn()

    
