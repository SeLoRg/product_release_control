from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from src.backend.core.configs.config import settings


class Database:
    def __init__(self, echo: bool, url: str):
        self._engine = create_async_engine(url=url, echo=echo)
        self._session_factory = async_sessionmaker(
            bind=self._engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    async def get_session(self) -> AsyncSession:
        async with self._session_factory() as sess:
            yield sess

    @property
    def async_session_factory(self):
        return self._session_factory


db = Database(url=settings.postgres_url, echo=False)
