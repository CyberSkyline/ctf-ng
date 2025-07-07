"""
Retrieves information for a single user for admin.
"""

from flask import g
from typing import Any


def get_user_info(user_id: int) -> Any:
    """Gets info for a single user by their ID (Admin).

    Returns:
        dict: User data.
    """
    user_data = g.user_data

    return user_data
