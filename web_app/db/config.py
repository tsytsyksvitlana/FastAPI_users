from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PG_USER: str
    PG_PASS: str
    PG_NAME: str
    PG_HOST: str
    PG_PORT: str

    echo: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def url(self):
        return (
            f"postgresql+asyncpg://"
            f"{self.PG_USER}:{self.PG_PASS}@"
            f"{self.PG_HOST}:{self.PG_PORT}/{self.PG_NAME}"
        )


settings = Settings()
