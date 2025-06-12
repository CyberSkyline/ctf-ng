"""
/backend/ctfd/plugin/team/controllers/create_team.py
Creates a new team in an event with the creator as captain.
"""

from datetime import datetime
from typing import Any

from ...utils.logger import get_logger
from ...event.models.Event import Event
from ...user.models.User import User
from ..models.Team import Team
from ..models.TeamMember import TeamMember
from ..models.enums import TeamRole
from ._generate_invite_code import _generate_invite_code

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
    event = Event.query.get(event_id)
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

    existing_team = Team.query.filter_by(name=name, event_id=event_id).first()
    if existing_team:
        logger.warning(
            "Team creation failed - name already exists",
            extra={
                "context": {
                    "team_name": name,
                    "event_id": event_id,
                    "event_name": event.name,
                    "existing_team_id": existing_team.id,
                }
            },
        )
        return {
            "success": False,
            "error": f"Team '{name}' already exists in {event.name}",
        }

    existing_team_member = TeamMember.query.filter_by(user_id=creator_id, event_id=event_id).first()
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

    team = Team.create_team(
        name=name,
        event_id=event_id,
        ranked=ranked,
        invite_code=invite_code,
        flush_only=True,
    )

    ng_user = User.query.get(creator_id)
    if not ng_user:
        ng_user = User.create_user(creator_id, commit=False)

    TeamMember.create_team_member(
        user_id=creator_id,
        team_id=team.id,
        event_id=event_id,
        role=TeamRole.CAPTAIN,
        joined_at=datetime.utcnow(),
    )

    logger.info(
        "Team created successfully",
        extra={
            "context": {
                "team_id": team.id,
                "team_name": name,
                "event_id": event_id,
                "event_name": event.name,
                "creator_id": creator_id,
                "invite_code": invite_code,
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
