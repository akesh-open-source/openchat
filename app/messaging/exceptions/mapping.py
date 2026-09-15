from fastapi import status

from app.messaging.domain.exceptions import DomainError

EXCEPTION_STATUS_MAP: dict[type[Exception], int] = {
    DomainError: status.HTTP_400_BAD_REQUEST,
}
