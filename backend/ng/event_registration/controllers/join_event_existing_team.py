from typing import Any
from CTFd.models import db
from ...core.utils.logger import get_logger
from ..models.EventRegistration import EventRegistration
from ..models.Demographic import Demographic
from ...team.controllers.join_team import join_team


logger = get_logger(__name__)

def join_event_existing_team(event_id: int, user_id: int, invite_code: str) -> dict[str, Any]:
    """Join an existing team in an event using an invite code.
    Args:
        event_id (int): The event ID where the team exists.
        user_id (int): The user ID joining the team.
        invite_code (str): The team's invite code.
    Returns:
        dict: Success status, team info, and membership details or error info.
    """

    response = join_team(
        user_id=user_id,
        invite_code=invite_code
    )
    team = response.get("team")

    if not response["success"]:
        return response

    Demographic.create_demographic(
        user_id=user_id,
        event_id=event_id,
        reg_timestamp=db.func.now(),
    )


    return {
        "success": True,
        "team": team.serialize(),
    }
    



