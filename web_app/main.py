import asyncio
import logging
from contextlib import asynccontextmanager

import uvloop
from fastapi import FastAPI

from web_app.api.v1.routers.auth.router import router as auth_router
from web_app.api.v1.routers.users.router import router as users_router
from web_app.db.config import settings
from web_app.logging.logger import setup_logger
from web_app.services.auth.config import redis_client

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logger(settings.ENV_MODE)
    logger.info("Starting up...")
    yield
    await redis_client.close()
    logger.info("Shutting down...")


app = FastAPI(title="Fox project", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(users_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
