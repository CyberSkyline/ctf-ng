"""
Retrieves all team memberships for a user across all events.
"""

from flask import g
from typing import Any


def get_user_teams(user_id: int) -> dict[str, Any]:
    """Gets all team members for a user across all events.

    Returns:
        dict: List of teams with event info and total count.
    """
    teams_data = g.user_teams_data

    return {
        "teams": teams_data,
        "total_teams": len(teams_data),
    }
