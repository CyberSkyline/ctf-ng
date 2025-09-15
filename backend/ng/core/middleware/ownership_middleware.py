"""
Ownership validation middleware for resource access control
"""

from functools import wraps
from ..exceptions import PermissionError


def check_ownership(resource_key: str, user_field: str, error_message: str = None):
    """
    Decorator to check that the current user owns the specified resource.

    Args:
        resource_key: The key in kwargs where the resource object is stored
        user_field: The field name on the resource that contains the user ID
        error_message: Optional custom error message for permission violations
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resource = kwargs.get(resource_key)
            if not resource:
                raise ValueError(f"Resource '{resource_key}' must be loaded first")

            current_user = kwargs.get("current_user")
            if not current_user:
                raise ValueError("current_user must be loaded first")

            resource_user_id = getattr(resource, user_field, None)
            if resource_user_id is None:
                raise ValueError(
                    f"Resource '{resource_key}' does not have field '{user_field}'"
                )

            if resource_user_id != current_user.id:
                message = error_message or f"You can only access your own {resource_key}"
                raise PermissionError(message)

            return f(*args, **kwargs)

        return decorated_function

    return decorator
