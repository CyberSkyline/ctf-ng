"""
Retrieves information about the current captain of a team.
"""

from flask import g
from typing import Any

from ..models.TeamMember import TeamMember


def get_team_captain(team_id: int) -> dict[str, Any]:
    """Gets the current captain info for a team.

    Returns:
        dict: Captain TeamMember object if exists, or indication of no captain.
    """
    team = g.team

    captain = TeamMember.find_captain_by_team(team.id)
    if captain:
        return {
            "captain": captain,
            "has_captain": True,
        }
    else:
        return {"captain": None, "has_captain": False}
