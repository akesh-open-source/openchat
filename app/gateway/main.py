from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.gateway.config.settings import settings
from app.gateway.exceptions.handlers import register_exception_handlers
from app.gateway.infrastructure.http.client import close_http_client, init_http_client
from app.gateway.presentation.http.routes import router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_http_client()
    yield
    await close_http_client()


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
        "app.gateway.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run()
