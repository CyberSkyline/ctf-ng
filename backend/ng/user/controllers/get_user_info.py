"""
Retrieves information for a single user for admin.
"""

from typing import Any
from ..models.User import User


def get_user_info(user_id: int) -> dict[str, Any]:
    """
    Gets info for a single user by their ID (Admin).

    Args:
        user_id (int): The ID of the user to retrieve.

    Returns:
        dict: Success status and the user data.
    """
    user_data = User.get_user_details_by_id(user_id)

    if not user_data:
        return {"success": False, "error": "User not found."}

    return {"success": True, "user": user_data}
