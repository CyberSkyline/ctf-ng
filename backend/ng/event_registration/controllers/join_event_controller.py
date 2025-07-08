"""
Main controller for coordinating the event joining process.
"""

from CTFd.models import db

from ...core import NotFoundError, ValidationError
from ...team.models.Team import Team
from ...event_registration.models.Demographic import Demographic
from ...event.models.Event import Event
from ...user.models.User import User

def join_event_controller(event: Event, user : User, invite_code : str | None, team_name : str | None) -> None:
    """Main controller for the event joining process.
    """
    if not invite_code or not team_name:
        raise ValidationError("Either invite_code or team_name must be provided")
    
    try:
        Demographic.create_demographic(user_id=user.id, event_id=event._id, commit=False)
        if invite_code:
            team = Team.find_by_invite_code(invite_code)
            if not team:
                raise NotFoundError(f"Team with invite code {invite_code} not found")
            
            team.add_member(user.id, commit=False)
        else:
            Team.create_team_with_captain(
                name=team_name,
                event_id=event._id,
                creator_id=user.id,
                ranked=True,
                commit=False,
            )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
