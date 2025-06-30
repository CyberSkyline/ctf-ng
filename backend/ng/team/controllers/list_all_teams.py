"""
Retrieves a list of all teams for admin.
"""

from typing import Any
from ..models.Team import Team


def list_all_teams() -> dict[str, Any]:
    """
    Gets all teams with their information.

    Returns:
        dict: List of teams and total count.
    """
    all_teams_data = Team.get_all_teams_for_admin()

    return {
        "teams": all_teams_data,
        "total": len(all_teams_data),
    }
