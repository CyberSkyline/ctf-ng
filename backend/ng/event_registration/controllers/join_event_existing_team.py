from typing import Any
from ...core.utils.logger import get_logger
from ...team.controllers.join_team import join_team
from ..controllers.create_demographic import create_demographic
from ...team.controllers.leave_team import leave_team


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

    response = create_demographic(
        user_id=user_id,
        event_id=event_id,
    )
    if not response["success"]:
        leave_team(user_id, event_id)
        return response


    return {
        "success": True,
        "team": team.serialize(),
    }
    



