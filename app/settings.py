from pydantic import BaseSettings


class Settings(BaseSettings):
    AUTH0_CLIENT_ID: str  # read from .env
    AUTH0_CLIENT_SECRET: str  # read from .env
    # Values below are for running in our local development stack
    # Work with Noteable eng team to update these to appropriate production values
    AUTH0_DOMAIN: str = "noteable-development.us.auth0.com"
    AUTH0_REDIRECT_URI: str = "http://localhost:8000/auth0/callback"
    AUTH0_AUDIENCE: str = "https://apps.noteable.live/gate"
    NOTEABLE_API_URL: str = "http://localhost:8001/api"

    class Config:
        env_file = ".env"


settings = Settings()
