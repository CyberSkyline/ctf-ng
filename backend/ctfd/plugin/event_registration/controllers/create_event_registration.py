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

def create_event_registration(event_id: int, public=False, reg_open=False, reg_start_date=None, reg_end_date=None) -> Dict[str, Any]:
    """Create an event registration period for an event

    Args:
        event_id (int): The ID of the event to create registration for.
        public (bool, optional): Whether the registration is public. Defaults to False.
        reg_ (bool, optional): Whether the registration is reg_. Defaults to False.
        reg_start_date (datetime, optional): The start date of the registration period. Defaults to None.
        reg_end_date (datetime, optional): The reg_end_date date of the registration period. Defaults to None.
    Returns:
        dict: Success status, event registration info, and confirmation message or error info.
    """

    event = EventRegistration.create_event_registration(
        event_id=event_id,
        public=public,
        reg_open=reg_open,
        reg_start_date=reg_start_date,
        reg_end_date=reg_end_date
    )
    if not event:
        logger.warning(
            "Event registration creation failed",
            extra={"context": {"event_id": event_id, "public": public, "reg_open": reg_open, "start": reg_start_date, "reg_end_date": reg_end_date}}
        )
        return {
            "success": False,
            "error": "Failed to create event registration"
        }
    logger.info(
        "Event registration created successfully",
        extra={"context": {"event_id": event_id, "public": public, "reg_open": reg_open, "start": reg_start_date, "reg_end_date": reg_end_date}}
    )
    return {
        "success": True,
        "event_registration": {
            "id": event.reg_id,
            "event_id": event.event_id,
            "public": event.public,
            "reg_open": event.reg_open,
            "reg_start_date": event.reg_start_date.isoformat() if event.reg_start_date else None,
            "reg_end_date": event.reg_end_date.isoformat() if event.reg_end_date else None
        },
        "message": "Event registration created successfully"
    }
