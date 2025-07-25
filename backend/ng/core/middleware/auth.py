"""
Simplified main decorators - just handle auth and input validation.
Resource loading and permissions are handled by separate decorators.
"""

from functools import wraps

from CTFd.utils.decorators import admins_only, authed_only
from CTFd.utils.user import get_current_user
from CTFd.utils.user import is_admin as is_admin_ctfd
from flask import request

from ...user.models.User import User
from ..exceptions import PermissionError, ValidationError
from .error_handler import handle_exceptions


def api_endpoint(auth_required=True, admin_required=False, json_required=False, validation_func=None):
    """
    API endpoint decorator that handles:
    - Authentication (optional/required/admin)
    - JSON body validation and parsing
    - Input data validation
    - Error handling

    Resource loading and permission checking is handled by other decorators.

    Args:
        auth_required: Whether authentication is required
        admin_required: Whether admin privileges are required
        json_required: Whether JSON body is required
        validation_func: Function to validate request data

    Usage:
        @api_endpoint(auth_required=True, json_required=True, validation_func=validate_team_creation)
        @load_event()  # Loads event from route params
        def create_team(self, event_id, event, validated_data, current_user):
            validated_data  # Already parsed and validated
            event # Already loaded
            current_user # Already loaded
            # ... business logic
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if admin_required:
                return admins_only(_auth_handler(f, auth_required, json_required, validation_func))(*args, **kwargs)
            elif auth_required:
                return authed_only(_auth_handler(f, auth_required, json_required, validation_func))(*args, **kwargs)
            else:
                return _auth_handler(f, auth_required, json_required, validation_func)(*args, **kwargs)

        return decorated_function

    return decorator


def _auth_handler(f, auth_required, json_required, validation_func):
    """Internal helper to handle the actual endpoint logic"""


    @handle_exceptions
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if auth_required:
            current_user = get_current_user()
            if not current_user:
                raise PermissionError("Authentication is required to access this resource.")
            kwargs["current_user"] = User.find_or_create_by_ctfd_id(current_user.id)
        if json_required:
            if not request.is_json:
                raise ValidationError("Request must have a JSON body.")
            data = request.get_json()
            if not data:
                raise ValidationError("JSON body is malformed or empty.")
            kwargs["json_data"] = data
            if validation_func:
                kwargs["validated_data"] = validation_func(data)
        return f(*args, **kwargs)

    return decorated_function


# Convenience decorators for common patterns
def user_endpoint(json_required=False, validation_func=None):
    """Shorthand for authenticated user endpoints"""
    return api_endpoint(
        auth_required=True,
        admin_required=False,
        json_required=json_required,
        validation_func=validation_func,
    )


def admin_endpoint(json_required=False, validation_func=None):
    """Shorthand for admin-only endpoints"""
    return api_endpoint(
        auth_required=True,
        admin_required=True,
        json_required=json_required,
        validation_func=validation_func,
    )


def public_endpoint(json_required=False, validation_func=None):
    """Shorthand for public endpoints (no auth required)"""
    return api_endpoint(
        auth_required=False,
        admin_required=False,
        json_required=json_required,
        validation_func=validation_func,
    )


# Testing Decorator
def admin_view(f):
    """
    Decorator for traditional Flask views that require admin access.
    It integrates with our plugin's custom exception handling by raising
    a PermissionError, ensuring consistent error responses.
    """

    @wraps(f)
    @handle_exceptions
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            raise PermissionError("You must be logged in to view this page.")
        if not is_admin_ctfd():
            raise PermissionError("You must be an administrator to view this page.")
        kwargs["current_user"] = User.find_or_create_by_ctfd_id(user.id)
        return f(*args, **kwargs)

    return decorated_function
