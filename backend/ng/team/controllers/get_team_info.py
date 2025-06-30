"""
Retrieves detailed information about a team and its members.
"""

from flask import g
from typing import Any

from ..models.Team import Team


def get_team_info(team_id: int) -> dict[str, Any]:
    """Gets detailed info about a team.

    Returns:
        dict: Full team details including members and event.
    """

    team = g.team

    full_details = Team.get_full_team_details(team.id)
    return full_details
