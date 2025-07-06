"""
Contains the business logic for the
destructive operation of resetting all data for a single event.
"""

from flask import g
from typing import Any

from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember


def reset_event_data(event_id: int) -> dict[str, Any]:
    """Deletes all teams and team members for a event.

    Returns:
        dict: Success status and deletion counts.
    """

    team_members_count = TeamMember.count_by_event(event_id)
    teams_count = Team.count_by_event(event_id)

    TeamMember.delete_by_event(event_id)
    Team.delete_by_event(event_id)

    return {
        "deleted_counts": {"team_members": team_members_count, "teams": teams_count},
    }
