# OAuth Origami Demo

This FastAPI app demonstrates implementing OAuth flow to Auth0, and using the logged-in-User JWT to make API calls to Noteable, and connect to Notebooks in realtime.

## Run

1. `git clone https://github.com/noteable-io/oauth_origami_demo.git`
2. `poetry install`
3. `poetry run uvicorn app.main:app --debug`

## Config

You'll need to update `app/settings.py` with the appropriate Auth0 settings and create a `.env` file with the Auth0 Client ID and Client Secret.

## Demo

1. Navigate to `http://localhost:8000` to see an endpoint that doesn't require Auth0 login.
2. Navigate to `http://localhost:8000/me` to force an Auth0 login and see the logged in users info.
3. Navigate to `http://localhost:8000/project_files` with optional url argument `project_id` to list files in a project. With no param, default to the ChatGPT plugin default project.
4. Navigate to `http://localhost:8000/notebook/{file-id}` to connect to a Notebook in realtime and see the Notebook model output.
5. Navigate to `http://localhost:8000/run_all/{file-id}` to execut eall cells in a Notebook and see the modeled Notebook afterwards.