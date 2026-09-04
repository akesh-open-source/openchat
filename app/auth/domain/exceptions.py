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
