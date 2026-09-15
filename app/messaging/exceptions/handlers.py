from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.messaging.domain.exceptions import DomainError
from app.messaging.exceptions.mapping import EXCEPTION_STATUS_MAP


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(
        _request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        status_code = EXCEPTION_STATUS_MAP.get(
            type(exc),
            EXCEPTION_STATUS_MAP[DomainError],
        )
        return JSONResponse(
            status_code=status_code,
            content={
                "detail": str(exc) or exc.__class__.__name__,
            },
        )
