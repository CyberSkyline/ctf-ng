"""
Custom exceptions used by global error handler
"""

from __future__ import annotations


class APIException(Exception): # noqa: N818
    """Base exception class for all plugin API exceptions."""

    status_code: int = 500
    message: str = "An internal server error occurred."
    error_field: str = "general"

    def __init__(self, message: str | None = None, error_field: str | None = None):
        if message:
            self.message = message
        if error_field:
            self.error_field = error_field
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to dictionary for API response."""
        return {"success": False, "errors": {self.error_field: self.message}}


class NotFoundError(APIException):
    """Raised when a requested resource does not exist."""

    status_code = 404
    message = "The requested resource was not found."
    error_field = "not_found"


class ValidationError(APIException):
    """Raised when input validation fails (e.g., from a decorator)."""

    status_code = 400
    message = "Input validation failed."
    error_field = "validation"

    def __init__(self, message: str, errors: dict[str, str] | None = None):
        """Initialize with a message and optional detailed errors dictionary."""
        if errors is None:
            super().__init__(message)
        else:
            if len(errors) == 1:
                # If only one error, set the main message to that error
                key, val = next(iter(errors.items()))
                super().__init__(val, key)
            else:
                super().__init__(f"{message}: {str(errors)}")
        self.errors = errors

    def to_dict(self) -> dict:
        """Convert exception to dictionary for API response, including detailed errors."""
        if self.errors:
            return {"success": False, "errors": self.errors}
        else:
            return {"success": False, "errors": {self.error_field: self.message}}


class PermissionError(APIException):
    """Raised when user lacks permission to perform an action."""

    status_code = 403
    message = "You do not have permission to perform this action."
    error_field = "permission"

class AuthenticationError(APIException):
    """Raised when authentication fails or is required."""

    status_code = 401
    message = "Authentication is required to access this resource."
    error_field = "authentication"


class ConflictError(APIException):
    """Raised when a request conflicts with the current state of the resource"""

    status_code = 409
    message = "A conflict occurred with existing data."
    error_field = "conflict"


class BusinessLogicError(APIException):
    """
    Raised for general business rule violations that aren't a conflict or validation issue.
    For example: "Captains cannot leave a team with members."
    Defaults to 400 Bad Request.
    """

    status_code = 400
    message = "The request could not be processed due to a business rule."
    error_field = "business_logic"
