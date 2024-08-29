from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    echo: bool = True

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def url(self):
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @url.setter
    def url(self, new_url: str):
        self._update_db_url(new_url)

    def _update_db_url(self, new_url: str):
        """
        Function parses url and updates db url accordingly
        """
        user, password, host, port, name = self._parse_url(new_url)
        self.POSTGRES_USER = user
        self.POSTGRES_PASSWORD = password
        self.POSTGRES_HOST = host
        self.POSTGRES_PORT = port
        self.POSTGRES_DB = name

    def _parse_url(self, url: str):
        """
        Function parses url into components
        """
        url_parts = url.split("@")
        credentials, host_info = url_parts[0].split("://")[1], url_parts[1]
        user, password = credentials.split(":")
        host, port_name = host_info.split(":")
        port, name = port_name.split("/")

        return user, password, host, port, name


settings = Settings()


class TestSettings(Settings):
    model_config = ConfigDict(env_file=".env.test", env_file_encoding="utf-8")


test_settings = TestSettings()
