class DomainError(Exception):
    """Base exception for domain errors."""


class InvalidEmailError(DomainError):
    pass


class InvalidPasswordError(DomainError):
    pass


class InvalidDisplayNameError(DomainError):
    pass


class UserAlreadyExistsError(DomainError):
    pass


class InvalidCredentialsError(DomainError):
    """Raised when login email/password do not match an active user."""


class InvalidTokenError(DomainError):
    """Raised when an access token is missing, malformed, or expired."""


class SessionNotFoundError(DomainError):
    """Raised when a session does not exist for the authenticated user."""


class RateLimitExceededError(DomainError):
    """Raised when a client exceeds an endpoint rate limit."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Try again later.",
        *,
        retry_after: int = 60,
    ) -> None:
        super().__init__(message)
        self.retry_after = retry_after
