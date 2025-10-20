"""
Loader for announcements
"""

from ._util import (
    LoaderType,
    get_param_val,
    get_model_class,
    check_output_exists,
)
from functools import wraps
from collections.abc import Callable

from ...exceptions import NotFoundError


def load_announcement(
    source: LoaderType,
    input_key = "announcement_id",
    output_key = "announcement"
) -> Callable:
    """
    Load announcement middleware
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            check_output_exists(kwargs, output_key)
            Announcement = get_model_class("Announcement")

            if source == LoaderType.PARAM:
                announcement_id = get_param_val(kwargs, input_key)
            else:
                raise ValueError(
                    f"Invalid loader type for announcements: {source}"
                )

            announcement = Announcement.find_by_id(announcement_id)
            if not announcement:
                raise NotFoundError(
                    f"Announcement {announcement_id} not found"
                )

            kwargs[output_key] = announcement
            return f(*args, **kwargs)

        return decorated_function

    return decorator
