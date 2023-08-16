import asyncio
import uuid
from typing import List, Optional

import httpx
import structlog
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from origami.clients.api import APIClient
from origami.models.api.files import File
from origami.models.api.users import User
from origami.models.notebook import Notebook

from app.auth0 import auth_router
from app.dependencies import api_client
from app.settings import settings

logger = structlog.get_logger(__name__)

app = FastAPI()

router = APIRouter()


@app.get("/")
async def index():
    """Endpoint that doesn't require authentication"""
    return {"message": "Hello World!"}


@app.get("/me")
async def get_current_user(api_client: APIClient = Depends(api_client)) -> User:
    """Show currently-logged-in Noteable User information"""
    try:
        return await api_client.user_info()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code, detail=e.response.json()
        )


@app.get("/projects")
async def list_projects(
    project_id: Optional[uuid.UUID] = None, api_client: APIClient = Depends(api_client)
) -> List[File]:
    """List all projects in a file, or in the Users default origamist project"""
    if not project_id:
        logger.info(
            "Listing files for users default Origamist (ChatGPT plugin) project"
        )
        user_info = await api_client.user_info()
        project_id = user_info.origamist_default_project_id
    return await api_client.list_project_files(project_id)


@app.get("/notebook/{file_id}")
async def get_notebook(
    file_id: uuid.UUID, api_client: APIClient = Depends(api_client)
) -> Notebook:
    """Get the current model of the Notebook, including squashing any realtime updates"""
    logger.info("Downloading Notebook and applying realtime updates")
    rtu_client = await api_client.connect_realtime(file_id)
    logger.info("Notebook is up to date")
    return rtu_client.builder.nb


@app.get("/run_all/{file_id}")
async def run_all(file_id: uuid.UUID, api_client: APIClient = Depends(api_client)):
    """Run all cells in a notebook"""
    logger.info("Downloading Notebook and applying realtime updates")
    rtu_client = await api_client.connect_realtime(file_id)
    if rtu_client.kernel_state == "not_started":
        logger.info("No running Kernel, launching Kernel now")
        await api_client.launch_kernel(file_id)
        logger.info("Kernel is launched, waiting for idle status")
        await rtu_client.wait_for_kernel_idle()
    logger.info("Queueing execute requests")
    queued_execution = await rtu_client.queue_execution(run_all=True)
    logger.info("Waiting for execution to complete", queued_execution=queued_execution)
    try:
        await asyncio.wait_for(asyncio.gather(*queued_execution), timeout=10)
    except asyncio.TimeoutError:
        logger.warning("Execution timed out, returning as-is")
    return rtu_client.builder.nb


@app.get("/logout")
async def logout(request: Request):
    """Log user out of Auth0 so they can try login flow again"""
    url = f"https://{settings.AUTH0_DOMAIN}/v2/logout?returnTo=http://localhost:8000/"
    response = RedirectResponse(url=url)
    if request.cookies.get("noteable_jwt"):
        response.delete_cookie("noteable_jwt")
    return response


app.include_router(auth_router, tags=["auth"], include_in_schema=False)
app.include_router(router)
