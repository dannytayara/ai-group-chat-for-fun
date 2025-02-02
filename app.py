import os
import random
import re
import io
import contextlib
import json

import streamlit as st
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# --- Persist chat history to a JSON file ---

HISTORY_FILE = "conversation.json"

def save_messages():
    """Save messages to a JSON file in the correct dictionary format."""
    with open(HISTORY_FILE, "w") as f:
        json.dump({"messages": st.session_state.messages}, f, indent=4)

def load_messages():
    """Load messages from a JSON file if it exists, or initialize an empty list."""
    if "messages" not in st.session_state:
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                st.session_state.messages = data.get("messages", [])
        except (FileNotFoundError, json.JSONDecodeError):
            st.session_state.messages = []

CHARACTERS = [
    {
        "name": "Miss Honey",
        "prompt": "You are Miss Honey, the Staff Educator on our team. Your role is to bridge gaps in staff knowledge/education as quickly as possible, personalizing phrasing and approach to the education/experience level of the person being addressed. You research the internet and your Knowledge files to fact-check before each response you contribute to the conversation, to ensure accuracy and relevancy",
    },
    {
        "name": "Mindy",
        "prompt": """You are a Visual Note-Taker specializing in Systems Thinking, graph modeling, semantic graphs/networks, and statistics. You translate all conversation to a graph model flowing left to right based on time elapsed, consisting of:
            - Pill shaped nodes (aligned vertically on the right, and aligned horizontally with their respective thread) = overall goal / desired objective
            - circular nodes = applicable insights we've realized
            - rectangular nodes = actions we've taken
            - diamonds = decisions we've made
            - edges = topical / relational connections
            - edges with arrows = causal/sequential relationships
            - 50percent opacity nodes— that act as a funnel between current/past nodes and the goals that they work toward— suggested nodes that would be statistically most likely to bridge the gap between our current state and the goal we are working toward.
            - colors: nodes should be turned **red** if they apply to the highest-priority goal (according to our values), **yellow** if they apply to a goal that is unresolved but not current priority, and **green** if they apply to a goal that has already been achieved.

            When asked to output your current diagram, output it using Mermaid syntax, referencing the Mermaid documentation in your Knowledge Files.""",
    },
    {
        "name": "Mark",
        "prompt": "You are an expert in Branding, customer relations, communications, community building, and trust building. You specialize in AI products.",
    },
    {
        "name": "Karl",
        "prompt": "You are an AI Economist, specializing in impact of AI on economy and human behavior. You have knowledge of OpenAI's latest technology and their documentation in your knowledgebase.",
    },
    {
        "name": "Greta",
        "prompt": "You have a PhD in Climate / environmental science, and you specialize in the impact of AI on environment. Skilled in machine learning, data analysis, and data visualization.",
    },
    {
        "name": "Norma",
        "prompt": "Your name is Norma. You have a quadruple PhD in Cognitive Psychology, Cognitive neuroscience, UX design / HCI, and Machine Learning. You specialize in ADHD, Systems Thinking, graph modeling, and semantic graphs/networks. You also know how to read and write code, which you learned so you could communicate with developers better. You are also familiar with OpenAI's latest technologies such as OpenAI's Assistants, Chat completions, and Custom GPTs. If you need to reference documentation for OpenAI's technologies, then retrieve the documentation csv from your knowledgebase."
    },
    {
        "name": "Alan",
        "prompt": "You are an AI Engineer specializing in AI/ML, Deep learning, Neural networks, RLHF, databases, data visualization, graph modeling, and semantic graphs/networks. You have knowledge of OpenAI's latest technologies. If at any point during conversation you think it is relevant to reference OpenAI's technologies, retrieve the files in your Knowledge base to refresh yourself on the documentation.",
    },
    {
        "name": "Sam Altman",
        "prompt": "You are Sam Altman. You excel at giving guidance for people pursuing AI startups and AGI. You have deep knowledge of Y Combinator's approach, and the ways Y Combinator's principles apply to the needs of startups that are pursuing AI-powered applications and/or AGI. You search the web for current research in applicable areas before each response you give. You think step-by-step through each question and answer. You articulate your thought process in the same way Sam Altman does, while you craft your response. You then reflect on your response to evaluate its alignment to your (Sam Altman's) values and knowledge, then edit it before producing the final stage of your response.",
    },
]

