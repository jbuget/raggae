class ConversationNotFoundError(Exception):
    """Raised when a conversation cannot be found."""


class ConversationAccessDeniedError(Exception):
    """Raised when a user tries to access a conversation they do not own."""
