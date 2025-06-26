"""
Handles joining an event by joining an existing team.
"""

from typing import Any
from flask import g
from sqlalchemy.exc import IntegrityError

from ...core import BusinessLogicError
from .create_demographic import create_demographic
from ...team.controllers.join_team import join_team


def join_event_existing_team() -> dict[str, Any]:
    """Join an existing team in an event using an invite code.

    Returns:
        dict: Team and demographic data
    """
    team = g.team
    event = g.event
    user = g.user

    team_result = join_team(user.id, team.invite_code)
    team_member = team_result["team_member"]

    try:
        demo_result = create_demographic(user.id, event.id)

        return {
            "team": team,
            "team_member": team_member,
            "demographic": demo_result["demographic"],
        }
    except IntegrityError:
        team_member.remove_team_member()
        raise BusinessLogicError("You have already registered for this event")
