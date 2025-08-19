"""
Contains the business logic to efficiently query
and retrieve basic data counts for all plugin entities.
"""

from typing import Any

from ...event.models.Event import Event
from ...team.models.Team import Team
from ...user.models.User import User


def get_data_counts() -> dict[str, Any]:
    """Gets count stats for all plugin data.

    Returns:
        dict: Counts of events, teams, users, and team members.
    """

    return {
        "events": Event.get_total_count(),
        "teams": Team.get_total_count(),
        "users": User.get_total_count(),
    }
