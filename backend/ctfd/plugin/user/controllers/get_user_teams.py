"""
/backend/ctfd/plugin/user/controllers/get_user_teams.py
Retrieves all team memberships for a user across all events.
"""

from typing import Any

from plugin.core.utils.logger import get_logger
from plugin.user.models.User import User

logger = get_logger(__name__)


def get_user_teams(user_id: int) -> dict[str, Any]:
    """Gets all team members for a user across all events.

    Args:
        user_id (int): The user ID to get teams for.

    Returns:
        dict: Success status, list of teams with event info, and total count.
    """

    if not User.find_by_id(user_id):
        logger.warning(
            "Get user teams failed - user not found",
            extra={"context": {"user_id": user_id}},
        )
        return {"success": False, "error": "User not found in extended system"}

    teams_data = User.get_user_teams_data(user_id)

    logger.info(
        "User teams retrieved successfully",
        extra={
            "context": {
                "user_id": user_id,
                "total_teams": len(teams_data),
                "total_team_members": len(teams_data),
            }
        },
    )

    return {
        "success": True,
        "teams": teams_data,
        "total_teams": len(teams_data),
    }
