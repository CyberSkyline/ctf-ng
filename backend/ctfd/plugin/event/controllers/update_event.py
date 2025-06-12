"""
/backend/ctfd/plugin/event/controllers/update_event.py
Contains the business logic for updating an existing event's properties.
"""

from typing import Any
from datetime import datetime

from CTFd.models import db
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ...utils.logger import get_logger
from ...team.models.Team import Team
from ..models.Event import Event

logger = get_logger(__name__)


def update_event(
    event_id: int,
    name: str | None = None,
    description: str | None = None,
    max_team_size: int | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    locked: bool | None = None,
) -> dict[str, Any]:
    """Updates event info with the provided fields.

    Args:
        event_id (int): The event ID to update.
        name (str, optional): New name for the event if changing.
        description (str, optional): New description for the event if changing.
        max_team_size (int, optional): New maximum team size for teams in this event if changing.
        start_time (datetime, optional): New start time for the event if changing.
        end_time (datetime, optional): New end time for the event if changing.
        locked (bool, optional): New locked status for the event if changing.

    Returns:
        dict: Success status, updated event object, and confirmation message or error info.
    """

    event = Event.query.get(event_id)
    if not event:
        logger.warning(
            "Event update failed - event not found",
            extra={"context": {"event_id": event_id}},
        )
        return {"success": False, "error": "Event not found."}

    changes_made = {}
    old_name = event.name
    old_description = event.description
    old_start_time = event.start_time
    old_end_time = event.end_time
    old_locked = event.locked

    if name and name != event.name:
        existing = Event.query.filter_by(name=name).first()
        if existing:
            logger.warning(
                "Event update failed - name already exists",
                extra={
                    "context": {
                        "event_id": event_id,
                        "old_name": old_name,
                        "new_name": name,
                        "existing_event_id": existing.id,
                    }
                },
            )
            return {
                "success": False,
                "error": f"Event name '{name}' already exists",
            }
        changes_made["name"] = {"old": old_name, "new": name}

    if description is not None:
        changes_made["description"] = {
            "old": old_description,
            "new": description,
        }

    if max_team_size is not None and max_team_size != event.max_team_size:
        validation_result = _validate_max_team_size_change(event, max_team_size, changes_made)
        if not validation_result["success"]:
            return validation_result

    if start_time is not None:
        changes_made["start_time"] = {
            "old": old_start_time.isoformat() if old_start_time else None,
            "new": start_time.isoformat() if start_time else None,
        }

    if end_time is not None:
        changes_made["end_time"] = {
            "old": old_end_time.isoformat() if old_end_time else None,
            "new": end_time.isoformat() if end_time else None,
        }

    if locked is not None:
        changes_made["locked"] = {
            "old": old_locked,
            "new": locked,
        }

    try:
        # Build update data with actual values (not ISO strings)
        update_data = {}
        if name and name != event.name:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if max_team_size is not None and max_team_size != event.max_team_size:
            update_data["max_team_size"] = max_team_size
        if start_time is not None:
            update_data["start_time"] = start_time
        if end_time is not None:
            update_data["end_time"] = end_time
        if locked is not None:
            update_data["locked"] = locked

        event.update_event(**update_data)
    except IntegrityError as e:
        db.session.rollback()
        logger.warning(
            "Event update failed - database constraint violation",
            extra={
                "context": {
                    "event_id": event_id,
                    "changes_made": changes_made,
                    "error": str(e),
                }
            },
        )
        return {
            "success": False,
            "error": "Invalid event time configuration. Both start_time and end_time must be provided together, and start_time must be before end_time.",
        }

    logger.info(
        "Event updated successfully",
        extra={
            "context": {
                "event_id": event_id,
                "changes_made": changes_made,
            }
        },
    )

    return {
        "success": True,
        "event": {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "max_team_size": event.max_team_size,
            "start_time": event.start_time.isoformat() if event.start_time else None,
            "end_time": event.end_time.isoformat() if event.end_time else None,
            "locked": event.locked,
        },
        "message": "Event updated successfully",
    }


def _validate_max_team_size_change(event, new_max_size, changes_made):
    """Validate max team size change against existing teams and log impact.

    Args:
        event: The event being updated
        new_max_size: The new maximum team size
        changes_made: Dictionary to track changes

    Returns:
        dict: Success status and error message if validation fails
    """
    largest_team_size = db.session.query(func.max(Team.member_count)).filter(Team.event_id == event.id).scalar() or 0

    if new_max_size < largest_team_size:
        return {
            "success": False,
            "error": f"Cannot set max size to {new_max_size}. A team in this event already has {largest_team_size} members.",
        }

    changes_made["max_team_size"] = {
        "old": event.max_team_size,
        "new": new_max_size,
    }

    affected_teams = Team.query.filter_by(event_id=event.id).count()
    logger.info(f"Updated max team size affects {affected_teams} teams in event '{event.name}'")

    return {"success": True}
