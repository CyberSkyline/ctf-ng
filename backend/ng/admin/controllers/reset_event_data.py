"""
Contains the business logic for the
destructive operation of resetting all data for a single event.
"""

from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember

def reset_event_data(event_id: int) -> None:
    """Deletes all teams and team members for a event.

    Returns:
        dict: Success status and deletion counts.
    """
    TeamMember.delete_by_event(event_id)
    Team.delete_by_event(event_id)
