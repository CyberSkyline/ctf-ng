"""
Retrieves a user's team membership details within a specific event.
"""

from flask import g
from typing import Any


def get_user_team_for_event(user_id: int, event_id: int) -> dict[str, Any]:
    """Gets a user's team membership in an event.
    Returns:

        dict: Team info if user is in a team, or None if not.
    """
    team_data = g.user_event_team_data

    if not team_data["team_member"]:
        return {
            "in_team": False,
            "team": None,
            "team_member": None,
            "event": team_data["event"],
        }

    return {
        "in_team": True,
        "team": team_data["team"],
        "team_member": team_data["team_member"],
        "event": team_data["event"],
    }