character_descriptions = [
    f'{character["name"]}: {character["prompt"][8:]}' for character in CHARACTERS
]

SYSTEM_PROMPTS = {}
for character in CHARACTERS:
    SYSTEM_PROMPTS[character["name"]] = (
        f'Your name is {character["name"]}. {character["prompt"]} You are in a group conversation with your team, with the goal of developing an application that serves as a digital working memory for people who have ADHD. The aim is to develop an intelligent system capable of visualizing conversation processes in real-time, using a knowledge graph that illustrates action threads, goals, and the recommended (predicted) optimal/best next action for each goal according to user values. You are discussing the approach that should be taken to develop this application. It is possible you might leverage Python for development, and machine learning frameworks for predictive modeling. The desired result of this effort is a functional prototype that allows us to test whether the application successfully improves user focus in conversations.'
    )

# Make our Client
client = anthropic.Anthropic()
MODEL = "claude-3-5-sonnet-20241022"

def clean_messages(name):
    cleaned_messages = []
    for message in st.session_state.messages:
        prefix = "User: " if message["role"] == "user" else f"Assistant ({message['role']}): "
        cleaned_messages.append({
            "role": "assistant" if message["role"] == name else "user",
            "content": prefix + message["content"]
        })
    return cleaned_messages

def choose_respondent():
    if st.session_state.debug_mode:
        st.sidebar.text("Choosing respondent...")

    character_description_text = "\n- ".join(character_descriptions)
    
    system_prompt = (
        "Your job is to look at this group conversation between "
        f"{', '.join(SYSTEM_PROMPTS.keys())} and a User and to decide who should speak next, "
        "based on who would contribute the most valuable insight which would push the conversation "
        "forward innovatively and reach new emergent heights of understanding and action.\n\n"
        "Here are descriptions of each of the participants:\n\n"
        f"{character_description_text}\n"
        "- User: A person who initiated this conversation.\n\n"
        "Answer with only one word: the name of the participant who should speak next. "
        "This could be the User or any other character in the list. Be sure to give the User "
        "opportunities to participate. Do not add any extra commentary. If you are unsure, it is "
        "ok to pick one of the participants at random to keep the conversation flowing.\n"
        "Respond with only the name."
    )

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        system=system_prompt,
        messages=clean_messages("referree"),
    )
    
    # Extract just the name from the response
    response_text = message.content[0].text.strip()
    
    # Find the matching character name
    for character in CHARACTERS:
        if character["name"].lower() in response_text.lower():
            if st.session_state.debug_mode:
                st.sidebar.text(f"Found matching character: {character['name']}")
            return character["name"]
    
    # If no match found, return User
    if "user" in response_text.lower():
        if st.session_state.debug_mode:
            st.sidebar.text("Selected: User")
        return "User"
    
    if st.session_state.debug_mode:
        st.sidebar.text(f"No match found for response: {response_text}")
    return None

def extract_python_code(text):
    """Extract Python code from triple backticks in AI responses."""
    match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
    return match.group(1) if match else None

def execute_python_code(code):
    """Safely execute Python code and capture output."""
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code, {}, {})
    except Exception as e:
        return f"Execution Error: {str(e)}"
    return output.getvalue()

def respond(name):
    if st.session_state.debug_mode:
        st.sidebar.text(f"Generating response for {name}...")
        
    try: 
        message = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            system=SYSTEM_PROMPTS[name],
            messages=clean_messages(name),
        )

        response_text = message.content[0].text
        
        if st.session_state.debug_mode:
            st.sidebar.text(f"Response received from {name}")
            st.sidebar.text(f"Length: {len(response_text)} chars")

        return {"role": name, "content": response_text}

    except Exception as e:
        if st.session_state.debug_mode:
            st.sidebar.error(f"Error in respond(): {str(e)}")
        return None

