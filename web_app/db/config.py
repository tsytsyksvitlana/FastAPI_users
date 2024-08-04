import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PG_USER: str = os.getenv("PG_USER")
    PG_PASS: str = os.getenv("PG_PASS")
    PG_NAME: str = os.getenv("PG_NAME")
    PG_HOST: str = os.getenv("PG_HOST")
    PG_PORT: str = os.getenv("PG_PORT")


settings = Settings()
