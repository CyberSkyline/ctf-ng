from typing import Any
from CTFd.models import db
from ...core.utils.logger import get_logger
from ..models.EventRegistration import EventRegistration
from ..models.Demographic import Demographic
from ...team.controllers.create_team import create_team


logger = get_logger(__name__)

def join_event_new_team(event_id: int, user_id: int, team_name: str) -> dict[str, Any]:
    """Join an event by creating a new team.
    Args:
        event_id (int): The event ID where the team will be created.
        user_id (int): The user ID who becomes the team captain.
        team_name (str): The name of the new team.
    Returns:
        dict: Success status, team info, and confirmation message or error info.
    """

    can_join,reason = EventRegistration.event_joinable(event_id)
    if not can_join:
        logger.warning(
            "Join event failed - user cannot join",
            extra={"context": {"event_id": event_id, "user_id": user_id, "reason": reason}},
        )
        return {
            "success": False,
            "error": reason
        }


    response = create_team(
        name=team_name,
        event_id=event_id,
        creator_id=user_id,
    )
    if not response["success"]:
        return {
            "success": False,
            "error": response["error"]
        }
    team = response.get("team")

    logger.info(
        "User joined new team for event",
        extra={"context": {"user_id": user_id, "team_name": team_name, "event_id": event_id}}
    )

    Demographic.create_demographic(
        user_id=user_id,
        event_id=event_id,
        reg_timestamp=db.func.now(),
    )

    return {
        "success": True,
        "team": {
            "id": team.id,
            "name": team.name,
            "invite_code": team.invite_code,
            "event_id": team.event_id,
            "ranked": team.ranked,
            "member_count": team.member_count
        },
        "message": f"Successfully created the team '{team_name}' for the event."
    }
