from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PG_USER: str
    PG_PASS: str
    PG_NAME: str
    PG_HOST: str
    PG_PORT: str

    echo: bool = True

    class Config:
        env_file: Optional[str] = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, _env_file: Optional[str] = None, **kwargs):
        if _env_file:
            self.Config.env_file = _env_file
        super().__init__(**kwargs)

    def url(self):
        return (
            f"postgresql+asyncpg://"
            f"{self.PG_USER}:{self.PG_PASS}@"
            f"{self.PG_HOST}:{self.PG_PORT}/{self.PG_NAME}"
        )


settings = Settings()
