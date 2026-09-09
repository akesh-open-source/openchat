from fastapi import status

from app.gateway.exceptions.errors import (
    GatewayError,
    InvalidTokenError,
    UnauthenticatedError,
    UpstreamUnavailableError,
)

# Edge/gateway errors only. Upstream auth domain statuses (400/401/409/…)
# are forwarded as-is by the auth proxy and are not remapped here.
EXCEPTION_STATUS_MAP: dict[type[Exception], int] = {
    UpstreamUnavailableError: status.HTTP_502_BAD_GATEWAY,
    UnauthenticatedError: status.HTTP_401_UNAUTHORIZED,
    InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
    GatewayError: status.HTTP_500_INTERNAL_SERVER_ERROR,
}
