"""
Handles joining an event by creating a new team.
"""

from typing import Any
from flask import g
from sqlalchemy.exc import IntegrityError

from ...core import BusinessLogicError
from .create_demographic import create_demographic
from ...team.controllers.create_team import create_team


def join_event_new_team() -> dict[str, Any]:
    """Join an event by creating a new team.

    Returns:
        dict: Team and demographic data
    """
    data = g.validated_data
    event = g.event
    user = g.user

    team_result = create_team(name=data["team_name"])

    team = team_result["team"]

    try:
        demo_result = create_demographic(user.id, event.id)

        return {
            "team": team,
            "demographic": demo_result["demographic"],
        }
    except IntegrityError:
        team.disband_team()
        raise BusinessLogicError("You have already registered for this event")
