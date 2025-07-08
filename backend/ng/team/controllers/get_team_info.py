"""
Retrieves detailed information about a team and its members.
"""

from typing import Any

from ..models.Team import Team

def get_team_info(team: Team) -> dict[str, Any]:
    """Gets detailed info about a team.

    Returns:
        dict: Full team details including members and event.
    """
    return team.get_full_team_details()