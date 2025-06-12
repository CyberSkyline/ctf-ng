"""
/backend/ctfd/plugin/team/controllers/join_team.py
Allows a user to join a team using an invite code.
"""

from datetime import datetime
from typing import Any

from ...utils.logger import get_logger
from ...event.models.Event import Event
from ...user.models.User import User
from ..models.Team import Team
from ..models.TeamMember import TeamMember
from ..models.enums import TeamRole

logger = get_logger(__name__)


def join_team(user_id: int, invite_code: str) -> dict[str, Any]:
    """Join a team - using invite code.

    Args:
        user_id (int): The user ID joining the team.
        invite_code (str): The team's invite code.

    Returns:
        dict: Success status, team info, and membership details or error info.
    """
    # Find and validate team
    team_validation = _validate_team_exists(invite_code, user_id)
    if not team_validation["success"]:
        return team_validation

    team = team_validation["team"]
    event = team_validation["event"]

    # Validate team join eligibility
    eligibility_check = _validate_team_join_eligibility(team, event, user_id, invite_code)
    if not eligibility_check["success"]:
        return eligibility_check

    # Validate user and existing membership
    user_validation = _validate_user_membership(user_id, team.event_id, team, invite_code)
    if not user_validation["success"]:
        return user_validation

    role = TeamRole.MEMBER
    team_member = TeamMember.create_team_member(
        user_id=user_id,
        team_id=team.id,
        event_id=team.event_id,
        joined_at=datetime.utcnow(),
        role=role,
    )

    logger.info(
        "User successfully joined team via invite code",
        extra={
            "context": {
                "user_id": user_id,
                "team_id": team.id,
                "team_name": team.name,
                "event_id": team.event_id,
                "role": role,
                "invite_code": invite_code,
            }
        },
    )

    return {
        "success": True,
        "message": f"User successfully joined team '{team.name}'",
        "team": team,
        "team_member": team_member,
        "joined_via_invite": True,
        "invite_code": invite_code,
    }


def _validate_team_exists(invite_code, user_id):
    """Validate that team exists for the given invite code.

    Args:
        invite_code (str): The team invite code
        user_id (int): User ID for logging

    Returns:
        dict: Success status, team and event objects, or error
    """
    team = Team.query.filter_by(invite_code=invite_code).first()
    if not team:
        logger.warning(
            "Team join failed - invalid invite code",
            extra={
                "context": {
                    "invite_code": invite_code,
                    "user_id": user_id,
                }
            },
        )
        return {"success": False, "error": "Invalid invite code"}

    event = Event.query.get(team.event_id)
    return {"success": True, "team": team, "event": event}


def _validate_team_join_eligibility(team, event, user_id, invite_code):
    """Validate team and event eligibility for joining.

    Args:
        team: Team object
        event: Event object
        user_id (int): User ID for logging
        invite_code (str): Invite code for logging

    Returns:
        dict: Success status or error message
    """
    # Check if event is locked
    if event and event.locked:
        logger.warning(
            "Team join failed - event is locked",
            extra={
                "context": {
                    "team_id": team.id,
                    "team_name": team.name,
                    "event_id": team.event_id,
                    "event_name": event.name,
                    "user_id": user_id,
                    "invite_code": invite_code,
                }
            },
        )
        return {
            "success": False,
            "error": f"Event '{event.name}' is locked and not accepting new team members",
        }

    # Check if team is locked
    if team.locked:
        logger.warning(
            "Team join failed - team is locked",
            extra={
                "context": {
                    "team_id": team.id,
                    "team_name": team.name,
                    "event_id": team.event_id,
                    "user_id": user_id,
                    "invite_code": invite_code,
                }
            },
        )
        return {
            "success": False,
            "error": f"Team '{team.name}' is locked and not accepting new members",
        }

    # Check if team is full based on event's max_team_size
    if team.member_count >= event.max_team_size:
        logger.warning(
            "Team join failed - team is full",
            extra={
                "context": {
                    "team_id": team.id,
                    "team_name": team.name,
                    "event_id": team.event_id,
                    "user_id": user_id,
                    "member_count": team.member_count,
                    "max_team_size": event.max_team_size,
                    "invite_code": invite_code,
                }
            },
        )
        return {
            "success": False,
            "error": f"Team {team.name} is full ({team.member_count}/{event.max_team_size})",
        }

    return {"success": True}


def _validate_user_membership(user_id, event_id, team, invite_code):
    """Validate user doesn't already belong to another team in this event.

    Args:
        user_id (int): User ID
        event_id (int): Event ID
        team: Team object for logging
        invite_code (str): Invite code for logging

    Returns:
        dict: Success status and user object, or error message
    """
    user = User.query.get(user_id)
    if not user:
        user = User.create_user(user_id, commit=False)

    existing_team_member = TeamMember.query.filter_by(user_id=user_id, event_id=event_id).first()

    if existing_team_member:
        existing_team = Team.query.get(existing_team_member.team_id)
        logger.warning(
            "Team join failed - user already in team",
            extra={
                "context": {
                    "user_id": user_id,
                    "event_id": event_id,
                    "existing_team_id": existing_team_member.team_id,
                    "existing_team_name": existing_team.name if existing_team else "Unknown",
                    "requested_team_id": team.id,
                    "requested_team_name": team.name,
                    "invite_code": invite_code,
                }
            },
        )
        return {
            "success": False,
            "error": f"User is already in team '{existing_team.name}' for this event",
        }

    return {"success": True, "user": user}
