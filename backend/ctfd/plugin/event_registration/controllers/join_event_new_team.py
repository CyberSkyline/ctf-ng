from typing import Any, Dict
from sqlalchemy import func
from CTFd.models import db
from flask import request, jsonify
from datetime import datetime, timedelta
from ...utils.logger import get_logger
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ...user.models.User import User
from ..models.EventRegistration import EventRegistration
from ..models.Demographics import Demographics
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

    can_join,reason = event_joinable(event_id)
    if not can_join:
        logger.warning(
            "Join event failed - user cannot join event",
            extra={"context": {"event_id": event_id, "user_id": user_id}},
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
    team = response.get("team")



    if not response["success"]:
        logger.warning(
            "Join event failed - team creation failed",
            extra={"context": {"event_id": event_id, "user_id": user_id, "error": response["error"]}},
        )
        return {
            "success": False,
            "error": response["error"]
        }


    logger.info(
        "User joined new team for event",
        extra={"context": {"user_id": user_id, "team_name": team_name, "event_id": event_id}}
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

def event_joinable(event_id: int) -> dict[str, Any]:
    """Check if an event is joinable"""
    event = EventRegistration.query.get(event_id)
    print(type(event.reg_start_date))
    print(type(func.now()))
    if not event:
        return False, "Event does not exist."
    if not event.reg_open:
        return False, "Event registration is not open."
    if event.reg_start_date is not None and event.reg_start_date > datetime.now():
        return False, "Event registration has not started yet."
    if event.reg_end_date is not None and event.reg_end_date < datetime.now():
        return False, "Event registration has ended."

    return True, None
