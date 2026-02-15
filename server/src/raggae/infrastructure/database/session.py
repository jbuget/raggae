from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from raggae.infrastructure.config.settings import settings

engine: AsyncEngine = create_async_engine(settings.database_url, echo=False, future=True)
SessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
