from fastapi import FastAPI

app = FastAPI(title="Fox project")


@app.get("/")
async def root():
    return {"message": "Hello World"}
