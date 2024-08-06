import asyncio
from contextlib import asynccontextmanager

import uvloop
from fastapi import FastAPI

from web_app.db.db_helper import db_helper
from web_app.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI(title="Fox project", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}
