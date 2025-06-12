"""
/backend/ctfd/plugin/admin/database/get_data_counts.py
Contains the business logic to efficiently query and retrieve basic data counts for all plugin entities.
"""

from typing import Any

from ...event.models.Event import Event
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ...user.models.User import User


def get_data_counts() -> dict[str, Any]:
    """Gets count stats for all plugin data.

    Returns:
        dict: Counts of events, teams, users, and team members.
    """

    return {
        "events": Event.query.count(),
        "teams": Team.query.count(),
        "users": User.query.count(),
        "team_members": TeamMember.query.count(),
    }
