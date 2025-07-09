"""
Contains the business logic for the
destructive operation of resetting all plugin related data.
"""

from typing import Any

from ...event.models.Event import Event
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ...user.models.User import User
from .get_data_counts import get_data_counts


def reset_all_plugin_data() -> dict[str, Any]:
    """Deletes all plugin data from the database."""
    initial_counts = get_data_counts()

    TeamMember.delete_all()
    Team.delete_all()
    User.delete_all()
    Event.delete_all()

    return {
        "reset_completed": True,
        "deleted_counts": initial_counts,
    }
