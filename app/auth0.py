import uuid
from urllib.parse import quote, urlencode

import httpx
import structlog
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.settings import settings

logger = structlog.get_logger()
auth_router = APIRouter()


@auth_router.get("/auth0/login")
async def auth0_login():
    """
    Step one of auth0 login process, redirect user to Auth0 with appropriate url params
    """
    base_url = f"https://{settings.AUTH0_DOMAIN}/authorize"
    params = {
        "audience": settings.AUTH0_AUDIENCE,
        "response_type": "code",
        "client_id": settings.AUTH0_CLIENT_ID,
        "redirect_uri": settings.AUTH0_REDIRECT_URI,
        "scope": "openid profile email",
        "state": uuid.uuid4().hex,
    }
    url = base_url + "?" + urlencode(params, quote_via=quote)
    logger.info("Redirecting to auth0", url=url)
    return RedirectResponse(url)


@auth_router.get("/auth0/callback")
async def auth0_callback(code: str):
    """
    Step 1.5 of auth0 login process, auth0 has redirected user back to us. Now we POST to get jwt
    """
    # Optional extra security: check that state in url params matched state you sent out
    # Not done here to keep code minimal
    logger.info("Auth0 callback", code=code)
    url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            json={
                "client_id": settings.AUTH0_CLIENT_ID,
                "client_secret": settings.AUTH0_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.AUTH0_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
    logger.info("Auth0 token response", status_code=resp.status_code)
    # print / log resp.json() here to see access token, id token and other payload info
    if resp.status_code == 200:
        token_data = resp.json()
        jwt = token_data.get("access_token")
    else:
        raise HTTPException(status_code=500, detail="Failed to get access token")
    logger.info(f"Redirecting user to / with noteable_jwt cookie set to {jwt[:5]}...")
    http_response = RedirectResponse("/me")
    http_response.set_cookie("noteable_jwt", jwt)
    return http_response
