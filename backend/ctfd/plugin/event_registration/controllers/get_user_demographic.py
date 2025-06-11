from typing import Any, Dict
from sqlalchemy import func
from CTFd.models import db
from flask import request, jsonify
from ...utils.logger import get_logger
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ...user.models.User import User
from ..models.EventRegistration import EventRegistration
from ..models.Demographics import Demographics


logger = get_logger(__name__)

def get_user_demographic(user_id: int, event_id: int) -> Dict[str, Any]:
    """Get the demographic information for a user in a specific event.

    Args:
        user_id (int): The ID of the user.
        event_id (int): The ID of the event.

    Returns:
        dict: Success status and demographic data or error info.
    """
    user = User.query.get(user_id)
    if not user:
        logger.warning(
            "Get user demographic failed - user does not exist",
            extra={"context": {"user_id": user_id, "event_id": event_id}},
        )
        return {"success": False, "error": "User does not exist"}

    event = EventRegistration.query.get(event_id)
    if not event:
        logger.warning(
            "Get user demographic failed - event does not exist",
            extra={"context": {"user_id": user_id, "event_id": event_id}},
        )
        return {"success": False, "error": "Event does not exist"}

    demographics = Demographics.query.filter_by(user_id=user_id, event_id=event_id).first()
    if not demographics:
        logger.info(
            "No demographics found for user in event",
            extra={"context": {"user_id": user_id, "event_id": event_id}},
        )
        return {"success": True, "demographics": None}

    return {
        "success": True,
        "demographics": {
            "id": demographics.id,
            "user_id": demographics.user_id,
            "event_id": demographics.event_id,
            "data": demographics.data,
            "timestamp": demographics.timestamp.isoformat(),
        },
    }