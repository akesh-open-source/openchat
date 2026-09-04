from fastapi import status

from app.gateway.exceptions.errors import GatewayError, UpstreamUnavailableError

EXCEPTION_STATUS_MAP: dict[type[Exception], int] = {
    UpstreamUnavailableError: status.HTTP_502_BAD_GATEWAY,
    GatewayError: status.HTTP_500_INTERNAL_SERVER_ERROR,
}
