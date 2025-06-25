"""
Retrieves detailed information about a team and its members.
"""

from typing import Any
from ..models.Team import Team


def get_team_info(team_id: int) -> dict[str, Any]:
    """Gets detailed info about a team."""

    full_details = Team.get_full_team_details(team_id)

    if not full_details:
        return {"success": False, "error": "Team not found."}

    return {"success": True, **full_details}
