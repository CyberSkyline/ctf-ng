"""
Main controller for coordinating the event joining process.
"""

from typing import Any
from flask import g

from ...core import NotFoundError, ValidationError
from ...team.models.Team import Team
from .join_event_existing_team import join_event_existing_team
from .join_event_new_team import join_event_new_team


def join_event_controller() -> dict[str, Any]:
    """Main controller for the event joining process.

    Returns:
        dict: Team and demographic data
    """
    data = g.validated_data

    if "invite_code" in data:
        team = Team.find_by_invite_code(data["invite_code"])
        if not team:
            raise NotFoundError("Invalid invite code")
        if team.event_id != g.event.id:
            raise ValidationError("This invite code is for a different event")
        g.team = team

        return join_event_existing_team()
    else:
        return join_event_new_team()
