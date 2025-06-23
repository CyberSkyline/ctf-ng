"""
/backend/ctfd/plugin/team/controllers/create_team.py
Creates a new team in an event with the creator as captain.
"""

from typing import Any

from plugin.core.utils.logger import get_logger
from plugin.event.models.Event import Event
from plugin.team.models.Team import Team
from plugin.team.models.TeamMember import TeamMember
from plugin.team.controllers._generate_invite_code import _generate_invite_code

logger = get_logger(__name__)


def create_team(
    name: str,
    event_id: int,
    creator_id: int,
    ranked: bool = False,
) -> dict[str, Any]:
    """Creates a new team in the event with the creator as captain.

    Args:
        name (str): The team name.
        event_id (int): The event ID where the team will be created.
        creator_id (int): The user ID who becomes captain.
        ranked (bool, optional): Whether the team is ranked. Defaults to False.

    Returns:
        dict: Success status, team object, invite code, and message or error info.
    """

    event = Event.find_by_id(event_id)
    if not event:
        logger.warning(
            "Team creation failed - event not found",
            extra={"context": {"event_id": event_id, "team_name": name}},
        )
        return {
            "success": False,
            "error": f"Event with ID {event_id} does not exist",
        }

    if event.locked:
        logger.warning(
            "Team creation failed - event is locked",
            extra={
                "context": {
                    "event_id": event_id,
                    "event_name": event.name,
                    "team_name": name,
                    "creator_id": creator_id,
                }
            },
        )
        return {
            "success": False,
            "error": f"Event '{event.name}' is locked and not accepting new teams",
        }

    existing_team_member = TeamMember.find_by_user_and_event(creator_id, event_id)
    if existing_team_member:
        logger.warning(
            "Team creation failed - user already in team",
            extra={
                "context": {
                    "user_id": creator_id,
                    "event_id": event_id,
                    "existing_team_id": existing_team_member.team_id,
                }
            },
        )
        return {
            "success": False,
            "error": "You are already in a team for this event.",
        }

    invite_code = _generate_invite_code()

    success, result = Team.create_team_with_captain(
        name=name,
        event_id=event_id,
        creator_id=creator_id,
        invite_code=invite_code,
        ranked=ranked,
    )

    if success:
        team = result["team"]
        logger.info(
            "Team created successfully",
            extra={
                "context": {
                    "team_id": team.id,
                    "team_name": name,
                    "event_id": event_id,
                    "event_name": event.name,
                    "creator_id": creator_id,
                    "ranked": ranked,
                }
            },
        )

        return {
            "success": True,
            "team": team,
            "invite_code": invite_code,
            "message": f"Team '{name}' created successfully in {event.name}",
        }
    else:
        logger.warning(
            "Team creation failed",
            extra={
                "context": {
                    "team_name": name,
                    "event_id": event_id,
                    "creator_id": creator_id,
                    "error": result["error"],
                }
            },
        )
        return {
            "success": False,
            "error": result["error"],
        }
