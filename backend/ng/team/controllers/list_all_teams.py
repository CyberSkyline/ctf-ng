"""
Retrieves a list of all teams for admin.
"""

from typing import Any
from ..models.Team import Team

def list_all_teams() -> dict[str, Any]:
    """
    Gets all teams with their information.

    """
    return Team.get_all_teams_for_admin()
