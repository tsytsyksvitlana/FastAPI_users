import os

from dotenv import load_dotenv

from web_app.db.config import settings

ENV = os.getenv("ENV")

if ENV == "TEST":
    load_dotenv(".env.test")
else:
    load_dotenv(".env")


DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{settings.PG_USER}:{settings.PG_PASS}@"
    f"{settings.PG_HOST}:{settings.PG_PORT}/{settings.PG_NAME}"
)
