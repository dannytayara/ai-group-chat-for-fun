Create a virtual environment with 

    python -m venv .venv

Activate the environment 

    source .venv/bin/activate

Make sure your Anthropic API key is set as an environment variable called `ANTHROPIC_API_KEY`

Install requirements: 

    pip install -r requirements.txt

Run it with 

    streamlit run app.py --server.runOnSave true

# TODO:

- Make it so all clients update instead of just one (this might be a streamlit thing)
- Allow each client to specify their own username and multiple people can participate in the chat
- Lots of improvement to make (like structured output for the referee, better type safety)
- Ability for user to select different models for the chat
- Edit the different characters. Add new ones. Add or remove existing characters from the room.
- Update the chat history to be stored in a database (could be unique per user?)
- User login? Maybe later...