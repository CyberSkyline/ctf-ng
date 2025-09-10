"""
Loader for notifications
"""

from ._util import (
    LoaderType,
    get_param_val,
    get_model_class,
    check_output_exists,
)
from ...exceptions import (
    NotFoundError,
    PermissionError,
)
from functools import wraps
from collections.abc import Callable


def load_notification(
    source: LoaderType,
    input_key = "notification_id",
    output_key = "notification"
) -> Callable:
    """
    Load notification middleware with user
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            check_output_exists(kwargs, output_key)
            Notification = get_model_class("Notification")

            if source == LoaderType.PARAM:
                notification_id = get_param_val(kwargs, input_key)
            else:
                raise ValueError(
                    f"Invalid loader type for notifications: {source}"
                )

            notification = Notification.find_by_id(notification_id)
            if not notification:
                raise NotFoundError(
                    f"Notification {notification_id} not found"
                )

            current_user = kwargs.get("current_user")
            if not current_user:
                raise ValueError("User must be loaded first")

            if notification.recipient_id != current_user.id:
                raise PermissionError(
                    "You cannot access other users' notifications"
                )

            kwargs[output_key] = notification
            return f(*args, **kwargs)

        return decorated_function

    return decorator
