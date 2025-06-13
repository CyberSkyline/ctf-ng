from typing import Any, Dict
from sqlalchemy import func
from CTFd.models import db
from datetime import datetime, timedelta
from flask import request, jsonify
from ...utils.logger import get_logger
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ...user.models.User import User
from ..models.EventRegistration import EventRegistration
from ..models.Demographics import Demographics
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

    can_join, reason = event_joinable(event_id)
    if not can_join:
        logger.warning(
            "Join event failed - user cannot join event",
            extra={"context": {"event_id": event_id, "user_id": user_id}},
        )
        return {
            "success": False,
            "error": reason
        }

    response = join_team(
        user_id=user_id,
        invite_code=invite_code
    )
    team = response.get("team")

    if not response["success"]:
        logger.warning(
            "Join event failed - team join failed",
            extra={"context": {"event_id": event_id, "user_id": user_id, "error": response["error"]}},
        )
        return {
            "success": False,
            "error": response["error"]
        }

    demographics = Demographics.create_demographics(
        user_id=user_id,
        event_id=event_id,
        reg_timestamp=db.func.now(),
    )
    logger.info(
        "User joined existing team for event",
        extra={"context": {"user_id": user_id, "team_id": team.id, "event_id": event_id}}
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
        "message": f"Successfully joined the team '{team.name}' for the event.",
    }
    



def event_joinable(event_id: int) -> dict[str, Any]:
    """Check if an event is joinable"""
    event = EventRegistration.query.get(event_id)
    print(type(event.reg_start_date))
    print(type(func.now()))
    if not event:
        return False, "Event does not exist."
    if not event.reg_open:
        return False, "Event registration is not open."
    if event.reg_start_date is not None and event.reg_start_date > func.now():
        return False, "Event registration has not started yet."
    if event.reg_end_date is not None and event.reg_end_date < func.now():
        return False, "Event registration has ended."

    return True, None
    