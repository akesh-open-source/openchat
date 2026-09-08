from fastapi import status

from app.auth.domain.exceptions import (
    DomainError,
    InvalidCredentialsError,
    InvalidDisplayNameError,
    InvalidEmailError,
    InvalidPasswordError,
    InvalidTokenError,
    UserAlreadyExistsError,
)

EXCEPTION_STATUS_MAP: dict[type[Exception], int] = {
    InvalidEmailError: status.HTTP_400_BAD_REQUEST,
    InvalidPasswordError: status.HTTP_400_BAD_REQUEST,
    InvalidDisplayNameError: status.HTTP_400_BAD_REQUEST,
    UserAlreadyExistsError: status.HTTP_409_CONFLICT,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
    DomainError: status.HTTP_400_BAD_REQUEST,
}
