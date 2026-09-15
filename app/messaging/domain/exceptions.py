class DomainError(Exception):
    """Base exception for messaging domain errors."""


class SelfConversationError(DomainError):
    """Raised when both participants of a direct chat are the same user."""


class InvalidConversationTypeError(DomainError):
    """Raised when a conversation type is not supported."""


class ConversationNotFoundError(DomainError):
    """Raised when a conversation does not exist."""


class ConversationAlreadyExistsError(DomainError):
    """Raised when a direct pair already has a conversation."""


class MembershipNotFoundError(DomainError):
    """Raised when a user is not a member of a conversation."""


class MembershipAlreadyExistsError(DomainError):
    """Raised when a membership row already exists."""


class InvalidTokenError(DomainError):
    """Raised when an access token is missing, malformed, or expired."""


class PeerNotFoundError(DomainError):
    """Raised when peer_user_id has no profile in the users service."""


class UsersUnavailableError(DomainError):
    """Raised when the users service cannot be reached for peer lookup."""
