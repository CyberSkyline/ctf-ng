"""
/backend/ng/user/controllers/list_users.py
Retrieves a list of all users with extended details for administrative purposes.
"""

from typing import Any
from ..models.User import User


def list_users() -> dict[str, Any]:
    """
    Gets all users with their detailed information.

    Returns:
        dict: Success status, list of users, and total count.
    """
    users_data = User.get_all_users_with_details()

    return {
        "success": True,
        "users": users_data,
        "total": len(users_data),
    }
