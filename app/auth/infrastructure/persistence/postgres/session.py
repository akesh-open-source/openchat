from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.auth.config.settings import settings

# One engine (and pool) for the process. Sessions are created per request
# and must be closed so connections return to this pool.
# Schema changes are applied via Alembic (`alembic upgrade head`), not at startup.
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh AsyncSession for this API call.

    Lifecycle:
    - success → commit, then close (connection returns to pool)
    - failure → rollback, then close (connection returns to pool)

    Closing in ``finally`` prevents leaked sessions/connections that
    otherwise exhaust Postgres under concurrent load.
    """
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    else:
        await session.commit()
    finally:
        await session.close()


async def dispose_engine() -> None:
    """Dispose the shared engine/pool on application shutdown."""
    await engine.dispose()
