import asyncio
from contextlib import asynccontextmanager

import uvloop
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # startup
    # async with db_helper.engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    yield
    # shutdown
    # await db_helper.dispose()


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI(title="Fox project", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}
