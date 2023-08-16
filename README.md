# OAuth Origami Demo

This FastAPI app demonstrates implementing OAuth flow to Auth0, and using the logged-in-User JWT to make API calls to Noteable, and connect to Notebooks in realtime.

## Run

1. `git clone https://github.com/noteable-io/oauth_origami_demo.git`
2. `poetry install`
3. `poetry run uvicorn app.main:app --debug`

## Config

You'll need to update `app/settings.py` with the appropriate Auth0 settings and create a `.env` file with the Auth0 Client ID and Client Secret.

