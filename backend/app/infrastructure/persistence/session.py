"""Async SQLAlchemy engine and session factory."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.settings import Settings, get_settings


def create_engine(settings: Settings | None = None) -> AsyncEngine:
    """Create an async SQLAlchemy engine from settings."""
    cfg = settings or get_settings()
    return create_async_engine(
        cfg.database_url,
        echo=cfg.debug,
        pool_pre_ping=True,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Build a session factory bound to the given engine."""
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields a request-scoped DB session."""
    engine = create_engine()
    session_factory = create_session_factory(engine)
    async with session_factory() as session:
        yield session
    await engine.dispose()
