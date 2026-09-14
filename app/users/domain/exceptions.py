class DomainError(Exception):
    """Base exception for users domain errors."""


class InvalidDisplayNameError(DomainError):
    pass


class ProfileAlreadyExistsError(DomainError):
    """Raised when a profile for the given user_id already exists."""


class ProfileNotFoundError(DomainError):
    """Raised when a profile does not exist for the given user_id."""
