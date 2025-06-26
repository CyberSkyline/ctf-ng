"""
/backend/ng/support/exceptions.py
Custom exceptions for support ticket operations.
"""


class TicketNotFoundError(Exception):
    """Raised when a ticket cannot be found."""
    pass


class TicketPermissionError(Exception):
    """Raised when user lacks permission for ticket operation."""
    pass


class TicketValidationError(Exception):
    """Raised when ticket data validation fails."""
    pass


class TicketOperationError(Exception):
    """Raised when a ticket operation fails."""
    pass


class TagNotFoundError(Exception):
    """Raised when a tag cannot be found."""
    pass


class MessageValidationError(Exception):
    """Raised when message data validation fails."""
    pass
