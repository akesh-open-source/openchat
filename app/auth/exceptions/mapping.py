from fastapi import status

from app.auth.domain.exceptions import (
    DomainError,
    InvalidDisplayNameError,
    InvalidEmailError,
    InvalidPasswordError,
    UserAlreadyExistsError,
)

EXCEPTION_STATUS_MAP: dict[type[Exception], int] = {
    InvalidEmailError: status.HTTP_400_BAD_REQUEST,
    InvalidPasswordError: status.HTTP_400_BAD_REQUEST,
    InvalidDisplayNameError: status.HTTP_400_BAD_REQUEST,
    UserAlreadyExistsError: status.HTTP_409_CONFLICT,
    DomainError: status.HTTP_400_BAD_REQUEST,
}
