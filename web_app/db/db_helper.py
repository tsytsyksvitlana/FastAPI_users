from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from web_app.config import DATABASE_URL
from web_app.db.config import settings


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )


db_helper = DatabaseHelper(url=DATABASE_URL, echo=settings.echo)
