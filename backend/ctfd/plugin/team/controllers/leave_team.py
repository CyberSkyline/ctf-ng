"""
/backend/ctfd/plugin/team/controllers/leave_team.py
Removes a user from their current team in an event.
"""

from typing import Any
from datetime import datetime

from ...utils.logger import get_logger
from ...event.models.Event import Event
from ..models.Team import Team
from ..models.TeamMember import TeamMember
from ..models.enums import TeamRole

logger = get_logger(__name__)


def leave_team(user_id: int, event_id: int) -> dict[str, Any]:
    """Removes a user from their current team in the event.

    Args:
        user_id (int): The user ID leaving the team.
        event_id (int): The event ID containing the team.

    Returns:
        dict: Success status, former team name, and message or error info.
    """
    team_member = TeamMember.query.filter_by(user_id=user_id, event_id=event_id).first()
    if not team_member:
        logger.warning(
            "Team leave failed - user not in any team",
            extra={"context": {"user_id": user_id, "event_id": event_id}},
        )
        return {
            "success": False,
            "error": "User is not in any team for this event",
        }

    # Fetch the team and event to check locked status
    team = Team.query.get(team_member.team_id)
    event = Event.query.get(event_id)

    # Block leaving if event/team is locked or event has started
    if event and (event.locked or (event.start_time and datetime.utcnow() >= event.start_time)):
        logger.warning(
            "Team leave failed - event is locked or started",
            extra={
                "context": {
                    "user_id": user_id,
                    "event_id": event_id,
                    "team_id": team_member.team_id,
                    "event_locked": event.locked,
                    "event_started": event.start_time and datetime.utcnow() >= event.start_time
                    if event.start_time
                    else False,
                }
            },
        )
        return {
            "success": False,
            "error": "Cannot leave team after the event has started or been locked.",
        }

    if team and team.locked:
        logger.warning(
            "Team leave failed - team is locked",
            extra={
                "context": {
                    "user_id": user_id,
                    "event_id": event_id,
                    "team_id": team.id,
                    "team_name": team.name,
                }
            },
        )
        return {
            "success": False,
            "error": f"Team '{team.name}' is locked and members cannot leave.",
        }

    if team_member.role == TeamRole.CAPTAIN:
        team = Team.query.get(team_member.team_id)
        other_members_count = TeamMember.query.filter(
            TeamMember.team_id == team.id, TeamMember.id != team_member.id
        ).count()

        if other_members_count > 0:
            return {
                "success": False,
                "error": "Captains cannot leave a team that has other members. You must transfer captaincy first or disband the team.",
            }
        else:
            team_name = team.name
            team.disband_team()
            return {
                "success": True,
                "message": f"You have left and disbanded '{team_name}' as you were the last member.",
                "team_disbanded": True,
            }

    team_name = team.name if team else "Unknown Team"

    team_member.remove_team_member()

    logger.info(
        "User successfully left team",
        extra={
            "context": {
                "user_id": user_id,
                "event_id": event_id,
                "team_id": team_member.team_id,
                "team_name": team_name,
            }
        },
    )

    return {
        "success": True,
        "message": f"Successfully left team '{team_name}'",
        "former_team": team_name,
    }
