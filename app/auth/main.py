from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.auth.config.settings import settings
from app.auth.exceptions.handlers import register_exception_handlers
from app.auth.infrastructure.persistence.postgres.session import dispose_engine
from app.auth.infrastructure.persistence.redis.client import close_redis, init_redis
from app.auth.presentation.http.routes import router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_redis()
    yield
    await close_redis()
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
        "app.auth.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run()
