from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.auth.domain.exceptions import DomainError, InvalidTokenError
from app.auth.exceptions.mapping import EXCEPTION_STATUS_MAP


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
        headers: dict[str, str] = {}
        if isinstance(exc, InvalidTokenError):
            headers["WWW-Authenticate"] = "Bearer"

        return JSONResponse(
            status_code=status_code,
            content={
                "detail": str(exc) or exc.__class__.__name__,
            },
            headers=headers,
        )
