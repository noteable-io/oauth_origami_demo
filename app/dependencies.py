import structlog
from fastapi import Depends, HTTPException, Request
from origami.clients.api import APIClient

from app.settings import settings

logger = structlog.get_logger()


async def bearer_token(request: Request) -> str:
    """
    Returns jwt from Authorization header or noteable_jwt cookie.
    If neither are found, redirect user to /auth0/login
    """
    if request.headers.get("Authorization"):
        # Optionally use FastAPI's bearer_token syntax for extracting bearer token
        _, jwt = request.headers.get("Authorization").split()
        logger.info(f"Found Authorization header with jwt {jwt[:5]}...")
        return jwt
    if request.cookies.get("noteable_jwt"):
        jwt = request.cookies.get("noteable_jwt")
        logger.info(f"Found Authorization cookie with jwt {jwt[:5]}...")
        print(jwt)
        return jwt
    logger.info("No Authorization header/cookie found, redirecting to /auth0/login")
    raise HTTPException(status_code=307, headers={"Location": "/auth0/login"})


async def api_client(jwt: str = Depends(bearer_token)) -> APIClient:
    logger.info("Instantiating APIClient for jwt {jwt[:5]}...")
    return APIClient(jwt, api_base_url=settings.NOTEABLE_API_URL)