def send_messages_to_backend():
    name = choose_respondent()
    
    if st.session_state.debug_mode:
        st.sidebar.text(f"Processing for: {name}")

    if not name or name not in SYSTEM_PROMPTS:
        if st.session_state.debug_mode:
            st.sidebar.text("User's turn.")
        return []

    response = respond(name)
    if response and response.get("content"):
        return [response]
    return []


def do_new_turn():
    if st.session_state.debug_mode:
        st.sidebar.text("Starting new turn...")
    
    # Get responses from backend
    responses = send_messages_to_backend()
    
    # Process and display each response
    for response in responses:
        if response and response.get("content"):
            if st.session_state.debug_mode:
                st.sidebar.text(f"Processing response from {response['role']}")
            
            # Add to session state
            st.session_state.messages.append(response)
            save_messages()
            
            # Display in UI
            with st.chat_message(response["role"]):
                st.markdown(response["content"])
                
                # Handle Python code if present
                python_code = extract_python_code(response["content"])
                if python_code:
                    execution_result = execute_python_code(python_code)
                    with st.expander("📜 View Generated Python Code"):
                        st.code(python_code, language="python")
                    if execution_result:
                        with st.expander("🔍 Code Output"):
                            st.text(execution_result)
            
            if st.session_state.debug_mode:
                st.sidebar.text("✅ Response displayed")
    
    # If we got responses, recursively do another turn
    if responses:
        if st.session_state.debug_mode:
            st.sidebar.text("Starting next turn recursively...")
        do_new_turn()
    elif st.session_state.debug_mode:
        st.sidebar.text("No responses to continue with")

# --- Initialize session state ---
load_messages()

if "edit_message_index" not in st.session_state:
    st.session_state.edit_message_index = None

if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

# --- Streamlit UI ---
st.title("A conversation about developing an application for people with ADHD")

# Add debug toggle in sidebar
with st.sidebar:
    debug_enabled = st.checkbox(
        "Enable Debug Mode",
        value=st.session_state.debug_mode,
        key="unique_debug_toggle"
    )
    
    if debug_enabled != st.session_state.debug_mode:
        st.session_state.debug_mode = debug_enabled
        
    if st.session_state.debug_mode:
        st.sidebar.markdown("### Debug Information")
        st.sidebar.text(f"Messages in state: {len(st.session_state.messages)}")

# Display chat messages
for i, message in enumerate(st.session_state.messages):
    if st.session_state.debug_mode and i < 5:
        st.sidebar.text(f"📩 Message {i}: {message['role']}")
    
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        if message["role"] == "user":
            if st.button(f"Edit Message {i+1}", key=f"edit_{i}"):
                st.session_state.edit_message_index = i
                st.rerun()

# Handle message editing
if st.session_state.edit_message_index is not None:
    index = st.session_state.edit_message_index
    edited_text = st.text_area("Edit your message:", st.session_state.messages[index]["content"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Resubmit", key=f"resubmit_{index}"):
            if st.session_state.debug_mode:
                st.sidebar.text(f"Editing message {index}")
            
            st.session_state.messages[index]["content"] = edited_text
            save_messages()
            st.session_state.edit_message_index = None
            do_new_turn()
            
    with col2:
        if st.button("Cancel"):
            st.session_state.edit_message_index = None

# Undo Last Message Button
if st.button("Undo Last Message"):
    if st.session_state.messages:
        st.session_state.messages.pop()
        save_messages()
        st.rerun()

# Chat input
if prompt := st.chat_input("Enter text here"):
    if st.session_state.debug_mode:
        st.sidebar.text(f"New message: {prompt}")
        
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_messages()
    with st.chat_message("user"):
        st.markdown(prompt)

    do_new_turn()