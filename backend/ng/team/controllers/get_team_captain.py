"""
Retrieves information about the current captain of a team.
"""

from typing import Any

from ..models.TeamMember import TeamMember
from ..models.Team import Team

def get_team_captain(team: Team) -> dict[str, Any]:
    """Gets the current captain info for a team.

    Returns:
        dict: Captain TeamMember object if exists, or indication of no captain.
    """
    return TeamMember.find_captain_by_team(team.id)
