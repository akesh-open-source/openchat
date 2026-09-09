from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.gateway.exceptions.errors import GatewayError
from app.gateway.exceptions.mapping import EXCEPTION_STATUS_MAP


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(GatewayError)
    async def gateway_error_handler(
        _request: Request,
        exc: GatewayError,
    ) -> JSONResponse:
        status_code = EXCEPTION_STATUS_MAP.get(
            type(exc),
            EXCEPTION_STATUS_MAP[GatewayError],
        )
        headers: dict[str, str] = {}
        if status_code == status.HTTP_401_UNAUTHORIZED:
            headers["WWW-Authenticate"] = "Bearer"

        return JSONResponse(
            status_code=status_code,
            content={
                "detail": str(exc) or exc.__class__.__name__,
            },
            headers=headers,
        )
