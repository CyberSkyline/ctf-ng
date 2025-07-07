"""
Retrieves a list of all users with extended details for admin.
"""

from typing import Any
from ..models.User import User


def list_users() -> list[Any]:
    """Gets all users with their detailed information (Admin).

    """
    users_data = User.get_all_users_with_details()

    return users_data
