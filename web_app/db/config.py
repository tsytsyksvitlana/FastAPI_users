from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PG_USER: str
    PG_PASS: str
    PG_NAME: str
    PG_HOST: str
    PG_PORT: str

    TEST_PG_USER: str
    TEST_PG_PASS: str
    TEST_PG_NAME: str
    TEST_PG_HOST: str
    TEST_PG_PORT: str

    echo: bool = True

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    def url(self):
        return (
            f"postgresql+asyncpg://"
            f"{self.PG_USER}:{self.PG_PASS}@"
            f"{self.PG_HOST}:{self.PG_PORT}/{self.PG_NAME}"
        )

    def test_db_url(self):
        return (
            f"postgresql+asyncpg://"
            f"{self.TEST_PG_USER}:{self.TEST_PG_PASS}@"
            f"{self.TEST_PG_HOST}:{self.TEST_PG_PORT}/{self.TEST_PG_NAME}"
        )


settings = Settings()
