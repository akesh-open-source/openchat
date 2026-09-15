from fastapi import status

from app.messaging.domain.exceptions import (
    ConversationAlreadyExistsError,
    ConversationNotFoundError,
    DomainError,
    InvalidConversationTypeError,
    InvalidTokenError,
    MembershipAlreadyExistsError,
    MembershipNotFoundError,
    PeerNotFoundError,
    SelfConversationError,
    UsersUnavailableError,
)

EXCEPTION_STATUS_MAP: dict[type[Exception], int] = {
    SelfConversationError: status.HTTP_400_BAD_REQUEST,
    InvalidConversationTypeError: status.HTTP_400_BAD_REQUEST,
    ConversationAlreadyExistsError: status.HTTP_409_CONFLICT,
    ConversationNotFoundError: status.HTTP_404_NOT_FOUND,
    MembershipAlreadyExistsError: status.HTTP_409_CONFLICT,
    MembershipNotFoundError: status.HTTP_404_NOT_FOUND,
    PeerNotFoundError: status.HTTP_404_NOT_FOUND,
    UsersUnavailableError: status.HTTP_502_BAD_GATEWAY,
    InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
    DomainError: status.HTTP_400_BAD_REQUEST,
}
