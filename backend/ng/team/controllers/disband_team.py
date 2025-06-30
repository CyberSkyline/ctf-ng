"""
Disbands a team and removes all its members.
"""

from flask import g
from typing import Any


def disband_team(team_id: int, actor_id: int, is_admin: bool = False) -> dict[str, Any]:
    """Deletes a team and all its team members.

    Returns:
        dict: Confirmation message.
    """
    team = g.team

    team_name = team.name
    team.disband_team()

    return {
        "message": f"Team '{team_name}' has been disbanded.",
    }
