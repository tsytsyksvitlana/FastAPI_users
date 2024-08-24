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

    @property
    def url(self):
        return (
            f"postgresql+asyncpg://"
            f"{self.PG_USER}:{self.PG_PASS}@"
            f"{self.PG_HOST}:{self.PG_PORT}/{self.PG_NAME}"
        )

    @url.setter
    def url(self, new_url: str):
        self._update_db_url(new_url)

    @property
    def test_db_url(self):
        return (
            f"postgresql+asyncpg://"
            f"{self.TEST_PG_USER}:{self.TEST_PG_PASS}@"
            f"{self.TEST_PG_HOST}:{self.TEST_PG_PORT}/{self.TEST_PG_NAME}"
        )

    @test_db_url.setter
    def test_db_url(self, new_test_url: str):
        self._update_db_url(new_test_url, is_test=True)

    def _update_db_url(self, new_url: str, is_test: bool = False):
        """
        Function parses url and updates db url accordingly
        """
        user, password, host, port, name = self._parse_url(new_url)

        if is_test:
            self.TEST_PG_USER = user
            self.TEST_PG_PASS = password
            self.TEST_PG_HOST = host
            self.TEST_PG_PORT = port
            self.TEST_PG_NAME = name
        else:
            self.PG_USER = user
            self.PG_PASS = password
            self.PG_HOST = host
            self.PG_PORT = port
            self.PG_NAME = name

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
