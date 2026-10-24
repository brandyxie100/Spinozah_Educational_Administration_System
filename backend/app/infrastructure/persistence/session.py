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


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _get_shared_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the process-wide session factory, creating it on first use.

    A single engine/pool is reused across requests; creating one per request
    let a new pool's teardown race the previous request's connection cleanup,
    occasionally orphaning a connection in Postgres as `idle in transaction`
    and wedging the event loop for every later request.
    """
    global _engine, _session_factory
    if _session_factory is None:
        _engine = create_engine()
        _session_factory = create_session_factory(_engine)
    return _session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields a request-scoped DB session."""
    session_factory = _get_shared_session_factory()
    async with session_factory() as session:
        yield session
