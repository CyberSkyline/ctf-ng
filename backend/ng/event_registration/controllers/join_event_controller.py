"""
Main controller for coordinating the event joining process.
"""

from typing import Any
from flask import g
from sqlalchemy.exc import IntegrityError

from ...core import NotFoundError, ValidationError
from ...team.models.Team import Team
from ...core import BusinessLogicError
from ...team.controllers.join_team import join_team
from ...team.controllers.create_team import create_team
from ...event_registration.models.Demographic import Demographic

def join_event_controller(data: dict[str, Any]) -> dict[str, Any]:
    """Main controller for the event joining process.

    Returns:
        dict: Team and demographic data
    """
    if "invite_code" in data:
        team = Team.find_by_invite_code(data["invite_code"])
        if not team:
            raise NotFoundError("Invalid invite code")
        if team.event_id != g.event.id:
            raise ValidationError("This invite code is for a different event")

        return _join_event_existing_team(team, g.event, g.user)
    else:
        return _join_event_new_team(g.validated_data["team_name"], g.event, g.user)


def _join_event_existing_team(team, event, user) -> dict[str, Any]:
    team_result = join_team(user.id, team.invite_code)
    team_member = team_result["team_member"]

    try:
        demographic = Demographic.create_demographic(user_id=user.id, event_id=event._id)

        return {
            "team": team,
            "team_member": team_member,
            "demographic": demographic,
        }
    except IntegrityError:
        team_member.remove_team_member()
        raise BusinessLogicError("You have already registered for this event")
    
def _join_event_new_team(team_name, event, user) -> dict[str, Any]:
    team_result = create_team(name=team_name)

    team = team_result["team"]

    try:
        demographic = Demographic.create_demographic(user_id=user.id, event_id=event._id)

        return {
            "team": team,
            "demographic": demographic,
        }
    except IntegrityError:
        team.disband_team()
        raise BusinessLogicError("You have already registered for this event")
