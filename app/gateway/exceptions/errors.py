class GatewayError(Exception):
    """Base exception for gateway-level errors."""


class UpstreamUnavailableError(GatewayError):
    """Raised when an upstream service cannot be reached."""

    def __init__(self, service: str, detail: str | None = None) -> None:
        self.service = service
        message = detail or f"Upstream service '{service}' is unavailable"
        super().__init__(message)
