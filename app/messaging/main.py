from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.messaging.config.settings import settings
from app.messaging.exceptions.handlers import register_exception_handlers
from app.messaging.infrastructure.persistence.postgres.session import dispose_engine
from app.messaging.presentation.http.routes import router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Stub: wire Kafka / outbox publisher here when needed (Phase 3).
    yield
    await dispose_engine()


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(router)


def run() -> None:
    import uvicorn

    uvicorn.run(
        "app.messaging.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run()
