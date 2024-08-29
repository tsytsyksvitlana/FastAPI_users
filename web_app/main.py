import asyncio
import logging
from contextlib import asynccontextmanager

import uvloop
from fastapi import FastAPI

from web_app.auth.router import router as auth_router

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        logger.info("Starting up...")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

    yield

    try:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


app = FastAPI(title="Fox project", lifespan=lifespan)
app.include_router(auth_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
