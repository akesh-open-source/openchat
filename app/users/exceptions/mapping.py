from fastapi import status

from app.users.domain.exceptions import (
    DomainError,
    InvalidDisplayNameError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)

EXCEPTION_STATUS_MAP: dict[type[Exception], int] = {
    InvalidDisplayNameError: status.HTTP_400_BAD_REQUEST,
    ProfileAlreadyExistsError: status.HTTP_409_CONFLICT,
    ProfileNotFoundError: status.HTTP_404_NOT_FOUND,
    DomainError: status.HTTP_400_BAD_REQUEST,
}
