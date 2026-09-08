from fastapi import status

from app.gateway.exceptions.errors import (
    GatewayError,
    InvalidAccessTokenError,
    UnauthenticatedError,
    UpstreamUnavailableError,
)

EXCEPTION_STATUS_MAP: dict[type[Exception], int] = {
    UpstreamUnavailableError: status.HTTP_502_BAD_GATEWAY,
    UnauthenticatedError: status.HTTP_401_UNAUTHORIZED,
    InvalidAccessTokenError: status.HTTP_401_UNAUTHORIZED,
    GatewayError: status.HTTP_500_INTERNAL_SERVER_ERROR,
}
