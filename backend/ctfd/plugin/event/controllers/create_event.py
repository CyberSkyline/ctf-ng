"""
/backend/ctfd/plugin/event/controllers/create_event.py
Contains the business logic for creating and persisting a new event.
"""

from typing import Any
from datetime import datetime


from ...utils.logger import get_logger
from ..models.Event import Event

logger = get_logger(__name__)


def create_event(
    name: str,
    description: str | None = None,
    max_team_size: int | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    locked: bool = False,
) -> dict[str, Any]:
    """Creates a new training event with the given config.

    Args:
        name (str): The unique name for the event.
        description (str, optional): A description of the event's purpose. Defaults to None.
        max_team_size (int, optional): Maximum team size for teams in this event. Defaults to config.MAX_TEAM_SIZE.
        start_time (datetime, optional): When the event starts. Defaults to None.
        end_time (datetime, optional): When the event ends. Defaults to None.
        locked (bool, optional): Whether the event is locked from new teams. Defaults to False.

    Returns:
        dict: Success status, event object, and confirmation message or error info.
    """

    existing_event = Event.query.filter_by(name=name).first()
    if existing_event:
        logger.warning(
            "Event creation failed - name already exists",
            extra={
                "context": {
                    "event_name": name,
                    "existing_event_id": existing_event.id,
                }
            },
        )
        return {"success": False, "error": f"Event '{name}' already exists"}

    event = Event.create_event(
        name=name,
        description=description,
        max_team_size=max_team_size,
        start_time=start_time,
        end_time=end_time,
        locked=locked,
    )

    logger.info(
        "Event created successfully",
        extra={
            "context": {
                "event_id": event.id,
                "event_name": name,
                "description": description,
                "max_team_size": max_team_size,
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
                "locked": locked,
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
        "message": f"Event '{name}' created successfully",
    }
