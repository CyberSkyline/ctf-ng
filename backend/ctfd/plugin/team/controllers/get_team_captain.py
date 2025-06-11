"""
/backend/ctfd/plugin/team/controllers/get_team_captain.py
Retrieves information about the current captain of a team.
"""

from typing import Any

from CTFd.models import Users
from ..models.TeamMember import TeamMember
from ..models.enums import TeamRole


def get_team_captain(team_id: int) -> dict[str, Any]:
    """Gets the current captain info for a team.

    Args:
        team_id (int): The team ID.

    Returns:
        dict: Success status, captain ID if exists, and captain status info.
    """
    captain = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.CAPTAIN).first()

    if captain:
        captain_user = Users.query.filter_by(id=captain.user_id).first()
        captain_name = captain_user.name if captain_user else f"User ID {captain.user_id}"

        return {
            "success": True,
            "captain_id": captain.user_id,
            "captain_name": captain_name,
            "has_captain": True,
        }
    else:
        return {"success": True, "captain_id": None, "has_captain": False}
