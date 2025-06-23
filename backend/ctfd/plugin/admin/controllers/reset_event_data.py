"""
Contains the business logic for the destructive operation of resetting all data for a single event.
/backend/ctfd/plugin/admin/controllers/reset_event_data.py
"""

from typing import Any


from plugin.core.utils.logger import get_logger
from plugin.event.models.Event import Event
from plugin.team.models.Team import Team
from plugin.team.models.TeamMember import TeamMember

logger = get_logger(__name__)


def reset_event_data(event_id: int) -> dict[str, Any]:
    """Deletes all teams and team members for a event.

    Args:
        event_id (int): The ID of the event to reset.

    Returns:
        dict: Success status and deletion counts or error info.
    """

    event = Event.find_by_id(event_id)
    if not event:
        logger.warning(
            "Event reset failed - event not found",
            extra={"context": {"event_id": event_id}},
        )
        return {"success": False, "error": "Event not found."}

    team_members_count = TeamMember.count_by_event(event_id)
    teams_count = Team.count_by_event(event_id)

    logger.warning(
        "Initiating event data reset",
        extra={
            "context": {
                "event_id": event_id,
                "event_name": event.name,
                "teams_to_delete": teams_count,
                "team_members_to_delete": team_members_count,
            }
        },
    )

    TeamMember.delete_by_event(event_id)
    Team.delete_by_event(event_id)

    logger.info(
        "Event data reset successfully",
        extra={
            "context": {
                "event_id": event_id,
                "event_name": event.name,
                "deleted_teams": teams_count,
                "deleted_team_members": team_members_count,
            }
        },
    )

    return {
        "success": True,
        "message": f"Reset event '{event.name}' successfully",
        "deleted": {"team_members": team_members_count, "teams": teams_count},
        "event": {"id": event.id, "name": event.name},
    }
