Create a virtual environment with 

    python -m venv .venv

Activate the environment 

    source .venv/bin/activate

Make sure your Anthropic API key is set as an environment variable called `ANTHROPIC_API_KEY`

Install requirements: 

    pip install -r requirements.txt

Run it with 

    streamlit run app.py --server.runOnSave true

