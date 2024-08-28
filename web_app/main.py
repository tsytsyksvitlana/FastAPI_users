import asyncio

import uvloop
from fastapi import FastAPI

from web_app.auth.router import router as auth_router

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI(title="Fox project")
app.include_router(auth_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
