from typing import Any
from ...core.utils.logger import get_logger
from ...team.controllers.create_team import create_team
from ..controllers.create_demographic import create_demographic
from ...team.controllers.disband_team import disband_team


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

    response = create_team(
        name=team_name,
        event_id=event_id,
        creator_id=user_id,
    )

    if not response["success"]:
        return response
        
    team = response.get("team")

    response = create_demographic(
        user_id=user_id,
        event_id=event_id,
    )
    if not response["success"]:
        disband_team(team.id, user_id)
        return response

    logger.info(
        "User joined new team for event",
        extra={"context": {"user_id": user_id, "team_name": team_name, "event_id": event_id}}
    )

    return {
        "success": True,
        "team": team,
    }
