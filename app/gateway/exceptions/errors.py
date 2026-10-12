class GatewayError(Exception):
    """Base exception for gateway-level errors."""


class UpstreamUnavailableError(GatewayError):
    """Raised when an upstream service cannot be reached."""

    def __init__(self, service: str, detail: str | None = None) -> None:
        self.service = service
        message = detail or f"Upstream service '{service}' is unavailable"
        super().__init__(message)


class UnauthenticatedError(GatewayError):
    """Raised when a required Bearer token is missing or malformed."""


class InvalidTokenError(GatewayError):
    """Raised when a Bearer access token is invalid or expired."""


class RateLimitExceededError(GatewayError):
    """Raised when a client exceeds an edge rate limit."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Try again later.",
        *,
        retry_after: int = 60,
    ) -> None:
        super().__init__(message)
        self.retry_after = retry_after
