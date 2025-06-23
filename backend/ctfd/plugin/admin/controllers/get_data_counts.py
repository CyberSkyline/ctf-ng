"""
Contains the business logic to efficiently query and retrieve basic data counts for all plugin entities.
/backend/ctfd/plugin/admin/controllers/get_data_counts.py
"""

from typing import Any

from plugin.event.models.Event import Event
from plugin.team.models.Team import Team
from plugin.team.models.TeamMember import TeamMember
from plugin.user.models.User import User


def get_data_counts() -> dict[str, Any]:
    """Gets count stats for all plugin data.

    Returns:
        dict: Counts of events, teams, users, and team members.
    """

    return {
        "events": Event.get_total_count(),
        "teams": Team.get_total_count(),
        "users": User.get_total_count(),
        "team_members": TeamMember.get_total_count(),
    }
