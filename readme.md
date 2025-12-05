# Alice, Bob, and Dizzy's Chatroom

A Streamlit-based multi-character chat that uses Anthropic models. The code is now split into small modules to keep UI, state, storage, and LLM calls easy to follow.

## Quick start

1) Create a virtual environment
```
python -m venv .venv
source .venv/bin/activate
```

2) Install dependencies
```
pip install -r requirements.txt
```

3) Configure your API key (copy `.env.example` to `.env` and fill in `ANTHROPIC_API_KEY`, or export it)

4) Run the app
```
streamlit run app.py --server.runOnSave true
```

## Project structure

- `app.py` — Streamlit entrypoint (UI flow + wiring)
- `app_core/config.py` — character definitions, model names, tunables (history window, auto-turn cap)
- `app_core/models.py` — small dataclasses for `Chat` and `Message`
- `app_core/state.py` — session-state helpers (create/rename/delete chats, title updates)
- `app_core/llm.py` — referee selection + character responses with Anthropics
- `app_core/storage.py` — JSON persistence to `.data/chats.json`
- `app_core/ui.py` — shared UI helpers and CSS injector
- `static/sidebar.css` — sidebar styling

Chat history is stored locally at `.data/chats.json` (ignored by git). If the file is missing or malformed the app starts fresh.

## Notes

- The auto-responder runs up to 4 turns per user message (configurable via `MAX_AUTO_TURNS` in `config.py`).
- History is windowed when talking to the models to keep prompts compact.
- If you add characters or change models, adjust `CHARACTERS`/`MODEL`/`REFEREE_MODEL` in `config.py`.
