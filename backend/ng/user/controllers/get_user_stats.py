"""
/backend/ng/user/controllers/get_user_stats.py
Calculates participation statistics for a user across all events.
"""

from typing import Any

from ..models.User import User


def get_user_stats(user_id: int) -> dict[str, Any]:
    """Gets participation stats for a user across all events.

    Args:
        user_id (int): The user ID to get stats for.

    Returns:
        dict: Success status and participation stats.
    """

    stats = User.get_user_participation_stats(user_id)
    if not stats:
        return {"success": False, "error": "User not found in extended system"}

    return {
        "success": True,
        "stats": stats,
    }
