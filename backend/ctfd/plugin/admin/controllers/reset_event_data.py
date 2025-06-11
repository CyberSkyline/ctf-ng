"""
/backend/ctfd/plugin/admin/database/reset_event_data.py
Contains the business logic for the destructive operation of resetting all data for a single event.
"""

from typing import Any

from CTFd.models import db

from ...utils.logger import get_logger
from ...event.models.Event import Event
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember

logger = get_logger(__name__)


def reset_event_data(event_id: int) -> dict[str, Any]:
    """Deletes all teams and team members for a event.

    Args:
        event_id (int): The ID of the event to reset.

    Returns:
        dict: Success status and deletion counts or error info.
    """

    event = Event.query.get(event_id)
    if not event:
        logger.warning(
            "Event reset failed - event not found",
            extra={"context": {"event_id": event_id}},
        )
        return {"success": False, "error": "Event not found."}

    team_members_count = TeamMember.query.filter_by(event_id=event_id).count()
    teams_count = Team.query.filter_by(event_id=event_id).count()

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

    TeamMember.query.filter_by(event_id=event_id).delete()
    Team.query.filter_by(event_id=event_id).delete()

    db.session.commit()

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
